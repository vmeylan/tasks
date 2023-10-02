
from src import uniswap, aave, decoding_transactions_with_ABIs, decoding_traces_with_ABIs


uniswap.main.run()
decoding_transactions_with_ABIs.main.run()
aave.main.run()  # query error
decoding_traces_with_ABIs.main.run()  # require paid plan (tested with Alchemy, Infura, QuickNode, Etherscan)

