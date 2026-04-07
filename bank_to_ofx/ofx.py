from datetime import datetime


def format_ofx_date(dt: datetime) -> str:
    return dt.strftime("%Y%m%d000000")


def generate_ofx(account_id, transactions):
    now = datetime.now().strftime("%Y%m%d%H%M%S")

    lines = []

    lines.append("OFXHEADER:100")
    lines.append("DATA:OFXSGML")
    lines.append("VERSION:102")
    lines.append("SECURITY:NONE")
    lines.append("ENCODING:UTF-8")
    lines.append("CHARSET:UTF-8")
    lines.append("")
    lines.append("<OFX>")

    lines.append("<SIGNONMSGSRSV1>")
    lines.append("<SONRS>")
    lines.append(f"<DTSERVER>{now}")
    lines.append("<STATUS><CODE>0<SEVERITY>INFO</STATUS>")
    lines.append("</SONRS>")
    lines.append("</SIGNONMSGSRSV1>")

    lines.append("<BANKMSGSRSV1>")
    lines.append("<STMTTRNRS>")
    lines.append("<TRNUID>1")
    lines.append("<STATUS><CODE>0<SEVERITY>INFO</STATUS>")
    lines.append("<STMTRS>")

    lines.append("<BANKACCTFROM>")
    lines.append("<BANKID>DESJARDINS")
    lines.append(f"<ACCTID>{account_id}")
    lines.append("<ACCTTYPE>CHECKING")
    lines.append("</BANKACCTFROM>")

    lines.append("<BANKTRANLIST>")

    if transactions:
        start = min(t["date"] for t in transactions)
        end = max(t["date"] for t in transactions)
        lines.append(f"<DTSTART>{format_ofx_date(start)}")
        lines.append(f"<DTEND>{format_ofx_date(end)}")

    for t in transactions:
        trn_type = "CREDIT" if t["amount"] > 0 else "DEBIT"

        lines.append("<STMTTRN>")
        lines.append(f"<TRNTYPE>{trn_type}")
        lines.append(f"<DTPOSTED>{format_ofx_date(t['date'])}")
        lines.append(f"<TRNAMT>{t['amount']}")
        lines.append(f"<FITID>{t['seq']}")
        lines.append(f"<NAME>{t['memo'][:32]}")
        lines.append(f"<MEMO>{t['memo']}")
        lines.append("</STMTTRN>")

    lines.append("</BANKTRANLIST>")
    lines.append("</STMTRS>")
    lines.append("</STMTTRNRS>")
    lines.append("</BANKMSGSRSV1>")
    lines.append("</OFX>")

    return "\n".join(lines)
