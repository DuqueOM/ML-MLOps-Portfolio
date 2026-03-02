#!/usr/bin/env python3
"""
Production Load Testing — ML-MLOps Portfolio (Wrapper).

DEPRECATED: This script delegates to the canonical Locust load tests.
Prefer running directly:
    locust -f tests/load/locustfile.py --headless --users 10 --run-time 30s

This wrapper is kept for backward compatibility with existing
documentation and CI scripts that reference scripts/load_test_services.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCUSTFILE = ROOT / "tests" / "load" / "locustfile.py"


def main():
    print("═" * 60)
    print("  ML-MLOps Portfolio — Load Tests (via Locust)")
    print("═" * 60)
    print()

    if not LOCUSTFILE.exists():
        print(f"❌ Locustfile not found: {LOCUSTFILE}")
        sys.exit(1)

    # Parse args or use defaults
    host = "http://localhost"
    users = "10"
    runtime = "30s"

    for i, arg in enumerate(sys.argv[1:]):
        if arg in ("--host", "-h") and i + 2 <= len(sys.argv[1:]):
            host = sys.argv[i + 2]
        elif arg in ("--users", "-u") and i + 2 <= len(sys.argv[1:]):
            users = sys.argv[i + 2]
        elif arg in ("--time", "-t") and i + 2 <= len(sys.argv[1:]):
            runtime = sys.argv[i + 2]

    print(f"→ Delegating to: locust -f {LOCUSTFILE}")
    print(f"  Host: {host}, Users: {users}, Runtime: {runtime}")
    print()

    cmd = [
        sys.executable,
        "-m",
        "locust",
        "-f",
        str(LOCUSTFILE),
        "--headless",
        "--users",
        users,
        "--spawn-rate",
        "2",
        "--run-time",
        runtime,
        "--host",
        host,
    ]

    try:
        result = subprocess.run(cmd, cwd=str(ROOT))
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("⚠️  Locust not installed. Install: pip install locust")
        print("   Or run directly: locust -f tests/load/locustfile.py --headless")
        sys.exit(1)


if __name__ == "__main__":
    main()
