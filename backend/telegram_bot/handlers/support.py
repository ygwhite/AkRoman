from typing import Dict

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from fluent.runtime import FluentLocalization

from .. import loggers
from ..utils import stop_monitoring

router = Router()


@loggers.telegram.catch
# @router.message(Command("support"))
async def handle_cmd_support(message: Message, wsocket: Dict, state: FSMContext, l10n: FluentLocalization):
    """Обработчик команды `/support`"""

    user = message.from_user
    loggers.telegram.debug(f"Вызвана команда `/support` (id: {user.id})")

    await stop_monitoring(user, state, wsocket)

    await message.reply(l10n.format_value("support"))
