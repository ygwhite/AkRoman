import os
import django
from ssl import SSLContext, PROTOCOL_TLS_SERVER

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from interface.backend import BackendInterface
from tradingview_uapi.scan import TVUAPI
from websocket.server import WSServer
from utils.requests import BaseRequest, RotationManager, IdManager
from TradingViewApi.requests import TradingViewApi
from settings import (
    DEBUG_WSS, DEBUG,
    WSS_HOST,
    WSS_PORT,
    WSS_QLIMIT,
    WSS_LOGGER,

    TRADING_VIEW_API_URL,
    TRADING_VIEW_API_LOGGER,
    SSL_KEY_PATH,
    SSL_CERT_PATH,
    TRADING_VIEW_INIDICATORS_DICT,
    TRADING_VIEW_API_SESSIONID,
    TRADING_VIEW_API_SESSIONIDSIGN,
    TV_HEADERS, TV_TIMEOUT

)

if DEBUG_WSS == False:
    ssl_context = SSLContext(PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(SSL_CERT_PATH, keyfile=SSL_KEY_PATH)
else:
    ssl_context = None

if __name__ == "__main__":

    idmanager = IdManager(
        TV_HEADERS,
    )

    request_handler = BaseRequest(
        idmanager,
        TV_TIMEOUT
    )
    bi = BackendInterface()

    tva = TradingViewApi(
        TRADING_VIEW_API_URL,
        request_handler,
        TRADING_VIEW_API_LOGGER,
        TRADING_VIEW_INIDICATORS_DICT, TRADING_VIEW_API_SESSIONID, TRADING_VIEW_API_SESSIONIDSIGN
    )
    service = WSServer(
        WSS_HOST,
        WSS_PORT,
        ssl_context,
        10,
        tva,
        bi,
        WSS_QLIMIT,
        WSS_LOGGER
    )

    service.start()
