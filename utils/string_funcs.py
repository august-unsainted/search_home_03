import pytz
import locale

from datetime import datetime, timedelta

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
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
    now = datetime.now(tz=local_tz)
    date = datetime.fromtimestamp(float(date), local_tz).strftime("%d %B в %H:%M")
    for i in range(2):
        day = (now - timedelta(days=i)).strftime('%d %B')
        if day in date:
            date = f'{date.replace(day, 'Сегодня' if i == 0 else 'Завтра')}'
    return date


def find_plural(obj: str):
    return obj.replace('ель', 'ели').replace('во', 'ва').replace('па', 'пы')
