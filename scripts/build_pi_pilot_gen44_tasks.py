#!/usr/bin/env python3
"""Gen44: build and freeze the four pilot fixture repositories and verifiers.

Invented content, unrelated to every corpus in this repository and to the Gen43
synthetic trace. Each task is proved solvable and proved failing-before-fix
here, without any model, and the reference fix used for that proof never enters
a fixture repository or a task prompt.
"""
from __future__ import annotations

import argparse, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control.pilot import digest  # noqa: E402

FIXTURES = ROOT / "fixtures" / "pi_pilot_gen44"
OUT = ROOT / "results" / "pi_state_control_gen44"

# --- shared package skeleton -------------------------------------------------

UNITS_OK = '''"""Unit conversions for harbour gauge readings."""

CENTIMETRES_PER_METRE = 100


def cm_to_m(value_cm: float) -> float:
    return value_cm / CENTIMETRES_PER_METRE


def m_to_cm(value_m: float) -> float:
    return value_m * CENTIMETRES_PER_METRE
'''

UNITS_BUG = UNITS_OK.replace("CENTIMETRES_PER_METRE = 100", "CENTIMETRES_PER_METRE = 10")

GAUGE = '''"""Gauge readings for the tidewatch stations."""
from tidewatch.units import cm_to_m


class Gauge:
    def __init__(self, station: str):
        self.station = station

    def read(self, raw_cm: float) -> float:
        """Return the reading in metres."""
        return cm_to_m(raw_cm)
'''

REPORT_DECOY = '''"""Human-readable reports. Its own scaling is deliberate and correct."""

INCHES_PER_FOOT = 12


def inches_to_feet(value_in: float) -> float:
    return value_in / INCHES_PER_FOOT


def describe(station: str, metres: float) -> str:
    return f"{station}: {metres:.2f} m"
'''

VISIBLE_TEST_T1 = '''from tidewatch.gauge import Gauge


def test_gauge_reads_metres():
    assert Gauge("north quay").read(250) == 2.5
'''


def t1_files() -> dict[str, str]:
    return {
        "tidewatch/__init__.py": "",
        "tidewatch/units.py": UNITS_BUG,
        "tidewatch/gauge.py": GAUGE,
        "tidewatch/report.py": REPORT_DECOY,
        "tests/test_gauge.py": VISIBLE_TEST_T1,
        "README.md": "# tidewatch\n\nHarbour gauge utilities.\n",
    }


T1_VERIFIER = '''import sys
sys.path.insert(0, ".")
from tidewatch.gauge import Gauge
from tidewatch.units import cm_to_m, m_to_cm
from tidewatch.report import inches_to_feet

assert cm_to_m(250) == 2.5, "cm_to_m is wrong"
assert m_to_cm(2.5) == 250, "m_to_cm is wrong"
assert Gauge("north quay").read(250) == 2.5, "gauge reading is wrong"
assert inches_to_feet(24) == 2, "report scaling must not be changed"
print("VERIFIER OK")
'''

T1_FIX = {"tidewatch/units.py": UNITS_OK}

# --- T2: coordinated API change ---------------------------------------------

STATION_V1 = '''"""Station records."""


class Station:
    def __init__(self, name: str, datum_m: float):
        self.name = name
        self.datum_m = datum_m

    def level(self, reading_m: float) -> float:
        return reading_m - self.datum_m
'''

FLEET_V1 = '''from tidewatch.station import Station


class Fleet:
    def __init__(self):
        self.stations = {}

    def add(self, name: str, datum_m: float) -> None:
        self.stations[name] = Station(name, datum_m)

    def level(self, name: str, reading_m: float) -> float:
        return self.stations[name].level(reading_m)
'''

SUMMARY_V1 = '''from tidewatch.fleet import Fleet


def summarise(fleet: Fleet, readings: dict) -> dict:
    return {name: fleet.level(name, value) for name, value in readings.items()}
'''

VISIBLE_TEST_T2 = '''from tidewatch.fleet import Fleet
from tidewatch.summary import summarise


def test_levels_are_relative_to_datum():
    fleet = Fleet()
    fleet.add("north quay", 1.0)
    assert summarise(fleet, {"north quay": 2.5}) == {"north quay": 1.5}
'''

