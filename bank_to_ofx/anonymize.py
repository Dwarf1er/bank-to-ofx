import calendar


def anonymize_transactions(transactions, rng):
    """
    Return a new list of transactions with memo/name, amount, and date
    scrubbed for safe sharing (e.g. in bug reports):
    - date: shifted to a random day within the same year/month
    - amount: perturbed by a random factor, sign preserved
    - memo/name: replaced with a sequential placeholder
    """
    anonymized = [
        {**t, "date": _shift_date_within_month(t["date"], rng), "amount": _perturb_amount(t["amount"], rng)}
        for t in transactions
    ]
    anonymized.sort(key=lambda t: t["date"])

    for i, t in enumerate(anonymized, start=1):
        t["memo"] = f"TRANSACTION {i}"

    return anonymized


def _shift_date_within_month(date, rng):
    days_in_month = calendar.monthrange(date.year, date.month)[1]
    return date.replace(day=rng.randint(1, days_in_month))


def _perturb_amount(amount, rng):
    if amount == 0:
        return 0.0
    return round(amount * rng.uniform(0.5, 1.5), 2)
