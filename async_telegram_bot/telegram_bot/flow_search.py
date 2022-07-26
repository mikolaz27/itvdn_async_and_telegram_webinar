from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from django.core.paginator import Paginator

from config.settings import BASE_DIR
from telegram_bot.common import (
    BUTTON_CANCEL,
    BUTTON_MORE,
    BUTTON_MORE_STARTSWITH,
    BUTTON_SKIP,
    NUM_RECORDS_LIMIT,
    MSG_MISSING_DATA,
    MSG_CANCELED,
    MSG_INVALID_DATA
)
from telegram_bot.common import tg_format_records, normalize_name_input, \
    CustomStatesGroup, CustomState
from telegram_bot.db_users import find_user_by_tg_id, create_user, \
    find_vehicle_by_vin
from telegram_bot.handlers import BaseHandler
from telegram_bot.keyboards import keyboard_no_skip, keyboard_default
from telegram_bot.models import SearchHistory, Vehicle
from telegram_bot.validators import validate_email


class Search(CustomStatesGroup):
    """Search flow states """
    waiting_for_detail = State()

    waiting_for_brand = CustomState(
        hint_to_enter="Пошук по бренду:",
        hint_to_exit="Бренд отримано",
        input_name="search_by_brand",
        normalize=normalize_name_input,
        keyboard=keyboard_no_skip,
    )
    waiting_for_model = CustomState(
        hint_to_enter="Введіть модель:",
        hint_to_exit="Модель отримано",
        input_name="search_by_model",
        normalize=normalize_name_input,
        keyboard=keyboard_no_skip,
    )
    waiting_for_comments = CustomState(
        hint_to_enter="Мета пошуку:",
        hint_to_exit="Мета пошуку отримана",
        input_name="comments",
        keyboard=keyboard_no_skip,
    )


class Contact(StatesGroup):
    """Input states for User """
    waiting_for_contact_input = State()
    waiting_for_email_input = State()


def register_handlers(dp):
    dp.register_message_handler(search_start, regexp='.*')
    dp.register_message_handler(search_start, commands='search_data',
                                state='*')
    dp.register_message_handler(search_cancel,
                                Text(equals=BUTTON_CANCEL, ignore_case=True),
                                state="*")
    dp.register_message_handler(search_more_records,
                                Text(startswith=BUTTON_MORE_STARTSWITH,
                                     ignore_case=True),
                                state="*")
    dp.register_message_handler(SearchHandler.skip_action,
                                Text(equals=BUTTON_SKIP, ignore_case=True),
                                state="*")
    dp.register_message_handler(start_mode_search, commands=['start'],
                                state='*')

    dp.register_message_handler(search_show_details,
                                state=Search.waiting_for_detail)

    dp.register_message_handler(SearchHandler.default_action,
                                state=[
                                    Search.waiting_for_brand,
                                    Search.waiting_for_model,
                                    Search.waiting_for_comments,
                                ])

    return dp


def register_handlers_for_contact(dp):
    dp.register_message_handler(share_contact_data_entered,
                                state=Contact.waiting_for_contact_input,
                                content_types=['contact'])
    dp.register_message_handler(share_contact_email_entered,
                                state=Contact.waiting_for_email_input)
    return dp


# ---------------------------------------------------------------------------------------------
# SEARCH
# ---------------------------------------------------------------------------------------------
async def start_mode_search(message: types.Message):
    await message.answer(text='Виберіть дію:\n'
                              '\nПошук: \t/search_data')


async def search_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(MSG_CANCELED,
                         reply_markup=types.ReplyKeyboardRemove())
    await search_start(message)


async def search_start(message: types.Message):
    if await exists_contact(message):
        await message.answer("Пошук по бренду:", reply_markup=keyboard_no_skip)
        await Search.waiting_for_brand.set()
    else:
        await share_contact(message)


