import asyncio
from aiogram import Bot, Dispatcher

from utils.logger import logger
from utils.file_system import get_json
from utils.cooking_posts import handle_posts
from handlers import start
from config import TG_TOKEN

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()


async def parse():
    while True:
        await handle_posts(bot)
        await asyncio.sleep(get_json("filters")['delay'])


async def main():
    dp.include_routers(start.router)
    logger.info('Бот включен :)')
    logger.info(' ')
    asyncio.create_task(parse())
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Бот выключен :(')
