from aiogram.fsm.state import StatesGroup, State

class IncomeStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_amount = State()


class ExpenseStates(StatesGroup):
    waiting_for_expense_type = State()
    waiting_for_amount = State()


class EarlyRepaymentStates(StatesGroup):
    waiting_for_early_type = State()
    waiting_for_amount = State()


class AccumulationStates(StatesGroup):
    waiting_for_goal = State()
    waiting_for_duration = State()
    waiting_for_amount = State()


class TaskStates(StatesGroup):
    waiting_for_task_description = State()
    waiting_for_task_date = State()
    
class SharedStates(StatesGroup):
    waiting_for_shared_input = State()