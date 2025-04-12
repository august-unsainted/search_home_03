from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from utils.file_system import write_info, test_groups
from utils.filters import filters_actions, get_filters_list

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(str(message.chat.id))


@router.message(Command('delay'))
async def cmd_test(message: Message):
    delay = message.text.replace('/delay ', '')
    if delay.isdigit():
        write_info('sleep', int(delay), 'filters')
        answer = 'Готово!'
    else:
        answer = 'Значение не подходит!'
    await message.answer(answer, parse_mode='HTML')


@router.message(F.text.startswith(('/add', '/del', '/ban', '/un')))
async def cmd_filters_actions(message: Message):
    await message.answer(filters_actions(message.text), parse_mode='HTML')


@router.message(F.text.startswith('/list'))
async def cmd_list(message: Message):
    answer = get_filters_list(message.text)
    await message.answer(answer, parse_mode='HTML')


@router.message(Command('test'))
async def cmd_test(message: Message):
    test_groups(message.text.replace('/test ', ''))
    await message.answer('Готово!', parse_mode='HTML')
