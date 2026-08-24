# bank_to_ofx/ofx_reader.py
import re
from datetime import datetime

TAG_RE = re.compile(r"<(/?[A-Za-z0-9.]+)>([^<\r\n]*)")


def parse_ofx(text):
    """
    Parse an OFX 1.x (SGML) statement export into:
        {account_id: {"account_type": "CHECKING"|"CREDITCARD", "transactions": [...]}}

    Tolerant of both SGML-style (no closing tag on leaf values, e.g.
    <TRNAMT>12.34) and XML-style (<TRNAMT>12.34</TRNAMT>) OFX, since it only
    reads the value up to the next '<' or end of line. Scans tags across the
    whole text rather than line-by-line, since some banks (e.g. Tangerine)
    emit the entire OFX body as a single unbroken line with no newlines
    between tags at all.
    """
    accounts = {}
    current_account_id = None
    current_account_type = "CHECKING"
    current_txn = None

    for match in TAG_RE.finditer(text):
        tag, value = match.group(1).upper(), match.group(2).strip()

        if tag == "STMTTRN":
            current_txn = {}
            continue

        if tag == "/STMTTRN":
            if current_txn is not None and current_account_id and "date" in current_txn and "amount" in current_txn:
                bucket = accounts.setdefault(
                    current_account_id,
                    {"account_type": current_account_type, "transactions": []},
                )
                current_txn.setdefault("memo", "")
                current_txn.setdefault("seq", "")
                current_txn.setdefault("balance", None)
                bucket["transactions"].append(current_txn)
            current_txn = None
            continue

        if tag == "CCACCTFROM":
            current_account_type = "CREDITCARD"
        elif tag == "BANKACCTFROM":
            current_account_type = "CHECKING"

        if current_txn is not None:
            if tag == "DTPOSTED":
                current_txn["date"] = _parse_ofx_date(value)
            elif tag == "TRNAMT":
                current_txn["amount"] = float(value)
            elif tag == "FITID":
                current_txn["seq"] = value
            elif tag == "MEMO":
                current_txn["memo"] = value
            elif tag == "NAME" and not current_txn.get("memo"):
                current_txn["memo"] = value
        elif tag == "ACCTID":
            current_account_id = value

    return accounts


def _parse_ofx_date(value):
    digits = value.split("[")[0].split(".")[0].strip()
    return datetime.strptime(digits[:8], "%Y%m%d").date()
