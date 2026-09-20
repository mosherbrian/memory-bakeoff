#!/usr/bin/env python3
"""Gate for QUEUE row S10-3 (evaluator integrity: a fail-closed pre-sweep
canary, and the exit-contract driver extended to the sprint gates).

plumb-fable, row S10-3G, 2026-09-18. Written FROM ROW S10-3's TEXT ALONE, while
`team/S9-EVAL-CANARY/` did not exist. Read for this gate: the board row and
team/tools/check_checker_exit_contracts.py, the driver the row extends. The
interface below is declared by the gate, not fitted to a document; every
finding names what it wants.

The row repairs two gaps, and a repair of this kind is only worth what it does
when things go wrong. So this gate does not read the two tools, it DRIVES them
on throwaway trees it builds itself: guards that fail, crash, vanish and hang;
gates that are blind, silent, crashing or unlisted. "Fail-closed" is tested by
failing.

Declared interface (ROOT = team/S9-EVAL-CANARY, TEAM = team)
  canary.py           python3 canary.py --team TEAM --manifest FILE
                      [--timeout SECONDS] [-- COMMAND ...]
                      Runs every guard in the manifest. Exit 0, and COMMAND
                      run, only when every guard passed. Names each failure.
  guards.json         [{script (relative to TEAM), argv: [...]}] - every
                      team/tools/check_*.py
  gate_contracts.py   python3 gate_contracts.py --team TEAM --covered FILE
                      For each covered gate: `--selftest` exits 0, and a run
                      on a target that does not exist exits 1 with a [MARKER]
                      and no traceback. A live gate outside the covered set,
                      or a covered gate that is gone, fails the sweep. Names
                      each failure. Exit 0 only when all hold.
  covered_gates.json  [paths relative to TEAM] - every sprint gate: S*/check.py,
                      S*-check.py, D-*/check.py
  manifest.json       {sweep_entrypoints: [files, relative to the repository,
                      that launch an expensive run and call canary.py first],
                      prior (names INTEL/SYNTHESIS-2026-09-18.md),
                      advances (says: neither)}

What the row turns on (marker in brackets)
  (a) FAIL-CLOSED. With the wrapped command watched by a sentinel file:
      all guards pass -> exit 0 and the command ran [CANARY-BLOCKS-CLEAN];
      a guard exits 1, exits 3, is missing from disk, or hangs past the
      timeout -> non-zero and the command did NOT run [CANARY-FAILS-OPEN];
      zero guards is not a pass [CANARY-PASSES-ON-NOTHING]; the failing guard
      is named [CANARY-SILENT]; the canary itself does not crash
      [CANARY-BROKEN].
  (b) BEFORE the expensive run. At least one sweep entry point exists and
      calls canary.py [NOT-WIRED].
  (c) The driver reaches the SPRINT GATES. All good -> exit 0
      [DRIVER-BLOCKS-CLEAN]; a gate whose dirty run exits 0, crashes, exits 1
      with no marker, or whose selftest fails -> exit 1 [DRIVER-BLIND]; a live
      gate outside the covered set, or a covered gate that is gone -> exit 1
      [DRIVER-COVERAGE-BLIND]; the offender is named [DRIVER-SILENT]; the
      driver does not crash [DRIVER-BROKEN].
  (d) The real lists are COMPLETE. guards.json holds every live guard
      [GUARD-UNLISTED] and none that is gone [GUARD-GONE]; covered_gates.json
      holds every live sprint gate [GATE-UNCOVERED] and none that is gone
      [COVERED-GATE-GONE].
  (e) Prior cited [PRIOR-NOT-CITED]; advances-neither said plainly
      [ADVANCES-UNSTATED]; no LLM or network [LLM-OR-NETWORK].
  other  [MISSING-FILE] [BAD-JSON] [SCHEMA]

Limits, stated on purpose: by default the gate does NOT run the two tools on
the live tree, because that runs every sprint gate's selftest and this check
is called on every sweep; `--live` does it. "Calls canary.py" is a text match
in the entry point; whether the call sits before the expensive step, and
whether every expensive run is listed, stays with the named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S10-3 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT] [--team DIR] [--repo DIR] [--live]
  python3 check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ("canary.py", "guards.json", "gate_contracts.py", "covered_gates.json",
         "manifest.json")
GATE_GLOBS = ("S*/check.py", "S*-check.py", "D-*/check.py")
PRIOR = "INTEL/SYNTHESIS-2026-09-18.md"
HANG, CANARY_TIMEOUT, PATIENCE = 8, 1, 6  # seconds
NETWORK = re.compile(r"^\s*(import|from)\s+(anthropic|openai|requests|httpx|"
                     r"aiohttp|socket|urllib|http)\b|api_key|/v1/(chat|messages)",
                     re.I | re.M)
TRACEBACK = "Traceback (most recent call last)"

_PASS = "raise SystemExit(0)\n"
_GATE = ('import sys\nif "--selftest" in sys.argv:\n    raise SystemExit({st})\n'
         '{dirty}\n')
_GOOD_GATE = _GATE.format(st=0, dirty='print("[MISSING-FILE] target")\n'
                          'print("gate findings: 1")\nraise SystemExit(1)')
_BAD_GATES = {
    "dirty run exits 0": _GATE.format(st=0, dirty='print("all fine")\n'
                                      'raise SystemExit(0)'),
    "dirty run crashes": _GATE.format(st=0, dirty="raise RuntimeError('boom')"),
    "exit 1 with no marker": _GATE.format(st=0, dirty="raise SystemExit(1)"),
    "selftest fails": _GATE.format(st=1, dirty='print("[MISSING-FILE] target")\n'
                                   'raise SystemExit(1)'),
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def live_gates(team: Path) -> set[str]:
    return {str(p.relative_to(team)) for g in GATE_GLOBS for p in team.glob(g)}


def _run(argv: list, timeout: float) -> tuple[int | None, str]:
    """(exit code, output); exit code None when it ran past `timeout`."""
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return None, ""


def drive_canary(canary: Path) -> list[tuple[str, str]]:
    f: list[tuple[str, str]] = []
    guards = {"pass": _PASS, "exits 1": "print('drift')\nraise SystemExit(1)\n",
              "exits 3": "raise SystemExit(3)\n",
              "hangs": f"import time\ntime.sleep({HANG})\n"}
    cases = [("all guards pass", ["pass"], True, None),
             ("a guard exits 1", ["pass", "exits 1"], False, "check_exits_1.py"),
             ("a guard exits 3", ["pass", "exits 3"], False, "check_exits_3.py"),
             ("a listed guard is missing from disk", ["pass", "GONE"], False,
              "check_GONE.py"),
             ("a guard hangs past the timeout", ["pass", "hangs"], False,
              "check_hangs.py"),
             ("no guards listed", [], False, None)]
    for label, names, clean, culprit in cases:
        with tempfile.TemporaryDirectory() as td:
            team = Path(td)
            (team / "tools").mkdir()
            for n in names:
                if n in guards:
                    (team / "tools" / f"check_{n.replace(' ', '_')}.py"
                     ).write_text(guards[n])
            manifest = team / "guards.json"
            manifest.write_text(json.dumps(
                [{"script": f"tools/check_{n.replace(' ', '_')}.py", "argv": []}
                 for n in names]))
            sentinel = team / "the-expensive-run-started"
            rc, out = _run([sys.executable, str(canary), "--team", str(team),
                            "--manifest", str(manifest), "--timeout",
                            str(CANARY_TIMEOUT), "--", sys.executable, "-c",
                            f"open({str(sentinel)!r}, 'w').close()"], PATIENCE)
            ran = sentinel.exists()
        if TRACEBACK in out:
            f.append(("CANARY-BROKEN", f"{label}: canary.py crashed"))
        elif clean and (rc != 0 or not ran):
            f.append(("CANARY-BLOCKS-CLEAN", f"{label}: exit {rc}, command ran: "
                      f"{ran}; must be exit 0 and the command run"))
        elif not clean and (rc == 0 or rc is None or ran):
            f.append(("CANARY-PASSES-ON-NOTHING" if not names else
                      "CANARY-FAILS-OPEN", f"{label}: exit "
                      f"{'none within ' + str(PATIENCE) + ' s' if rc is None else rc}"
                      f", command ran: {ran}; must be non-zero and the command "
                      f"NOT run"))
        elif culprit and culprit not in out:
            f.append(("CANARY-SILENT", f"{label}: the output does not name "
                      f"{culprit}"))
    return f


def drive_driver(driver: Path) -> list[tuple[str, str]]:
    f: list[tuple[str, str]] = []
    good = {"S1-ALPHA/check.py": _GOOD_GATE, "S2-BETA-check.py": _GOOD_GATE}
    cases = [("every gate honours the contract", good, list(good), True, None,
              "DRIVER-BLOCKS-CLEAN")]
    for label, src in _BAD_GATES.items():
        gates = dict(good, **{"S3-BAD/check.py": src})
        cases.append((f"a gate whose {label}", gates, list(gates), False,
                      "S3-BAD/check.py", "DRIVER-BLIND"))
    cases.append(("a live gate outside the covered set",
                  dict(good, **{"D-9-NEW/check.py": _GOOD_GATE}), list(good),
                  False, "D-9-NEW/check.py", "DRIVER-COVERAGE-BLIND"))
    cases.append(("a covered gate that is gone", good,
                  list(good) + ["S4-GONE/check.py"], False, "S4-GONE/check.py",
                  "DRIVER-COVERAGE-BLIND"))
    for label, gates, covered, clean, culprit, marker in cases:
        with tempfile.TemporaryDirectory() as td:
            team = Path(td)
            for rel, src in gates.items():
                (team / rel).parent.mkdir(parents=True, exist_ok=True)
                (team / rel).write_text(src)
            listing = team / "covered_gates.json"
            listing.write_text(json.dumps(covered))
            rc, out = _run([sys.executable, str(driver), "--team", str(team),
                            "--covered", str(listing)], 60)
        if TRACEBACK in out or rc is None:
            f.append(("DRIVER-BROKEN", f"{label}: gate_contracts.py crashed or "
                      f"did not finish"))
        elif clean and rc != 0:
            f.append((marker, f"{label}: exit {rc}, must be 0"))
        elif not clean and rc == 0:
            f.append((marker, f"{label}: exit 0, must be 1. The sweep read a "
                      f"broken gate as clean"))
        elif culprit and culprit not in out:
            f.append(("DRIVER-SILENT", f"{label}: the output does not name "
                      f"{culprit}"))
    return f


def check(root: Path, team: Path, repo: Path, live: bool) -> tuple[list, str]:
    missing = [n for n in FILES if not (root / n).is_file()]
    if missing:
        return [("MISSING-FILE", f"{root}/{n}") for n in missing], ""
    try:
        guards = _load(root / "guards.json")
        covered = _load(root / "covered_gates.json")
        manifest = _load(root / "manifest.json")
    except ValueError as e:
        return [("BAD-JSON", str(e))], ""
    f: list[tuple[str, str]] = []
    if not (isinstance(guards, list) and all(
            isinstance(g, dict) and isinstance(g.get("script"), str)
            and isinstance(g.get("argv", []), list) for g in guards)):
        f.append(("SCHEMA", "guards.json needs [{script, argv: [...]}]"))
    if not (isinstance(covered, list) and all(isinstance(c, str) for c in covered)):
        f.append(("SCHEMA", "covered_gates.json needs [paths relative to team/]"))
    if not (isinstance(manifest, dict)
            and isinstance(manifest.get("sweep_entrypoints"), list)
            and all(isinstance(e, str) for e in manifest["sweep_entrypoints"])):
        f.append(("SCHEMA", "manifest.json needs sweep_entrypoints: [files], "
                  "prior, advances"))
    if f:
        return f, ""

    # (d) the real lists are complete
    live_guards = {f"tools/{p.name}" for p in (team / "tools").glob("check_*.py")}
    listed = {g["script"] for g in guards}
    for marker, names, why in (
            ("GUARD-UNLISTED", live_guards - listed, "live guards not in "
             "guards.json, so the canary never runs them"),
            ("GUARD-GONE", {s for s in listed if not (team / s).is_file()},
             "guards.json lists scripts that do not exist"),
            ("GATE-UNCOVERED", live_gates(team) - set(covered), "live sprint "
             "gates not in covered_gates.json, still exercised ad hoc"),
            ("COVERED-GATE-GONE", {c for c in covered
                                   if not (team / c).is_file()},
             "covered_gates.json lists gates that do not exist")):
        if names:
            f.append((marker, f"{why}: {', '.join(sorted(names)[:6])}"
                      + (f" (+{len(names) - 6} more)" if len(names) > 6 else "")))

    # (b) wired before the expensive run
    entries = manifest["sweep_entrypoints"]
    unwired = [e for e in entries if not (repo / e).is_file() or "canary.py"
               not in (repo / e).read_text(encoding="utf-8", errors="replace")]
    if not entries or unwired:
        f.append(("NOT-WIRED", "manifest.json sweep_entrypoints must name at "
                  "least one existing file that calls canary.py"
                  + (f"; not so: {', '.join(unwired)}" if unwired else "")))

    # (e) prior, advances, local
    if PRIOR not in str(manifest.get("prior", "")):
        f.append(("PRIOR-NOT-CITED", f"manifest.json prior must name {PRIOR}, "
                  f"the first valid record of the gap"))
    if not re.search(r"neither", str(manifest.get("advances", "")), re.I):
        f.append(("ADVANCES-UNSTATED", "manifest.json advances must say it "
                  "advances neither a frozen goal nor a roadmap item"))
    code = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                     for p in sorted(root.glob("*.py")) if p.name != "check.py")
    hit = NETWORK.search(code)
    if hit:
        f.append(("LLM-OR-NETWORK", f"build code reaches for a model or the "
                  f"network ({hit.group(0).strip()!r})"))

    # (a) (c) the two tools, driven on throwaway trees
    f += drive_canary(root / "canary.py")
    f += drive_driver(root / "gate_contracts.py")

    if live and not f:
        for name, argv in (
                ("canary.py", ["--team", str(team), "--manifest",
                               str(root / "guards.json")]),
                ("gate_contracts.py", ["--team", str(team), "--covered",
                                       str(root / "covered_gates.json")])):
            rc, out = _run([sys.executable, str(root / name), *argv], 3600)
            if rc != 0:
                f.append(("LIVE-TREE-FAILS", f"{name} on the live tree: exit "
                          f"{rc} :: {(out.strip().splitlines() or [''])[-1][:120]}"))
    return f, (f"{len(listed)} guards listed, {len(covered)} gates covered, "
               f"{len(entries)} sweep entry point(s) wired; canary driven on 6 "
               f"trees, driver on 7" + ("; live tree clean" if live else ""))


def run(root: Path, team: Path, repo: Path, live: bool) -> int:
    findings, summary = check(root, team, repo, live)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S10-3 gate findings: {len(findings)}")
        return 1
    print(f"S10-3 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_CANARY = '''import argparse, json, subprocess, sys
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument("--team", required=True)
ap.add_argument("--manifest", required=True)
ap.add_argument("--timeout", type=float, default=120)
ap.add_argument("cmd", nargs=argparse.REMAINDER)
a = ap.parse_args()
guards = json.loads(Path(a.manifest).read_text())
bad = [] if guards else ["no guards listed: nothing was checked"]
for g in guards:
    script = Path(a.team) / g["script"]
    if not script.is_file():
        bad.append(f"{g['script']}: missing")
        continue
    try:
        p = subprocess.run([sys.executable, str(script), *g.get("argv", [])],
                           capture_output=True, text=True, timeout=a.timeout)
        if p.returncode != 0:
            bad.append(f"{g['script']}: exit {p.returncode}")
    except subprocess.TimeoutExpired:
        bad.append(f"{g['script']}: timed out")
for b in bad:
    print(f"CANARY FAIL: {b}")
if bad:
    raise SystemExit(1)
cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
raise SystemExit(subprocess.run(cmd).returncode if cmd else 0)
'''
_DRIVER = '''import argparse, json, re, subprocess, sys
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument("--team", required=True)
ap.add_argument("--covered", required=True)
a = ap.parse_args()
team = Path(a.team)
covered = json.loads(Path(a.covered).read_text())
live = {str(p.relative_to(team)) for g in ("S*/check.py", "S*-check.py",
        "D-*/check.py") for p in team.glob(g)}
bad = [f"{g}: NO CONTROL (live gate outside the covered set)"
       for g in sorted(live - set(covered))]
for g in covered:
    if not (team / g).is_file():
        bad.append(f"{g}: covered gate is gone")
        continue
    st = subprocess.run([sys.executable, str(team / g), "--selftest"],
                        capture_output=True, text=True, timeout=900)
    if st.returncode != 0:
        bad.append(f"{g}: selftest exit {st.returncode}")
    d = subprocess.run([sys.executable, str(team / g),
                        str(team / "__absent__" / "target")],
                       capture_output=True, text=True, timeout=900)
    text = d.stdout + d.stderr
    if DIRTY_IS_BAD:
        bad.append(f"{g}: dirty run exit {d.returncode}, contract not honoured")
for b in bad:
    print(f"CONTRACT FAIL: {b}")
print(f"gate contracts: {len(covered) - len({b.split(':')[0] for b in bad})} hold")
raise SystemExit(1 if bad else 0)
'''
_GOOD_DRIVER = _DRIVER.replace(
    "DIRTY_IS_BAD", 'd.returncode != 1 or "Traceback (most recent call last)" '
    'in text or not re.search(r"^\\[[A-Z]", text, re.M)')
_SELFTEST_ONLY = _DRIVER.replace("DIRTY_IS_BAD", "False")
_NO_COVERAGE = _GOOD_DRIVER.replace(
    'bad = [f"{g}: NO CONTROL (live gate outside the covered set)"\n'
    '       for g in sorted(live - set(covered))]', "bad = []").replace(
    '        bad.append(f"{g}: covered gate is gone")\n', "")
_OPEN_CANARY = _CANARY.replace("if bad:\n    raise SystemExit(1)\n", "")
_EMPTY_OK = _CANARY.replace(
    'bad = [] if guards else ["no guards listed: nothing was checked"]',
    "bad = []")
_NO_TIMEOUT = _CANARY.replace("timeout=a.timeout", "timeout=None")
_MUTE = _CANARY.replace('    print(f"CANARY FAIL: {b}")', '    print("CANARY FAIL")')


def _fixture() -> dict:
    return {"canary": _CANARY, "driver": _GOOD_DRIVER,
            "guards": ["tools/check_a.py", "tools/check_b.py"],
            "covered": ["S1-ALPHA/check.py", "S2-BETA-check.py",
                        "S9-EVAL-CANARY/check.py"],
            "entry": "python3 team/S9-EVAL-CANARY/canary.py --team team "
                     "--manifest team/S9-EVAL-CANARY/guards.json -- "
                     "python3 -m memory_bakeoff sweep\n",
            "manifest": {"sweep_entrypoints": ["implementer/run_sweep.sh"],
                         "prior": f"team/{PRIOR}, first valid record",
                         "advances": "neither a frozen goal nor a roadmap item"},
            "extra_py": {}, "raw": {}}


def _write(td: Path, fx: dict) -> tuple[Path, Path, Path]:
    repo, team = td, td / "team"
    root = team / "S9-EVAL-CANARY"
    root.mkdir(parents=True)
    (team / "tools").mkdir()
    for n in ("check_a.py", "check_b.py"):
        (team / "tools" / n).write_text(_PASS)
    (team / "S1-ALPHA").mkdir()
    (team / "S1-ALPHA" / "check.py").write_text(_GOOD_GATE)
    (team / "S2-BETA-check.py").write_text(_GOOD_GATE)
    (root / "check.py").write_text(_GOOD_GATE)  # the gate is itself a live gate
    (repo / "implementer").mkdir()
    (repo / "implementer" / "run_sweep.sh").write_text(fx["entry"])
    (root / "canary.py").write_text(fx["canary"])
    (root / "gate_contracts.py").write_text(fx["driver"])
    (root / "guards.json").write_text(json.dumps(
        [{"script": g, "argv": []} for g in fx["guards"]]))
    (root / "covered_gates.json").write_text(json.dumps(fx["covered"]))
    (root / "manifest.json").write_text(json.dumps(fx["manifest"]))
    for name, text in {**fx["extra_py"], **fx["raw"]}.items():
        if text is None:
            (root / name).unlink()
        else:
            (root / name).write_text(text)
    return root, team, repo


def _m_open(fx): fx["canary"] = _OPEN_CANARY
def _m_empty_ok(fx): fx["canary"] = _EMPTY_OK
def _m_no_timeout(fx): fx["canary"] = _NO_TIMEOUT
def _m_mute(fx): fx["canary"] = _MUTE
def _m_canary_crash(fx): fx["canary"] = "raise RuntimeError('boom')\n"
def _m_selftest_only(fx): fx["driver"] = _SELFTEST_ONLY
def _m_no_coverage(fx): fx["driver"] = _NO_COVERAGE
def _m_driver_crash(fx): fx["driver"] = "raise RuntimeError('boom')\n"
def _m_guard_unlisted(fx): fx["guards"].pop()
def _m_guard_gone(fx): fx["guards"].append("tools/check_retired.py")
def _m_gate_uncovered(fx): fx["covered"].remove("S2-BETA-check.py")
def _m_gate_gone(fx): fx["covered"].append("S7-OLD/check.py")
def _m_unwired(fx): fx["entry"] = "python3 -m memory_bakeoff sweep\n"
def _m_no_entry(fx): fx["manifest"]["sweep_entrypoints"] = []
def _m_entry_absent(fx): fx["manifest"]["sweep_entrypoints"] = ["run_all.sh"]
def _m_prior(fx): fx["manifest"]["prior"] = "team/CORVID-S7-1G-VERIFY.md"
def _m_advances(fx): fx["manifest"]["advances"] = "G3 invocation"
def _m_llm(fx): fx["extra_py"]["triage.py"] = "import anthropic\n"
def _m_badjson(fx): fx["raw"]["guards.json"] = "{not json"
def _m_hostile(fx): fx["raw"]["covered_gates.json"] = "{\"a\": 1}"
def _m_nofile(fx): fx["raw"]["gate_contracts.py"] = None
def _m_receipts(fx): fx["raw"] = {"canary.py": "\n", "gate_contracts.py": "\n",
                                  "guards.json": "[]", "covered_gates.json":
                                  "[]", "manifest.json":
                                  "{\"sweep_entrypoints\": []}"}


# name -> (mutation, markers that must be EXACTLY the ones raised)
_MUTANTS = {
    "canary runs the sweep whatever the guards say": (_m_open,
                                                      {"CANARY-FAILS-OPEN",
                                                       "CANARY-PASSES-ON-NOTHING"}),
    "canary passes with zero guards": (_m_empty_ok, {"CANARY-PASSES-ON-NOTHING"}),
    "canary waits for a hung guard": (_m_no_timeout, {"CANARY-FAILS-OPEN"}),
    "canary does not name the guard": (_m_mute, {"CANARY-SILENT"}),
    "canary crashes": (_m_canary_crash, {"CANARY-BROKEN"}),
    "driver runs selftests only": (_m_selftest_only, {"DRIVER-BLIND"}),
    "driver ignores its covered set": (_m_no_coverage, {"DRIVER-COVERAGE-BLIND"}),
    "driver crashes": (_m_driver_crash, {"DRIVER-BROKEN"}),
    "a live guard not listed": (_m_guard_unlisted, {"GUARD-UNLISTED"}),
    "a listed guard is gone": (_m_guard_gone, {"GUARD-GONE"}),
    "a live sprint gate not covered": (_m_gate_uncovered, {"GATE-UNCOVERED"}),
    "a covered gate is gone": (_m_gate_gone, {"COVERED-GATE-GONE"}),
    "entry point never calls the canary": (_m_unwired, {"NOT-WIRED"}),
    "no entry point named": (_m_no_entry, {"NOT-WIRED"}),
    "entry point does not exist": (_m_entry_absent, {"NOT-WIRED"}),
    "prior cites the corrected-away file": (_m_prior, {"PRIOR-NOT-CITED"}),
    "advances overstated": (_m_advances, {"ADVANCES-UNSTATED"}),
    "a model in the integrity path": (_m_llm, {"LLM-OR-NETWORK"}),
    "broken json": (_m_badjson, {"BAD-JSON"}),
    "hostile list": (_m_hostile, {"SCHEMA"}),
    "file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _selftest() -> int:
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []

    def case(name, fx, want):
        with tempfile.TemporaryDirectory() as td:
            root, team, repo = _write(Path(td), fx)
            rc, out = _run([sys.executable, __file__, str(root), "--team",
                            str(team), "--repo", str(repo)], 600)
        got = set(marker.findall(out))
        ok = want(got) if callable(want) else got == want
        if TRACEBACK in out:
            bad.append(f"{name}: traceback")
        elif want is None and (rc != 0 or got):
            bad.append(f"{name}: should be ACCEPTED, got exit {rc} {sorted(got)}")
        elif want is not None and (rc != 1 or not ok
                                   or "S10-3 gate findings: " not in out):
            bad.append(f"{name}: wrong rejection, got exit {rc} {sorted(got)}")

    case("conforming", _fixture(), None)
    receipts = _fixture()
    _m_receipts(receipts)
    case("receipts only: all files present, no substance", receipts,
         lambda got: len(got) >= 3 and "MISSING-FILE" not in got)
    for name, (mutate, want) in _MUTANTS.items():
        fx = _fixture()
        mutate(fx)
        case(name, fx, want)

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (the conforming build accepted; a receipts-only "
          f"directory and {len(_MUTANTS)} mutants each rejected by exactly "
          f"their own markers - a canary that fails open, one that passes on "
          f"zero guards, one that waits on a hung guard, and a driver that "
          f"never makes a dirty run among them; no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S10-3")
    ap.add_argument("root", nargs="?", default=str(HERE))
    ap.add_argument("--team", default=str(HERE.parent))
    ap.add_argument("--repo", default=str(HERE.parent.parent))
    ap.add_argument("--live", action="store_true",
                    help="also run both tools on the live tree (slow)")
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    return run(Path(a.root), Path(a.team), Path(a.repo), a.live)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S10-3 gate findings: 1")
        raise SystemExit(1)
