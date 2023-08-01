
import requests
from loguru._logger import Logger



class CoinglassAPI:
    __slots__ = "log", "url", "api_key"

    def __init__(self,
                 baseurl: str, api_key: str,
                 log: Logger,
                 ):

        self.url = baseurl
        self.api_key = api_key
        self.log = log

    def get_funding_rates(self):
        res = {}
        try:
            api_route = 'funding'
            params = {}
            headers = {"accept": "application/json", 'coinglassSecret': self.api_key}
            data = requests.get(self.url + api_route, params=params, headers=headers).json()
            data_lst = data['data']
            for i in data_lst:
                res[i['symbol']] = i['uMarginList'][0].get('rate', 0)

        except Exception as e:
            self.log.exception(e)
        return res

