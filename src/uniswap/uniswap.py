from web3 import Web3
from constants import UNISWAP_V2_FACTORY_ADDR, UNISWAP_V3_FACTORY_ADDR, UNISWAP_V3_TIERS_BPS, ROOT_DIRECTORY, ERC20_ABI, UNISWAP_V3_POOL_ABI, UNISWAP_V3_FACTORY_ABI, UNISWAP_V2_FACTORY_ABI
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
    token0_balance = token0_balance / (10 ** token0_decimals)
    token1_balance = token1_balance / (10 ** token1_decimals)

    # Calculate prices using the Q64.96 format
    sqrtPriceX96 = pool_contract.functions.slot0().call()[0]
    # Calculate prices using the Q64.96 format
    sqrtPriceX96_decimal = Decimal(sqrtPriceX96)
    priceToken0inToken1_decimal = (sqrtPriceX96_decimal ** 2) / (Decimal(2) ** 96)
    priceToken1inToken0_decimal = (Decimal(2) ** 96) / (sqrtPriceX96_decimal ** 2)

    # Convert Decimals back to float for further processing if necessary
    priceToken0inToken1 = float(priceToken0inToken1_decimal)
    priceToken1inToken0 = float(priceToken1inToken0_decimal)

    # Fetch the token prices in USD from an external source (placeholder)
    # Replace with your actual implementation
    token0_usd_price, token1_usd_price = get_token_prices(token0_address.lower(), token1_address.lower())

    # Calculate values as per CSV format
    token0_usd_value = token0_balance * token0_usd_price
    token1_usd_value = token1_balance * token1_usd_price

    fee_tier = w3.eth.contract(address=pool_address, abi=UNISWAP_V3_POOL_ABI).functions.fee().call()

    # Return data in the format of the CSV headers
    return [
        "v3",
        pool_address,
        token0_address,
        token1_address,
        fee_tier,
        token0_balance,
        token1_balance,
        token0_usd_value,
        token1_usd_value,
        priceToken0inToken1,
        priceToken1inToken0,
        token0_usd_price,
        token1_usd_price
    ]


def fetch_pool_data(pool_address, version):
    details = {}
    assert False, "This function is not implemented yet"
    return details
