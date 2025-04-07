from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from utils.file_system import write_info, del_group
from utils.parsing import get_group_id, get_group_list

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
