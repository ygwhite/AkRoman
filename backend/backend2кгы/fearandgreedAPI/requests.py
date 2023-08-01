import asyncio as aio
import json
from collections import OrderedDict
from io import BytesIO

from loguru._logger import Logger
import requests


class FearAndGreedAPI:
    __slots__ = "baseurl", "log", "url"

    def __init__(self,
                 baseurl: str,
                 log: Logger,
                 ):

        self.url = baseurl
        self.log = log

    def send_req(self) -> str:
        try:
            response = requests.get(self.url)
            content_json = response.content
            content_lst = json.loads(content_json)
            return content_lst
        except Exception as e:
            self.log.exception(e)
            return None

    def get_fear_gred_index(self):
        # https://api.alternative.me/fng
        res = self.send_req()
        if res:
            try:
                return res['data'][0]['value']
            except Exception as err:
                return 0
        else:
            return 0
