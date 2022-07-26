import re
from datetime import datetime


def validate_datetime_input(imput_data):
    datetime.strptime(imput_data, '%Y-%m-%d').date()
    return True


def validate_email(email):
    EMAIL_REGEX = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(EMAIL_REGEX, email.lower()) is not None
