#!/usr/bin/env python3
"""Verify SSH and discover Cadence executables in the RedHat guest."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="192.168.44.128")
    parser.add_argument("--user", required=True)
    parser.add_argument("--key", type=Path, required=True)
    args = parser.parse_args()

    probe = r'''printf 'user=%s\n' "$(id -un)"
printf 'host=%s\n' "$(hostname -f 2>/dev/null || hostname)"
for tool in ocean spectre virtuoso; do
  found="$(command -v "$tool" 2>/dev/null || true)"
  printf '%s=%s\n' "$tool" "$found"
done'''
    command = [
        "ssh", "-i", str(args.key.resolve()),
        "-o", "BatchMode=yes",
        "-o", "IdentitiesOnly=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        f"{args.user}@{args.host}", f"bash -lc {shlex.quote(probe)}",
    ]
    completed = subprocess.run(
        command,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    print(json.dumps({
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }, ensure_ascii=False, indent=2))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
