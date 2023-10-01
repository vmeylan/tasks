from web3 import Web3
from constants import *
from dotenv import load_dotenv
import os
from decimal import Decimal, getcontext
getcontext().prec = 100  # Setting precision to a large number

from src.uniswap.coingecko import get_token_prices

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.environ.get('ETHEREUM_HTTP_ENDPOINT')))  # https://www.quicknode.com/

# https://docs.uniswap.org/contracts/v2/reference/smart-contracts/factory, https://unpkg.com/@uniswap/v2-core@1.0.0/build/IUniswapV2Factory.json
# https://web3py.readthedocs.io/en/stable/overview.html
# https://web3py.readthedocs.io/en/stable/overview.html#overview-contracts


def get_v2_pool_address(token0_address, token1_address):
    v2_factory = w3.eth.contract(address=UNISWAP_V2_FACTORY_ADDR, abi=UNISWAP_V2_FACTORY_ABI)
    return v2_factory.functions.getPair(token0_address, token1_address).call()


def get_v3_pool_addresses(token0_address, token1_address, fee_tiers=UNISWAP_V3_TIERS_BPS):
    # https://docs.uniswap.org/contracts/v3/reference/core/UniswapV3Factory
    # https://etherscan.io/address/0x7858e59e0c01ea06df3af3d20ac7b0003275d4bf USDC-USDT example
    v3_factory = w3.eth.contract(address=UNISWAP_V3_FACTORY_ADDR, abi=UNISWAP_V3_FACTORY_ABI)
    return [v3_factory.functions.getPool(token0_address, token1_address, fee).call() for fee in fee_tiers]


def get_v3_pool_balances(pool_address, token0_address, token1_address):
    # Create contract objects
    token0_contract = w3.eth.contract(address=token0_address, abi=ERC20_ABI)
    token1_contract = w3.eth.contract(address=token1_address, abi=ERC20_ABI)

    # Fetch balances
    token0_balance = token0_contract.functions.balanceOf(pool_address).call()
    token1_balance = token1_contract.functions.balanceOf(pool_address).call()

    return token0_balance, token1_balance


def sqrt_price_to_price(sqrtPriceX96, token0Decimals, token1Decimals):
    """Converts the sqrt price to actual price."""
    # https://blog.uniswap.org/uniswap-v3-math-primer
    math_price = (Decimal(sqrtPriceX96) ** 2) / (Decimal(2) ** 192)
    decimal_adjustment = Decimal(10) ** (token0Decimals - token1Decimals)
    price = math_price * decimal_adjustment
    return float(price)


def get_pool_level_prices(token0_balance, token1_balance, token0_decimals, token1_decimals, pool_contract, quote_token="token1"):
    """
    Calculate the pool level price of token0 quoted by token1 and vice versa.

    Parameters:
    - token0_balance: Balance of token0 in the pool.
    - token1_balance: Balance of token1 in the pool.
    - pool_contract: The pool contract object.
    - method: The method to compute price ("average" or "spot"). Defaults to "average".
    - quote_token: Which token to use as the quote currency ("token1" or "token0"). Defaults to "token1".

    Returns:
    A tuple (priceToken0inToken1, priceToken1inToken0)
    """

    # Ensure precision for Decimal calculations
    getcontext().prec = 100

    # Assert non-zero balances
    assert token0_balance > 0, "Token0 balance must be greater than 0"
    assert token1_balance > 0, "Token1 balance must be greater than 0"

    sqrtPriceX96 = pool_contract.functions.slot0().call()[0]
    assert sqrtPriceX96 > 0, "sqrtPriceX96 should be greater than 0"

    # Use the helper to convert sqrt price to actual price
    priceToken0inToken1 = sqrt_price_to_price(sqrtPriceX96, token0_decimals, token1_decimals)
    priceToken1inToken0 = 1 / priceToken0inToken1

    if quote_token == "token1":
        return priceToken0inToken1
    elif quote_token == "token0":
        return priceToken1inToken0
    else:
        raise ValueError("Invalid quote_token specified. Must be 'token1' or 'token0'.")


