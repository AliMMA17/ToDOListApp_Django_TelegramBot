# main.py
import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TOKEN
from loader import dp  # central dispatcher

# Import handlers to register them
import handlers.command_handlers  
import handlers.task_handlers  

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
