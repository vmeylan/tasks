from src.uniswap.constants import TOKEN_CONTRACT_MAP
from uniswap import *
from coingecko import get_usd_price
from utils import write_to_csv


def main():
    token0_address = TOKEN_CONTRACT_MAP['USDC']
    token1_address = TOKEN_CONTRACT_MAP['USDC']
    # Fetching pool addresses
    v2_pool_address = get_v2_pool_address(token0_address, token1_address)
    v3_pool_addresses = get_v3_pool_addresses(token0_address, token1_address)

    # Fetching pool data (placeholder)
    pool_data = []
    for addr in v3_pool_addresses:
        pool_data.append(get_v3_pool_details(addr))

    pool_data.append(fetch_pool_data(v2_pool_address, 'v2'))

    # Get token prices from Coingecko
    token0_usd_price = get_usd_price(token0)
    token1_usd_price = get_usd_price(token1)

    # Compile data (this is a placeholder)
    data = {
        'Uniswap version': [],
        'Pool address': [],
    }

    write_to_csv(data)


if __name__ == "__main__":
    main()
