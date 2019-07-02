import requests

def get_bch_price():
    api_response = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin-cash/').json()
    usd_price = api_response[0]['price_usd']
    return usd_price
