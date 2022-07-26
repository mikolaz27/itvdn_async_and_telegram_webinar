from django.contrib.admin import site

from telegram_bot.models import SearchHistory, Vehicle, User

site.register([SearchHistory, Vehicle, User])
