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
* Desjardins CSV
* Wealthsimple CSV

The tool is designed to be extensible so that adding another parser for different financial institutions is easy.

## Table of Contents

<!-- mtoc-start -->

* [Installation](#installation)
* [Usage](#usage)
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
uv run bank-to-ofx <bank> <path_to_statement> [-o output_dir]
```

* `<bank>`: bank identifier, e.g., desjardins, wealthsimple
* `<path_to_statement>`: path to your bank's statement file
* `-o output_dir`: optional output folder (default: `./output`)

Examples:
```bash
uv run bank-to-ofx desjardins ~/Downloads/releve.csv -o ~/bank-to-ofx-output
uv run bank-to-ofx wealthsimple ~/Downloads/wealthsimple.csv
```

The output folder will contain per-account OFX files named in kebab-case.

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
