from datetime import datetime, date
from aiogram import types
from aiogram.fsm.context import FSMContext
from keyboards import get_main_menu_keyboard
from states import TaskStates
from db import Task, async_session, get_or_create_user

async def tasks_handler(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("tasks:")[1]
    if action == "add":
        await callback.message.edit_text("Введите описание задачи:")
        await TaskStates.waiting_for_task_description.set()
    elif action == "today":
        async with async_session() as session:
            user = await get_or_create_user(callback.from_user.id, session)
            today_str = date.today().isoformat()
            result = await session.execute(
                Task.__table__.select().where(
                    (Task.user_id == user.id) & (Task.date == today_str)
                )
            )
            tasks = result.fetchall()
        if tasks:
            text = "<b>Задачи на сегодня:</b>\n"
            for t in tasks:
                text += f"- {t.description}\n"
        else:
            text = "На сегодня задач нет."
        await callback.message.answer(text, reply_markup=get_main_menu_keyboard())
    elif action == "date":
        await callback.message.edit_text("Введите дату в формате ГГГГ-ММ-ДД, чтобы посмотреть задачи на этот день:")
    await callback.answer()


async def task_description(message: types.Message, state: FSMContext):
    task_desc = message.text.strip()
    await state.update_data(task_description=task_desc)
    await message.answer("Введите дату, когда нужно выполнить задачу (ГГГГ-ММ-ДД):")
    await TaskStates.waiting_for_task_date.set()


async def task_date(message: types.Message, state: FSMContext):
    try:
        task_date_obj = datetime.strptime(message.text.strip(), "%Y-%m-%d").date()
    except ValueError:
        await message.answer("Неверный формат даты. Введите дату в формате ГГГГ-ММ-ДД:")
        return
    data = await state.get_data()
    async with async_session() as session:
        user = await get_or_create_user(message.from_user.id, session)
        task = Task(
            user_id=user.id,
            description=data["task_description"],
            date=task_date_obj,
            timestamp=datetime.utcnow()
        )
        session.add(task)
        await session.commit()
    await message.answer(f"Добавлена задача: {data['task_description']} на {task_date_obj.isoformat()}",
                         reply_markup=get_main_menu_keyboard())
    await state.clear()


# Если пользователь отправляет дату вне активного состояния:
async def tasks_by_date(message: types.Message):
    try:
        query_date = datetime.strptime(message.text.strip(), "%Y-%m-%d").date().isoformat()
    except ValueError:
        return
    async with async_session() as session:
        user = await get_or_create_user(message.from_user.id, session)
        result = await session.execute(
            Task.__table__.select().where(
                (Task.user_id == user.id) & (Task.date == query_date)
            )
        )
        tasks = result.fetchall()
    if tasks:
        text = f"<b>Задачи на {query_date}:</b>\n"
        for t in tasks:
            text += f"- {t.description}\n"
    else:
        text = f"Задач на {query_date} нет."
    await message.answer(text, reply_markup=get_main_menu_keyboard())