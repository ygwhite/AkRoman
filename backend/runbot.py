import os
import django
import asyncio

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()
from interface.backend import BackendInterface
bi = BackendInterface()

from chartimg.requests import ChartImgAPI
from cryptoBubbles.requests import CryptoBubbleAPI
from binanceOrderbook.requests import BinanceOrderbook
from payments.requests import PaymentsAPI
from settings import (
    CHARTIMG_BASEURL,
    CHARTIMG_API_TOKEN,
    CHARTIMG_API_URL_BETA,
    CHARTIMG_API_TOKEN_BETA,
    CHARTIMG_LOGGER,
    CHARTIMG_TIMEOUT,
    TELEGRAM_API_TOKEN,
    TELEGRAM_LOGGER,
    CRYPTOBUBBLES_1000_URL,
    CRYPTOBUBBLES_LOGGER,
    BINANCE_ORDERBOOK_URL,
    BINANCE_ORDERBOOK_LOGGER,
    PAY_API_KEY,
    PAY_SHOP_ID
)
from settings import WEBAPP_LINK
from telegram_bot import setup_bot, loggers
from utils.requests import BaseRequest


async def main() -> None:
    request_handler = BaseRequest(timeout=CHARTIMG_TIMEOUT)
    ci = ChartImgAPI(
        CHARTIMG_BASEURL,
        CHARTIMG_API_TOKEN,
        CHARTIMG_API_URL_BETA,
        CHARTIMG_API_TOKEN_BETA,
        "advanced-chart",
        "v1",
        request_handler,
        CHARTIMG_LOGGER,
    )

    cb = CryptoBubbleAPI(
        CRYPTOBUBBLES_1000_URL,
        request_handler,
        CRYPTOBUBBLES_LOGGER,
    )

    bo = BinanceOrderbook(
        BINANCE_ORDERBOOK_URL,
        BINANCE_ORDERBOOK_LOGGER,
    )

    pm = PaymentsAPI(PAY_API_KEY, PAY_SHOP_ID)

    loggers.telegram = TELEGRAM_LOGGER
    await setup_bot(TELEGRAM_API_TOKEN, bi, ci, cb, bo, pm, WEBAPP_LINK)

if __name__ == "__main__":
    try:
        TELEGRAM_LOGGER.success("Starting bot...")
        asyncio.run(main())
    except (SystemExit, KeyboardInterrupt):
        TELEGRAM_LOGGER.success("Bot stopped!")
