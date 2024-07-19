from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


phone_button = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Telefon raqam 📞",request_contact=True)
        ]
    ],resize_keyboard=True
)
