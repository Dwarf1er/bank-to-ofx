import argparse
import os
from .ofx import generate_ofx
from .parsers import PARSERS
from .utils import to_kebab_case

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bank", help="Bank name (desjardins, wealthsimple)")
    parser.add_argument("input_file", help="Path to statement file")
    parser.add_argument("-o", "--output-dir", default="output")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    if args.bank not in PARSERS:
        raise ValueError(f"Unknown bank: {args.bank}")

    bank_parser = PARSERS[args.bank]()
    accounts = bank_parser.parse(args.input_file)

    for account_id, transactions in accounts.items():
        ofx_data = generate_ofx(account_id, transactions)
        filename = f"{to_kebab_case(account_id)}.ofx"
        output_path = os.path.join(args.output_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ofx_data)
        print(f"Wrote {output_path}")
