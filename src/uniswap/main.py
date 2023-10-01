from src.uniswap.csv_writer import write_to_csv
from uniswap import *


def main():
    token0_name = 'WETH'
    token1_name = 'USDC'
    token0_address = TOKEN_CONTRACT_MAP[token0_name]
    token1_address = TOKEN_CONTRACT_MAP[token1_name]
    # Fetching pool addresses
    v2_pool_address = get_v2_pool_address(token0_address, token1_address)
    v3_pool_addresses = get_v3_pool_addresses(token0_address, token1_address)

    # Fetching pool data (placeholder)
    pool_data = []
    for addr in v3_pool_addresses:
        pool_data.append(get_v3_pool_details(addr))

    pool_data.append(get_v2_pool_details(v2_pool_address))

    write_to_csv(pool_data, pool_name=f"{token0_name}-{token1_name}")


if __name__ == "__main__":
    main()
