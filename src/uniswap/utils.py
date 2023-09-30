import pandas as pd

def write_to_csv(data, file_name='uniswap_pools.csv'):
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)