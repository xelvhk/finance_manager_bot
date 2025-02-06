from datetime import datetime
from aiogram import types
from aiogram.fsm.context import FSMContext
from keyboards import get_accumulation_keyboard, get_main_menu_keyboard
from states import AccumulationStates
from db import Accumulation, async_session, get_or_create_user

async def accum_handler(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("accum:")[1]
    if action == "add":
        await callback.message.edit_text("Введите цель накопления:")
        await AccumulationStates.waiting_for_goal.set()
    elif action == "view":
        async with async_session() as session:
            user = await get_or_create_user(callback.from_user.id, session)
            result = await session.execute(
                Accumulation.__table__.select().where(Accumulation.user_id == user.id)
            )
            accumulations = result.fetchall()
        if accumulations:
            text = "<b>Цели накоплений:</b>\n"
            for acc in accumulations:
                text += f"Цель: {acc.goal}, срок: {acc.duration} мес, сумма: {acc.amount}\n"
        else:
            text = "Цели накоплений отсутствуют."
        await callback.message.answer(text, reply_markup=get_main_menu_keyboard())
    await callback.answer()


async def accum_goal(message: types.Message, state: FSMContext):
    goal = message.text.strip()
    await state.update_data(goal=goal)
    await message.answer("Введите срок накопления (в месяцах):")
    await AccumulationStates.waiting_for_duration.set()


async def accum_duration(message: types.Message, state: FSMContext):
    try:
        duration = int(message.text)
    except ValueError:
        await message.answer("Введите целое число для срока накопления (в месяцах).")
        return
    await state.update_data(duration=duration)
    await message.answer("Введите сумму накопления:")
    await AccumulationStates.waiting_for_amount.set()


async def accum_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректное числовое значение суммы.")
        return
    data = await state.get_data()
    async with async_session() as session:
        user = await get_or_create_user(message.from_user.id, session)
        accumulation = Accumulation(
            user_id=user.id,
            goal=data["goal"],
            duration=data["duration"],
            amount=amount,
            timestamp=datetime.utcnow()
        )
        session.add(accumulation)
        await session.commit()
    await message.answer(f"Добавлена цель: {data['goal']} на сумму {amount} за {data['duration']} мес.",
                         reply_markup=get_main_menu_keyboard())
    await state.clear()