from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fluent.runtime import FluentLocalization


def get_cancel_monitoring_kb(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=l10n.format_value("cancel-monitoring-button"), callback_data="btn_cancel_monitoring")]
    ])
