from typing import Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from fluent.runtime import FluentLocalization
from settings import BACKEND_ADMIN_URL

from .. import loggers
from ..ui import get_admin_kb
from ..utils import stop_monitoring

router = Router()


@loggers.telegram.catch
@router.message(Command("admin"))
async def handle_cmd_admin(message: Message, wsocket: Dict, state: FSMContext, l10n: FluentLocalization):
    """Обработчик команды `/admin`"""
    user = message.from_user
    loggers.telegram.debug(f"Вызвана команда `/admin` (id: {user.id})")

    await stop_monitoring(user, state, wsocket)
    await state.set_state("admin")

    # text = "Добро пожаловать в админку"
    # await self.bot.send_message(
    #     user.id,
    #     text,
    #     reply_markup=remove()
    # )

    await message.answer(l10n.format_value("admin"), reply_markup=get_admin_kb(l10n, url=BACKEND_ADMIN_URL))
