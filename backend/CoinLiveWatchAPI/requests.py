import requests
import json

url = "https://api.livecoinwatch.com/coins/list"


class InterfaceApi:
    def __init__(self, currency):
        self.response = None
        self.currency = currency
        self.dict_data = {}
        self.dict = {}

        payload = json.dumps({
            "currency": currency,
            "sort": "rank",
            "order": "ascending",
            "offset": 0,
            "limit": 100, "meta": True,
        })
        headers = {
            'content-type': 'application/json',
            'x-api-key': 'd5ced3cf-21b8-46c1-a767-21c7cd200fdb'
        }
        self.response = requests.request("POST", url, headers=headers, data=payload)
        self.response = self.response.json()
        for item in self.response.copy():
            item_keys = list(item.keys())
            for key in item_keys:
                if key not in ['name', 'rank', 'delta', 'volume']:
                    del item[key]
            delta_data = item.get('delta', {})
            delta_keys = list(delta_data.keys())
            for key in delta_keys:
                if key != 'day':
                    del delta_data[key]
            print(item)


def get_dict(self):
    self.dict[f'{self.currency}'] = self.response


api = InterfaceApi("USD")
