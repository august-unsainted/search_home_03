from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from utils.file_system import write_info, del_group, test_groups
from utils.filters import filters_actions, get_filters_list
from utils.parsing import get_group_id, get_group_list

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(str(message.chat.id))


# @router.message(Command(commands=['add', 'del']))
# async def cmd_add_del(message: Message):
#     group_id = await get_group_id(message.text.split(' ')[1])
#     if message.text.startswith('/add'):
#         write_info(group_id)
#         action = 'была добавлена в список'
#     else:
#         action = 'была удалена из списка' if del_group(group_id) else 'не в списке'
#     await message.answer(f'📌 Группа «<code>{group_id}</code>» {action} отслеживаемых!', parse_mode='HTML')


@router.message(Command('list'))
async def cmd_list(message: Message):
    await message.answer(await get_group_list(), disable_web_page_preview=True, parse_mode='HTML')


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
