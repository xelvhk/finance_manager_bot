from aiogram import Dispatcher
from aiogram import types
from handlers import start, finance, accumulations, tasks
from aiogram.filters import Command

def register_all_handlers(dp: Dispatcher):
    # Регистрация стартовых команд и колбэков
    dp.message.register(start.cmd_start, Command("start"))
    dp.callback_query.register(start.month_chosen, lambda c: c.data.startswith("month:"))

    # Финансовые обработчики
    dp.callback_query.register(finance.income_type_chosen, lambda c: c.data.startswith("income:type:"))
    dp.message.register(finance.process_income_amount, finance.IncomeStates.waiting_for_amount)
    dp.message.register(finance.process_expense_type, finance.ExpenseStates.waiting_for_expense_type)
    dp.message.register(finance.process_expense_amount, finance.ExpenseStates.waiting_for_amount)
    dp.message.register(finance.process_early_type, finance.EarlyRepaymentStates.waiting_for_early_type)
    dp.message.register(finance.process_early_amount, finance.EarlyRepaymentStates.waiting_for_amount)
    dp.callback_query.register(finance.main_menu_handler, lambda c: c.data.startswith("menu:"))
    dp.message.register(finance.send_balance, lambda m: m.text and m.text.startswith("/balance"))

    # Обработчики накоплений
    dp.callback_query.register(accumulations.accum_handler, lambda c: c.data.startswith("accum:"))
    dp.message.register(accumulations.accum_goal, accumulations.AccumulationStates.waiting_for_goal)
    dp.message.register(accumulations.accum_duration, accumulations.AccumulationStates.waiting_for_duration)
    dp.message.register(accumulations.accum_amount, accumulations.AccumulationStates.waiting_for_amount)

    # Обработчики задач
    dp.callback_query.register(tasks.tasks_handler, lambda c: c.data.startswith("tasks:"))
    dp.message.register(tasks.task_description, tasks.TaskStates.waiting_for_task_description)
    dp.message.register(tasks.task_date, tasks.TaskStates.waiting_for_task_date)
    dp.message.register(tasks.tasks_by_date)

async def cmd_start(message: types.Message):
    await message.answer("Привет. Это бот - финансовый помощник")

async def month_chosen(callback: types.CallbackQuery):
    await callback.answer("Вы выбрали месяц {callback.data}")