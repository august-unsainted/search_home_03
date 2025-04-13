import datetime
import pytz
import vk_api
import asyncio
import locale

from aiogram.types import InputMediaPhoto
from aiogram import Bot

from config import VK_LOGIN, VK_PASS, TG_MAIN, TG_TRASH
from utils.logger import logger
from utils.ai import send_ai_request
from utils.file_system import get_json, write_info

vk_session = vk_api.VkApi(login=VK_LOGIN, password=VK_PASS)
vk_session.auth(token_only=True)
vk = vk_session.get_api()

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
local_tz = pytz.timezone('Asia/Irkutsk')


def find_str(text: str, strings: list) -> str:
    for string in strings:
        if string.lower() in text.lower():
            return string
    return ''


def log(text: str) -> None:
    logger.info('\t\t' + text)
    if '\n' in text:
        logger.info('')
        
        
def justify(data: int | str) -> str:
    return str(data).ljust(9, " ")


async def skip_message(group: str, post: dict, bot: Bot, reason: str) -> None:
    log(reason[reason.find(' ') + 1:])
    write_info(group, post['id'])
    log('Сохранил ID этого поста. Готово!\n')
    date = datetime.datetime.fromtimestamp(float(post['date']), local_tz).strftime("%d %B в %H:%M")
    await bot.send_message(
        chat_id=TG_TRASH,
        text=(f'ID группы: <code>{group}</code>\n\n'
              f'{date}\n\n{reason}\n\n'
              f'<blockquote expandable>{post['text']}</blockquote>{"\n\n" if post["text"] else ""}'
              f'<a href="https://vk.com/club{group}?w=wall-{group}_{post["id"]}">Перейти к объявлению</a>'),
        parse_mode='HTML', disable_web_page_preview=True)


async def receive_last_posts(last_post: dict, group: str) -> list:
    last_data = get_json()[str(group)]
    log(f'{justify(last_data)} — сохранённое ID последнего поста.')
    count = last_post['id'] - last_data

    if count <= 0:
        if count == 0:
            write_info(group, last_post["id"])
            info = 'Сохранил ID последнего поста.'
        else:
            info = 'Новых постов нет. Перехожу к проверке следующей группы.'
        log(info + '\n')
        return []
    else:
        log(justify(count) + ' — кол-во новых постов.\n')
        return vk.wall.get(domain="club" + group, offset=0, count=count)['items'][::-1]


async def get_posts(bot: Bot):
    filters = get_json('filters')
    try:
        logger.info('==================[НАЧАЛО НОВОЙ ПРОВЕРКИ]===================')
        for group, last_post in get_json().items():
            logger.info('Проверяю последние посты в группе:')
            response = vk.wall.get(domain="club" + group, offset=0, count=1)
            if "error" in response:
                error = response['error']['error_msg']
                logger.error(f"\t\tОшибка в запросе: {error}.")
                await bot.send_message(chat_id=TG_TRASH, text=error)
                return

            first_post = response["items"][0]
            log(f'{justify(group)} — ID группы.')
            log(f'{justify(first_post["id"])} — ID последнего поста.')

            if last_post is None:
                log('============[НОВАЯ ГРУППА]============')
                write_info(group, first_post["id"])
                log('Сохранил ID последнего поста.')
                continue

            posts = await receive_last_posts(first_post, group)
            for post in posts:
                orig_text = post['text']
                log('==========[ВЫШЕЛ НОВЫЙ ПОСТ]==========')
                blacklist = find_str(orig_text, filters['bw'])
                ban_user = post['from_id'] in filters['ban']
                if blacklist or ban_user or orig_text == '':
                    if blacklist:
                        reason = f'🚫 Запрещенное слово «{blacklist}».'
                    elif ban_user:
                        reason = f'⛔️ Пользователь с ID {post['from_id']} в бане.'
                    else:
                        reason = '📣 Репост.'
                    await skip_message(group, post, bot, reason)
                    continue

                log('Текст поста отправляется AI, ожидаю ответа...')
                answer = await send_ai_request(orig_text)
                log('Ответ от AI был получен.')
                price = int(''.join([symbol for symbol in answer.split('┃')[1] if symbol.isdigit()]))
                tag = answer.split('│')[1].lower()

                if price > filters['price'] or tag == 'другое':
                    await skip_message(
                        group, post, bot,
                        f'🗑 Не является объявлением о сдаче квартиры/комнаты.'
                        if tag == 'другое' else f'💰 Превышает бюджет: {price} > {filters["price"]}.'
                    )
                    continue

                chat_id = TG_MAIN if find_str(answer, ['🟢', '🟠']) or find_str(orig_text,
                                                                              filters['lw']) else TG_TRASH
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
                log('Отправил готовое сообщение в Telegram.')
                write_info(group, post['id'])
                log('Сохранил ID этого поста. Готово!\n')
            write_info(group, first_post['id'])
        logger.info(f'Все группы проверены. Проверю снова через {get_json("filters")['delay']} сек. Сплю :)')
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
        await asyncio.sleep(get_json("filters")['delay'])


def get_group_id(link: str) -> int:
    if 'https' in link:
        domain = link.replace('https://vk.com/', '').split('?')[0]
        group = vk.groups.getById(group_id=domain)
        return group[0]['id']
    return int(link)


def get_groups() -> list:
    groups = ', '.join(get_json().keys())
    return vk.groups.getById(group_ids=groups)


def get_users(data: list) -> list:
    return vk.users.get(user_ids=str(data)[1:-1])
