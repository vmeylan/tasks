import json


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
