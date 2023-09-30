import graphql_helper
import data_processor
import csv_writer

def main():
    # Sample token_address for testing
    token_address = '0x...'

    # Fetch data using GraphQL
    raw_data = graphql_helper.fetch_data(graphql_helper.construct_query(token_address), {'tokenAddress': token_address})

    # Process and aggregate data
    daily_data = data_processor.aggregate_daily_data(raw_data)
    computed_data = data_processor.compute_daily_rate(daily_data)

    # Write data to CSV
    csv_writer.write_to_csv(computed_data, 'output.csv')

if __name__ == '__main__':
    main()

