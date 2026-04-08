import asyncio
from aiogram import Bot, Dispatcher
from app.handlers import router
from settings import config
from aiogram.types import BotCommand
from tables.database import engine, Base
from redis.asyncio import Redis
from settings import config

bot = Bot(token=config.TOKEN)
dp = Dispatcher()
redis_client = Redis.from_url(config.REDIS_URL) 

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы")

async def main():

    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="vote", description="🗳️ Голосовать"),
        BotCommand(command="del_vote", description="◀️ Отменить голос")
               ]
    
    
    dp.include_router(router)
    await init_db()
    await bot.set_my_commands(commands)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        print("✅ Бот запущен")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🚫 Бот остановлен")
