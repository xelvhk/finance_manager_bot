import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from config import Config,load_config, REDIS_URL, logger
from db import init_db, engine
from handlers import register_all_handlers
from redis_manager import init_redis

# Загружаем конфиг в переменную config
config: Config = load_config()
async def main():
    # Используем RedisStorage для FSM (при наличии Redis)
    storage = RedisStorage.from_url(REDIS_URL, key_builder=DefaultKeyBuilder(with_bot_id=True))
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher(storage=storage)

    # Инициализируем базу данных и Redis-соединение
    await init_db()
    await init_redis()

    register_all_handlers(dp)

    try:
        logger.info("Бот запущен.")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())