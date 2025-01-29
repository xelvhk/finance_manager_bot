from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
import sqlite3
import re
from keyboards.keyboards import months_keyboard,savings_keyboard,actions_keyboard
from lexicon.lexicon_ru import LEXICON_RU
from aiogram.fsm.storage.base import Database
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

router = Router()
bot = Bot
db = Database()
class Form(StatesGroup):
        month_selection = State()
        income_type = State()
        income_amount = State()
        expense_type = State()
        expense_amount = State()
        prepayment_type = State()
        prepayment_amount = State()
        saving_goal = State()
        saving_target = State()
        saving_months = State()

@router.message(commands=['start'])
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Form.month_selection)
    await message.answer("Выберите месяц:", reply_markup=await months_keyboard())

@router.callback_query(F.data.startswith("month_"), Form.month_selection)
async def process_month(callback: types.CallbackQuery, state: FSMContext):
    month = callback.data.split("_")[1]
    await state.update_data(month=month)
    await state.set_state(None)
    await callback.message.edit_text(
        f"Месяц: {month}\nВыберите действие:",
        reply_markup=await actions_keyboard()
    )

@router.callback_query(F.data == "income")
async def process_income(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.income_type)
    await callback.message.answer("Введите тип дохода:")

@router.message(Form.income_type)
async def process_income_type(message: Message, state: FSMContext):
    await state.update_data(income_type=message.text)
    await state.set_state(Form.income_amount)
    await message.answer("Введите сумму:")

@router.message(Form.income_amount)
async def process_income_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        data = await state.get_data()
        await db.add_income(message.from_user.id, data['month'], data['income_type'], amount)
        await message.answer("Доход добавлен!")
        await state.clear()
    except ValueError:
        await message.answer("Ошибка! Введите число.")

@router.callback_query(F.data == "savings")
async def process_savings(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Накопления:",
        reply_markup=await savings_keyboard()
    )

@router.callback_query(F.data == "add_saving")
async def add_saving(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.saving_goal)
    await callback.message.answer("Введите цель накопления:")

@router.message(Form.saving_goal)
async def process_saving_goal(message: Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await state.set_state(Form.saving_target)
    await message.answer("Введите целевую сумму:")

@router.message(Form.saving_target)
async def process_saving_target(message: Message, state: FSMContext):
    try:
        target = float(message.text)
        await state.update_data(target=target)
        await state.set_state(Form.saving_months)
        await message.answer("Введите срок (в месяцах):")
    except ValueError:
        await message.answer("Ошибка! Введите число.")

@router.message(Form.saving_months)
async def process_saving_months(message: Message, state: FSMContext):
    try:
        months = int(message.text)
        data = await state.get_data()
        await db.add_saving(message.from_user.id, data['goal'], data['target'], months)
        await message.answer("Цель добавлена!")
        await state.clear()
    except ValueError:
        await message.answer("Ошибка! Введите целое число.")

@router.callback_query(F.data == "view_savings")
async def view_savings(callback: types.CallbackQuery):
    savings = await db.get_savings(callback.from_user.id)
    text = "Ваши цели:\n\n"
    for goal in savings:
        text += f"• {goal[0]}\nЦель: {goal[1]}₽\nНакоплено: {goal[2]}₽\nСрок: {goal[3]} мес.\n\n"
    await callback.message.answer(text)

@router.callback_query(F.data == "prepayment")
async def process_prepayment(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.prepayment_type)
    await callback.message.answer("Введите тип досрочного погашения:")

@router.message(Form.prepayment_type)
async def process_prepayment_type(message: Message, state: FSMContext):
    await state.update_data(prepayment_type=message.text)
    await state.set_state(Form.prepayment_amount)
    await message.answer("Введите сумму:")

@router.message(Form.prepayment_amount)
async def process_prepayment_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        data = await state.get_data()
        await db.add_expense(
            message.from_user.id,
            data['month'],
            f"Досрочное погашение: {data['prepayment_type']}",
            amount
        )
        await message.answer("Досрочное погашение добавлено!")
        await state.clear()
    except ValueError:
        await message.answer("Ошибка! Введите число.")

@router.callback_query(F.data == "balance")
async def show_balance(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    incomes, expenses = await db.get_month_data(callback.from_user.id, data['month'])
    
    total_income = sum(amount for _, amount in incomes)
    total_expense = sum(amount for _, amount in expenses)
    
    text = f"Баланс за {data['month']}:\n\n"
    text += "Доходы:\n" + "\n".join([f"- {t}: {a}₽" for t, a in incomes]) + f"\nИтого: {total_income}₽\n\n"
    text += "Расходы:\n" + "\n".join([f"- {t}: {a}₽" for t, a in expenses]) + f"\nИтого: {total_expense}₽\n\n"
    text += f"Остаток: {total_income - total_expense}₽"
    
    await callback.message.answer(text)