import json
import re

from loguru._logger import Logger

from utils.requests import BaseRequest


class CryptoBubbleAPI:
    __slots__ = "baseurl", "log", "rh", "url_1000data"

    def __init__(self,
                 baseurl: str,
                 request_handler: BaseRequest,
                 log: Logger,
                 ):

        self.url_1000data = baseurl
        self.rh = request_handler
        self.log = log

    async def get_thousand(self) -> str:
        try:
            response = await self.rh.request("get", self.url_1000data)
            content_json = response.content
            content_lst = json.loads(content_json)
            return content_lst
        except Exception as e:
            self.log.exception(e)
            return None

    async def _get_names_performance_dict(self):
        res_lst = await self.get_thousand()
        res_dict = {i['symbol']: i['performance']for i in res_lst}
        for items in res_lst:
            res_dict[items['symbol']].setdefault('24h', re.sub(r'(?<!^)(?=(\d{3})+$)', '.', str(items['volume'])))
            res_dict[items['symbol']].setdefault('marketcap', re.sub(r'(?<!^)(?=(\d{3})+$)', '.', str(items['marketcap'])))


        return res_dict

    async def get_currancy(self, name):
        res_dict = await self._get_names_performance_dict()
        return res_dict.get(name, None)
