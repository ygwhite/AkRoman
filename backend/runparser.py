import asyncio
import os

import aiogram as aiogram
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from interface.backend import BackendInterface

from parserTelethone.parser import SignalsParser
from utils.requests import BaseRequest

from settings import (
    CHARTIMG_TIMEOUT,
    PARSER_LOGGER,
    TELETHONE_API_ID, TELETHONE_API_HASH, BOT_PARSER_TOKEN, TELETHONE_PROXY
)


async def main():
    bi = BackendInterface()
    bot = aiogram.Bot(token=BOT_PARSER_TOKEN)
    service = SignalsParser(bot, TELETHONE_API_ID, TELETHONE_API_HASH, bi, PARSER_LOGGER, proxy=TELETHONE_PROXY)

    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
