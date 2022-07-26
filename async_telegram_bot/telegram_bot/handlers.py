import typing

from aiogram import types
from aiogram.dispatcher import FSMContext

from telegram_bot.common import CustomStatesGroup


class BaseHandler:
    states_class: CustomStatesGroup = None
    on_final_state: typing.Callable[[types.Message, FSMContext], typing.Any] = None
    msg_invalid_data = ''

    @classmethod
    async def skip_action(cls, message: types.Message, state: FSMContext):
        await message.answer("(Пропущено)")
        await cls.do_next(message, state)

    @classmethod
    async def default_action(cls, message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is None:
            return
        current_state_obj = cls.states_class.get_state_obj(await state.get_state())
        input_data = message.text
        if current_state_obj.normalize:
            input_data = current_state_obj.normalize(input_data)
        if current_state_obj.validate:
            try:
                current_state_obj.validate(input_data)
            except Exception as ex:
                extra_params = {'reply_markup': current_state_obj.keyboard} \
                    if current_state_obj.keyboard else {}
                await message.reply(cls.msg_invalid_data.format(f'{ex}'))
                await message.answer(current_state_obj.hint_to_enter, **extra_params)
                return

        await message.reply(current_state_obj.hint_to_exit)
        await state.update_data(**{current_state_obj.input_name: input_data})
        await cls.do_next(message, state)

    @classmethod
    async def do_next(cls, message: types.Message, state: FSMContext):
        current_state = await cls.states_class.next()

        if current_state is None:
            await cls.on_final_state(message, state)
        else:
            current_state_obj = cls.states_class.get_state_obj(await state.get_state())
            extra_params = {'reply_markup': current_state_obj.keyboard} \
                if current_state_obj.keyboard else {}
            await message.answer(current_state_obj.hint_to_enter, **extra_params)
