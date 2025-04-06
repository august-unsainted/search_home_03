import vk_api
import time
from aiogram.types import InputMediaPhoto
from aiogram import Bot

from config import VK_KEY, TG_MAIN, TG_TRASH
from utils.ai import send_ai_request
from utils.file_system import get_json, write_id

# LAST_POST_ID = None
vk_session = vk_api.VkApi(token=VK_KEY)
vk = vk_session.get_api()


async def receive_last_posts(last_post: dict, group: str) -> list:
    last_data = get_json()[str(group)]
    print('\tID последнего записанного поста:', last_data)
    if last_data != last_post['id']:
        count = last_post['id'] - last_data
    else:
        count = 0
    print('\tКоличество вышедших постов, после последнего записанного ID:', count)
    if count == 0:
        return []
    else:
        return vk.wall.get(domain="club" + group, offset=0, count=count)['items']


async def get_posts(bot: Bot):
    # global LAST_POST_ID
    try:
        for group, last_post in get_json().items():
            print('Сканирую...')
            response = vk.wall.get(domain="club" + group, offset=0, count=1)
            if "error" in response:
                print(f"\tОшибка в запросе: {response['error']['error_msg']}")
                return

            first_post = response["items"][0]
            print('\n\tПост найдет! Его айди:', first_post["id"])

            if last_post is None:
                write_id(group, first_post["id"])
                print('\tЗаписал этот айдишник к себе')
                return

            posts = await receive_last_posts(first_post, group)
            print('\tПроверяю все вышедшие посты после записанного...')
            print('\tКол-во полученных сейчас постов:', len(posts))
            for post in posts:
                # await bot.send_chat_action(chat_id=TG_CHAT, action="typing")
                # answer = None
                print('\tЖду ответ от нейронки...')
                # while not answer:
                answer = await send_ai_request(post['text'])
                print('\tПолучил ответ от нейронки!')

                # chat_id = TG_MAIN if '🟢' in answer else TG_TRASH
                # print('TG_MAIN' if '🟢' in answer else 'TG_TRASH')
                # print(chat_id)

                link = f'https://vk.com/club{group}?w=wall-{group}'
                caption = f'{answer}\n\n{link}_{post['id']}'
                attachments = post['attachments']
                media_group = []

                i = 0
                for media in attachments:
                    if media['type'] == 'photo':
                        if i != 0:
                            caption = ""
                        else:
                            i = 1
                        media_group.append(InputMediaPhoto(media=media['photo']['orig_photo']['url'], caption=caption))

                chat_id = TG_MAIN if '🟢' in answer else TG_TRASH
                if media_group:
                    await bot.send_media_group(chat_id=chat_id, media=media_group)
                else:
                    await bot.send_message(chat_id=chat_id, text=caption)

                # write_id(group, post['id'])

            write_id(group, first_post['id'])

    except Exception as e:
        print(f"\tОшибка в функции: {e}\n")
        

async def parse(bot):
    while True:
        await get_posts(bot)
        time.sleep(10)
