from uniswap import get_v2_pool_address, get_v3_pool_addresses, fetch_pool_data
from coingecko import get_usd_price
from utils import write_to_csv


def main():
    # Fetching pool addresses
    v2_pool_address = get_v2_pool_address()
    v3_pool_addresses = get_v3_pool_addresses()

    # Fetching pool data (placeholder)
    pool_data = []
    pool_data.append(fetch_pool_data(v2_pool_address, 'v2'))
    for addr in v3_pool_addresses:
        pool_data.append(fetch_pool_data(addr, 'v3'))

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
