#!/usr/bin/env python3
"""
Entry point for BankChurn Predictor.
Wrapper around src.bankchurn.cli.

Run from project root: python main.py --mode train --config configs/config.yaml
Or install the package first: pip install -e .
"""
import sys

from src.bankchurn.cli import cli_main

if __name__ == "__main__":
    sys.exit(cli_main())
