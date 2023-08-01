import os
from sys import version_info
from pathlib import Path

import socks as socks
from dotenv import load_dotenv

from django.core.management.utils import get_random_secret_key

from logs import add_named_logger

# if version_info.major < 3 or version_info.minor < 10:
#   raise Exception("Unsupported version of python")

# COMMON
DEBUG = True
DEBUG_WSS = True
BASE_DIR = Path(__file__).resolve().parent

assert (BASE_DIR / ".env").exists(), "Для работы приложения необходим файл .env"
load_dotenv()

# LOGGING
LOGGER_PATH = BASE_DIR / "logs"
LOGGER_ROTATION = "10 MB"
LOGGER_COMPRESSION = "zip"
LOGGER_LEVELS = ["DEBUG", "WARNING"] if DEBUG == True else ["INFO", "ERROR"]

# TELEGRAM
TELEGRAM_DIR = BASE_DIR / "telegram_bot"
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
TELEGRAM_MEDIA_PATH = TELEGRAM_DIR / "media"
TELEGRAM_LOGGER = add_named_logger("telegram_bot")
# WEBAPP
WEBAPP_HOST = os.getenv("WEBAPP_HOST")
WEBAPP_PORT = os.getenv("WEBAPP_PORT", "")
WEBAPP_URL = f"https://{WEBAPP_HOST}{WEBAPP_PORT and ':%s' % WEBAPP_PORT}"
WEBAPP_LINK = f"{WEBAPP_URL}/webapp"

# BROKER
# 2022-11-10: Ожидается ссылка вида 
# "https://bin.gd/?partner_id=p138126p44167p871c&subid="

REG_LIFETIME = 15  # minutes
DEP_LIFETIME = 15  # minutes
# TODO Вынести ссылку брокера в django admin
# TODO Вынести таймауты ожидания в django admin


# POSTBACK
POSTBACK_SIMULATE_REG = DEBUG and False
POSTBACK_SIMULATE_DEP = DEBUG and False
POSTBACK_HOST = os.getenv("POSTBACK_HOST", "hotalgo.com")
POSTBACK_URL = f"{WEBAPP_URL}/postback"
POSTBACK_FAKE_REG_URL = POSTBACK_URL + "?status=reg&sid={sid}&uid={uid}"
POSTBACK_FAKE_DEP_URL = POSTBACK_URL + "?status=dep&sid={sid}&uid=4173756&payout=7.75"
# TODO Вынести адрес хоста постбэков в django admin


# BACKEND
# Настройки бэкенда находятся в файле backend/backend/settings.py
BACKEND_DIR = BASE_DIR
BACKEND_SECRET_KEY = os.getenv("BACKEND_SECRET_KEY", get_random_secret_key())
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8080")
BACKEND_URL = f"http://{BACKEND_HOST}{BACKEND_PORT and ':%s' % BACKEND_PORT}"
BACKEND_ADMIN_URL = f"{WEBAPP_URL}/admin"
BACKEND_LOGGER = add_named_logger("django")

# DATABASE
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "")
DATABASE_NAME = os.getenv("DATABASE_NAME", "tradingbot")
DATABASE_USER = os.getenv("DATABASE_USER", "admin")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

# WEBSOCKET SERVER
WSS_HOST = os.getenv("WSS_HOST", BACKEND_HOST)
WSS_PORT = os.getenv("WSS_PORT", "7890")
WSS_PROTOCOL = "ws" if DEBUG == True else "ws"
WSS_APP_PORT = 2043
WSS_HTTPS_URL = f"wss://{BACKEND_HOST}"
WSS_URL = f"wss://{BACKEND_HOST}{WSS_APP_PORT and ':%s' % WSS_APP_PORT}"
WSS_BOT_URL = f'ws://localhost:{WSS_PORT}'
WSS_QLIMIT = 100
WSS_LOGGER = add_named_logger("websocket_server")
# SSL
SSL_CERT_PATH = os.getenv("SSL_CERT_PATH")
SSL_KEY_PATH = os.getenv("SSL_KEY_PATH")
SECURE_SSL_REDIRECT = True
# REQUESTS
# ENCRYPTION
# Пока используется только для шифрования url параметоров.
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
# PROXIES
DEFAULT_TIMEOUT = 100  # seconds
# TODO Вынести значение таймаута в django admin
# TODO Вынести включение использования proxy в django admin


