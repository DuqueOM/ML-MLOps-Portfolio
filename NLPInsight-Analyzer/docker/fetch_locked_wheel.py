#!/usr/bin/env python3
"""Download the exact wheel uv.lock pins for a package, with curl, hash-verified.

Why this exists
---------------
pip/urllib3 has been observed to fail the TLS handshake against
download.pytorch.org's CDN edge from GitHub-hosted runners while curl, against
the same URL, succeeds (see the Dockerfile). uv uses a different TLS stack and
is tried first; this is the fallback when it fails too.

The previous fallback scraped the index for the newest wheel matching the
interpreter tag — a version nobody had locked. This one reads the URL and the
sha256 from uv.lock, so the fallback installs the same file the lock names, or
nothing.

Usage: fetch_locked_wheel.py <uv.lock> <package> <dest-dir>   (prints the path)
"""

from __future__ import annotations

import hashlib
import platform
import subprocess
import sys
import tomllib
from pathlib import Path


def main() -> int:
    lock_path, package, dest = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    lock = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    entries = [p for p in lock.get("package", []) if p.get("name") == package]
    if not entries:
        sys.exit(f"{package} is not in {lock_path}")

    py_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
    arch = platform.machine()  # x86_64 / aarch64
    candidates = [
        w
        for entry in entries
        for w in entry.get("wheels", [])
        if f"-{py_tag}-{py_tag}-" in w["url"] and arch in w["url"] and "linux" in w["url"]
    ]
    if len(candidates) != 1:
        sys.exit(f"expected one locked {package} wheel for {py_tag}/{arch}, found {len(candidates)}")

    wheel = candidates[0]
    expected = wheel["hash"].removeprefix("sha256:")
    target = dest / wheel["url"].rsplit("/", 1)[-1].split("#", 1)[0]
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["curl", "-fsSL", "--retry", "3", "--retry-delay", "3", "-o", str(target), wheel["url"]],
        check=True,
    )
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    if actual != expected:
        target.unlink()
        sys.exit(f"sha256 mismatch for {target.name}: lock {expected}, downloaded {actual}")
    print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
