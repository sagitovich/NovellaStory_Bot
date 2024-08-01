import logging
from db.db_gino import db
from config import BOT_TOKEN
from config import POSTGRES_URI
from aiogram import Bot, Dispatcher
from handlers import register_commands
from aiogram.types import BotCommand, BotCommandScopeDefault

logger = logging.getLogger(__name__)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
register_commands(dp)


async def start_bot():
    await bot.set_my_commands(
        commands=[
            BotCommand(command='/start', description='Запуск игры')
        ],
        scope=BotCommandScopeDefault()
    )
    await db.set_bind(POSTGRES_URI)
    await db.gino.create_all()
    logger.info("Таблицы созданы.")
    await dp.start_polling(bot)
