from typing import Dict
from uuid import uuid4

from aiogram import Router, Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from interface.backend import BackendInterface
from fluent.runtime import FluentLocalization

from .. import loggers
from ..ui import set_default_commands
from ..utils import init_menu, stop_monitoring

router = Router()


@loggers.telegram.catch
@router.message(CommandStart())
async def start_cmd(
        message: Message,
        bot: Bot,
        state: FSMContext,
        webapp_link: str,
        backend_interface: BackendInterface,
        wsocket: Dict,
        l10n: FluentLocalization
) -> None:
    user = message.from_user
    loggers.telegram.debug(f"Вызвана команда `/start` (user_id: {user.id})")
    await state.clear()

    await stop_monitoring(user, state, wsocket)
    await backend_interface.connect()

    profile: Dict = await backend_interface.get_tg_profile(user.id)
    await state.update_data(session_id=str(uuid4()))

    await set_default_commands(bot, l10n, is_admin=profile.get("is_admin"))
    await init_menu(message.from_user, bot, l10n, state, webapp_link)
