#!/usr/bin/env python3
"""Sweep folded-cascode MOS W/L through SSH and Spectre."""

from __future__ import annotations

import argparse
import csv
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

from psfascii_metrics import calculate


def run(command: list[str], *, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
    )


def render_netlist(template: str, point: dict[str, str], parameter_keys: list[str]) -> str:
    rendered = template
    for key in parameter_keys:
        if key not in point:
            raise ValueError(f"{point.get('name', '<unnamed>')}: missing {key}")
        rendered, count = re.subn(
            rf"(?<![A-Za-z0-9_]){re.escape(key)}=[^\s]+",
            f"{key}={point[key]}",
            rendered,
            count=1,
        )
        if count != 1:
            raise ValueError(f"template parameter not found exactly once: {key}")
    return rendered


def main() -> int:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="192.168.44.128")
    parser.add_argument("--user", default="userone")
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--template", type=Path, default=base / "fc_ota_template.scs")
    parser.add_argument("--config", type=Path, default=base / "size_sweep.json")
    parser.add_argument("--output", type=Path, default=base / "sweep_results.csv")
    parser.add_argument("--work", type=Path, default=base / "runs")
    parser.add_argument("--remote-root", default="/home/userone/codex_sweeps")
    parser.add_argument("--spectre", default="/opt/eda/cadence/SPECTRE251/bin/spectre")
    parser.add_argument("--signal", default="out")
    parser.add_argument("--negative-signal")
    args = parser.parse_args()

    key = args.key.resolve()
    template = args.template.read_text(encoding="utf-8")
    points = json.loads(args.config.read_text(encoding="utf-8"))
    parameter_keys = [key for key in points[0] if key != "name"]
    args.work.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    destination = f"{args.user}@{args.host}"
    ssh_options = [
        "-i", str(key), "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes",
        "-o", "StrictHostKeyChecking=accept-new",
    ]
    rows: list[dict[str, object]] = []

    for point in points:
        name = re.sub(r"[^A-Za-z0-9_.-]+", "_", point["name"])
        local_dir = args.work / name
        local_dir.mkdir(parents=True, exist_ok=True)
        netlist = local_dir / "fc_ota.scs"
        netlist.write_text(
            render_netlist(template, point, parameter_keys),
            encoding="utf-8",
            newline="\n",
        )
        remote_dir = f"{args.remote_root}/{name}"
        row: dict[str, object] = {
            "name": name,
            **{key: point[key] for key in parameter_keys},
        }
        print(f"[{name}] running", flush=True)

        mkdir = run(["ssh", *ssh_options, destination, f"mkdir -p -- {shlex.quote(remote_dir)}"])
        if mkdir.returncode != 0:
            row.update(status="ssh_error", error=mkdir.stderr.strip())
            rows.append(row)
            continue
        upload = run(["scp", *ssh_options, str(netlist), f"{destination}:{remote_dir}/fc_ota.scs"])
        if upload.returncode != 0:
            row.update(status="upload_error", error=upload.stderr.strip())
            rows.append(row)
            continue

        remote_command = (
            f"cd {shlex.quote(remote_dir)} && "
            f"{shlex.quote(args.spectre)} -64 +escchars -format psfascii "
            "-raw fc_ota.raw fc_ota.scs"
        )
        simulation = run(["ssh", *ssh_options, destination, remote_command])
        (local_dir / "spectre.stdout.log").write_text(simulation.stdout, encoding="utf-8")
        (local_dir / "spectre.stderr.log").write_text(simulation.stderr, encoding="utf-8")
        if simulation.returncode != 0:
            row.update(status="spectre_error", error=simulation.stderr.strip()[-1000:])
            rows.append(row)
            continue

        ac_path = local_dir / "ac.ac"
        dc_path = local_dir / "dcOp.dc"
        for remote_name, local_path in (("ac.ac", ac_path), ("dcOp.dc", dc_path)):
            fetch = run([
                "scp", *ssh_options,
                f"{destination}:{remote_dir}/fc_ota.raw/{remote_name}", str(local_path),
            ])
            if fetch.returncode != 0:
                row.update(status="fetch_error", error=fetch.stderr.strip())
                break
        else:
            row.update(
                status="ok",
                error="",
                **calculate(ac_path, dc_path, args.signal, args.negative_signal),
            )
        rows.append(row)
        print(f"[{name}] {row['status']} gain={row.get('gain_db')} ugf={row.get('ugf_hz')}", flush=True)

    metric_keys = [
        "gain_db", "ugf_hz", "phase_at_ugf_deg", "phase_margin_deg",
        "out_dc_v", "supply_current_a",
    ]
    fieldnames = ["name", *parameter_keys, "status", *metric_keys, "error"]
    with args.output.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    json_path = args.output.with_suffix(".json")
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {args.output} and {json_path}")
    return 0 if all(row.get("status") == "ok" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
