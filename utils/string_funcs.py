import pytz
import locale
import humanize

from datetime import datetime, timedelta

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
_t = humanize.i18n.activate("ru_RU")
local_tz = pytz.timezone('Asia/Irkutsk')


def find_string(text: str, strings: list) -> str:
    for string in strings:
        if string.lower() in text.lower():
            return string
    return ''


def replace_strings(string: str, strings_to_replace: list) -> str:
    for substring in strings_to_replace:
        string = string.replace(substring, '')
    return string


def justify(data: int | str) -> str:
    return str(data).ljust(10, " ")


def format_date(date: int):
    date = datetime.fromtimestamp(float(date), local_tz)
    time = date.strftime(" в %H:%M")
    day_name = humanize.naturalday(date, format='%d %B').capitalize() + time
    return day_name


def find_plural(obj: str):
    return obj.replace('ель', 'ели').replace('во', 'ва').replace('па', 'пы')
