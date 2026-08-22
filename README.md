<div align="center">

# Bank to OFX
#### Convert your bank statements to OFX

<img alt="bank-to-ofx logo" src="https://raw.githubusercontent.com/Dwarf1er/bank-to-ofx/master/assets/bank-to-ofx-logo.png" height="250" />

![License](https://img.shields.io/github/license/Dwarf1er/bank-to-ofx?style=for-the-badge)
![Issues](https://img.shields.io/github/issues/Dwarf1er/bank-to-ofx?style=for-the-badge)
![PRs](https://img.shields.io/github/issues-pr/Dwarf1er/bank-to-ofx?style=for-the-badge)
![Contributors](https://img.shields.io/github/contributors/Dwarf1er/bank-to-ofx?style=for-the-badge)
![Stars](https://img.shields.io/github/stars/Dwarf1er/bank-to-ofx?style=for-the-badge)

</div>

## Project Description

`bank-to-ofx` is a command-line tool to convert various bank statement formats into OFX files for personal finance software like HomeBank or GnuCash.

It currently supports:
* Desjardins CSV (checking/savings accounts)
* Desjardins PDF (credit card statements)
* Wealthsimple CSV

The tool is designed to be extensible so that adding another parser for different financial institutions is easy.

## Table of Contents

<!-- mtoc-start -->

* [Installation](#installation)
* [Usage](#usage)
* [Splitting Statements into Calendar Months](#splitting-statements-into-calendar-months)
* [Adding Support for New Banks](#adding-support-for-new-banks)
* [License](#license)

<!-- mtoc-end -->

## Installation

`bank-to-ofx` uses [UV](https://github.com/astral-sh/uv) for project management. To install the CLI:

Clone the repository:
```bash
git clone https://github.com/yourusername/bank-to-ofx.git
cd bank-to-ofx
```

Sync dependencies and build the editable package:
```bash
uv sync
uv tool install .
uv tool update-shell
```

This will install `bank-to-ofx` in editable mode inside UV’s virtual environment.
Changes you make to the source code will immediately reflect in the CLI.

Run the CLI using UV:
```bash
uv run bank-to-ofx --help
```

## Usage

```bash
uv run bank-to-ofx <bank> <path_to_statement>... [-o output_dir] [-m|--monthly]
```

* `<bank>`: bank identifier, e.g., desjardins, desjardins-credit, wealthsimple
* `<path_to_statement>...`: one or more paths to your bank's statement files
* `-o output_dir`: optional output folder (default: `./output`)
* `-m, --monthly`: merge all given statements per account and split the result into one OFX file per calendar month (see [Splitting Statements into Calendar Months](#splitting-statements-into-calendar-months))

Examples:
```bash
uv run bank-to-ofx desjardins ~/Downloads/releve.csv -o ~/bank-to-ofx-output
uv run bank-to-ofx desjardins-credit ~/Downloads/releve-visa.pdf -o ~/bank-to-ofx-output
uv run bank-to-ofx wealthsimple ~/Downloads/wealthsimple.csv
```

Desjardins only offers CSV export for checking/savings accounts; credit card
(Visa) statements are PDF-only. `desjardins-credit` extracts transactions
directly from that PDF's text, so results may need double-checking against
statement layout changes Desjardins introduces over time.

The output folder will contain per-account OFX files named in kebab-case,
suffixed with the transaction date range covered by that statement (e.g.
`4540xxxxxxxx1234-20260820-20260915.ofx`), so converting several statements
for the same account into the same folder won't overwrite each other.

## Splitting Statements into Calendar Months

Credit card billing cycles rarely align with calendar months (e.g. Aug 20 –
Sep 19), which is awkward for month-by-month bookkeeping. There are two ways
to get one OFX file per calendar month, pulling together the tail end of one
statement and the start of the next (and any number of statements in
between) wherever a month is split across more than one of them:

**Directly from statement files**, with `-m`/`--monthly` on the bank
subcommand — pass all your statement files for one account in a single call:

```bash
uv run bank-to-ofx desjardins-credit ~/Downloads/releve-*.pdf --monthly -o ~/monthly
```

**From already-converted OFX files**, with the standalone `split-monthly`
command — useful if you've already run each statement through `bank-to-ofx`
separately, or have OFX files from somewhere else entirely:

```bash
uv run bank-to-ofx split-monthly <path_to_ofx_file>... [-o output_dir]
```

Example:
```bash
uv run bank-to-ofx desjardins-credit ~/Downloads/releve-aout.pdf -o ~/statements
uv run bank-to-ofx desjardins-credit ~/Downloads/releve-septembre.pdf -o ~/statements
uv run bank-to-ofx split-monthly ~/statements/*.ofx -o ~/monthly
```

Both approaches produce one file per account per month, e.g.
`<account>-2026-08.ofx` and `<account>-2026-09.ofx`, each containing every
transaction dated within that month regardless of which source statement it
came from.

Note: `FITID`s are regenerated during both conversion and splitting, derived
from each transaction's date rather than the source statement's own
numbering — this keeps them unique when merging multiple statements and
stable across re-runs, so most accounting software will recognize a repeat
import as a duplicate instead of double-counting it.

## Adding Support for New Banks
Create a new parser class in `bank_to_ofx/parsers/` implementing:
```python
class MyBankParser:
    def parse(self, path) -> dict[str, list[dict]]:
        # return {account_id: [transactions]}
        pass
```

Register it in `bank_to_ofx/parsers/__init__.py`:
```bash
PARSERS["mybank"] = MyBankParser
```

Run via CLI:
```bash
uv run bank-to-ofx mybank path/to/file
```

## License

This software is licensed under the [MIT license](LICENSE).
