from typing import Any

from aiogram.filters import Filter
from aiogram.types import Message
from django.core.exceptions import ObjectDoesNotExist
from interface.backend import BackendInterface
from payments.utils import get_user_active_subs

from backend.telegram_bot import loggers
from backend.telegram_bot.ui import get_lang_kb


class PermissionFilter(Filter):
    def __init__(self, *permissions: str) -> None:
        self.permissions = permissions

    # @loggers.telegram.catch
    async def __call__(self, message: Message, backend_interface: BackendInterface) -> Any:

        user = message.from_user

        try:
            tg_profile = await backend_interface.get_tg_profile(user.id)
            is_test_sub = False
        except ObjectDoesNotExist as e:
            is_test_sub = True
            await message.reply("👋Welcome! \n\n👇Choose a language👇", reply_markup=get_lang_kb())

        customer = await backend_interface.get_or_create_customer(user)
        # Если юзер новый - мы ему даем тестовую подписку
        if is_test_sub:
            loggers.telegram.debug(f"User has test sub (id: {user.id})")
            test_sub = await backend_interface.get_test_subscription()
            await backend_interface.add_pay_subscription(user.id, test_sub['id'])
        user_sub = await backend_interface.get_user_subs(user.id)
        check_user_sub = await get_user_active_subs(user_sub, backend_interface)
        if not check_user_sub:
            await message.reply("Write to the bot /pay to renew your subscription")
        if customer is None:
            raise Exception(f"Не удалось создать пользователя (id: {user.id})")
        loggers.telegram.debug(f"Проверка прав пользователя (id: {user.id})")

        for permission in self.permissions:
            match permission:
                case "tg_allowed":
                    if not customer.get("tg_profile", {}).get("is_allowed", True):
                        loggers.telegram.debug(f"В доступе отказано [(tg_allowed, False)] (id: {user.id})")
                        return False

                case "tg_admin":
                    if not customer.get("tg_profile", {}).get("is_admin", False):
                        loggers.telegram.debug(f"В доступе отказано [(tg_admin, False)] (id: {user.id})")
                        return False

                case "payed":
                    if not check_user_sub:
                        return False

        loggers.telegram.debug(f"Доступ разрешен (id: {user.id})")
        return True