# CHARTIMG
CHARTIMG_API_TOKEN = os.getenv("CHARTIMG_API_TOKEN")
CHARTIMG_API_URL_BETA = os.getenv("CHARTIMG_API_URL_BETA")
CHARTIMG_API_TOKEN_BETA = os.getenv("CHARTIMG_API_TOKEN_BETA")
CHARTIMG_BASEURL = "https://api.chart-img.com"
CHARTIMG_DIR = BASE_DIR / "chartimg"
CHARTIMG_LOGGER = add_named_logger("chartimg_api")
CHARTIMG_TIMEOUT = DEFAULT_TIMEOUT

# CRYPTOBUBBLES
CRYPTOBUBBLES_1000_URL = os.getenv("CRYPTOBUBBLES_1000_URL")
CRYPTOBUBBLES_LOGGER = add_named_logger("cryptobubble_api")

# Binance orderbook
BINANCE_ORDERBOOK_URL = os.getenv("BINANCE_ORDERBOOK_URL")
BINANCE_ORDERBOOK_LOGGER = add_named_logger("binance_orderbook_api")

# OUR TRADING VIEW API
TRADING_VIEW_API_URL = os.getenv("TRADING_VIEW_API_URL")
TRADING_VIEW_API_SESSIONID = os.getenv("TRADING_VIEW_API_SESSIONID")
TRADING_VIEW_API_SESSIONIDSIGN = os.getenv("TRADING_VIEW_API_SESSIONIDSIGN")
TRADING_VIEW_API_LOGGER = add_named_logger("trading_view_logger")
TRADING_VIEW_INIDICATORS_DICT = {"Market Cipher B": "PUB;ULSuJHspklYwmfZRjRObSo0BLF6PdP2Y",
                                 "VuManChu Cipher B": "PUB;uA35GeckoTA2EfgI63SD2WCSmca4njxp",
                                 "RSI": "STD;RSI",
                                 "Squize Momentum": "PUB;175",
                                 "Fund master": "PUB;e040dc1958234beda533dfc57c1cb342",
                                 "Wolfpack Id": "PUB;qEd8N9GtniL0SigDrgnzF1lYLUjT2Sz0"}
TV_HEADERS = {
    "Origin": "https://data.tradingview.com"
}
TV_LOGGER = add_named_logger("tradingview_uapi")
TV_TIMEOUT = DEFAULT_TIMEOUT

# PARSER
TELETHONE_API_ID = os.getenv("TELETHONE_API_ID")
TELETHONE_API_HASH = os.getenv("TELETHONE_API_HASH")
TELETHONE_PROXY = os.getenv('TELETHONE_PROXY')
TELETHONE_PROXY = TELETHONE_PROXY.split(':') if TELETHONE_PROXY else None
if TELETHONE_PROXY and len(TELETHONE_PROXY.split(':')) == 5:
    TELETHONE_PROXY[1] = int(TELETHONE_PROXY[1])
    TELETHONE_PROXY[2] = bool(TELETHONE_PROXY[2])
    TELETHONE_PROXY = (socks.SOCKS5, *TELETHONE_PROXY)
else:
    TELETHONE_PROXY = None
PARSER_LOGGER = add_named_logger("parser_logger")
BOT_PARSER_TOKEN = os.getenv("BOT_PARSER_TOKEN")

# PAY
PAY_API_KEY = os.getenv("PAY_API_KEY")
PAY_SHOP_ID = os.getenv("PAY_SHOP_ID")
CREATE_PAY_URL = os.getenv("CREATE_PAY_URL")
PAYMENT_LOGGER = add_named_logger("payment_logger")

# FEAR AND GREED INDEX API
Fear_And_Greed_API_URL = os.getenv("Fear_And_Greed_API_URL")

# COIN GLASS API
COINGLASS_API_URL = os.getenv("COINGLASS_API_URL")
COINGLASS_API_KEY = os.getenv("COINGLASS_API_KEY")
COINGLASS_LOGGER = add_named_logger("coinglass_logger")

# COINMARKERCUP API
COINMARKERCUP_API_URL = os.getenv("COINMARKERCUP_API_URL")
COINMARKERCUP_LOGGER = add_named_logger("coinmarketcup_logger")

# ASSERTIONS
# TODO добавить assert-проверки настроек, необходимых для работы приложения
required_for_debug_list = (
    TELEGRAM_API_TOKEN,
    CHARTIMG_API_TOKEN,
    DATABASE_PASSWORD,
    WEBAPP_HOST,
)

required_for_prod_list = (
    SSL_CERT_PATH,
    SSL_KEY_PATH,
)

check_list = required_for_debug_list
if DEBUG is False:
    check_list += required_for_prod_list

for value in check_list:
    assert value is not None
