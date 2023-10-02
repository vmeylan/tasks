import json
import logging
import csv

from src.utils import root_directory


def initialize_csv(filename, headers):
    """ Initialize a CSV file with headers if it doesn't exist """
    try:
        with open(filename, 'x', newline='') as f:  # 'x' mode will raise a FileExistsError if the file exists
            writer = csv.writer(f)
            writer.writerow(headers)
    except FileExistsError:
        pass


def append_supplies_to_csv(supplies):
    filename = f"{root_directory}/data/supplies.csv"
    with open(filename, 'a', newline='') as f:  # 'a' mode for appending
        writer = csv.writer(f)
        # Write data rows
        for supply in supplies:
            writer.writerow([
                supply["timestamp"],
                supply["reserve"]["stableBorrowRate"],
                supply["reserve"]["variableBorrowRate"],
                supply["reserve"]["utilizationRate"],
                supply["reserve"]["lastUpdateTimestamp"]
            ])
    logging.info(f"Appended supplies data to {filename}")


def append_borrows_to_csv(borrows):
    filename = f"{root_directory}/data/borrows.csv"
    with open(filename, 'a', newline='') as f:  # 'a' mode for appending
        writer = csv.writer(f)
        # Write data rows
        for borrow in borrows:
            writer.writerow([
                borrow["user"]["id"],
                borrow["amount"],
                borrow["timestamp"],
                borrow["txHash"],
                borrow["borrowRate"]
            ])
    logging.info(f"Appended borrows data to {filename}")


def write_to_csv(data, filename):
    # Write data to CSV file here
    headers = [
        "date",  # in YY-MM-DD format, UTC timezone
        "min_deposit_APR",
        "max_deposit_APR",
        "min_utilization_rate",
        "max_utilization_rate",
        "daily_deposit_rate",
        "daily_deposit_APR",
        # Optional headers for borrowing rates:
        "min_variable_borrow_rate",
        "max_variable_borrow_rate",
        "min_stable_borrow_rate",
        "max_stable_borrow_rate"
    ]
    pass

