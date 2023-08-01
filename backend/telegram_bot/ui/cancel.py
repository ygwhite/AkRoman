from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fluent.runtime import FluentLocalization


def get_cancel_kb(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=l10n.format_value("cancel"), callback_data="btn_cancel")]
    ])