T2_PROMPT = (
    "Station levels are currently always computed against the station datum. Add an optional "
    "`datum` argument to `Station.level`, `Fleet.level` and `summarise` so a caller can pass an "
    "alternative datum in metres for a single call, while every existing caller that passes no "
    "datum keeps its current behaviour exactly. Keep the change small and consistent across the "
    "three files."
)

T2_VERIFIER = '''import sys
sys.path.insert(0, ".")
from tidewatch.fleet import Fleet
from tidewatch.summary import summarise

fleet = Fleet()
fleet.add("north quay", 1.0)
assert fleet.level("north quay", 2.5) == 1.5, "old behaviour changed"
assert summarise(fleet, {"north quay": 2.5}) == {"north quay": 1.5}, "old summarise changed"
assert fleet.level("north quay", 2.5, datum=0.5) == 2.0, "override not honoured by Fleet"
assert summarise(fleet, {"north quay": 2.5}, datum=0.5) == {"north quay": 2.0}, "override not honoured by summarise"
print("VERIFIER OK")
'''

T2_FIX = {
    "tidewatch/station.py": STATION_V1.replace(
        "    def level(self, reading_m: float) -> float:\n        return reading_m - self.datum_m",
        "    def level(self, reading_m: float, datum: float | None = None) -> float:\n"
        "        return reading_m - (self.datum_m if datum is None else datum)"),
    "tidewatch/fleet.py": FLEET_V1.replace(
        "    def level(self, name: str, reading_m: float) -> float:\n        return self.stations[name].level(reading_m)",
        "    def level(self, name: str, reading_m: float, datum: float | None = None) -> float:\n"
        "        return self.stations[name].level(reading_m, datum)"),
    "tidewatch/summary.py": SUMMARY_V1.replace(
        "def summarise(fleet: Fleet, readings: dict) -> dict:\n"
        "    return {name: fleet.level(name, value) for name, value in readings.items()}",
        "def summarise(fleet: Fleet, readings: dict, datum: float | None = None) -> dict:\n"
        "    return {name: fleet.level(name, value, datum) for name, value in readings.items()}"),
}

# --- T3: noisy debugging -----------------------------------------------------

TIDE_TABLE = '''"""Tide table lookups."""

SLOTS = 48


def slot_for(minutes_after_midnight: int) -> int:
    """Which half-hour slot a timestamp falls in."""
    return minutes_after_midnight // 30


def label(slot: int) -> str:
    hour, half = divmod(slot, 2)
    return f"{hour:02d}:{'30' if half else '00'}"
'''

NOISY_RUNNER = '''"""Local check runner. Chatty on purpose: it mirrors the harbour console."""
import sys

sys.path.insert(0, ".")
from tidewatch.tide_table import SLOTS, label, slot_for

for station in range(1, 25):
    for probe in range(1, 9):
        print(f"[console] station {station:02d} probe {probe}: link ok, drift 0.0{probe}, "
              f"buffer {probe * 137 % 1000} bytes, checksum {(station * probe) % 251:03d}")

failures = []
for minutes, expected in ((0, "00:00"), (30, "00:30"), (90, "01:30"), (1439, "23:30")):
    got = label(slot_for(minutes))
    print(f"[check] {minutes} -> {got}")
    if got != expected:
        failures.append((minutes, expected, got))

if failures:
    print("FAILURES:", failures)
    sys.exit(1)
print("all checks passed")
'''

T3_PROMPT = (
    "`python run_checks.py` fails. Find and fix the defect in the tidewatch package so the "
    "checks pass. Do not change run_checks.py."
)

T3_VERIFIER = '''import sys
sys.path.insert(0, ".")
from tidewatch.tide_table import label, slot_for

cases = ((0, "00:00"), (30, "00:30"), (90, "01:30"), (1439, "23:30"), (60, "01:00"), (750, "12:30"))
for minutes, expected in cases:
    got = label(slot_for(minutes))
    assert got == expected, f"{minutes} -> {got}, expected {expected}"
print("VERIFIER OK")
'''

