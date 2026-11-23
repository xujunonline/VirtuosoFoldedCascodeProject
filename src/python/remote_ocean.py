#!/usr/bin/env python3
"""Run an OCEAN/SKILL file inside the Virtuoso VM over SSH.

The private key is intentionally kept outside this deliverable directory.
No third-party Python packages are required.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=check,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="192.168.44.128")
    parser.add_argument("--user", required=True)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--ocean", default="ocean", help="Remote ocean executable or wrapper")
    parser.add_argument("--display", default=":1", help="Remote X display used by Cadence")
    parser.add_argument(
        "--xauthority",
        default="/run/user/1000/gdm/Xauthority",
        help="Remote Xauthority file",
    )
    parser.add_argument(
        "--nograph",
        action="store_true",
        help="Use Cadence -nograph mode (requires Xvfb in this VM)",
    )
    parser.add_argument(
        "--remote-dir",
        help="Absolute remote working directory (default: /home/USER/codex_ocean)",
    )
    parser.add_argument("script", type=Path, help="Local .ocn/.il file")
    args = parser.parse_args()

    script = args.script.resolve()
    key = args.key.resolve()
    if not script.is_file():
        parser.error(f"script not found: {script}")
    if not key.is_file():
        parser.error(f"private key not found: {key}")

    destination = f"{args.user}@{args.host}"
    remote_dir = args.remote_dir or f"/home/{args.user}/codex_ocean"
    ssh_base = [
        "ssh",
        "-i",
        str(key),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]
    remote_name = script.name
    remote_file = f"{remote_dir}/{remote_name}"

    run([*ssh_base, destination, f"mkdir -p -- {shlex.quote(remote_dir)}"])
    run([
        "scp",
        "-i",
        str(key),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        str(script),
        f"{destination}:{remote_file}",
    ])

    ocean_command = [
        "env",
        f"DISPLAY={args.display}",
        f"XAUTHORITY={args.xauthority}",
        args.ocean,
    ]
    if args.nograph:
        ocean_command.append("-nograph")
    ocean_command.extend([
        "-restore",
        remote_name,
        "-log",
        f"{remote_dir}/ocean_{script.stem}.log",
    ])
    remote_command = (
        f"cd {shlex.quote(remote_dir)} && "
        + " ".join(shlex.quote(part) for part in ocean_command)
    )
    completed = run(
        [*ssh_base, destination, f"bash -lc {shlex.quote(remote_command)}"],
        check=False,
    )
    if completed.stdout:
        sys.stdout.write(completed.stdout)
    if completed.stderr:
        sys.stderr.write(completed.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
