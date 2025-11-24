#!/usr/bin/env python3
"""
Entry point for BankChurn Predictor.
Wrapper around src.bankchurn.cli.
"""
import sys
from pathlib import Path

# Add src to path if needed (though typically running from root works)
# This ensures we can find the package even if not installed as a package
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.bankchurn.cli import cli_main
except ImportError as e:
    print(f"Error importing src.bankchurn.cli: {e}")
    print("Make sure you are running from the project root.")
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(cli_main())
