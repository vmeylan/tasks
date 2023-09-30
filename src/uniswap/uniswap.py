from web3 import Web3
from constants import UNISWAP_V2_FACTORY_ADDR, UNISWAP_V3_FACTORY_ADDR, TOKEN_CONTRACT_MAP, UNISWAP_V3_TIERS_BPS, ROOT_DIRECTORY
from dotenv import load_dotenv
import json
import os
load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.environ.get('ETHEREUM_HTTP_ENDPOINT')))  # https://www.quicknode.com/

# https://docs.uniswap.org/contracts/v2/reference/smart-contracts/factory, https://unpkg.com/@uniswap/v2-core@1.0.0/build/IUniswapV2Factory.json
# https://web3py.readthedocs.io/en/stable/overview.html
# https://web3py.readthedocs.io/en/stable/overview.html#overview-contracts


def load_abi(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
        if 'result' in data:
            return data['result']
        raise ValueError("Invalid ABI format")


def get_v2_pool_address(token0_address=TOKEN_CONTRACT_MAP['WETH'], token1_address=TOKEN_CONTRACT_MAP['USDC']):
    v2_factory = w3.eth.contract(address=UNISWAP_V2_FACTORY_ADDR, abi=load_abi(f"{ROOT_DIRECTORY}/src/uniswap/UNISWAP_V2_FACTORY_ABI.json"))
    return v2_factory.functions.getPair(token0_address, token1_address).call()


def get_v3_pool_addresses(token0_address=TOKEN_CONTRACT_MAP['USDC'], token1_address=TOKEN_CONTRACT_MAP['WETH'], fee_tiers=UNISWAP_V3_TIERS_BPS):
    # https://docs.uniswap.org/contracts/v3/reference/core/UniswapV3Factory
    # https://etherscan.io/address/0x7858e59e0c01ea06df3af3d20ac7b0003275d4bf USDC-USDT example
    # The pool's fee in hundredths of a bip, i.e. 1e-6, e.g. 500
    v3_factory = w3.eth.contract(address=UNISWAP_V3_FACTORY_ADDR, abi=load_abi(f"{ROOT_DIRECTORY}/src/uniswap/UNISWAP_V3_FACTORY_ABI.json"))
    return [v3_factory.functions.getPool(token0_address, token1_address, fee).call() for fee in fee_tiers]


def fetch_pool_data(pool_address, version):
    # Fetch pool data based on the version and return
    # Placeholder implementation
    pass
    # what is the function name hidden variable
    assert False, f"{fetch_pool_data.__name__} not implemented yet"



