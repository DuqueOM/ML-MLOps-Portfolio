#!/usr/bin/env python3
"""Fix import ordering in CarVision files."""

import subprocess
import sys

files_to_fix = [
    "CarVision-Market-Intelligence/src/carvision/training.py",
    "CarVision-Market-Intelligence/src/carvision/evaluation.py",
]

print("Installing isort and black...")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "isort", "black"], check=True)

print("\nFixing imports with isort...")
for file in files_to_fix:
    print(f"  Fixing {file}")
    subprocess.run([sys.executable, "-m", "isort", file], check=True)

print("\nFixing formatting with black...")
subprocess.run(
    [
        sys.executable,
        "-m",
        "black",
        "CarVision-Market-Intelligence/src/carvision/data.py",
    ],
    check=True,
)

print("\n✅ All files fixed!")
