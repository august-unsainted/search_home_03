import datetime
import pytz
import vk_api
import asyncio
import locale

from aiogram.types import InputMediaPhoto
from aiogram import Bot

from utils.logger import logger
from config import VK_LOGIN, VK_PASS, TG_MAIN, TG_TRASH
from utils.ai import send_ai_request
from utils.file_system import get_json, write_info

vk_session = vk_api.VkApi(login=VK_LOGIN, password=VK_PASS)
vk_session.auth(token_only=True)
vk = vk_session.get_api()

SLEEP_TIME = 120
FILTERS = get_json('filters')

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
local_tz = pytz.timezone('Asia/Irkutsk')


def find_str(text: str, strings: list) -> str:
    text = text.lower()
    for string in strings:
        if string in text:
            return string
    return ''


async def skip_message(group: str, post: dict, bot: Bot, reason: str) -> None:
    logger.info('\t\t' + reason)
    write_info(group, post['id'])
    logger.info('\t\tСохранил ID этого поста. Готово!')
    logger.info(' ')
    date = datetime.datetime.fromtimestamp(float(post['date']), local_tz).strftime("%d %B в %H:%M")
    await bot.send_message(chat_id=TG_TRASH,
                           text=(f'{date}\n\n'
                                 f'{reason}\n\n'
                                 f'<blockquote expandable>{post['text']}</blockquote>\n\n'
                                 f'<a href="https://vk.com/club{group}?w=wall-{group}_{post["id"]}">Перейти к объявлению</a>'),
                           parse_mode='HTML')


async def receive_last_posts(last_post: dict, group: str) -> list:
    last_data = get_json()[str(group)]
    logger.info(f'\t\t{str(last_data).ljust(9, " ")} — сохранённое ID последнего поста.')
    if last_data != last_post['id']:
        count = last_post['id'] - last_data
    else:
        count = 0

    if count == 0:
        logger.info(f'\t\tНовых постов нет. Перехожу к проверке следующей группы.')
        logger.info(" ")
        return []
    else:
        logger.info(f'\t\t{str(count).ljust(9, " ")} — кол-во новых постов.')
        logger.info(" ")
        return vk.wall.get(domain="club" + group, offset=0, count=count)['items']


