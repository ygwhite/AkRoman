from pathlib import Path
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import User, Update
from fluent.runtime import FluentLocalization, FluentResourceLoader
from interface.backend import BackendInterface


class L10nMiddleware(BaseMiddleware):
    langs = ("english", "russian", "spanish", "chinese")
    _loader = FluentResourceLoader(str(Path(__file__).parent.parent.resolve() / "locales" / "{locale}"))

    @classmethod
    def get_default_locale(cls) -> FluentLocalization:
        return FluentLocalization(["english"], ["main.ftl"], cls._loader)

    @classmethod
    def get_locale(cls, lang: str) -> FluentLocalization:
        return FluentLocalization([lang], ["main.ftl"], cls._loader) if lang in cls.langs else cls.get_default_locale()

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        user: User = data["event_from_user"]
        backend_interface: BackendInterface = data.get("backend_interface")
        tg_profile: Dict = await backend_interface.get_tg_profile(user.id)

        data["l10n"] = self.get_locale(tg_profile.get("language"))

        return await handler(event, data)