async def search_more_records(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    current_page = user_data.get("current_page")
    paginator = user_data.get("paginator")

    records = paginator.page(current_page).object_list
    formatted_records = await tg_format_records(
        records=records,
    )
    await message.answer(formatted_records, parse_mode="MarkdownV2")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True,
                                         row_width=4)

    choices = [str(rec.vin) for rec in records]
    keyboard.add(*choices)
    if current_page < paginator.num_pages:
        keyboard.add(BUTTON_MORE.format(current_page, paginator.num_pages))
        await state.update_data(current_page=current_page + 1)
    await state.update_data(choices=choices)
    keyboard.add(BUTTON_CANCEL)
    await Search.waiting_for_detail.set()


async def find_and_create_if_missing(message: types.Message,
                                     state: FSMContext):
    user_data = await state.get_data()
    brand = user_data.get('search_by_brand', '')
    model = user_data.get('search_by_model', '')
    await message.answer(f"Пошук по даних...")

    records = await Vehicle.find_by_model_and_brand(model=model,
                                                    brand=brand)
    found = records is not None
    return found, records or ["Нічого не знайдено по заданим параметрам"]


async def search_final_step(message: types.Message, state: FSMContext):
    found, records = await find_and_create_if_missing(message, state)

    if found:
        await message.answer(f"Знайдена інформація: \n\n")
        if len(records) > 1:
            paginator = Paginator(records, NUM_RECORDS_LIMIT)
            current_page = 1
            await state.update_data(paginator=paginator,
                                    current_page=current_page)
            await search_more_records(message, state)
        else:
            message.text = str(records[0].vin)
            await state.update_data(choices=[message.text])
            await search_show_details(message, state)
    else:
        await message.answer(MSG_MISSING_DATA)

    user_data = await state.get_data()
    await dump_search_history(message, user_data, records[0])
    await state.finish()
    await search_start(message)


async def search_show_details(message: types.Message, state: FSMContext):
    search_input = message.text
    user_data = await state.get_data()
    if search_input not in user_data['choices']:
        await message.answer("Виберіть VIN:")
        return
    record = await find_vehicle_by_vin(search_input)

    formatted_record = await tg_format_records([record])
    await message.answer(formatted_record, parse_mode="MarkdownV2")

    if record.image is not None:
        await message.answer("Фото: \n")
        photo_path = f"{BASE_DIR}/{record.image.url}".replace('//', '/')
        await message.answer_photo(photo=open(f'{photo_path}',
                                              'rb'))


# ---------------------------------------------------------------------------------------------
# HANDLE USERS
# ---------------------------------------------------------------------------------------------
async def exists_contact(message: types.Message):
    user = await find_user_by_tg_id(message.chat['id'])
    return user is not None


async def get_contact(message: types.Message):
    user = await find_user_by_tg_id(message.chat['id'])
    return user


async def share_contact(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)
    reg_button = types.KeyboardButton(text="Поділитися контактом",
                                      request_contact=True)
    keyboard.add(reg_button)
    await Contact.waiting_for_contact_input.set()
    await message.answer(
        "Перед початком поділіться контактами для зворотнього зв'язку:",
        reply_markup=keyboard)


async def share_contact_data_entered(message: types.Message, state):
    await state.update_data(user_data={
        'username': message.chat.username,
        'tg_id': message.contact.user_id,
        'name': message.contact.full_name,
        'phone': message.contact.phone_number
    })

    await Contact.waiting_for_email_input.set()
    await message.answer("Також введіть свій email (*):")


async def share_contact_email_entered(message: types.Message, state):
    email_input = message.text
    if not validate_email(email_input):
        await message.reply(f"Невірний email.")
        await message.answer("Введіть свій email (*):")
        return

    user_data = await state.get_data()
    user_data = user_data['user_data']
    user_data['email'] = email_input

    await create_user(data=user_data)
    await message.answer("Ваш контакт збережений!")
    await state.finish()
    await search_start(message)


# ------------------------------------------------------------------------------------------------
# SEARCH HISTORY
# ------------------------------------------------------------------------------------------------
async def dump_search_history(message: types.Message, user_data, record):
    user = await get_contact(message)
    data = {
        'user': user,
        'vehicle': None if isinstance(record, str) else record,
        'comment': user_data['comments'],
    }
    await SearchHistory.create_record(data)


class SearchHandler(BaseHandler):
    states_class = Search
    on_final_state = search_final_step
    msg_invalid_data = MSG_INVALID_DATA
