from aiogram import types

from telegram_bot.common import (
    BUTTON_SKIP,
    BUTTON_CANCEL,
)

keyboard_default = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
) \
    .add(BUTTON_SKIP) \
    .add(BUTTON_CANCEL)

keyboard_no_skip = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
) \
    .add(BUTTON_CANCEL)

keyboard_status = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
) \
    .add(BUTTON_SKIP) \
    .add(BUTTON_CANCEL)
