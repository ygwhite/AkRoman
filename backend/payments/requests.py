import asyncio as aio
import json
import requests
from collections import OrderedDict
from io import BytesIO

from loguru._logger import Logger



class PaymentsAPI:

    def __init__(self, api_key, shop_id):
        self.api_key = api_key
        self.shop_id = shop_id
        self.base_url = 'https://api.cryptocloud.plus/v1'
        self.headers = {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json'
        }

    def create_invoice(self, amount, currency='USD', order_id=None, email=None):
        url = f'{self.base_url}/invoice/create'
        payload = {
            'shop_id': self.shop_id,
            'amount': amount,
            'order_id': order_id,
            'currency': currency,
            'email': email
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def get_invoice_info(self, uuid):
        url = f'{self.base_url}/invoice/info'
        params = {
            'uuid': uuid
        }
        response = requests.get(url, params=params, headers=self.headers)
        return response.json()
