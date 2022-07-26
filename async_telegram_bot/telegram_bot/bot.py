import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from config.settings import TG_BOT_API_TOKEN
from config.settings import TG_BOT_MODE
from telegram_bot.common import MODE_SEARCH, MODE_UPDATE
from telegram_bot.flow_search import \
    register_handlers as register_handlers_search, \
    register_handlers_for_contact

logging.basicConfig(level=logging.INFO)

handlers = {
    MODE_SEARCH: (
        register_handlers_search,
        register_handlers_for_contact,
    ),
    # MODE_UPDATE: (
    #     register_handlers_update,
    #     register_handlers_create,
    #     register_handlers_common
    # )
}


def run_bot():
    # Initialize bot and dispatcher
    print(TG_BOT_API_TOKEN)
    bot = Bot(token=TG_BOT_API_TOKEN)
    storage = MemoryStorage()  # memory storage for input data
    dp = Dispatcher(bot, storage=storage)
    executor.start_polling(install_handlers(dp), skip_updates=False)


def install_handlers(dp):
    handler = handlers[TG_BOT_MODE.lower()]
    if isinstance(handler, (tuple, list)):
        for entry in handler:
            entry(dp)
    else:
        handler(dp)
    return dp
