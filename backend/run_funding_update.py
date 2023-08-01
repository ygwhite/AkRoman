import asyncio

import aiogram

import os
import django

from settings import (
    BOT_PARSER_TOKEN
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()
from interface.backend import BackendInterface

bi = BackendInterface()
from coinglassAPI.requests import CoinglassAPI
from common.models import Currency

from settings import (

    COINGLASS_LOGGER, COINGLASS_API_URL, COINGLASS_API_KEY
)


async def run_update():
    while True:
        currencies_for_funging = {}
        # получаем все валютные пары
        currencies = await bi.get_allcurrencypairs()
        # Бд представление структурируем в словарь
        for cur in currencies:
            currencies_for_funging[cur['first']['abbr']] = True

        coinglass_obj = CoinglassAPI(COINGLASS_API_URL, COINGLASS_API_KEY, COINGLASS_LOGGER)
        coinglass_data = coinglass_obj.get_funding_rates()
        print(coinglass_data)

        for name,value in coinglass_data.items():
            if currencies_for_funging.get(name, None):
                await bi.update_coinglass_currency(name, value)
        await asyncio.sleep(10)

asyncio.run(run_update())
