from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from fluent.runtime import FluentLocalization


def get_menu_kb(l10n: FluentLocalization, url: str) -> ReplyKeyboardMarkup:
    webapp = WebAppInfo(url=url)
    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text=l10n.format_value("webapp-button"), web_app=webapp),
            KeyboardButton(text=l10n.format_value("profile"))
        ]
    ], resize_keyboard=True)
