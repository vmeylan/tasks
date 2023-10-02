import json

import requests
from selenium import webdriver
import os

from src.constants import root_directory, ADDRESS_TO_ABI_MAPPING


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


def return_driver():
    # set up Chrome driver options
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # NOTE: ChromeDriverManager().install() no longer works
    # needed to manually go here https://googlechromelabs.github.io/chrome-for-testing/#stable
    # and provide direct paths to script for both binary and driver
    # First run the script get_correct_chromedriver.sh
    # Paths for the Chrome binary and ChromeDriver
    CHROME_BINARY_PATH = f'{root_directory()}/src/chromium/chrome-linux64/chrome'
    CHROMEDRIVER_PATH = f'{root_directory()}/src/chromium/chromedriver-linux64/chromedriver'

    options = webdriver.ChromeOptions()
    options.binary_location = CHROME_BINARY_PATH

    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=options)
    return driver


ETHERSCAN_API_URL = "https://api.etherscan.io/api"
ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")  # Replace with your Etherscan API key


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


def decode_transaction(w3, transaction, contract_address):
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


