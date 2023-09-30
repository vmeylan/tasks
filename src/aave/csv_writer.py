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

