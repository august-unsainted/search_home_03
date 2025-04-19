from aiogram import Router
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message

from utils.file_system import get_json
from utils.filters import filters_actions, get_filters_list, tools_actions

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(str(message.chat.id))


@router.message(Command(commands=['spam', 'delay', 'price']))
async def cmds_set_values(message: Message, command: CommandObject):
    answer = tools_actions(command)
    await message.answer(answer, parse_mode='HTML')


@router.message(Command(commands=['groups', 'groups-', 'bw', 'bw-', 'ban', 'ban-']))
async def list_cmds(message: Message, command: CommandObject):
    if command.args:
        answer = filters_actions(command)
    elif command.command.endswith('-'):
        answer = '<b>Введите значения!</b>'
    else:
        answer = get_filters_list(command.command)
    await message.answer(answer, parse_mode='HTML')


@router.message(Command('price'))
async def cmd_price(message: Message):
    await message.answer(f'💰 Бюджет составляет {get_json('filters')['price']} руб.!', parse_mode='HTML')
