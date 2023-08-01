from aiogram import Dispatcher


def setup_handlers(dp: Dispatcher) -> None:
    from ..filters import PermissionFilter
    allowed = PermissionFilter("tg_allowed")

    from . import start
    start.router.message.filter(allowed)
    dp.include_router(start.router)

    from . import admin
    admin.router.message.filter(PermissionFilter("tg_allowed", "tg_admin"))
    dp.include_router(admin.router)

    from . import binance
    binance.router.message.filter(allowed)
    dp.include_router(binance.router)

    from . import cancel
    dp.include_router(cancel.router)

    from . import pay
    pay.router.message.filter(allowed)
    dp.include_router(pay.router)

    from . import profile
    profile.router.message.filter(allowed)
    dp.include_router(profile.router)

    from . import support
    support.router.message.filter(allowed)
    dp.include_router(support.router)

    from . import webapp
    dp.include_router(webapp.router)

    from . import stateless
    dp.include_router(stateless.router)

    from . import buttons
    dp.include_router(buttons.router)
