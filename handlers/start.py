from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from utils.file_system import write_info, test_groups, get_json
from utils.filters import filters_actions, get_filters_list, replace_many

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(str(message.chat.id))


data = {
    'test': ['🧑‍💻', '‍🧑‍💻 У всех групп были сброшены позиции: {}.'],
    'delay': ['⏱️', '⏱️ Задержка парсинга была изменена {} сек.!'],
    'price': ['💰', '💰 Бюджет был изменен {} руб.!']
}


@router.message(Command(commands=['test', 'delay', 'setprice']))
async def cmds_set_values(message: Message):
    command, value = replace_many(message.text, ['/', 'set']).split(' ')
    emoji, onchange = data[command]
    if value.isdigit():
        if command == 'test':
            test_groups(value)
        else:
            old_value = get_json('filters')[command]
            write_info(command, int(value), 'filters')
            value = f'с {old_value} на {value}'
        answer = onchange.format(value)
    else:
        answer = f'{emoji} Ошибка: не поддерживаемое значение!'
    await message.answer(answer, parse_mode='HTML')


@router.message(F.text.startswith(('/list', '/add', '/del', '/ban', '/un',)))
async def list_cmds(message: Message):
    if message.text.startswith('/list'):
        answer = get_filters_list(message.text)
    else:
        answer = filters_actions(message.text)
    await message.answer(answer, parse_mode='HTML')


@router.message(Command('price'))
async def cmd_price(message: Message):
    await message.answer(f'💰 Бюджет составляет {get_json('filters')['price']} руб.!', parse_mode='HTML')
