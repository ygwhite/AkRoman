from aiogram import Router, F
from aiogram.types import Message
from interface.backend import BackendInterface
from payments.utils import get_user_active_subs
from fluent.runtime import FluentLocalization

from .. import loggers
from ..ui import get_lang_kb

router = Router()


@loggers.telegram.catch
@router.message(F.text.lower() == "profile")
async def handle_btn_profile(message: Message, backend_interface: BackendInterface, l10n: FluentLocalization):
    """Обработчик кнопки \"Профиль\""""

    user = message.from_user

    customer = await backend_interface.get_customer(user.id)

    timeframes = [t['abbr'] for t in customer['timeframes']]
    user_sub = await backend_interface.get_user_subs(user.id)
    active_user_sub = await get_user_active_subs(user_sub, backend_interface)
    active_user_sub = [i['subscription_name']['name'] for i in active_user_sub]
    is_binance_api = bool(customer['tg_profile']['binance_secret_key'])

    text = l10n.format_value("profile", args={
        "timeframes": str(timeframes),
        "active_user_sub": str(active_user_sub),
        "text_binance_api_connected": "Binance API Connected" if is_binance_api else "❌ BINANCE API ❌"
    })

    # text = f"Available timeframes: {timeframes}\n\n" \
    #        f"Yours subscription: {active_user_sub}\n\n" \
    #        f"{'Binance API Connected' if is_binance_api else '❌ BINANCE API ❌'}\n\n" \
    #        "Choose language:"

    await message.answer(text, reply_markup=get_lang_kb())