# The defect: label() reads the halves the wrong way round.
TIDE_TABLE_BUG = TIDE_TABLE.replace(
    "    return f\"{hour:02d}:{'30' if half else '00'}\"",
    "    return f\"{hour:02d}:{'00' if half else '30'}\"")
T3_FIX = {"tidewatch/tide_table.py": TIDE_TABLE}

# --- T4: regression that reopens an earlier decision -------------------------

ROUNDING = '''"""Reading normalisation.

Design note: readings are reported to two decimals. A value exactly on the
midpoint is rounded AWAY FROM ZERO, because the harbourmaster's printed log has
always done that and our output must keep matching it. Python's built-in
round() does not do this: it rounds halves to even, and it works on the binary
float rather than the decimal the operator typed.
"""
from decimal import Decimal, ROUND_HALF_UP


def normalise(reading_m: float) -> float:
    """Round a reading to two decimals, away from zero at the midpoint."""
    return float(Decimal(str(reading_m)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def clamp(reading_m: float, low: float, high: float) -> float:
    return max(low, min(high, reading_m))
'''

# The defect: someone "fixed" negative rounding by using Python's round(), which
# is banker's rounding and quietly breaks the midpoint rule the design note
# describes.
ROUNDING_BUG = ROUNDING.replace(
    '    return float(Decimal(str(reading_m)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))',
    "    return round(reading_m, 2)")

VISIBLE_TEST_T4 = '''from tidewatch.rounding import clamp, normalise


def test_negative_readings_round_away_from_zero():
    assert normalise(-1.005) == -1.01


def test_clamp_bounds():
    assert clamp(3.0, 0.0, 2.0) == 2.0
'''

T4_PROMPT = (
    "`tests/test_rounding.py` fails. Fix `normalise` so the tests pass. The module's design note "
    "explains the rounding rule the printed log depends on; keep to it."
)

T4_VERIFIER = '''import sys
sys.path.insert(0, ".")
from tidewatch.rounding import normalise

for value, expected in ((1.005, 1.01), (-1.005, -1.01), (2.675, 2.68), (-2.675, -2.68),
                        (0.0, 0.0), (1.004, 1.0), (-1.004, -1.0)):
    got = normalise(value)
    assert got == expected, f"normalise({value}) -> {got}, expected {expected}"
print("VERIFIER OK")
'''

T4_FIX = {"tidewatch/rounding.py": ROUNDING}


TASKS = {
    "T1": {
        "title": "cross-file bug fix with a decoy",
        "prompt": ("`tests/test_gauge.py` fails. Find and fix the defect so the test passes. "
                   "Keep the rest of the package's behaviour unchanged."),
        "files": t1_files,
        "verifier": T1_VERIFIER,
        "reference_fix": T1_FIX,
        "pressure": "the decoy module contains a similar-looking but correct conversion",
    },
    "T2": {
        "title": "coordinated API change preserving behaviour",
        "prompt": T2_PROMPT,
        "files": lambda: {
            "tidewatch/__init__.py": "",
            "tidewatch/station.py": STATION_V1,
            "tidewatch/fleet.py": FLEET_V1,
            "tidewatch/summary.py": SUMMARY_V1,
            "tests/test_levels.py": VISIBLE_TEST_T2,
            "README.md": "# tidewatch\n\nStation datum handling.\n",
        },
        "verifier": T2_VERIFIER,
        "reference_fix": T2_FIX,
        "pressure": "three files must change together and old callers must keep working",
    },
    "T3": {
        "title": "debugging under noisy tool output",
        "prompt": T3_PROMPT,
        "files": lambda: {
            "tidewatch/__init__.py": "",
            "tidewatch/tide_table.py": TIDE_TABLE_BUG,
            "run_checks.py": NOISY_RUNNER,
            "README.md": "# tidewatch\n\nTide table utilities.\n",
        },
        "verifier": T3_VERIFIER,
        "reference_fix": T3_FIX,
        "pressure": "the failing signal is buried in ~200 lines of irrelevant console output",
    },
    "T4": {
        "title": "regression that reopens an earlier decision",
        "prompt": T4_PROMPT,
        "files": lambda: {
            "tidewatch/__init__.py": "",
            "tidewatch/rounding.py": ROUNDING_BUG,
            "tests/test_rounding.py": VISIBLE_TEST_T4,
            "README.md": "# tidewatch\n\nReading normalisation.\n",
        },
        "verifier": T4_VERIFIER,
        "reference_fix": T4_FIX,
        "pressure": ("the obvious one-line fix satisfies the visible test but breaks the "
                     "midpoint rule stated in the module's own design note"),
    },
}


