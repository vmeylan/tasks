import requests
import json

from src.aave.graphql_helper import fetch_entities


def fetch_utilization_rate(symbol="USDC"):
    # Endpoint for the Aave v3 subgraph
    endpoint = "https://api.thegraph.com/subgraphs/name/aave/protocol-v3"

    # GraphQL query to fetch utilizationRate for the given reserve symbol
    query = f"""
    {{
      reserves(where: {{symbol: "{symbol}"}}) {{
        utilizationRate
      }}
    }}
    """

    response = requests.post(endpoint, json={'query': query})
    data = response.json()

    return json.dumps(data, indent=4)


def main():
    symbol_to_query = "USDC"  # You can change this to another symbol if needed
    result = fetch_utilization_rate(symbol_to_query)
    print(result)
    print('')


if __name__ == "__main__":
    # main()
    fetch_entities()
