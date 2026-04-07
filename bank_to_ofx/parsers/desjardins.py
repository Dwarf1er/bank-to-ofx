# bank_to_ofx/parsers/desjardins.py
import csv
from collections import defaultdict
from datetime import datetime


class DesjardinsParser:
    """
    Parser for Desjardins CSV bank statements.
    Implements the interface: parse(file_path) -> dict[account_id, list[transactions]]
    """

    def parse(self, path):
        accounts = defaultdict(list)

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

            # skip first line (empty) and second line (header-like)
            for row in rows[2:]:
                if not any(row):
                    continue

                try:
                    folio = row[1].strip()
                    account = row[2].strip()
                    account_id = f"{folio}-{account}"
                    date = datetime.strptime(row[3], "%Y/%m/%d")
                    seq = row[4].strip()
                    memo = row[5].strip()
                    amount = float(row[8])
                    balance = float(row[13]) if row[13] else None
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
