import random

from telegram import Update
from telegram.ext import Updater, CommandHandler, ContextTypes

SECRET = "5513792965:AAGwNoYCzrHLyMx2SZJlsWI5Hd5SAc6WPLw"
NAME = "itvdn_telegram_webinar_bot"
updater = Updater(token=SECRET)
dispatcher = updater.dispatcher

my_list = ['\"this is line1\"',
           '\"this is line2\"',
           '\"this is line3\"',
           '\"this is line4\"',
           '\"this is line5\"'
           ]

my_random = random.choice(my_list)


def func1():
    return my_random


def start(update: Update, context: ContextTypes):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=func1())


my_handler = CommandHandler('start', start)

dispatcher.add_handler(my_handler)

updater.start_polling()
