import json
from typing import Dict

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import User
from fluent.runtime import FluentLocalization
from utils import encrypt

from ..ui import get_menu_kb


# async def resolve_init_restart(user: User, state: FSMContext, backend_interface: BackendInterface, webapp_link: str):
#     """Маршрутизатор состояния диалога после перезагрузки"""
#
#     await init_menu(user, state, backend_interface, webapp_link)


async def init_menu(
        user: User,
        bot: Bot,
        l10n: FluentLocalization,
        state: FSMContext,
        webapp_link: str,
        send_message: bool = False
) -> None:
    """Функция возвращает пользователя к этапу когда он успешно внес депозит"""

    await state.set_state("dep")

    if not send_message:
        return

    url_data = encrypt(json.dumps({
        "tg_uid": str(user.id),
    }))
    webapp_menu_link = f"{webapp_link}/menu?hello={url_data}"

    await bot.send_message(
        user.id,
        l10n.format_value("menu"),
        reply_markup=get_menu_kb(l10n, webapp_menu_link)
    )


async def stop_monitoring(user: User, state: FSMContext, websocket: Dict) -> None:
    await state.update_data(keep_monitoring=False)

    if websocket.get(user.id) is not None:
        websocket = websocket.pop(user.id)
        await websocket.close()
