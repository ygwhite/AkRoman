import copy

import asyncio as aio

from httpx import AsyncClient
from loguru._logger import Logger

from utils.requests import BaseRequest


class TVUAPI:
    __slots__ = "url", "rh", "log", "bi"

    # ключи идникаторов
    idc_keys = (
        "Recommend.Other", "Recommend.All", "Recommend.MA",
        "RSI", "RSI[1]",
        "Stoch.RSI.K", "Rec.Stoch.RSI",
        "Stoch.K", "Stoch.D", "Stoch.K[1]", "Stoch.D[1]",
        "CCI20", "CCI20[1]",
        "ADX", "ADX+DI", "ADX-DI", "ADX+DI[1]", "ADX-DI[1]",
        "AO", "AO[1]", "AO[2]",
        "Mom", "Mom[1]",
        "MACD.macd", "MACD.signal",
        "W.R", "Rec.WR",
        "BBPower", "BB.lower", "BB.upper", "Rec.BBPower",
        "P.SAR",
        "UO", "Rec.UO",
        "EMA5", "SMA5",
        "EMA10", "SMA10",
        "EMA20", "SMA20",
        "EMA30", "SMA30",
        "EMA50", "SMA50",
        "EMA100", "SMA100",
        "EMA200", "SMA200",
        "Ichimoku.BLine", "Rec.Ichimoku",
        "VWMA", "Rec.VWMA",
        "HullMA9", "Rec.HullMA9",
        "open", "close"
    )
    # словарь для перевода одних значений в другие
    conv = {
        "1m": "|1",
        "5m": "|5",
        "15m": "|15",
        "30m": "|30",
        "1h": "|60",
        "2h": "|120",
        "4h": "|240",
        "1d": "",
        "1W": "|1W",
        "1M": "|1M",
    }

    def __init__(self,
                 scanner_url: str,
                 request_handler: BaseRequest,
                 log: Logger, bi):

        self.url = scanner_url
        self.rh = request_handler
        self.log = log
        self.bi = bi

    async def form_req_data(self,
                            symbols: list[str],
                            timeframes: list[str],
                            idc_keys: list[str] | str = "*"):
        """Формирование POST запроса"""

        if idc_keys == "*":
            idc_keys = self.idc_keys

        assert isinstance(idc_keys, (list, tuple, set))
        assert all(isinstance(i, str) for i in idc_keys)

        data = {
            "symbols": {
                "tickers": [],
                "query": {
                    "types": []
                }
            },
            "columns": []
        }

        for symbol in symbols:
            # ticker = f"FX_IDC:{symbol}"
            ticker = f"BINANCE:{symbol}"
            data['symbols']['tickers'].append(ticker)

        # todo логика разных индикаторов
        for tf in timeframes:

            for idc_key in idc_keys:
                column = idc_key + self.conv.get(tf, '')
                data["columns"].append(column)

        return data

    async def group_idcs(self,
                         idcs: dict,
                         timeframes: list[str],
                         idc_keys: list[str] | str = "*"):

        if idc_keys == "*":
            idc_keys = self.idc_keys

        result = {}

        l = len(idc_keys)

        for data in idcs.get("data", []):
            # Future error prone!
            try:
                symbol = data['s'].split(':')[1]
                result[symbol] = dict()

                for i, tf in enumerate(timeframes):  # ?
                    # end can be out of bounds, that's ok
                    start, end = i * l, (i + 1) * l
                    idc_values = data['d'][start:end]
                    result[symbol][tf] = dict()

                    for j, idc_key in enumerate(idc_keys):
                        result[symbol][tf][idc_key] = idc_values[j]

            except Exception as e:
                self.log.exception(e)

        return result

    async def post_idcs(self,
                        symbols: list[str],
                        timeframes: list[str],
                        idc_keys: list[str] | str = "*",
                        session: AsyncClient | None = None) -> dict:
        """
        Request indicators for given symbols and timeframes.
        """
        # Формирование json данных для post запроса
        data = await self.form_req_data(symbols, timeframes, idc_keys=idc_keys)

        # POST запрос
        try:
            response = await self.rh.request("post", self.url,
                                             json=data, session=session)

        except Exception as e:
            self.log.exception(e)
            return None

        # Группировка списка во многоуровневый словарь
        result = await self.group_idcs(response.json(),
                                       timeframes, idc_keys=idc_keys)

        return result

    async def post_many_idcs(self, req_groups, idc_keys="*", loop=None):
        if loop is None:
            loop = aio.get_event_loop()

        async with self.rh.new_session() as sess:

            tasks = set()
            for timeframes, symbols in req_groups.items():
                task = loop.create_task(
                    self.post_idcs(
                        symbols,
                        timeframes,
                        idc_keys=idc_keys,
                        session=sess
                    )
                )
                tasks.add(task)

            idcs_groups_list = await aio.gather(*tasks)

        return idcs_groups_list
