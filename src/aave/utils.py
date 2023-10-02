def effective_daily_rate(rates):
    # Compounding the rates
    effective_rate = 1.0
    for rate in rates:
        effective_rate *= (1 + rate)
    return effective_rate - 1


def annualize_rate(daily_rate):
    return (1 + daily_rate) ** 365 - 1
