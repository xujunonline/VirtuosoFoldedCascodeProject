#!/usr/bin/env python3
"""Verify the project SHA-256 manifest, excluding local secrets."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    manifest = project_root / "MANIFEST.sha256"
    failures: list[str] = []
    entries = 0

    for raw_line in manifest.read_text(encoding="utf-8-sig").splitlines():
        if not raw_line.strip():
            continue
        expected, relative = raw_line.split("  ", 1)
        path = project_root / Path(relative)
        entries += 1
        if not path.is_file():
            failures.append(f"missing: {relative}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            failures.append(f"hash mismatch: {relative}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Manifest verified: {entries} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

