import argparse
import os
from collections import defaultdict

from .ofx import generate_ofx
from .ofx_reader import parse_ofx
from .parsers import PARSERS
from .utils import assign_fitids, to_kebab_case


def _write_ofx(account_id, transactions, account_type, output_dir, suffix=""):
    ofx_data = generate_ofx(account_id, transactions, account_type=account_type)
    filename = f"{to_kebab_case(account_id)}{suffix}.ofx"
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ofx_data)
    print(f"Wrote {output_path}")


def _write_full_range(account_id, transactions, account_type, output_dir):
    suffix = ""
    if transactions:
        start, end = transactions[0]["date"], transactions[-1]["date"]
        suffix = f"-{start:%Y%m%d}-{end:%Y%m%d}"
    _write_ofx(account_id, transactions, account_type, output_dir, suffix)


def _write_monthly(account_id, transactions, account_type, output_dir):
    by_month = defaultdict(list)
    for t in transactions:
        by_month[(t["date"].year, t["date"].month)].append(t)

    for (year, month), month_transactions in sorted(by_month.items()):
        suffix = f"-{year:04d}-{month:02d}"
        _write_ofx(account_id, month_transactions, account_type, output_dir, suffix)


def _convert(args):
    os.makedirs(args.output_dir, exist_ok=True)

    bank_parser = PARSERS[args.bank]()
    account_type = getattr(bank_parser, "account_type", "CHECKING")

    merged = defaultdict(list)
    for input_file in args.input_files:
        for account_id, transactions in bank_parser.parse(input_file).items():
            merged[account_id].extend(transactions)

    for account_id, transactions in merged.items():
        transactions.sort(key=lambda t: t["date"])
        assign_fitids(transactions)

        if args.monthly:
            _write_monthly(account_id, transactions, account_type, args.output_dir)
        else:
            _write_full_range(account_id, transactions, account_type, args.output_dir)


def _split_monthly(args):
    os.makedirs(args.output_dir, exist_ok=True)

    merged = {}
    for path in args.input_files:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for account_id, data in parse_ofx(text).items():
            bucket = merged.setdefault(
                account_id, {"account_type": data["account_type"], "transactions": []}
            )
            bucket["transactions"].extend(data["transactions"])

    for account_id, data in merged.items():
        transactions = sorted(data["transactions"], key=lambda t: t["date"])
        assign_fitids(transactions)
        _write_monthly(account_id, transactions, data["account_type"], args.output_dir)


def main():
    parser = argparse.ArgumentParser(prog="bank-to-ofx")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for bank_name in PARSERS:
        bank_subparser = subparsers.add_parser(bank_name, help=f"Convert one or more {bank_name} statements to OFX")
        bank_subparser.add_argument("input_files", nargs="+", help="Path(s) to statement file(s)")
        bank_subparser.add_argument("-o", "--output-dir", default="output", help="Output folder (default: ./output)")
        bank_subparser.add_argument(
            "-m",
            "--monthly",
            action="store_true",
            help="Merge all input files per account and split transactions into one OFX file per calendar month",
        )
        bank_subparser.set_defaults(func=_convert, bank=bank_name)

    split_subparser = subparsers.add_parser(
        "split-monthly",
        help="Merge one or more OFX files and split their transactions into one file per calendar month",
    )
    split_subparser.add_argument("input_files", nargs="+", help="Path(s) to OFX file(s) to merge and split")
    split_subparser.add_argument("-o", "--output-dir", default="output", help="Output folder (default: ./output)")
    split_subparser.set_defaults(func=_split_monthly)

    args = parser.parse_args()
    args.func(args)
