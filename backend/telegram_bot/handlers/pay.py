from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from interface.backend import BackendInterface

from fluent.runtime import FluentLocalization

from .. import loggers
from ..ui import get_pay_kb

router = Router()


@loggers.telegram.catch
@router.message(Command("pay"))
async def handle_pay(message: Message, backend_interface: BackendInterface, l10n: FluentLocalization):
    """Обработчик кнопки pay\""""

    subs = await backend_interface.get_subscriptions()
    subs = [i for i in subs if i['name'].lower() != 'test']

    await message.answer(l10n.format_value("select-plan"), reply_markup=get_pay_kb(subs))