async def get_posts(bot: Bot):
    try:
        logger.info('==================[НАЧАЛО НОВОЙ ПРОВЕРКИ]===================')
        for group, last_post in get_json().items():
            logger.info('Проверяю последние посты в группе:')
            response = vk.wall.get(domain="club" + group, offset=0, count=1)
            if "error" in response:
                logger.error(f"\t\tОшибка в запросе: {response['error']['error_msg']}.")
                await bot.send_message(chat_id=TG_TRASH, text=response['error']['error_msg'])
                return

            first_post = response["items"][0]
            logger.info(f'\t\t{group.ljust(9, " ")} — ID группы.')
            logger.info(f'\t\t{str(first_post["id"]).ljust(9, " ")} — ID последнего поста.')

            if last_post is None:
                logger.info('\t\t============[НОВАЯ ГРУППА]============')
                write_info(group, first_post["id"])
                logger.info('\t\tСохранил ID последнего поста.')
                logger.info(' ')
                continue

            posts = await receive_last_posts(first_post, group)
            for post in posts:
                orig_text = post['text']
                logger.info('\t\t==========[ВЫШЕЛ НОВЫЙ ПОСТ]==========')
                blacklist = find_str(orig_text, FILTERS['blacklist'])
                ban_user = post['from_id'] in FILTERS['ban']
                if blacklist or ban_user or orig_text == '':
                    if blacklist:
                        reason = f'Blacklist: «{blacklist}».'
                    elif ban_user:
                        reason = f'Blacklist: пользователь с ID {post['from_id']} в бане.'
                    else:
                        reason = 'Blacklist: репост.'
                    await skip_message(group, post, bot, reason)
                    continue

                logger.info('\t\tТекст поста отправляется AI, ожидаю ответа...')
                answer = await send_ai_request(orig_text)
                logger.info('\t\tОтвет от AI был получен.')
                price = int(''.join([symbol for symbol in answer.split('┃')[1] if symbol.isdigit()]))

                if price > FILTERS['price']:
                    await skip_message(group, post, bot, f'Blacklist: превышает бюджет ({price} > {FILTERS["price"]}).')
                    continue

                chat_id = TG_MAIN if find_str(answer, ['🟢', '🟠']) or find_str(orig_text,
                                                                              FILTERS['whitelist']) else TG_TRASH
                await bot.send_chat_action(chat_id=chat_id, action="typing")

                link = f'https://vk.com/club{group}?w=wall-{group}'

                group_name = vk.groups.getById(group_id=group)[0]['name']

                date = datetime.datetime.fromtimestamp(float(post['date']), local_tz).strftime("%d %B в %H:%M")

                caption = (f'{date}\n'
                           f'<b>{group_name} | Group ID: <code>{group}</code></b>\n\n'
                           f'{answer}\n\n'
                           f'—————————\n\n'
                           f'User ID: <code>{post['from_id'] if post['from_id'] > 0 else "Нет"}</code> | <a href="{link}_{post['id']}">Перейти к объявлению</a>\n\n'
                           f'<blockquote expandable>{orig_text}</blockquote>')
                attachments = post['attachments']
                media_group = []

                i = 0
                caption_continue = None

                for media in attachments:
                    if media['type'] == 'photo':
                        if i != 0:
                            caption = ""
                        else:
                            i = 1

                        if len(caption) > 1024:
                            captions = caption.split('\n\n<blockquote')
                            caption = captions[0]
                            caption_continue = '<blockquote' + captions[-1]

                        media_group.append(
                            InputMediaPhoto(media=media['photo']['orig_photo']['url'], caption=caption,
                                            parse_mode='HTML'))
                if media_group:
                    await bot.send_media_group(chat_id=chat_id, media=media_group)
                    if caption_continue:
                        await bot.send_message(chat_id=chat_id, text=caption_continue, parse_mode='HTML')
                else:
                    await bot.send_message(chat_id=chat_id, text=caption, parse_mode='HTML')
                logger.info('\t\tОтправил готовое сообщение в Telegram.')
                write_info(group, post['id'])
                logger.info('\t\tСохранил ID этого поста. Готово!')
                logger.info(' ')
            write_info(group, first_post['id'])
        logger.info(f'Все группы проверены. Проверю снова через {SLEEP_TIME} сек. Сплю :)')
        logger.info('======================[КОНЕЦ ПРОВЕРКИ]======================')
        logger.info(' ')
        logger.info(' ')
    except Exception as e:
        error = f"\t\tОшибка в функции: {e}.\n"
        logger.error(error)
        await bot.send_message(chat_id=TG_TRASH, text=error)


async def parse(bot):
    while True:
        await get_posts(bot)
        await asyncio.sleep(SLEEP_TIME)


async def get_group_id(link: str) -> int:
    if 'https' in link:
        domain = link.replace('https://vk.com/', '').split('?')[0]
        group = vk.groups.getById(group_id=domain)
        return group[0]['id']
    return int(link)


async def get_group_list() -> str:
    groups = ', '.join(get_json().keys())
    groups_objs = vk.groups.getById(group_ids=groups)
    return 'Отслеживаемые сообщества:\n\n' + ''.join(
        [f"ID: {group['id']}\n"
         f"Название: {group['name']}\n"
         f"Ссылка: https://vk.com/{group['screen_name']}\n\n" for group in
         groups_objs])


async def get_ban_list() -> str:
    data = get_json('filters')['ban']
    users = vk.users.get(user_ids=str(data)[1:-1])
    banlist = [f'<b>⛔️ Заблокированные пользователи</b>']
    for i in range(len(users)):
        banlist.append(f'{str(i + 1).rjust(2, "0")} | <code>{str(data[i]).ljust(9,' ')}</code> | {users[i]['first_name']} {users[i]['last_name']}')
    return '\n'.join(banlist)
