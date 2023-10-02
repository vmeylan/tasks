import json
import requests
from web3 import Web3
from typing import List, Union
from dotenv import load_dotenv

from src.constants import *
from src.decoding_transactions_with_ABIs.main import parse_args
from src.utils import save_abi_locally, decode_transaction

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.environ.get('ETHEREUM_HTTP_ENDPOINT_ALCHEMY')))

# https://www.quicknode.com/docs/ethereum/trace_block
# Please note that this RPC method is available by default for all Build & Scale plans. If you are using the Discover plan, you will need to upgrade to a paid plan to utilize this method. See our pricing for more information. Also, it is supported only on OpenEthereum & Erigon.
# https://docs.infura.io/networks/ethereum/how-to/trace-transactions
# Trace API is currently an open beta feature, available to paying Infura customers.
# https://docs.alchemy.com/reference/trace-get
# b'{"jsonrpc":"2.0","id":1,"error":{"code":-32600,"message":"trace_block is not available on the Free tier - upgrade to Growth, Scale, or Enterprise for access. See available methods at https://docs.alchemy.com/alchemy/documentation/apis"}}'


def get_traces(block_identifier: Union[int, str], contract_addresses: List[str], interaction_type: str = "both"):
    # Convert block number to block hash format if it's a number. Otherwise, use the given block hash.
    if isinstance(block_identifier, int):
        block_param = hex(block_identifier)
    else:
        block_param = block_identifier

    # Make the RPC call to Alchemy
    url = os.environ.get('ETHEREUM_HTTP_ENDPOINT_ALCHEMY')
    payload = {
        "method": "trace_block",
        "params": [block_param],
        "id": 1,
        "jsonrpc": "2.0"
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=payload)

    traces = response.json()['result']
    results = []

    for trace in traces:
        # Depending on the interaction type, decide if the trace should be processed
        process_trace = False
        if interaction_type == "both":
            process_trace = trace['action']['to'] in contract_addresses or trace['action']['from'] in contract_addresses
        elif interaction_type == "to":
            process_trace = trace['action']['to'] in contract_addresses
        elif interaction_type == "from":
            process_trace = trace['action']['from'] in contract_addresses
        else:
            raise ValueError(f"Invalid interaction type: {interaction_type}. Allowed values are 'both', 'to', 'from'.")

        # If the trace matches the filtering criteria
        if process_trace:
            # If the trace 'to' address is a contract address, attempt to decode it
            if trace['action']['to'] in contract_addresses:
                decoded_data = decode_transaction({'to': trace['action']['to'], 'input': trace['action'].get('input', '0x')}, trace['action']['to'])
            else:
                decoded_data = None

            results.append({
                "trace_type": trace["type"],
                "from": trace['action']['from'],
                "to": trace['action']['to'],
                "decoded": decoded_data
            })

    # Return only traces with decoded data
    return [result for result in results if result["decoded"] is not None]


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
    print(f"Returned traces for addresses {addresses_to_use} and for block {block_identifier}:")
    print(get_traces(block_identifier_to_use, addresses_to_use))
