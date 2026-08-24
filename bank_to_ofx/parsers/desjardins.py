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

            for row in rows:
                if not any(row):
                    continue

                try:
                    folio = row[1].strip()
                    account = row[2].strip()
                    account_id = f"{folio}-{account}"
                    date = datetime.strptime(row[3], "%Y/%m/%d")
                    seq = row[4].strip()
                    memo = row[5].strip()
                    balance = float(row[13]) if row[13] else None

                    # The debit/credit value lands in a different column
                    # depending on the row's folio type (e.g. "EOP" vs
                    # "PR1"), so scan the columns between memo and balance
                    # instead of assuming a fixed position. Odd column
                    # indices hold debits, even ones hold credits.
                    amount = None
                    for i in range(6, 13):
                        value = row[i].strip()
                        if not value:
                            continue
                        amount = -float(value) if i % 2 == 1 else float(value)
                        break
                    if amount is None:
                        continue
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
