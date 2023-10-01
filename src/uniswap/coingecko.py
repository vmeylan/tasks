import requests


def get_token_prices(token_address_1, token_address_2, platform_id='ethereum', currency='usd'):
    """
    Fetches the prices of two tokens using their contract addresses from CoinGecko API.

    :param platform_id: The platform ID issuing tokens (e.g., 'ethereum' for ETH tokens).
    :param token_address_1: Contract address of the first token.
    :param token_address_2: Contract address of the second token.
    :param currency: The currency in which the price should be returned. Default is 'usd'.
    :return: Prices of the two tokens.
    """

    COINGECKO_URL = f"https://api.coingecko.com/api/v3/simple/token_price/{platform_id}"

    parameters = {
        'contract_addresses': f"{token_address_1},{token_address_2}",
        'vs_currencies': currency
    }

    response = requests.get(COINGECKO_URL, params=parameters)

    # Ensure we got a valid response
    response.raise_for_status()

    data = response.json()

    # Fetching the prices
    token1_price = data[token_address_1][currency]
    token2_price = data[token_address_2][currency]

    return token1_price, token2_price
