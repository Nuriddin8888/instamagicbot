from aiogram.dispatcher.filters.state import State, StatesGroup



class Registration(StatesGroup):
    full_name = State()
    phone_number = State()
    rate_it_user = State()
    rate_it = State()


class Admin(StatesGroup):
    password = State()
