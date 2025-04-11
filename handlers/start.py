from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from utils.file_system import write_info, del_group, filters_actions, get_filters_list
from utils.parsing import get_group_id, get_group_list, get_ban_list

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(str(message.chat.id))


@router.message(Command(commands=['add', 'del']))
async def cmd_add_del(message: Message):
    group_id = await get_group_id(message.text.split(' ')[1])
    if message.text.startswith('/add'):
        write_info(group_id)
    else:
        del_group(group_id)
    await message.answer('Готово!')


@router.message(Command('list'))
async def cmd_list(message: Message):
    await message.answer(await get_group_list(), disable_web_page_preview=True)


@router.message(Command(commands=['ban', 'unban', 'addbw', 'delbw', 'addlw', 'dellw']))
async def cmd_filters_actions(message: Message):
    await message.answer(filters_actions(message.text), parse_mode='HTML')


@router.message(Command('banlist'))
async def cmd_banlist(message: Message):
    answer = await get_ban_list()
    if not answer:
        answer = 'Банлист пуст! 😨'
    await message.answer(answer, parse_mode='HTML')


@router.message(F.text.endswith('list'))
async def cmd_list(message: Message):
    answer = get_filters_list(message.text)
    if not answer:
        answer = 'Список пуст! 😨'
    await message.answer(answer, parse_mode='HTML')
