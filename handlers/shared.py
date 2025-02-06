from aiogram import types
from aiogram.fsm.context import FSMContext
from keyboards import get_main_menu_keyboard
from states import SharedStates
from config import logger
from redis_manager import redis

async def edit_shared_cmd(message: types.Message, state: FSMContext):
    """
    Команда /edit_shared. Запрашивает у пользователя ввод данных для обновления общего ресурса.
    """
    await message.answer("Введите данные для обновления общего ресурса:")
    await state.set_state(SharedStates.waiting_for_shared_input)


async def update_shared_data(message: types.Message, state: FSMContext):
    """
    После получения текста от пользователя, обновляет общий ресурс в Redis,
    используя распределённую блокировку.
    """
    user_id = message.from_user.id
    new_value = message.text

    # Получаем блокировку на ключ "shared_data_lock" с таймаутом 10 секунд
    lock = await redis.lock("shared_data_lock", timeout=10)
    async with lock:
        current_data = await redis.get("shared_data")
        if current_data is None:
            current_data = ""
        # Объединяем текущее содержимое с новым изменением от пользователя
        updated_data = f"{current_data}\nUser {user_id}: {new_value}"
        await redis.set("shared_data", updated_data)
        logger.info(f"Пользователь {user_id} обновил общий ресурс.")

    await message.answer("Общие данные обновлены.", reply_markup=get_main_menu_keyboard())
    await state.clear()