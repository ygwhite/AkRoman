from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from fluent.runtime import FluentLocalization


def get_pay_kb(subs: List) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"🤑{sub.get('name')}",
            callback_data=f"payment_{sub.get('name')}_{sub.get('day')}_{sub.get('price')}"
        )] for sub in subs
    ])


def get_pay_link_kb(l10n: FluentLocalization, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=l10n.format_value("pay"), url=url)]
    ])
