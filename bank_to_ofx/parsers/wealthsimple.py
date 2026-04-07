import csv
from collections import defaultdict
from datetime import datetime


class WealthsimpleParser:
    """
    Parser for Wealthsimple CSV bank statements.
    Implements parse(file_path) -> dict[account_id, list[transactions]]
    """

    def parse(self, path):
        accounts = defaultdict(list)
        account_id = "Wealthsimple"

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)  # headers are present
            for row in reader:
                try:
                    date = datetime.strptime(row["date"], "%Y-%m-%d")
                    memo = row["description"]
                    amount = float(row["amount"])
                    balance = float(row["balance"]) if row["balance"] else None
                    seq = ""  # Wealthsimple CSV has no per-account sequence
                except Exception:
                    # skip malformed rows
                    continue

                accounts[account_id].append({
                    "date": date,
                    "amount": amount,
                    "memo": memo,
                    "seq": seq,
                    "balance": balance,
                })

        return accounts
