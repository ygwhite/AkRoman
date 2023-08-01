
from aiogram import Bot, Dispatcher

import copy
import datetime
import re
import json
from time import time
from uuid import uuid4
from asyncio import sleep
from django.core.exceptions import ObjectDoesNotExist
from aiogram import executor, Dispatcher
from aiogram.types import (
    User,
    Message,
    MediaGroup,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.types.input_file import InputFile
from aiogram.types.message import ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.exceptions import BotBlocked
from loguru._logger import Logger
import websockets
from collections import defaultdict
from telegram_bot.langs_support import TextsManager

from settings import (
    REG_LIFETIME,
    DEP_LIFETIME,
    TELEGRAM_MEDIA_PATH,
    BACKEND_ADMIN_URL,
    POSTBACK_SIMULATE_REG,
    POSTBACK_SIMULATE_DEP,
    WSS_URL, WSS_BOT_URL,
    TELEGRAM_LOGGER as log,
    COINGLASS_LOGGER, COINGLASS_API_URL, COINGLASS_API_KEY
)

from telegram_bot.keyboards.keyboards import KeyboardManager

from payments.utils import get_user_active_subs

from coinglassAPI.requests import CoinglassAPI
from utils import encrypt
from interface.backend import BackendInterface
from chartimg.requests import ChartImgAPI
from binanceOrderbook.requests import BinanceOrderbook
from chartimg.requests import ChartImgAPI
from cryptoBubbles.requests import CryptoBubbleAPI
from interface.backend import BackendInterface
from payments.requests import PaymentsAPI


# from . import loggers
from .handlers import setup_handlers
from .middlewares import L10nMiddleware


# @loggers.telegram.catch
async def setup_bot(
        bot_token: str,
        backend_interface: BackendInterface,
        chart_img: ChartImgAPI,
        crypto_bubble: CryptoBubbleAPI,
        binance_orderbook: BinanceOrderbook,
        payments: PaymentsAPI,
        webapp_url: str
) -> None:
    bot = Bot(token=bot_token)
    dp = Dispatcher()

    setup_handlers(dp)
    dp.message.middleware(L10nMiddleware())

    dp["backend_interface"] = backend_interface
    dp["chart_img"] = chart_img
    dp["crypto_bubble"] = crypto_bubble
    dp["binance_orderbook"] = binance_orderbook
    dp["payments"] = payments
    dp["webapp_link"] = webapp_url

    dp["wsocket"] = dict()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
