import hashlib
import hmac
import json
import os
import time
from collections import OrderedDict
from urllib.parse import urlencode

import requests


class KunaApiClient:
    API_DOMAIN = 'https://kuna.io/api/v2'
    TIMESTAMP_URL = f'{API_DOMAIN}/timestamp'
    TICKERS_URL = f'{API_DOMAIN}/tickers/'
    ORDER_BOOK_URL = f'{API_DOMAIN}/depth'
    TRADES_HISTORY_URL = f'{API_DOMAIN}/trades'

    ORDERS_URL = f'{API_DOMAIN}/orders'
    CANCEL_ORDER_URL = f'{API_DOMAIN}/order/delete'
    TRADES_URL = f'{API_DOMAIN}/trades/my'
    ME_URL = f'{API_DOMAIN}/members/me'

    def __init__(self):
        self.api_key = os.getenv('KUNA_API_KEY')
        self.api_secret = os.getenv('KUNA_API_SECRET')

    def __build_personal_url(self, url, method, params):
        tonce = int(round(time.time() * 1000))
        params['tonce'] = tonce
        params['access_key'] = self.api_key
        params = OrderedDict(sorted(params.items(), key=lambda t: t[0]))
        msg = '{0}|{1}|{2}'.format(method.upper(), url.replace('https://kuna.io', ''), urlencode(params))
        signature = hmac.new(self.api_secret.encode('utf-8'), msg=msg.encode('utf-8'), digestmod=hashlib.sha256)
        signature = signature.hexdigest()
        return f'{url}?access_key={self.api_key}&tonce={tonce}&signature={signature}'

    def timestamp(self):
        r = requests.get(self.TIMESTAMP_URL)
        r.raise_for_status()
        return json.loads(r.content.decode())

    def tick(self, market):
        r = requests.get(f'{self.TICKERS_URL}/{market}')
        r.raise_for_status()
        return json.loads(r.content.decode())

    def order_book(self, market):
        r = requests.get(f'{self.ORDER_BOOK_URL}/?market={market}')
        r.raise_for_status()
        return json.loads(r.content.decode())

    def trades_history(self, market):
        r = requests.get(f'{self.TRADES_HISTORY_URL}/?market={market}')
        r.raise_for_status()
        return json.loads(r.content.decode())

    def me(self):
        r = requests.get(self.__build_personal_url(self.ME_URL, 'GET', {}))
        r.raise_for_status()
        return json.loads(r.content.decode('utf-8'))

    def place_order(self, side, volume, price, market):
        params = {'side': side,
                  'volume': volume,
                  'market': market,
                  'price': price}
        url = self.__build_personal_url(self.ORDERS_URL, 'POST', params)
        return requests.post(url, params)

    def cancel_order(self, order_id):
        params = {'id': order_id}
        url = self.__build_personal_url(self.CANCEL_ORDER_URL, 'POST', params)
        return requests.post(url, params)

    def active_orders(self, market):
        params = {'market': market}
        url = self.__build_personal_url(self.ORDERS_URL, 'GET', params)
        r = requests.get(url, params)
        r.raise_for_status()
        return json.loads(r.content.decode('utf-8'))

    def my_trades_history(self, market):
        params = {'market': market}
        url = self.__build_personal_url(self.TRADES_URL, 'GET', params)
        r = requests.get(url, params)
        r.raise_for_status()
        return json.loads(r.content.decode('utf-8'))
