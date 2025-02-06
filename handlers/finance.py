from datetime import datetime
from aiogram import types
from aiogram.fsm.context import FSMContext
from keyboards import get_main_menu_keyboard
from states import IncomeStates, ExpenseStates, EarlyRepaymentStates
from db import Finance, async_session, get_or_create_user

# Обработка выбора типа дохода
async def income_type_chosen(callback: types.CallbackQuery, state: FSMContext):
    income_type = callback.data.split("income:type:")[1]
    await state.update_data(income_type=income_type)
    await callback.message.edit_text(f"Вы выбрали доход: {income_type}\nВведите сумму дохода:")
    await IncomeStates.waiting_for_amount.set()
    await callback.answer()


async def process_income_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректное числовое значение суммы.")
        return
    data = await state.get_data()
    income_type = data.get("income_type", "не указано")
    async with async_session() as session:
        user = await get_or_create_user(message.from_user.id, session)
        if not user.selected_month:
            await message.answer("Сначала выберите месяц командой /start")
            return
        finance = Finance(
            user_id=user.id,
            month=user.selected_month,
            category="income",
            type=income_type,
            amount=amount,
            timestamp=datetime.utcnow()
        )
        session.add(finance)
        await session.commit()
    await message.answer(f"Записан доход: {income_type} на сумму {amount}", reply_markup=get_main_menu_keyboard())
    await state.clear()


# Аналогичные обработчики для расходов и досрочного погашения:

async def process_expense_type(message: types.Message, state: FSMContext):
    expense_type = message.text.strip()
    await state.update_data(expense_type=expense_type)
    await message.answer(f"Тип расхода: {expense_type}\nВведите сумму расхода:")
    await ExpenseStates.waiting_for_amount.set()


async def process_expense_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректное числовое значение суммы.")
        return
    data = await state.get_data()
    expense_type = data.get("expense_type", "не указано")
    async with async_session() as session:
        user = await get_or_create_user(message.from_user.id, session)
        if not user.selected_month:
            await message.answer("Сначала выберите месяц командой /start")
            return
        from db import Finance  # Если нужно, можно импортировать наверху
        finance = Finance(
            user_id=user.id,
            month=user.selected_month,
            category="expense",
            type=expense_type,
            amount=amount,
            timestamp=datetime.utcnow()
        )
        session.add(finance)
        await session.commit()
    await message.answer(f"Записан расход: {expense_type} на сумму {amount}", reply_markup=get_main_menu_keyboard())
    await state.clear()


async def process_early_type(message: types.Message, state: FSMContext):
    early_type = message.text.strip()
    await state.update_data(early_type=early_type)
    await message.answer(f"Тип досрочного погашения: {early_type}\nВведите сумму:")
    await EarlyRepaymentStates.waiting_for_amount.set()


async def process_early_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректное числовое значение суммы.")
        return
    data = await state.get_data()
    early_type = data.get("early_type", "не указано")
    async with async_session() as session:
        user = await get_or_create_user(message.from_user.id, session)
        if not user.selected_month:
            await message.answer("Сначала выберите месяц командой /start")
            return
        finance = Finance(
            user_id=user.id,
            month=user.selected_month,
            category="early",
            type=early_type,
            amount=amount,
            timestamp=datetime.utcnow()
        )
        session.add(finance)
        await session.commit()
    await message.answer(f"Записано досрочное погашение: {early_type} на сумму {amount}",
                         reply_markup=get_main_menu_keyboard())
    await state.clear()


async def send_balance(message: types.Message):
    async with async_session() as session:
        user = await get_or_create_user(message.from_user.id, session)
        if not user.selected_month:
            await message.answer("Сначала выберите месяц командой /start")
            return
        month = user.selected_month
        # Получаем все записи для выбранного месяца
        result = await session.execute(
            Finance.__table__.select().where(
                (Finance.user_id == user.id) & (Finance.month == month)
            )
        )
        finances = result.fetchall()

    # Группировка по категориям
    incomes = [f for f in finances if f.category == "income"]
    expenses = [f for f in finances if f.category == "expense"]
    earlys = [f for f in finances if f.category == "early"]

    text = f"<b>Баланс за {month}:</b>\n\n"
    if incomes:
        text += "<u>Доходы:</u>\n"
        for inc in incomes:
            text += f"{inc.type}: {inc.amount}\n"
    else:
        text += "Доходы: нет данных\n"

    if expenses:
        text += "\n<u>Обязательные расходы:</u>\n"
        for exp in expenses:
            text += f"{exp.type}: {exp.amount}\n"
    else:
        text += "\nОбязательные расходы: нет данных\n"

    if earlys:
        text += "\n<u>Досрочные погашения:</u>\n"
        for early in earlys:
            text += f"{early.type}: {early.amount}\n"
    else:
        text += "\nДосрочные погашения: нет данных\n"

    await message.answer(text, reply_markup=get_main_menu_keyboard())