import csv

from src.uniswap.constants import ROOT_DIRECTORY

headers = [
    "Uniswap version",  # e.g., "v2" or "v3"
    "Pool address",
    "Contract address for token0",
    "Contract address for token1",
    "Fee tier (in bps)",  # Basis Points
    "Amount of token0 in the pool (normalized by decimals)",
    "Amount of token1 in the pool (normalized by decimals)",
    "Total value locked in the pool as token0 denominated in USD",
    "Total value locked in the pool as token1 denominated in USD",
    "Pool level price of token0 quoted by token1",
    "Pool level price of token1 quoted by token0",
    "Price of token0 in USD from external API",
    "Price of token1 in USD from external API"
]


def write_to_csv(pool_data, pool_name):
    """
    Writes the pool data to a specified CSV file.

    Args:
    - pool_data (list): List of dictionaries containing pool data.
    - filename (str, optional): The name of the CSV file to save. Defaults to "uniswap_pools.csv".

    Returns:
    - None
    """

    # Check if the pool_data is empty
    if not pool_data:
        print("The provided data is empty.")
        return

    filename = f"{ROOT_DIRECTORY}/data/{pool_name}_uniswap_pools.csv"

    # Write data to the CSV file
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = pool_data[0].keys()  # use the keys from the first dictionary as the header
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in pool_data:
            writer.writerow(row)

    print(f"CSV written successfully to {filename}!")