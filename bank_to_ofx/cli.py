import argparse
import os
import random
from collections import defaultdict

from .anonymize import anonymize_transactions
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
        print(f"Reading {input_file}...")
        parsed = bank_parser.parse(input_file)
        if not parsed:
            print(f"  Found no accounts/transactions in {input_file}")
            continue
        for account_id, transactions in parsed.items():
            print(f"  Found account {account_id}: {len(transactions)} transaction(s)")
            merged[account_id].extend(transactions)

    if not merged:
        print("No accounts found in any input file, nothing to convert.")
        return

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
        print(f"Reading {path}...")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        parsed = parse_ofx(text)
        if not parsed:
            print(f"  Found no accounts/transactions in {path} (unrecognized OFX format?)")
            continue
        for account_id, data in parsed.items():
            print(
                f"  Found account {account_id} ({data['account_type']}): "
                f"{len(data['transactions'])} transaction(s)"
            )
            bucket = merged.setdefault(
                account_id, {"account_type": data["account_type"], "transactions": []}
            )
            bucket["transactions"].extend(data["transactions"])

    if not merged:
        print("No accounts found in any input file, nothing to split.")
        return

    for account_id, data in merged.items():
        transactions = sorted(data["transactions"], key=lambda t: t["date"])
        assign_fitids(transactions)
        _write_monthly(account_id, transactions, data["account_type"], args.output_dir)


def _anonymize(args):
    os.makedirs(args.output_dir, exist_ok=True)
    rng = random.Random(args.seed)

    merged = {}
    for path in args.input_files:
        print(f"Reading {path}...")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        parsed = parse_ofx(text)
        if not parsed:
            print(f"  Found no accounts/transactions in {path} (unrecognized OFX format?)")
            continue
        for account_id, data in parsed.items():
            print(
                f"  Found account {account_id} ({data['account_type']}): "
                f"{len(data['transactions'])} transaction(s)"
            )
            bucket = merged.setdefault(
                account_id, {"account_type": data["account_type"], "transactions": []}
            )
            bucket["transactions"].extend(data["transactions"])

    if not merged:
        print("No accounts found in any input file, nothing to anonymize.")
        return

    multiple_accounts = len(merged) > 1
    for i, (account_id, data) in enumerate(merged.items(), start=1):
        anon_account_id = f"ANONYMIZED{i}" if multiple_accounts else "ANONYMIZED"
        print(f"Anonymizing account {account_id} -> {anon_account_id} ({len(data['transactions'])} transaction(s))")
        transactions = anonymize_transactions(data["transactions"], rng)
        assign_fitids(transactions)
        _write_full_range(anon_account_id, transactions, data["account_type"], args.output_dir)


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

    anonymize_subparser = subparsers.add_parser(
        "anonymize",
        help="Scrub account IDs, memos, amounts, and dates from one or more OFX files for safe sharing (e.g. bug reports)",
    )
    anonymize_subparser.add_argument("input_files", nargs="+", help="Path(s) to OFX file(s) to anonymize")
    anonymize_subparser.add_argument("-o", "--output-dir", default="output", help="Output folder (default: ./output)")
    anonymize_subparser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducible anonymization"
    )
    anonymize_subparser.set_defaults(func=_anonymize)

    args = parser.parse_args()
    args.func(args)
