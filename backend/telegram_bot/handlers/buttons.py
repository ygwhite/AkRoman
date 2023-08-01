from typing import Dict

from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluent.runtime import FluentLocalization
from interface.backend import BackendInterface
from payments.requests import PaymentsAPI

from .. import loggers
from ..ui import get_pay_link_kb
from ..utils import init_menu

router = Router()


@loggers.telegram.catch
@router.callback_query(F.data.startswith("payment_"))
async def callback_btn_payment(callback: CallbackQuery, payments: PaymentsAPI, l10n: FluentLocalization):
    """Обработчик кнопки \"Отмена\""""
    user = callback.from_user
    loggers.telegram.debug("Нажата кнопка оплаты")
    data_splited = callback.data.split('_')
    # sub_name = data_splited[1]
    day = data_splited[2]
    price = data_splited[3]
    order_id = f"{user.id}S{day}"
    response_invoice: Dict = payments.create_invoice(float(price), order_id=order_id)
    kb = get_pay_link_kb(response_invoice.get('pay_url'))
    await callback.message.answer(l10n.format_value("callback-btn-payment"), reply_markup=kb)
    await callback.answer()


@loggers.telegram.catch
@router.callback_query(F.data.startswith("lang_"))
async def callback_btn_language(
        callback: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        backend_interface: BackendInterface,
        webapp_link: str,
        l10n: FluentLocalization
):
    """Обработчик кнопки смены языка"""
    user = callback.from_user
    loggers.telegram.debug("Нажата кнопка смены языка")
    lang_code = callback.data.split('_')[1]
    match lang_code:
        case "ru":
            new_lang_name = "russian"
        case "spa":
            new_lang_name = "spanish"
        case "chi":
            new_lang_name = "chinese"
        case _:
            new_lang_name = "english"
    customer = await backend_interface.update_customer(user.id, tg_profile={'language': new_lang_name})
    text = l10n.format_value("changed-language", {"new_lang_name": new_lang_name})

    await callback.message.answer(text)
    await init_menu(user, bot, l10n, state, webapp_link)
    await callback.answer()
