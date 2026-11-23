#!/usr/bin/env python3
"""Extract OTA AC/DC metrics from Spectre PSFASCII files."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


FREQ_RE = re.compile(r'^"freq"\s+([-+0-9.eE]+)$')
COMPLEX_RE = re.compile(
    r'^"(?P<name>[^"]+)"\s+\((?P<real>[-+0-9.eE]+)\s+(?P<imag>[-+0-9.eE]+)\)$'
)
DC_RE = re.compile(
    r'^"(?P<name>[^"]+)"\s+"(?P<kind>[^"]+)"\s+(?P<value>[-+0-9.eE]+)$'
)


def parse_ac(path: Path, signal: str) -> tuple[list[float], list[complex]]:
    frequencies: list[float] = []
    values: list[complex] = []
    current_frequency: float | None = None
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        freq_match = FREQ_RE.match(line)
        if freq_match:
            current_frequency = float(freq_match.group(1))
            continue
        value_match = COMPLEX_RE.match(line)
        if value_match and value_match.group("name") == signal and current_frequency is not None:
            frequencies.append(current_frequency)
            values.append(complex(float(value_match.group("real")), float(value_match.group("imag"))))
            current_frequency = None
    if not frequencies:
        raise ValueError(f"signal {signal!r} not found in {path}")
    return frequencies, values


def parse_dc(path: Path) -> dict[str, float]:
    result: dict[str, float] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = DC_RE.match(raw_line.strip())
        if match:
            result[match.group("name")] = float(match.group("value"))
    return result


def unwrap_degrees(values: list[complex]) -> list[float]:
    unwrapped: list[float] = []
    for value in values:
        phase = math.degrees(math.atan2(value.imag, value.real))
        if unwrapped:
            while phase - unwrapped[-1] > 180.0:
                phase -= 360.0
            while phase - unwrapped[-1] < -180.0:
                phase += 360.0
        unwrapped.append(phase)
    return unwrapped


def interpolate_crossing(
    frequencies: list[float], magnitudes_db: list[float], phases_deg: list[float]
) -> tuple[float | None, float | None]:
    for index in range(1, len(frequencies)):
        before = magnitudes_db[index - 1]
        after = magnitudes_db[index]
        if before >= 0.0 and after < 0.0:
            fraction = before / (before - after)
            log_frequency = math.log10(frequencies[index - 1]) + fraction * (
                math.log10(frequencies[index]) - math.log10(frequencies[index - 1])
            )
            phase = phases_deg[index - 1] + fraction * (
                phases_deg[index] - phases_deg[index - 1]
            )
            return 10.0**log_frequency, phase
    return None, None


def calculate(
    ac_path: Path,
    dc_path: Path,
    signal: str,
    negative_signal: str | None = None,
) -> dict[str, float | None]:
    frequencies, values = parse_ac(ac_path, signal)
    if negative_signal:
        negative_frequencies, negative_values = parse_ac(ac_path, negative_signal)
        if negative_frequencies != frequencies:
            raise ValueError("positive and negative signal sweeps do not match")
        values = [positive - negative for positive, negative in zip(values, negative_values)]
    magnitudes_db = [20.0 * math.log10(max(abs(value), 1e-300)) for value in values]
    phases_deg = unwrap_degrees(values)
    unity_frequency, unity_phase = interpolate_crossing(frequencies, magnitudes_db, phases_deg)
    dc_values = parse_dc(dc_path)
    supply_current = -dc_values.get("VDD:p", float("nan"))
    return {
        "gain_db": magnitudes_db[0],
        "ugf_hz": unity_frequency,
        "phase_at_ugf_deg": unity_phase,
        "phase_margin_deg": None if unity_phase is None else 180.0 + unity_phase,
        "out_dc_v": dc_values.get("out"),
        "supply_current_a": supply_current,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ac", type=Path)
    parser.add_argument("dc", type=Path)
    parser.add_argument("--signal", default="out")
    parser.add_argument("--negative-signal")
    args = parser.parse_args()
    print(json.dumps(calculate(args.ac, args.dc, args.signal, args.negative_signal), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
