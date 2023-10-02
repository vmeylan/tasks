from datetime import datetime
import requests
import asyncio
import aiohttp
import logging
import pandas as pd
from src.aave.utils import effective_daily_rate, annualize_rate
from src.utils import root_directory

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

RAY_DECIMALS = 10 ** 27


# The fetch_page function remains largely the same, but the query and function signature change slightly:

async def fetch_page(session, last_id, data_type, token_symbol="USDC"):
    assert data_type in ["supplies", "borrows"], "Invalid data_type. Choose either 'supplies' or 'borrows'."
    endpoint = "https://api.thegraph.com/subgraphs/name/aave/protocol-v3"
    query = f"""
    {{
        {data_type}(
            where: {{reserve_: {{symbol: "{token_symbol}"}}, id_gt: "{last_id}"}}
            orderBy: timestamp
            orderDirection: asc
            first: 1000
        ){{
            id
            timestamp
            reserve {{
                stableBorrowRate
                variableBorrowRate
                utilizationRate
                lastUpdateTimestamp
            }}
        }}
    }}
    """
    async with session.post(endpoint, json={"query": query}) as response:
        if response.status != 200:
            logging.error(f"Request failed with status code: {response.status}")
            raise ValueError(f"Request failed with status code: {response.status}")
        data = await response.json()
        if not data['data'][data_type]:
            logging.info(f"No more data to fetch for {data_type.upper()} with {token_symbol.upper()}")
            return data['data']
        logging.info(f"Data fetched for {data_type.upper()} with {token_symbol.upper()} with timestamp: {pd.to_datetime(data['data'][data_type][0]['timestamp'], unit='s')}")
        logging.info(data['data'])
        return data['data']


async def fetch_data_by_type(data_type, token_symbol="USDC"):
    async with aiohttp.ClientSession() as session:
        all_data = []
        last_id = ""  # initial value

        while True:
            fetched_data = await fetch_page(session, last_id, data_type, token_symbol)

            if not fetched_data[data_type]:
                break

            all_data.extend(fetched_data[data_type])
            last_id = fetched_data[data_type][-1]['id']  # set the last_id for the next iteration

        process_and_write_data(data_type, all_data)
        return all_data


def aggregate_data_by_date(data):
    df = pd.DataFrame(data)

    # Convert timestamp to date
    df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.strftime('%Y-%m-%d')

    # Unpack dictionary column into multiple columns
    reserve_df = df['reserve'].apply(pd.Series)

    # Convert rate columns
    df['stableBorrowRate'] = reserve_df['stableBorrowRate'].astype(float) / RAY_DECIMALS
    df['variableBorrowRate'] = reserve_df['variableBorrowRate'].astype(float) / RAY_DECIMALS
    df['utilizationRate'] = reserve_df['utilizationRate'].astype(float)

    # Get the min and max values for each rate
    df_min = df.groupby('date').min()[['stableBorrowRate', 'variableBorrowRate', 'utilizationRate']]
    df_max = df.groupby('date').max()[['stableBorrowRate', 'variableBorrowRate', 'utilizationRate']]

    # Renaming the min and max columns
    df_min.columns = [f"min_{col}" for col in df_min.columns]
    df_max.columns = [f"max_{col}" for col in df_max.columns]

    # Merging the min and max dataframes
    aggregated = pd.merge(df_min, df_max, on='date').reset_index()

    return aggregated


def process_and_write_data(data_type, data):
    aggregated = aggregate_data_by_date(data)

    # Depending on the data type, calculate some derived columns
    aggregated['daily_rate_stable'] = effective_daily_rate(aggregated['stableBorrowRate_max'])
    aggregated['daily_apr_stable'] = annualize_rate(aggregated['daily_rate_stable'])
    aggregated['daily_rate_variable'] = effective_daily_rate(aggregated['variableBorrowRate_max'])
    aggregated['daily_apr_variable'] = annualize_rate(aggregated['daily_rate_variable'])

    # Drop the original camel case columns
    columns_to_drop = ['stableBorrowRate_min', 'stableBorrowRate_max', 'variableBorrowRate_min', 'variableBorrowRate_max', 'utilizationRate_min', 'utilizationRate_max']
    aggregated.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    # Renaming based on data_type
    if data_type == "supplies":
        # For deposits
        aggregated.rename(columns={
            'date': 'date',
            'stableBorrowRate_min': 'min_deposit_APR',
            'stableBorrowRate_max': 'max_deposit_APR',
            'utilizationRate_min': 'min_utilization_rate',
            'utilizationRate_max': 'max_utilization_rate',
            'daily_rate_stable': 'daily_deposit_rate',
            'daily_apr_stable': 'daily_deposit_APR',
        }, inplace=True)

    elif data_type == "borrows":
        # For borrows
        aggregated.rename(columns={
            'date': 'date',
            'stableBorrowRate_min': 'min_stable_borrow_rate',
            'stableBorrowRate_max': 'max_stable_borrow_rate',
            'variableBorrowRate_min': 'min_variable_borrow_rate',
            'variableBorrowRate_max': 'max_variable_borrow_rate',
            'utilizationRate_min': 'min_utilization_rate',
            'utilizationRate_max': 'max_utilization_rate',
            'daily_rate_stable': 'daily_borrow_rate',
            'daily_apr_stable': 'daily_borrow_APR',
        }, inplace=True)

    # Save the processed data
    aggregated.to_csv(f"{root_directory()}/data/processed_{data_type}.csv", index=False)
    logging.info(f"Saved data for {data_type.upper()} with min and max dates: {aggregated['date'].min()} - {aggregated['date'].max()}")

    return aggregated


def get_pool_by_asset_from_graph(underlying_asset: str) -> str:
    """
    Queries the GraphQL endpoint to get the mapAssetPools data and
    fetches the pool associated with a given underlying asset.

    Args:
    - underlying_asset (str): The ERC20 token address (underlying asset).

    Returns:
    - str: The associated pool for the given underlying asset.
    """

    # Query the GraphQL endpoint
    endpoint = "https://api.thegraph.com/subgraphs/name/aave/protocol-v3"  # Replace with the actual endpoint

    query = """
    {
      mapAssetPools{
        id
        pool
        underlyingAsset
      }
    }
    """

    response = requests.post(endpoint, json={"query": query})
    data = response.json()

    # Save this data locally in a Python dictionary.
    asset_to_pool_mapping = {entry['underlyingAsset']: entry['pool'] for entry in data['data']['mapAssetPools']}

    # Given an underlyingAsset, fetch the pool.
    return asset_to_pool_mapping.get(underlying_asset)


# Example usage:


def fetch_and_aggregate_data(token_symbol):
    user_input = "0x6b175474e89094c44da98b954eedeac495271d0f"
    pool_address = get_pool_by_asset_from_graph(user_input)

    borrows = asyncio.run(fetch_data_by_type("borrows", token_symbol))
    supplies = asyncio.run(fetch_data_by_type("supplies", token_symbol))

    processed_supplies = process_and_write_data("supplies", supplies)
    processed_borrows = process_and_write_data("borrows", borrows)

    # Merging at the end
    merged = pd.merge(processed_supplies, processed_borrows, on='date', how='outer', suffixes=('_supply', '_borrow'))
    merged.to_csv(f"{root_directory()}/data/{user_input}_aave_data.csv", index=False)
    logging.info("Merged supplies and borrows data.")


# Example usage:
fetch_and_aggregate_data("USDC")
