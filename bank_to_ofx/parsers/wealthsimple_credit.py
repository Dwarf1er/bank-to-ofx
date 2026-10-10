import csv
from collections import defaultdict
from datetime import datetime

# Row types whose amount increases the available balance (like a deposit);
# everything else (purchases, fees, interest, ...) is treated as a debit.
CREDIT_TYPES = ("payment", "refund", "return", "credit", "reward", "cashback", "reversal")


class WealthsimpleCreditCardParser:
    """
    Parser for Wealthsimple credit card CSV statements.
    Columns: transaction_date, post_date, type, details, amount, currency
    Implements parse(file_path) -> dict[account_id, list[transactions]]
    """

    account_type = "CREDITCARD"

    def parse(self, path):
        accounts = defaultdict(list)
        account_id = "Wealthsimple-Credit"

        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date = datetime.strptime(row["transaction_date"].strip(), "%Y-%m-%d")
                    memo = row["details"].strip()
                    # Sign is derived from the row type rather than the CSV's
                    # own sign, so it's right whichever convention is used.
                    magnitude = abs(float(row["amount"]))
                    is_credit = row["type"].strip().lower().startswith(CREDIT_TYPES)
                    amount = magnitude if is_credit else -magnitude
                except Exception:
                    # skip malformed rows
                    continue

                accounts[account_id].append({
                    "date": date,
                    "amount": amount,
                    "memo": memo,
                    "seq": "",
                    "balance": None,
                })

        return accounts
