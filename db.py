from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# Модели базы данных

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)  # Telegram user id
    selected_month = Column(String, nullable=True)


class Finance(Base):
    __tablename__ = "finances"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    month = Column(String, nullable=False)
    category = Column(String, nullable=False)  # income, expense, early
    type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Accumulation(Base):
    __tablename__ = "accumulations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    goal = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    description = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Инициализация БД

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Хелпер для получения или создания пользователя:

async def get_or_create_user(user_id: int, session: AsyncSession) -> User:
    user = await session.get(User, user_id)
    if not user:
        user = User(id=user_id, selected_month=None)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user