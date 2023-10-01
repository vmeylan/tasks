import os

from src.uniswap.utils import load_abi

TOKEN_CONTRACT_MAP = {
    'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
}

UNISWAP_V2_FACTORY_ADDR = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'  # https://docs.uniswap.org/contracts/v2/reference/smart-contracts/factory
UNISWAP_V3_FACTORY_ADDR = '0x1F98431c8aD98523631AE4a59f267346ea31F984'  # https://docs.uniswap.org/contracts/v3/reference/deployments

UNISWAP_V3_TIERS = [0.05/100, 0.3/100, 1/100]
UNISWAP_V3_TIERS_BPS = [100, 500, 3000, 10000]
"""
In Uniswap V3, the fee amount is represented as a uint24 in hundredths of a bips. A bip is 1×10−41×10−4 or 0.01%.

For example, the fee tiers available in Uniswap V3 are:

    0.05% which is represented as 500 in uint24.
    0.30% which is represented as 3000 in uint24.
    1.00% which is represented as 10000 in uint24.

To convert a percentage into its uint24 representation, you multiply it by 10,000. So for 1%, the equivalent uint24 value would be:

1.00%×10,000=10,0001.00%×10,000=10,000

Thus, for 1%, you'd use the value 10000 as the uint24 representation.
"""


def root_directory() -> str:
    """
    Determine the root directory of the project based on the presence of '.git' directory.

    Returns:
    - str: The path to the root directory of the project.
    """
    current_dir = os.getcwd()

    while True:
        if '.git' in os.listdir(current_dir):
            return current_dir
        else:
            # Go up one level
            current_dir = os.path.dirname(current_dir)


ROOT_DIRECTORY = root_directory()

UNISWAP_V2_FACTORY_ABI = load_abi(f"{ROOT_DIRECTORY}/src/uniswap/ABI/UNISWAP_V2_FACTORY_ABI.json")
UNISWAP_V3_FACTORY_ABI = load_abi(f"{ROOT_DIRECTORY}/src/uniswap/ABI/UNISWAP_V3_FACTORY_ABI.json")
UNISWAP_V2_POOL_ABI = load_abi(f"{ROOT_DIRECTORY}/src/uniswap/ABI/UNISWAP_V2_POOL_ABI.json")
UNISWAP_V3_POOL_ABI = load_abi(f"{ROOT_DIRECTORY}/src/uniswap/ABI/UNISWAP_V3_POOL_ABI.json")
ERC20_ABI = load_abi(f"{ROOT_DIRECTORY}/src/uniswap/ABI/ERC20_ABI.json")  # https://gist.github.com/veox/8800debbf56e24718f9f483e1e40c35c#file-erc20-abi-json

