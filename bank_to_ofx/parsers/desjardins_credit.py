# bank_to_ofx/parsers/desjardins_credit.py
import re
from collections import defaultdict
from datetime import date

import pdfplumber

TRANSACTION_TABLE_HEADER = "Transactions effectuées avec la carte de"

# "DATE DU RELEVÉ Jour 21 Mois 08 Année 2026" (label and value order can vary
# slightly depending on how pdfplumber reconstructs the table, so the regex
# only anchors on the three field names and grabs the digits after each).
STATEMENT_DATE_RE = re.compile(
    r"DATE DU RELEV[ÉE].*?Jour\D*(\d{2}).*?Mois\D*(\d{2}).*?Ann[ée]e\D*(\d{4})",
    re.IGNORECASE | re.DOTALL,
)

# Masked card/account number, e.g. "4540 XXXX XXXX 1234"
ACCOUNT_NUMBER_RE = re.compile(r"\b(\d{4}(?:[ -]?X{4}){2}[ -]?\d{4})\b", re.IGNORECASE)

# A transaction row: transaction date (DD MM), posting date (DD MM), an
# optional 3-digit sequence number (only present on statements before
# 2021-05), a free-form description (may include city/province), then the
# amount, optionally suffixed with "CR" for credits/payments.
TRANSACTION_LINE_RE = re.compile(
    r"^(?P<tx_day>\d{2})\s+(?P<tx_month>\d{2})\s+"
    r"(?P<post_day>\d{2})\s+(?P<post_month>\d{2})\s+"
    r"(?:(?P<seq>\d{3})\s+)?"
    r"(?P<desc>.+?)\s+"
    r"(?P<amount>-?[\d\s]+,\d{2})\s*(?P<credit>CR)?$"
)


def _parse_amount(raw_amount, is_credit):
    value = float(raw_amount.replace(" ", "").replace(",", "."))
    # Purchases decrease the account balance (like a debit); payments and
    # refunds ("CR") increase it (like a credit), matching the sign
    # convention used by the other parsers in this project.
    return value if is_credit else -value


class DesjardinsCreditCardParser:
    """
    Parser for Desjardins Visa/credit card PDF statements.
    Implements the interface: parse(file_path) -> dict[account_id, list[transactions]]

    Desjardins only offers CSV export for checking/savings accounts;
    credit card statements are PDF-only, so transactions are extracted by
    scanning the extracted text for transaction-shaped lines rather than by
    relying on exact PDF layout/column coordinates, which vary between
    statement versions.
    """

    account_type = "CREDITCARD"

    def parse(self, path):
        accounts = defaultdict(list)

        text = self._extract_text(path)
        statement_date = self._find_statement_date(text)
        account_id = self._find_account_id(text) or "Desjardins-Carte-de-Credit"

        in_transactions = False
        seq_counter = 0
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            if TRANSACTION_TABLE_HEADER in line:
                in_transactions = True
                continue

            if not in_transactions:
                continue

            match = TRANSACTION_LINE_RE.match(line)
            if not match:
                continue

            seq_counter += 1
            try:
                tx_day = int(match.group("tx_day"))
                tx_month = int(match.group("tx_month"))
                txn_date = date(statement_date.year, tx_month, tx_day)
                # Transaction dates only carry day/month; a December
                # transaction on a January statement belongs to the
                # previous year.
                if txn_date > statement_date:
                    txn_date = txn_date.replace(year=txn_date.year - 1)
            except ValueError:
                continue

            amount = _parse_amount(match.group("amount"), bool(match.group("credit")))
            memo = match.group("desc").strip()
            seq = match.group("seq") or f"{seq_counter:03}"

            accounts[account_id].append({
                "date": txn_date,
                "amount": amount,
                "memo": memo,
                "seq": seq,
                "balance": None,
            })

        return accounts

    def _extract_text(self, path):
        pages_text = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                pages_text.append(page.extract_text() or "")
        return "\n".join(pages_text)

    def _find_statement_date(self, text):
        match = STATEMENT_DATE_RE.search(text)
        if match:
            day, month, year = (int(g) for g in match.groups())
            return date(year, month, day)
        return date.today()

    def _find_account_id(self, text):
        match = ACCOUNT_NUMBER_RE.search(text)
        if match:
            return match.group(1).replace(" ", "").replace("-", "")
        return None
