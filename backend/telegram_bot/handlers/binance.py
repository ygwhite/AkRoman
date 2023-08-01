from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from interface.backend import BackendInterface
from fluent.runtime import FluentLocalization

from .. import loggers
from ..ui import get_cancel_kb

router = Router()


@loggers.telegram.catch
@router.callback_query(F.data == "connect_binance")
async def handle_connect_binance(callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    """Обработчик кнопки \"Профиль\""""
    await state.set_state("binance_api_key")

    await callback.message.answer(l10n.format_value("binance-api"), reply_markup=get_cancel_kb(l10n))


@loggers.telegram.catch
@router.message(StateFilter("binance_api_key"))
async def waiting_binance_api_key(
        message: Message,
        backend_interface: BackendInterface,
        state: FSMContext,
        l10n: FluentLocalization
):
    """Обработчик кнопки pay\""""

    user = message.from_user

    res = await backend_interface.update_binance_api_key(user.id, message.text)

    await message.answer(l10n.format_value("binance-secret"), reply_markup=get_cancel_kb(l10n))
    await message.delete()
    await state.set_state("binance_secret_key")


@loggers.telegram.catch
@router.message(StateFilter("binance_secret_key"))
async def waiting_binance_secret_key(
        message: Message,
        state: FSMContext,
        backend_interface: BackendInterface,
        l10n: FluentLocalization
):
    """Обработчик кнопки pay\""""
    await state.clear()
    user = message.from_user

    res = await backend_interface.update_binance_secret_key(user.id, message.text)

    await message.answer(l10n.format_value("binance-connected"))
    await message.delete()
