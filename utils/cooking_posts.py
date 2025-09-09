import asyncio

from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import InputMediaPhoto
from aiogram import Bot
from vk_api import ApiError

from utils.logger import logger, log
from utils.ai import send_ai_request
from utils.string_funcs import *
from utils.file_system import write_info, get_json
from utils.parsing import get_info, get_posts
from utils.messages import REASON, ERROR, CAPTION

from config import TG_MAIN, TG_TRASH


def get_caption(post: dict, group_name: str, description: str):
    if post["from_id"] > 0:
        user_id = post["from_id"]
        user = get_info(user_id, 'user')[0]
        user_info = f'👤 {user['first_name']} {user['last_name']} | <code>{post["from_id"]}</code>\n'
    else:
        user_info = ''
    caption = CAPTION.format(description=description, group_name=group_name, group_id=-post['owner_id'],
                             date=format_date(post['date']),
                             post_id=post['id'], text=post['text'], user_info=user_info)
    return caption


async def skip_message(post: dict, bot: Bot, reason: str, send: bool = False) -> None:
    log(reason[reason.find(' ') + 1:])
    write_info(-post['owner_id'], post['id'])
    log(f'Сохранил ID этого поста — {post['id']}.')

    if send:
        message_text = get_caption(post, get_info(-post['owner_id'])[0]['name'], reason)
        try:
            await bot.send_message(chat_id=TG_TRASH, text=message_text, parse_mode='HTML',
                                   disable_web_page_preview=True)
            log('Отправил готовое сообщение в Telegram.\n')
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            await bot.send_message(chat_id=TG_TRASH, text=message_text, parse_mode='HTML',
                                   disable_web_page_preview=True)
            log('Отправил готовое сообщение в Telegram.\n')


async def receive_last_posts(last_post: dict) -> list:
    group = -last_post['owner_id']
    last_data = get_json()[str(group)]
    log(f'{justify(last_data)} — сохранённое ID последнего поста.')
    count = last_post['id'] - last_data

    if count == 0:
        log('Новых постов нет. Перехожу к проверке следующей группы.\n')
        return []
    elif count < 0 or count > 100:
        write_info(group, last_post["id"])
        log('Ошибка! Перезаписываю ID поста на актуальный.\n')
        return []
    else:
        posts = get_posts(group, count + 1)[::-1]
        if len(posts) == 1:
            new_posts = posts
        else:
            new_posts = []
            for post in posts:
                if post['id'] <= last_data or post.get('is_pinned', False):
                    continue
                new_posts.append(post)
        log(f'{justify(len(new_posts))} — кол-во новых постов.')
        return new_posts


async def check_text(post: dict, bot: Bot) -> bool:
    filters = get_json('filters')
    bw = find_string(post['text'], filters['bw'])
    ban_user = post['from_id'] in filters['ban']
    if bw or ban_user or post['text'] == '':
        if bw:
            reason = 'bw'
        elif ban_user:
            reason = 'ban'
        else:
            reason = 'repost'
        await skip_message(post, bot, REASON[reason].format(bw))
        return True
    return False


async def check_answer(answer: str, post: dict, bot: Bot) -> bool:
    filters = get_json('filters')
    raw_price = answer.split('┃')[1]
    digits = [symbol for symbol in raw_price if symbol.isdigit()]
    price = int(''.join(digits))

    tag = answer.split('│')[1].lower()
    reason = None

    if price > filters['price']:
        reason = REASON['overprice'].format(price=price, max_price=filters['price'])
    elif price == 0:
        reason = REASON['undefined_price']
    elif tag == 'другое':
        reason = REASON['not_rent']

    if reason:
        await skip_message(post, bot, reason, True)
        return True
    return False


async def send_mess(media_group, chat_id, bot, caption_mess, caption):
    try:
        args = {'chat_id': chat_id, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
        if media_group:
            await bot.send_media_group(chat_id=chat_id, media=media_group)
            if caption_mess:
                await bot.send_message(text=caption_mess, **args)
        else:
            await bot.send_message(text=caption, **args)
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await send_mess(media_group, chat_id, bot, caption_mess, caption)


async def send_post(answer: str, post: dict, bot: Bot, chat_id: str) -> None:
    caption = get_caption(post, get_info(-post['owner_id'])[0]['name'], answer)
    attachments = post['attachments']
    media_group, caption_mess = [], ''

    for i in range(len(attachments)):
        if attachments[i]['type'] == 'photo':
            if i != 0:
                caption = ''
            if len(caption) > 1024:
                captions = caption.split('\n\n<blockquote')
                caption = captions[0]
                caption_mess = '<blockquote' + captions[-1]
            media_group.append(
                InputMediaPhoto(media=attachments[i]['photo']['orig_photo']['url'], caption=caption,
                                parse_mode='HTML'))

    await send_mess(media_group, chat_id, bot, caption_mess, caption)


async def handle_post(post: dict, bot: Bot) -> None:
    logger.info('')
    log('==========[ВЫШЕЛ НОВЫЙ ПОСТ]==========')
    log(f'{post['id']} — ID нового поста.')

    if await check_text(post, bot):
        return

    log('Текст поста отправляется AI, ожидаю ответа...')
    answer = await send_ai_request(post['text'])
    log('Ответ от AI был получен.')

    if await check_answer(answer, post, bot):
        return

    await bot.send_chat_action(chat_id=TG_MAIN, action="typing")

    await send_post(answer, post, bot, TG_MAIN)
    log('Отправил готовое сообщение в Telegram.')
    write_info(-post['owner_id'], post['id'])
    log('Сохранил ID этого поста. Готово!\n')


async def handle_posts(bot: Bot):
    logger.info('==================[НАЧАЛО НОВОЙ ПРОВЕРКИ]===================')
    for group, last_post in get_json().items():
        logger.info('Проверяю последние посты в группе:')
        log(f'{justify(group)} — ID группы.')
        try:
            first_posts = get_posts(group, 2)
            first_post = first_posts[int(first_posts[0].get('is_pinned') == 1)]

            log(f'{justify(first_post["id"])} — ID последнего поста.')

            if last_post is None:
                log('============[НОВАЯ ГРУППА]============')
                write_info(group, first_post["id"])
                log('Сохранил ID последнего поста.')
                continue

            posts = await receive_last_posts(first_post)

            if not posts:
                continue
            for post in posts:
                await handle_post(post, bot)

            log('Все посты в группе проверены! Перехожу к следующей...\n')
        except ApiError:
            log('Частная группа, необходимо подписаться. Пропускаю.\n')
            continue
        except Exception as err:
            error = ERROR.format(err)
            logger.error(error)
            await bot.send_message(chat_id=TG_TRASH, text=error)
            continue
    logger.info(f'Все группы проверены. Проверю снова через {get_json("filters")['delay']} сек. Сплю :)')
    logger.info('======================[КОНЕЦ ПРОВЕРКИ]======================')
    log(' \n')
