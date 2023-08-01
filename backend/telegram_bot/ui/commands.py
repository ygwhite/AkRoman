from typing import List

from aiogram import Bot
from aiogram.types import BotCommand
from fluent.runtime import FluentLocalization


def get_default_commands(l10n: FluentLocalization, is_admin: bool = False) -> List[BotCommand]:
    admin = [BotCommand(command="admin", description=l10n.format_value("control-panel"))] if is_admin else []
    return [
        BotCommand(command="start", description=l10n.format_value("start-cmd")),
        BotCommand(command="support", description=l10n.format_value("support-cmd"))
    ] + admin


async def set_default_commands(bot: Bot, l10n: FluentLocalization, is_admin: bool = False) -> None:
    await bot.set_my_commands(get_default_commands(l10n, is_admin))
