import logging
from dataclasses import dataclass
from environs import Env


# Настройки для базы данных (можно использовать SQLite, PostgreSQL, MySQL и т.п.)
DATABASE_URL = "sqlite+aiosqlite:///database.db"

# URL для подключения к Redis (используется как FSM storage и для общих данных)
REDIS_URL = "redis://localhost:6379"

# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('API_TOKEN')))