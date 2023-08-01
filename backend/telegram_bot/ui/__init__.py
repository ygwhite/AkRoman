from aiogram.types import ReplyKeyboardRemove

from .admin import get_admin_kb
from .cancel import get_cancel_kb
from .commands import get_default_commands, set_default_commands
from .lang import get_lang_kb
from .menu import get_menu_kb
from .pay import get_pay_kb, get_pay_link_kb
from .monitoring import get_cancel_monitoring_kb

remove = ReplyKeyboardRemove

__all__ = (
    "get_default_commands",
    "set_default_commands",
    "get_menu_kb",
    "remove",
    "get_admin_kb",
    "get_lang_kb",
    "get_cancel_kb",
    "get_pay_kb",
    "get_pay_link_kb",
    "get_cancel_monitoring_kb"
)
