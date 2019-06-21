from bittrex.bittrex import Bittrex, API_V2_0
from exchanges.base import Exchange

my_bittrex = Bittrex(None, None)  # or defaulting to v1.1 as Bittrex(None, None)
def bch_price():
    info = my_bittrex.get_ticker('BTC-BCH')
    bid = info.get('result', {}).get('Bid')

    return bid
