import json
import requests
import time
import base64
import hmac
import hashlib
import urllib2

class Gemini_Helper:

    def __init__(self):
        self.load_key()
        self.prices = {}
        self.portfolio = {}
        self.totals = {}
        self.load_max_prices()
        self.update_all()

    def load_key(self):
        with open('key.json', 'rb') as f:
            key_dict = json.load(f)
        self.api_key = key_dict['key']
        self.api_secret = key_dict['secret']

    def load_max_prices(self):
        with open('max_prices.json', 'rb') as f:
            self.max_prices = json.load(f)

    def update_max_prices(self):
        with open('max_prices.json', 'wb') as f:
            json.dump(self.max_prices, f)

    def update_price(self, coin_url):
        base_url = "https://api.gemini.com/v1/pubticker"
        final_url = base_url + coin_url
        response = urllib2.urlopen(final_url)
        response_dict = json.loads(response.read())
        return float(response_dict['last'])

    def update_prices(self):
        self.prices['BTC'] = self.update_price("/btcusd")
        if self.prices['BTC'] > self.max_prices['BTC']:
            self.max_prices['BTC'] = self.prices['BTC']
            self.update_max_prices()
        self.prices['ETH'] = self.update_price("/ethusd")
        if self.prices['ETH'] > self.max_prices['ETH']:
            self.max_prices['ETH'] = self.prices['ETH']
            self.update_max_prices()

    def update_portfolio(self):
        # define request
        url = "https://api.gemini.com/v1/balances"
        request_str = "/v1/balances"
        nonce = str(int(round(time.time() * 1000)))

        # wrap up request and encrypt
        request_dict = {'request' : request_str,
                        'nonce' : nonce}
        request_json = json.dumps(request_dict)
        b64 = base64.b64encode(request_json)
        signature = hmac.new(str(self.api_secret), str(b64), hashlib.sha384).hexdigest()

        # define http headers and perform request
        headers = {
            'Content-Type': "text/plain",
            'Content-Length': "0",
            'X-GEMINI-APIKEY': self.api_key,
            'X-GEMINI-PAYLOAD': b64,
            'X-GEMINI-SIGNATURE': signature,
            'Cache-Control': "no-cache"
            }
        response = requests.request("POST", url, headers=headers)

        # put response into array
        response_arr = json.loads(response.text)
        for item in response_arr:
            self.portfolio[item['currency']] = float(item['amount'])

    def calculate_prices(self):
        self.totals['BTC'] = self.prices['BTC'] * self.portfolio['BTC']
        self.totals['ETH'] = self.prices['ETH'] * self.portfolio['ETH']
        self.totals['USD'] = self.portfolio['USD']

    def update_all(self):
        self.update_prices()
        self.update_portfolio()
        self.calculate_prices()

    def sell(self, coin, amount, price):
        # define request
        url = "https://api.gemini.com/v1/order/new"
        request_str = "/v1/order/new"
        nonce = str(int(round(time.time() * 1000)))
        amount_str = str(amount)
        price_str = str(price)
        coin_str = ""
        if coin == 'BTC':
            coin_str = "btcusd"
        elif coin == 'ETH':
            coin_str = "ethusd"
        else:
            print("something went wrong")

        # wrap up request and encrypt
        request_dict = {'request' : request_str,
                        'nonce' : nonce,
                        'symbol' : coin_str,
                        'amount' : amount_str,
                        'price' : price_str,
                        'side' : 'sell',
                        'type' : 'exchange limit',
                        'options' : ['immediate-or-cancel']
                        }
        request_json = json.dumps(request_dict)
        b64 = base64.b64encode(request_json)
        signature = hmac.new(str(self.api_secret), str(b64), hashlib.sha384).hexdigest()

        # define http headers and perform request
        headers = {
            'Content-Type': "text/plain",
            'Content-Length': "0",
            'X-GEMINI-APIKEY': self.api_key,
            'X-GEMINI-PAYLOAD': b64,
            'X-GEMINI-SIGNATURE': signature,
            'Cache-Control': "no-cache"
            }
        response = requests.request("POST", url, headers=headers)

        # put response into dictionary
        response_dict = json.loads(response.text)
        print("We just attempted to sell " + str(amount) + " of " + coin + " at " + price_str)
        print("This is what happened:")
        print(response_dict)
        return response_dict

    def sell_all(self, coin):
        return self.sell(coin, self.portfolio[coin], 9999.99)

