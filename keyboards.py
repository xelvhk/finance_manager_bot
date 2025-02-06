from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_months_keyboard() -> InlineKeyboardMarkup:
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
              "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    kb = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(text=m, callback_data=f"month:{m}") for m in months]
    kb.add(*buttons)
    return kb


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text="Доход", callback_data="menu:income"),
        InlineKeyboardButton(text="Обязательные расходы", callback_data="menu:expense"),
        InlineKeyboardButton(text="Досрочное погашение", callback_data="menu:early"),
        InlineKeyboardButton(text="Баланс", callback_data="menu:balance"),
        InlineKeyboardButton(text="Накопления", callback_data="menu:accum"),
        InlineKeyboardButton(text="Задачи", callback_data="menu:tasks")
    )
    return kb


def get_income_type_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text="Зарплата", callback_data="income:type:salary"),
        InlineKeyboardButton(text="Аванс", callback_data="income:type:advance")
    )
    return kb


def get_accumulation_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text="Добавить цель", callback_data="accum:add"),
        InlineKeyboardButton(text="Посмотреть цели", callback_data="accum:view")
    )
    return kb


def get_tasks_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text="Добавить задачу", callback_data="tasks:add"),
        InlineKeyboardButton(text="Задачи на сегодня", callback_data="tasks:today"),
        InlineKeyboardButton(text="Задачи по дате", callback_data="tasks:date")
    )
    return kb