from aiogram.fsm.state import State, StatesGroup


class BriefState(StatesGroup):
    waiting_brief = State()


class EditState(StatesGroup):
    waiting_text = State()