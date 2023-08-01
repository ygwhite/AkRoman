import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from telegram_bot.main import BotService
from settings import TELEGRAM_API_TOKEN, WEBAPP_LINK
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from interface.backend import BackendInterface
from chartimg.requests import ChartImgAPI
from cryptoBubbles.requests import CryptoBubbleAPI
from binanceOrderbook.requests import BinanceOrderbook
from payments.requests import PaymentsAPI
from TradingViewApi.requests import TradingViewApi
from utils.requests import BaseRequest

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
    TRADING_VIEW_API_URL,
    CREATE_PAY_URL,
    PAY_API_KEY,
    PAY_SHOP_ID
)

if __name__ == "__main__":
    bot = Bot(token=TELEGRAM_API_TOKEN)

    storage = MemoryStorage()

    dp = Dispatcher(bot, storage=storage)

    bi = BackendInterface()

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
    service = BotService(dp, WEBAPP_LINK, bi, ci, cb, bo, pm, TELEGRAM_LOGGER)

    service.start()
