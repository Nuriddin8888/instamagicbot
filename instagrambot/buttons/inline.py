from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

get_language = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Uzb""🇺🇿",callback_data="lang_uz"),
            InlineKeyboardButton(text="Rus""🇷🇺",callback_data="lang_ru"),
            InlineKeyboardButton(text="Eng""🇺🇸",callback_data="lang_eng")
        ]
    ]
)


rate_it = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👍",callback_data="like"),
            InlineKeyboardButton(text="👎",callback_data="dislike"),
        ]
    ]
)


admin_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
        InlineKeyboardButton(text="Foydalanuvchilarni ko'rish", callback_data="view_users")
        ],
        [
        InlineKeyboardButton(text="Bot statistikasini ko'rish", callback_data="view_stats")
        ]
    ]
)