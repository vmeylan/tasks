from typing import List
from dotenv import load_dotenv
load_dotenv()
import argparse
from web3 import Web3

from src.constants import *
from src.utils import save_abi_locally, decode_transaction


w3 = Web3(Web3.HTTPProvider(os.environ.get('ETHEREUM_HTTP_ENDPOINT')))  # https://www.quicknode.com/


def get_transactions(block_identifier: int, contract_addresses: List[str], interaction_type: str = "both"):
    """
    On the reason of using interaction_type selector and defaulting to both (GPT4):

    The task specifies to return transactions that "interact with one of the given smart contracts,"
    but the wording is somewhat ambiguous. In the context of Ethereum, transactions "interact" with a
    contract by sending data to the contract's address. So, it's standard to look for the contract's
    address in the to field of the transaction.
    However, in a broader interpretation, any transaction involving the contract, whether it's a contract
    creation transaction, a contract method call, or even Ether being sent from a contract, could be considered as "interacting" with the contract.

    To capture all interactions:
    Transactions To the Contract: These are typical transactions where someone sends Ether to
    the contract or triggers one of its methods. This is captured by the to field.

    Transactions From the Contract: These would be contract creation transactions
    (where the contract was first put on the blockchain). They are less common to track in this context,
    but if you wanted to, you could look for the from field being one of the contract addresses.
    """
    block = w3.eth.get_block(block_identifier, full_transactions=True)
    results = []

    for transaction in block.transactions:
        # Depending on the interaction type, decide if the transaction should be processed
        process_transaction = False

        if interaction_type == "both":
            process_transaction = transaction['to'] in contract_addresses or transaction['from'] in contract_addresses
        elif interaction_type == "to":
            process_transaction = transaction['to'] in contract_addresses
        elif interaction_type == "from":
            process_transaction = transaction['from'] in contract_addresses
        else:
            raise ValueError(f"Invalid interaction type: {interaction_type}. Allowed values are 'both', 'to', 'from'.")

        # If the transaction matches the filtering criteria
        if process_transaction:
            # If the transaction 'to' address is a contract address, attempt to decode it
            decoded_data = decode_transaction(w3, transaction, transaction['to']) if transaction['to'] in contract_addresses else None

            results.append({
                "transaction_hash": transaction.hash.hex(),
                "contract_address": transaction['to'] if transaction['to'] in contract_addresses else transaction['from'],
                "decoded": decoded_data
            })

    # Return only transactions with decoded data (i.e., only those which interacted 'to' a contract and were decodable)
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

def run():
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


if __name__ == "__main__":
    run()