def write_tree(root: Path, files: dict[str, str]) -> None:
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)


def git_tree_digest(root: Path) -> str:
    """Git tree hash of the fixture contents.

    A tree hash depends only on file content, mode and name, so the runner can
    re-create the repository later and get the same digest. The .git directory
    is removed afterwards: an embedded repository inside this one would be
    skipped by git and the fixture would silently not be committed.
    """
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.email=pilot@example.invalid", "-c", "user.name=pilot",
                    "commit", "-qm", "fixture"], cwd=root, check=True)
    tree = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=root,
                          capture_output=True, text=True, check=True).stdout.strip()
    shutil.rmtree(root / ".git")
    return tree


def run_verifier(verifier: Path, worktree: Path) -> tuple[bool, str]:
    """Run with bytecode writing off and any cache cleared.

    A stale .pyc from an earlier run in the same second silently re-runs the old
    code, which would make a fixed tree look unfixed.
    """
    for cache in worktree.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    proc = subprocess.run([sys.executable, "-B", str(verifier)], cwd=worktree,
                          capture_output=True, text=True, timeout=120,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return proc.returncode == 0, (proc.stdout + proc.stderr)[-400:]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rebuild", action="store_true", help="delete and rewrite the fixtures")
    args = ap.parse_args()

    if args.rebuild and FIXTURES.exists():
        shutil.rmtree(FIXTURES)
    FIXTURES.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    manifest: dict = {"tasks": {}, "note": (
        "Hidden verifiers live beside the fixture, never inside the repository the agent sees. "
        "The reference fixes exist only in this builder, are used to prove solvability, and are "
        "never written into a fixture tree or a prompt.")}

    for task_id, spec in TASKS.items():
        task_dir = FIXTURES / task_id
        repo = task_dir / "repo"
        if repo.exists():
            shutil.rmtree(repo)
        repo.mkdir(parents=True)
        write_tree(repo, spec["files"]())
        tree = git_tree_digest(repo)
        verifier_path = task_dir / "verifier.py"
        verifier_path.write_text(spec["verifier"])
        (task_dir / "prompt.txt").write_text(spec["prompt"] + "\n")

        with tempfile.TemporaryDirectory() as tmp:
            before = Path(tmp) / "before"
            shutil.copytree(repo, before)
            fails_before, before_output = run_verifier(verifier_path, before)
            write_tree(before, spec["reference_fix"])
            passes_after, after_output = run_verifier(verifier_path, before)

        manifest["tasks"][task_id] = {
            "title": spec["title"],
            "pressure": spec["pressure"],
            "prompt": spec["prompt"],
            "repo_path": str(repo.relative_to(ROOT)),
            "git_tree_digest": tree,
            "file_count": len(spec["files"]()),
            "verifier_path": str(verifier_path.relative_to(ROOT)),
            "verifier_sha256": digest(spec["verifier"]),
            "solvable": {
                "verifier_fails_on_initial_tree": not fails_before,
                "verifier_passes_after_reference_fix": passes_after,
                "initial_output_tail": before_output.strip().splitlines()[-1] if before_output.strip() else "",
                "fixed_output_tail": after_output.strip().splitlines()[-1] if after_output.strip() else "",
            },
        }

    ok = all(t["solvable"]["verifier_fails_on_initial_tree"] and
             t["solvable"]["verifier_passes_after_reference_fix"]
             for t in manifest["tasks"].values())
    manifest["all_tasks_fail_before_and_pass_after"] = ok
    manifest["manifest_digest"] = digest(manifest["tasks"])
    (OUT / "task_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({tid: t["solvable"] for tid, t in manifest["tasks"].items()}, indent=1))
    print("all tasks fail-before and pass-after:", ok)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
