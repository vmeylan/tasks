import requests

BASE_URL = 'https://api.coingecko.com/api/v3/simple/price'

def get_usd_price(token_contract):
    params = {
        'ids': token_contract,
        'vs_currencies': 'usd'
    }
    response = requests.get(BASE_URL, params=params)
    return response.json()[token_contract]['usd']
