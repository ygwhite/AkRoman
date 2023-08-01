from typing import Dict

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluent.runtime import FluentLocalization

from .. import loggers
from ..utils import init_menu, stop_monitoring

router = Router()


@loggers.telegram.catch
@router.callback_query(StateFilter("monitoring"), F.data == "btn_cancel_monitoring")
async def callback_btn_cancel_monitoring(
        callback: CallbackQuery,
        bot: Bot,
        wsocket: Dict,
        state: FSMContext,
        webapp_link: str,
        l10n: FluentLocalization
) -> None:
    """Обработчик кнопки \"Остановить мониторинг\""""

    loggers.telegram.debug(f"Нажата кнопка \"Остановить мониторинг\" (user_id={callback.from_user.id})")

    user = callback.from_user

    await stop_monitoring(user, state, wsocket)
    await init_menu(user, bot, l10n, state, webapp_link, send_message=True)
    await callback.answer()


@loggers.telegram.catch
@router.callback_query(F.data == "btn_cancel")
async def callback_btn_cancel(
        callback: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        webapp_link: str,
        l10n: FluentLocalization
) -> None:
    """Обработчик кнопки \"Отмена\""""

    loggers.telegram.debug(f"Нажата кнопка отмены (user_id={callback.from_user.id})")

    user = callback.from_user

    await state.clear()
    loggers.telegram.debug(f"Состояние очищено (user_id={callback.from_user.id})")

    await callback.message.answer(l10n.format_value("cancel"))
    await init_menu(user, bot, l10n, state, webapp_link)
    await callback.answer()
