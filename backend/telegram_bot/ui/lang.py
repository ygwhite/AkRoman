from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский", callback_data='lang_ru')],
        [InlineKeyboardButton(text="English", callback_data='lang_en')],
        [InlineKeyboardButton(text="Spanish", callback_data='lang_spa')],
        [InlineKeyboardButton(text="Chinese", callback_data='lang_chi')],
        [InlineKeyboardButton(text="🚀Binance 📈", callback_data='connect_binance')]
    ])
