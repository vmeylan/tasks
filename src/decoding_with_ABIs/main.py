import os
from typing import List
from web3 import Web3
import requests
import json
from dotenv import load_dotenv
load_dotenv()
import argparse

from src.constants import *

ETHERSCAN_API_URL = "https://api.etherscan.io/api"
ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")  # Replace with your Etherscan API key
# Setup web3 instance with the provider
w3 = Web3(Web3.HTTPProvider(os.environ.get('ETHEREUM_HTTP_ENDPOINT')))


def get_contract_abi(contract_address: str) -> dict:
    """
    Fetch ABI of a contract from Etherscan
    """
    params = {
        "module": "contract",
        "action": "getabi",
        "address": contract_address,
        "apikey": ETHERSCAN_API_KEY
    }

    response = requests.get(ETHERSCAN_API_URL, params=params)
    data = response.json()

    if data['status'] == '1' and 'result' in data:
        return json.loads(data['result'])
    else:
        raise Exception(f"Error fetching ABI for {contract_address}. Error: {data['message']}")


def save_abi_locally(contract_address: str, directory=f"{root_directory()}/src/uniswap/ABI/"):
    """
    Fetch ABI from Etherscan and save it locally in a specified directory. If ABI exists locally, load from the file.
    """
    filepath = os.path.join(directory, f"{contract_address}.json")

    # If ABI file exists locally, load and return
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            print(f"Loading ABI for {contract_address} from local file.")
            return json.load(file)

    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Fetch ABI from Etherscan
    abi = get_contract_abi(contract_address)

    # Save the ABI to a JSON file named after the contract address
    with open(filepath, 'w') as file:
        json.dump(abi, file, indent=4)

    print(f"ABI for {contract_address} saved successfully!")
    return abi


def decode_transaction(transaction, contract_address):
    abi = ADDRESS_TO_ABI_MAPPING.get(contract_address, None)  # Retrieve ABI directly from the mapping
    if not abi:
        return None
    contract = w3.eth.contract(address=contract_address, abi=abi)
    try:
        decoded_data = contract.decode_function_input(transaction['input'])
        return {
            "function_name": decoded_data[0].fn_name,
            "values": decoded_data[1]
        }
    except:
        return None


def get_transactions(block_identifier: int, contract_addresses: List[str]):
    block = w3.eth.get_block(block_identifier, full_transactions=True)
    results = []
    for transaction in block.transactions:
        if transaction['to'] in contract_addresses:
            decoded_data = decode_transaction(transaction, transaction['to'])
            results.append({
                "transaction_hash": transaction.hash.hex(),
                "contract_address": transaction['to'],
                "decoded": decoded_data
            })

    return [result for result in results if result["decoded"] is not None]


def parse_args():
    parser = argparse.ArgumentParser(description='Fetch and decode Ethereum transactions for a block and list of contract addresses.')

    # Adding command line arguments
    parser.add_argument('-b', '--block', type=int, help='Block identifier. If not provided, a default will be used.')
    parser.add_argument('-a', '--addresses', type=str, nargs='+', help='List of contract addresses. If not provided, default addresses will be used.')

    args = parser.parse_args()

    # Check if any arguments were provided
    if args.block or args.addresses:
        return args
    return None


contract_addresses = [UNISWAP_V2_FACTORY_ADDR, UNISWAP_V3_FACTORY_ADDR]
block_identifier = 10008355

if __name__ == "__main__":
    args = parse_args()

    if args:
        # Use provided block_identifier or default
        block_identifier_to_use = args.block if args.block else block_identifier

        # Use provided addresses or default
        addresses_to_use = args.addresses if args.addresses else contract_addresses
    else:
        block_identifier_to_use = input(f"Please enter a block identifier or press Enter to use default ({block_identifier}): ")
        block_identifier_to_use = int(block_identifier_to_use) if block_identifier_to_use else block_identifier

        input_addresses = input("Please enter one or more contract addresses (comma-separated), or press Enter to use default: ")
        if not input_addresses.strip():
            addresses_to_use = contract_addresses
        else:
            addresses_to_use = [addr.strip() for addr in input_addresses.split(',')]

    # Save ABI locally
    for contract in addresses_to_use:
        save_abi_locally(contract)

    # Fetch transactions for provided block and addresses
    print(f"Returned transactions for addresses {addresses_to_use} and for block {block_identifier}:")
    print(get_transactions(block_identifier_to_use, addresses_to_use))
