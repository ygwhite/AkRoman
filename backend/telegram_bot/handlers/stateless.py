from aiogram import Router
from aiogram.types import Message

from fluent.runtime import FluentLocalization

from .. import loggers

router = Router()


@loggers.telegram.catch
@router.message()
async def handle_stateless_input(message: Message, l10n: FluentLocalization):
    """Обработчик пользовательского ввода без состояния"""
    user = message.from_user

    loggers.telegram.debug(f"Пользователь {user.first_name} (id: {user.id}) ввел \"{message.text}\"")
    await message.reply(l10n.format_value("stateless-input"))
