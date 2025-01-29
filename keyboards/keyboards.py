from aiogram.utils.keyboard import InlineKeyboardBuilder

async def months_keyboard():
    builder = InlineKeyboardBuilder()
    months = [
        'Январь', 'Февраль', 'Март', 'Апрель',
        'Май', 'Июнь', 'Июль', 'Август',
        'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]
    for month in months:
        builder.button(text=month, callback_data=f"month_{month}")
    builder.button(text="Накопления", callback_data="savings")
    builder.adjust(3, 3, 3, 3, 1)
    return builder.as_markup()

async def actions_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Доход", callback_data="income")
    builder.button(text="Расходы", callback_data="expense")
    builder.button(text="Досрочное погашение", callback_data="prepayment")
    builder.button(text="Баланс", callback_data="balance")
    builder.adjust(2, 2)
    return builder.as_markup()

async def savings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить цель", callback_data="add_saving")
    builder.button(text="Посмотреть цели", callback_data="view_savings")
    builder.button(text="Назад", callback_data="back")
    builder.adjust(2, 1)
    return builder.as_markup()