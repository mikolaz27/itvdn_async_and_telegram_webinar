import os
import sys

import django

from telegram_bot.common import MODE_SEARCH, MODE_UPDATE


if __name__ == '__main__':
    mode = MODE_SEARCH
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode not in (MODE_SEARCH, MODE_UPDATE):
            raise RuntimeError('Only one of the modes is supported: {}')

    os.environ.setdefault('TG_BOT_MODE', mode)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

    from telegram_bot.bot import run_bot
    run_bot()
