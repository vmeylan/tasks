import argparse
from src.uniswap.csv_writer import write_to_csv
from uniswap import *


def main(token0_address=None, token1_address=None):
    # If the addresses are not provided, default to WETH-USDC
    if not token0_address or not token1_address:
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

    # If token names are not known, use addresses for the CSV filename
    pool_name = f"{token0_address}-{token1_address}"
    if 'TOKEN_CONTRACT_MAP' in globals():
        reverse_map = {v: k for k, v in TOKEN_CONTRACT_MAP.items()}
        token0_name = reverse_map.get(token0_address, token0_address)
        token1_name = reverse_map.get(token1_address, token1_address)
        if token0_name and token1_name:
            pool_name = f"{token0_name}-{token1_name}"
        else:
            pool_name = f"{token0_address}-{token1_address}"

    write_to_csv(pool_data, pool_name=pool_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Uniswap CSV for token pair.')
    parser.add_argument('--token0', type=str, help='Smart contract address of token0', default='')
    parser.add_argument('--token1', type=str, help='Smart contract address of token1', default='')
    args = parser.parse_args()

    use_defaults = False
    if not args.token0 or not args.token1:
        args.token0 = input("Enter the smart contract address for token0 (Press enter for default WETH): ")
        args.token1 = input("Enter the smart contract address for token1 (Press enter for default USDC): ")

        if not args.token0 and not args.token1:
            use_defaults = True

    # If token names are known, print them, else print the addresses
    if 'TOKEN_CONTRACT_MAP' in globals() and not use_defaults:
        reverse_map = {v: k for k, v in TOKEN_CONTRACT_MAP.items()}
        token0_name = reverse_map.get(args.token0, args.token0)
        token1_name = reverse_map.get(args.token1, args.token1)
        print(f"Starting processing for {token0_name} and {token1_name} ...")
    else:
        print(f"Starting processing for WETH and USDC pools ...")

    main(args.token0, args.token1)
