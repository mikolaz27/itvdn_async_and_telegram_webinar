import typing
from enum import Enum

from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup

BUTTON_CANCEL = "❌ Скасувати ❌"
BUTTON_SKIP = "☛ Пропустити ☛"
BUTTON_MORE_STARTSWITH = "↡ Показати ще "
BUTTON_MORE = BUTTON_MORE_STARTSWITH + "({}/{}) ↡"
MSG_MISSING_DATA = '⚠ ДАННІ ВІДСУТНІ ⚠'
MSG_INVALID_DATA = '⚠ Невірні данні: {} ⚠'
MSG_CANCELED = "(Скасовано)"

MODE_SEARCH = 'search'
MODE_UPDATE = 'update'


NUM_RECORDS_LIMIT = 12

TG_TEXT_MESSAGE_LIMIT_BYTES = 4096


class BaseEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value[0], cls))

    @classmethod
    def by_value(cls, value):
        return [c for c in cls if c.value[0] == value][0]

    @classmethod
    def db_field_by_value(cls, value):
        return [c.value[1] for c in cls if c.value[0] == value][0]


class CustomState(State):
    def __init__(self, hint_to_enter: str, hint_to_exit: str, input_name: str,
                 normalize: typing.Callable[[str], str] = None,
                 validate: typing.Callable[[str], bool] = None,
                 keyboard: types.ReplyKeyboardMarkup = None):
        self.hint_to_enter = hint_to_enter
        self.hint_to_exit = hint_to_exit
        self.input_name = input_name
        self.normalize = normalize
        self.validate = validate
        self.keyboard = keyboard
        super().__init__()


class CustomStatesGroup(StatesGroup):
    @classmethod
    def get_state_obj(cls, state) -> CustomState:
        state_idx = cls.states_names.index(state)
        state_obj = cls.states[state_idx]
        return state_obj


def normalize_search_input(search_input):
    return ' '.join(
        x.lower().capitalize()
        for x in search_input.split()
    )


def normalize_name_input(name_input):
    return name_input.strip().lower().capitalize()


def auth(func):
    from config.settings import ADMIN_USER
    async def wrapper(message, *args, **kwarg):
        if message['from']['id'] != ADMIN_USER:
            return await message.reply("No access", reply=False)
        return await func(message, *args, **kwarg)
    return wrapper


async def tg_format_records(records, extra_fields=None, only_fields=None):
    result = '\n'.join([
        rec.tg_formatted(extra_fields=extra_fields, only_fields=only_fields)
        for rec in records
    ])[:TG_TEXT_MESSAGE_LIMIT_BYTES]
    return f"```{result}```"