def get_v3_pool_details(pool_address):
    # Create a contract object using Web3
    pool_contract = w3.eth.contract(address=pool_address, abi=UNISWAP_V3_POOL_ABI)

    # Fetch the token addresses
    token0_address = pool_contract.functions.token0().call()
    token1_address = pool_contract.functions.token1().call()

    # Load the ABI for a standard ERC20 token
    # You'll need to have this ABI stored in your project
    token0_contract = w3.eth.contract(address=token0_address, abi=ERC20_ABI)
    token1_contract = w3.eth.contract(address=token1_address, abi=ERC20_ABI)

    # Fetch token decimals
    token0_decimals = token0_contract.functions.decimals().call()
    token1_decimals = token1_contract.functions.decimals().call()

    # Fetch token balances for given pool
    token0_balance, token1_balance = get_v3_pool_balances(pool_address, token0_address, token1_address)

    # Use our new method to fetch the prices
    priceToken0inToken1 = get_pool_level_prices(token0_balance, token1_balance, token0_decimals, token1_decimals, pool_contract, quote_token="token1")
    priceToken1inToken0 = get_pool_level_prices(token0_balance, token1_balance, token0_decimals, token1_decimals, pool_contract, quote_token="token0")

    token0_balance = token0_balance / (10 ** token0_decimals)
    token1_balance = token1_balance / (10 ** token1_decimals)

    # Fetch the token prices in USD from an external source (placeholder)
    # Replace with your actual implementation
    token0_usd_price, token1_usd_price = get_token_prices(token0_address.lower(), token1_address.lower())

    # Calculate values as per CSV format
    token0_usd_value = token0_balance * token0_usd_price
    token1_usd_value = token1_balance * token1_usd_price

    fee_tier = w3.eth.contract(address=pool_address, abi=UNISWAP_V3_POOL_ABI).functions.fee().call()

    # Return data in the format of the CSV headers
    return {
        "Uniswap version": "v3",
        "Pool address": pool_address,
        "Contract address for token0": token0_address,
        "Contract address for token1": token1_address,
        "Fee tier (in bps)": fee_tier,
        "Amount of token0 in the pool (normalized by decimals)": token0_balance,
        "Amount of token1 in the pool (normalized by decimals)": token1_balance,
        "Total value locked in the pool as token0 denominated in USD": token0_usd_value,
        "Total value locked in the pool as token1 denominated in USD": token1_usd_value,
        "Pool level price of token0 quoted by token1": priceToken0inToken1,
        "Pool level price of token1 quoted by token0": priceToken1inToken0,
        "Price of token0 in USD from external API": token0_usd_price,
        "Price of token1 in USD from external API": token1_usd_price
    }


def get_v2_pool_details(pool_address):
    # Create a contract object using Web3 for the v2 pool
    pool_contract = w3.eth.contract(address=pool_address, abi=UNISWAP_V2_POOL_ABI)

    # Fetch the token addresses
    token0_address = pool_contract.functions.token0().call()
    token1_address = pool_contract.functions.token1().call()

    # Create contract objects for the tokens
    token0_contract = w3.eth.contract(address=token0_address, abi=ERC20_ABI)
    token1_contract = w3.eth.contract(address=token1_address, abi=ERC20_ABI)

    # Fetch token decimals
    token0_decimals = token0_contract.functions.decimals().call()
    token1_decimals = token1_contract.functions.decimals().call()

    # Fetch token balances (reserves) for the given v2 pool
    token0_balance, token1_balance, _ = pool_contract.functions.getReserves().call()
    token0_balance, token1_balance = token0_balance / (10 ** token0_decimals), token1_balance / (10 ** token1_decimals)

    # Calculate pool-level prices
    priceToken0inToken1 = token0_balance / token1_balance
    priceToken1inToken0 = token1_balance / token0_balance

    # Fetch the token prices in USD from an external source (placeholder)
    # Replace with your actual implementation
    token0_usd_price, token1_usd_price = get_token_prices(token0_address.lower(), token1_address.lower())

    # Calculate values as per CSV format
    token0_usd_value = token0_balance * token0_usd_price
    token1_usd_value = token1_balance * token1_usd_price

    # Return data in the format of the CSV headers
    return {
        "Uniswap version": "v2",
        "Pool address": pool_address,
        "Contract address for token0": token0_address,
        "Contract address for token1": token1_address,
        "Fee tier (in bps)": "N/A",  # Not applicable for v2
        "Amount of token0 in the pool (normalized by decimals)": token0_balance,
        "Amount of token1 in the pool (normalized by decimals)": token1_balance,
        "Total value locked in the pool as token0 denominated in USD": token0_usd_value,
        "Total value locked in the pool as token1 denominated in USD": token1_usd_value,
        "Pool level price of token0 quoted by token1": priceToken0inToken1,
        "Pool level price of token1 quoted by token0": priceToken1inToken0,
        "Price of token0 in USD from external API": token0_usd_price,
        "Price of token1 in USD from external API": token1_usd_price
    }

