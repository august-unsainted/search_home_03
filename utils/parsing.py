import vk_api
import time
from aiogram.types import InputMediaPhoto
from aiogram import Bot

from config import VK_KEY, VK_GROUP_ID, TG_CHAT
from utils.ai import send_ai_request

LINK = f'https://vk.com/club{VK_GROUP_ID}?w=wall-{VK_GROUP_ID}'
LAST_POST_ID = None
vk_session = vk_api.VkApi(token=VK_KEY)
vk = vk_session.get_api()


async def get_posts(bot: Bot):
    global LAST_POST_ID
    try:
        response = vk.wall.get(domain="club" + VK_GROUP_ID, offset=0, count=1)
        if "error" in response:
            print(f"\tОшибка: {response['error']['error_msg']}")
            return

        post = response["items"][0]

        if LAST_POST_ID is None:
            LAST_POST_ID = post["id"]
            return

        if post["id"] > LAST_POST_ID:
            await bot.send_chat_action(chat_id=TG_CHAT, action="typing")
            answer = None
            while not answer:
                answer = await send_ai_request(post['text'])

            caption = f'{answer}\n\n{LINK}_{post['id']}'
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

            if media_group:
                await bot.send_media_group(chat_id=TG_CHAT, media=media_group)
            else:
                await bot.send_message(chat_id=TG_CHAT, text=caption)

        LAST_POST_ID = post["id"]

    except Exception as e:
        print(f"\tОшибка: {e}\n")
        

async def parse(bot):
    while True:
        await get_posts(bot)
        time.sleep(60)
