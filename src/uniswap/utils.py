import json

import pandas as pd

def write_to_csv(data, file_name='uniswap_pools.csv'):
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)


def load_abi(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
        try:
            if 'result' in data:
                return data['result']
            else:
                return data
        except Exception as e:
            raise ValueError(f"Invalid ABI format: {e}")
