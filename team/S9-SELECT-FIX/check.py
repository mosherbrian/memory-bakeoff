#!/usr/bin/env python3
"""Gate for QUEUE row S10-4 (planner integrity: sprint-next's duplicate
detector must key on candidate identity, not rank number).

plumb-fable, row S10-4G, 2026-09-18. Written FROM ROW S10-4's TEXT ALONE, while
`team/S9-SELECT-FIX/` did not exist. Read for this gate: the board row and the
tool it repairs (conductor-chat/workers/sprint-next: its SN_TEAM / SN_QUEUE /
SN_DIR settings and the `already_admitted` function). The interface below is
declared by the gate, not fitted to a document; every finding names what it
wants.

This gate is an INSTRUMENT. It does not read the fix, it DRIVES it: it loads
the patched tool with its board settings pointed at a scratch board the gate
wrote, calls already_admitted on candidates of its own, and checks both
directions the row demands. It drives the pre-fix copy the same way, so the
bug is shown to have been there. And it runs the build's proof against both
copies, so a proof that cannot fail is caught.

Declared interface (ROOT = team/S9-SELECT-FIX)
  sprint-next.before  the tool as it stood, verbatim
  sprint-next         the tool with the fix
  proof.py            python3 proof.py [--tool PATH]   (default: ROOT/sprint-next)
                      exit 0 when both directions hold on a SCRATCH board,
                      non-zero when either fails. Never the live board.
  manifest.json       {prior: names both dead proposals, advances: says
                      neither, deployed: true | false,
                      deployed_paths: [files] when true,
                      handoff: who deploys, when false}

What the row turns on (marker in brackets)
  (a) BOTH DIRECTIONS, on the patched tool, on the gate's scratch board:
      the same artifact re-declared under a new rank is still refused, and so
      is the same artifact under the same rank [READMISSION-ADMITTED]; a fresh
      artifact over a burned rank number is admitted, and rank 1 is not
      burned by a row that cites rank 12 [FRESH-REFUSED].
  (b) THE BUG WAS THERE. The pre-fix copy refuses the fresh candidate over the
      burned number [BEFORE-NOT-BUGGY]; the two copies differ in
      already_admitted [NO-FIX] and nowhere else, since this is a fleet script
      amended under one declared row [FIX-NOT-SCOPED].
  (c) THE PROOF CAN FAIL. proof.py exits 0 on the patched tool [PROOF-FAILS]
      and non-zero on the pre-fix copy [PROOF-CANNOT-FAIL]; it works on a
      scratch copy [PROOF-NOT-SCRATCH]; running it leaves the live board
      without a new sprint-next backup or admission line
      [LIVE-BOARD-TOUCHED].
  (d) WHERE THE FIX LIVES. If deployed, every deployed path passes both
      directions too [LIVE-TOOL-UNFIXED]; if not, the manifest names who
      deploys it [NOT-DEPLOYED-NO-HANDOFF].
  (e) Prior cited: both dead proposals [PRIOR-NOT-CITED]; advances-neither
      said plainly [ADVANCES-UNSTATED].
  other  [MISSING-FILE] [BAD-JSON] [SCHEMA] [TOOL-UNDRIVABLE]

Stated on purpose, and printed on a clean run: under the row's rule a row that
was RE-POINTED at admission (it cites rank N but carries another path) no
longer blocks the candidate it came from. The rank test was added on
2026-09-17 for exactly that case. The gate reports what the patched tool does
there; it does not fail it, because the row defines the rule.

Limits: the gate drives already_admitted, the function the row names, not a
whole planning run. Live-board safety is judged by sprint-next's own traces
(a `.bak-sprintnext-` file, an admission line), so an edit of another kind
would not be seen.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S10-4 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT] [--live-queue FILE]
  python3 check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ("sprint-next.before", "sprint-next", "proof.py", "manifest.json")
DEAD = ("SPRINT-NEXT-PROPOSAL.dead-20260918-110036.md",
        "SPRINT-NEXT-PROPOSAL.dead-20260918-122712.md")
FUNC = "already_admitted"
ADMIT_LINE = "by sprint-next from BACKLOG-NEXT rank"
TRACEBACK = "Traceback (most recent call last)"

_ROW = ("| {rid} | {what} | kiln-flash | pulse | `/scratch/team/{art}` (check: "
        "python3 /scratch/team/{art}/check.py) | $0.00 | open (admitted "
        "2026-09-17 by sprint-next from BACKLOG-NEXT rank {rank}) — verifier: "
        "corvid-dsh |\n")
_BOARD = ("# QUEUE\n\n## SPRINT 8 GOAL\n\n| # | task | owner | cadence | artifact "
          "| cost | status |\n|---|---|---|---|---|---|---|\n"
          + _ROW.format(rid="S8-1", what="alpha work", art="S7-ALPHA", rank=2)
          + _ROW.format(rid="S8-2", what="beta work, re-pointed at admission",
                        art="S8-BETA", rank=12))
# (label, candidate, expected row id or None, marker when wrong)
_CASES = [
    ("same artifact re-declared under a new rank",
     {"rank": 9, "artifact": "`/scratch/team/S7-ALPHA`"}, "S8-1",
     "READMISSION-ADMITTED"),
    ("same artifact under the same rank",
     {"rank": 2, "artifact": "`/scratch/team/S7-ALPHA`"}, "S8-1",
     "READMISSION-ADMITTED"),
    ("fresh artifact over burned rank 2",
     {"rank": 2, "artifact": "`/scratch/team/S9-FRESH`"}, None, "FRESH-REFUSED"),
    ("fresh artifact at rank 1, board cites rank 12",
     {"rank": 1, "artifact": "`/scratch/team/S9-ONE`"}, None, "FRESH-REFUSED"),
]
_REPOINTED = {"rank": 12, "artifact": "`/scratch/team/S7-BETA`"}
_DRIVER = """
import importlib.machinery, importlib.util, json, os, sys
tool, scratch, cases = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
os.environ.update(SN_TEAM=scratch, SN_QUEUE=os.path.join(scratch, "QUEUE.md"),
                  SN_DIR=scratch)
loader = importlib.machinery.SourceFileLoader("_sn_tool", tool)
mod = importlib.util.module_from_spec(importlib.util.spec_from_loader("_sn_tool", loader))
loader.exec_module(mod)
print("RESULT " + json.dumps([mod.already_admitted(c) for c in cases]))
"""


def drive(tool: Path, cases: list[dict]):
    """already_admitted(case) for each case, on the gate's scratch board; None
    when the tool cannot be loaded or called."""
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "QUEUE.md").write_text(_BOARD)
        try:
            p = subprocess.run([sys.executable, "-c", _DRIVER, str(tool), td,
                                json.dumps(cases)], capture_output=True,
                               text=True, timeout=60)
        except subprocess.TimeoutExpired:
            return None
    m = re.search(r"^RESULT (.*)$", p.stdout, re.M)
    try:
        return json.loads(m.group(1)) if p.returncode == 0 and m else None
    except ValueError:
        return None


def directions(tool: Path, label: str) -> list[tuple[str, str]]:
    got = drive(tool, [c for _, c, _, _ in _CASES])
    if got is None:
        return [("TOOL-UNDRIVABLE", f"{label}: could not load it with SN_TEAM / "
                 f"SN_QUEUE / SN_DIR set and call {FUNC}(candidate)")]
    return [(marker, f"{label}: {what}: returned {g!r}, must be {want!r}")
            for (what, _, want, marker), g in zip(_CASES, got) if g != want]


def _outside(path: Path) -> list[str]:
    """ast dumps of everything except the module docstring and FUNC."""
    body = ast.parse(path.read_text(encoding="utf-8", errors="replace")).body
    if body and isinstance(body[0], ast.Expr) and isinstance(
            getattr(body[0], "value", None), ast.Constant):
        body = body[1:]
    return [ast.dump(n) for n in body
            if not (isinstance(n, ast.FunctionDef) and n.name == FUNC)]


def _func(path: Path) -> str | None:
    for n in ast.parse(path.read_text(encoding="utf-8", errors="replace")).body:
        if isinstance(n, ast.FunctionDef) and n.name == FUNC:
            return ast.dump(n)
    return None


def _traces(queue: Path) -> tuple[int, int]:
    try:
        lines = queue.read_text(encoding="utf-8", errors="replace").count(ADMIT_LINE)
    except OSError:
        lines = 0
    return lines, len(list(queue.parent.glob(queue.name + ".bak-sprintnext-*")))


def _proof(proof: Path, tool: Path | None, live_queue: Path) -> tuple[int | None, str]:
    argv = [sys.executable, str(proof)] + (["--tool", str(tool)] if tool else [])
    env = {k: v for k, v in os.environ.items() if not k.startswith("SN_")}
    env["S10_4_LIVE_QUEUE"] = str(live_queue)  # the board this gate is watching
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=300,
                           env=env)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return None, ""


def check(root: Path, live_queue: Path) -> tuple[list[tuple[str, str]], str]:
    missing = [n for n in FILES if not (root / n).is_file()]
    if missing:
        return [("MISSING-FILE", f"{root}/{n}") for n in missing], ""
    try:
        manifest = json.loads((root / "manifest.json").read_text(
            encoding="utf-8", errors="replace"))
    except ValueError as e:
        return [("BAD-JSON", str(e))], ""
    if not isinstance(manifest, dict) or not isinstance(
            manifest.get("deployed"), bool):
        return [("SCHEMA", "manifest.json needs prior, advances, deployed: true "
                 "| false, and deployed_paths or handoff")], ""
    f: list[tuple[str, str]] = []
    before, after = root / "sprint-next.before", root / "sprint-next"

    # (a) both directions, on the patched tool
    f += directions(after, "sprint-next")

    # (b) the bug was there, and the fix is scoped
    old = drive(before, [c for _, c, _, _ in _CASES])
    if old is None:
        f.append(("TOOL-UNDRIVABLE", f"sprint-next.before: could not load it "
                  f"and call {FUNC}(candidate)"))
    elif old[2] is None:
        f.append(("BEFORE-NOT-BUGGY", "sprint-next.before admits the fresh "
                  "candidate over burned rank 2; it is not the tool that made "
                  "the false refusals, so nothing shows the fix fixed them"))
    try:
        if _func(before) == _func(after):
            f.append(("NO-FIX", f"{FUNC} is the same in both copies"))
        if _outside(before) != _outside(after):
            f.append(("FIX-NOT-SCOPED", f"the copies differ outside {FUNC}; "
                      f"this row amends the duplicate detector only"))
    except SyntaxError as e:
        f.append(("TOOL-UNDRIVABLE", f"a copy does not parse: {e}"))

    # (c) the proof can fail, and leaves the live board alone
    text = (root / "proof.py").read_text(encoding="utf-8", errors="replace")
    if not re.search(r"SN_QUEUE|SN_TEAM|tempfile|mkdtemp", text):
        f.append(("PROOF-NOT-SCRATCH", "proof.py shows no scratch board "
                  "(SN_QUEUE / SN_TEAM override or a temp directory); the row "
                  "says never the live board"))
    traces = _traces(live_queue)
    rc_new, out_new = _proof(root / "proof.py", None, live_queue)
    rc_old, out_old = _proof(root / "proof.py", before, live_queue)
    if rc_new != 0:
        f.append(("PROOF-FAILS", f"proof.py on the patched tool: exit {rc_new} "
                  f":: {(out_new.strip().splitlines() or [''])[-1][:100]}"))
    if rc_old == 0:
        f.append(("PROOF-CANNOT-FAIL", "proof.py --tool sprint-next.before "
                  "exits 0: it passes on the tool that made the false "
                  "refusals, so its pass proves nothing"))
    if _traces(live_queue) != traces:
        f.append(("LIVE-BOARD-TOUCHED", f"running proof.py left a sprint-next "
                  f"backup or admission line on {live_queue}"))

    # (d) where the fix lives
    if manifest["deployed"]:
        paths = manifest.get("deployed_paths")
        paths = paths if isinstance(paths, list) and paths else []
        if not paths:
            f.append(("LIVE-TOOL-UNFIXED", "deployed: true needs "
                      "deployed_paths: [files]"))
        for p in paths:
            target = Path(str(p)).expanduser()
            bad = directions(target, str(p)) if target.is_file() else [
                ("", f"{p}: no such file")]
            if bad:
                f.append(("LIVE-TOOL-UNFIXED", "; ".join(m for _, m in bad)[:300]))
    elif len(str(manifest.get("handoff", "")).strip()) < 15:
        f.append(("NOT-DEPLOYED-NO-HANDOFF", "deployed: false needs handoff: "
                  "who deploys the fix, and where. A fix in a scratch copy "
                  "stops no false refusal"))

    # (e) prior, advances
    if not all(d in str(manifest.get("prior", "")) for d in DEAD):
        f.append(("PRIOR-NOT-CITED", f"manifest.json prior must name both "
                  f"dead proposals: {' and '.join(DEAD)}"))
    if not re.search(r"neither", str(manifest.get("advances", "")), re.I):
        f.append(("ADVANCES-UNSTATED", "manifest.json advances must say it "
                  "advances neither a frozen goal nor a roadmap item"))

    note = drive(after, [_REPOINTED])
    repointed = ("admitted again" if note == [None] else
                 f"refused ({note[0]})" if note else "not driven")
    return f, (f"both directions hold on the patched tool; the pre-fix copy "
               f"shows the bug; proof.py fails on it. Note - a candidate whose "
               f"row was re-pointed at admission (same rank, other path) is "
               f"{repointed}")


def run(root: Path, live_queue: Path) -> int:
    findings, summary = check(root, live_queue)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S10-4 gate findings: {len(findings)}")
        return 1
    print(f"S10-4 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_TOOL = '''"""a small stand-in for sprint-next"""
import os
import re
from pathlib import Path

TEAM = Path(os.environ.get("SN_TEAM", "/nonexistent/team"))
QUEUE = Path(os.environ.get("SN_QUEUE", TEAM / "QUEUE.md"))
MAX_OPENS_PER_DAY = 3


def already_admitted(cand):
    art = (cand.get("artifact") or "").strip().strip("`")
    if not art or "/" not in art:
        return None
    text = QUEUE.read_text()
PATH_TEST
RANK_TEST
    return None


def main():
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
_PATH_TEST = '''    for line in text.split("\\n"):
        if line.startswith("|") and art in line:
            rid = line.split("|")[1].strip()
            if rid and rid != "#":
                return rid'''
_OLD_RANK = '''    m = re.search(r"\\| *([A-Za-z0-9-]+) *\\|[^\\n]*BACKLOG-NEXT rank %s\\b"
                  % cand.get("rank"), text)
    if m:
        return m.group(1)'''
_NEW_RANK = '''    for line in text.split("\\n"):
        if line.startswith("|") and art in line and re.search(
                r"BACKLOG-NEXT rank %s\\b" % cand.get("rank"), line):
            return line.split("|")[1].strip()'''


def _tool(path_test=_PATH_TEST, rank_test=_NEW_RANK, opens=3) -> str:
    return _TOOL.replace("PATH_TEST", path_test).replace(
        "RANK_TEST", rank_test).replace("MAX_OPENS_PER_DAY = 3",
                                        f"MAX_OPENS_PER_DAY = {opens}")


_PROOF = '''import argparse, importlib.machinery, importlib.util, os, tempfile
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument("--tool", default=str(Path(__file__).parent / "sprint-next"))
a = ap.parse_args()
row = ("| S8-1 | x | k | pulse | `/s/team/S7-A` | $0 | open (admitted by "
       "sprint-next from BACKLOG-NEXT rank 2) |\\n")
with tempfile.TemporaryDirectory() as td:
    (Path(td) / "QUEUE.md").write_text(row)
    os.environ.update(SN_TEAM=td, SN_QUEUE=str(Path(td) / "QUEUE.md"))
    loader = importlib.machinery.SourceFileLoader("_t", a.tool)
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader("_t", loader))
    loader.exec_module(mod)
    refused = mod.already_admitted({"rank": 7, "artifact": "/s/team/S7-A"})
    fresh = mod.already_admitted({"rank": 2, "artifact": "/s/team/S9-NEW"})
VANDAL
ok = refused == "S8-1" and fresh is None
print("both directions hold" if ok else f"FAIL refused={refused} fresh={fresh}")
raise SystemExit(0 if ok else 1)
'''
_GOOD_PROOF = _PROOF.replace("VANDAL\n", "")
_VANDAL = _PROOF.replace("VANDAL", (
    'live = Path(os.environ["S10_4_LIVE_QUEUE"])\n'
    'live.write_text(live.read_text() + "| S9-9 | x | admitted by sprint-next '
    'from BACKLOG-NEXT rank 2 |\\n")'))


def _fixture() -> dict:
    return {"before": _tool(rank_test=_OLD_RANK), "after": _tool(),
            "proof": _GOOD_PROOF, "deployed_tool": _tool(), "raw": {},
            "manifest": {"prior": " and ".join(f"team/{d}" for d in DEAD),
                         "advances": "neither a frozen goal nor a roadmap item",
                         "deployed": True, "deployed_paths": ["AUTO"]}}


def _write(td: Path, fx: dict) -> tuple[Path, Path]:
    root = td / "team" / "S9-SELECT-FIX"
    root.mkdir(parents=True)
    live = td / "team" / "QUEUE.md"
    live.write_text(_BOARD)
    deployed = td / "deployed-sprint-next"
    deployed.write_text(fx["deployed_tool"])
    (root / "sprint-next.before").write_text(fx["before"])
    (root / "sprint-next").write_text(fx["after"])
    (root / "proof.py").write_text(fx["proof"])
    m = fx["manifest"]
    if m.get("deployed_paths") == ["AUTO"]:
        m["deployed_paths"] = [str(deployed)]
    (root / "manifest.json").write_text(json.dumps(m))
    for name, text in fx["raw"].items():
        if text is None:
            (root / name).unlink()
        else:
            (root / name).write_text(text)
    return root, live


def _m_never_fixed(fx): fx["after"] = fx["before"]
def _m_overfixed(fx): fx["after"] = _tool(path_test="    pass", rank_test="    pass")
def _m_unscoped(fx): fx["after"] = _tool(opens=30)
def _m_before_clean(fx): fx["before"] = fx["after"]
def _m_proof_always(fx): fx["proof"] = "import tempfile\nraise SystemExit(0)\n"
def _m_proof_live(fx): fx["proof"] = ("import sys\n# runs against the board in place\n"
                                       "raise SystemExit(0 if len(sys.argv) == 1 else 1)\n")
def _m_vandal(fx): fx["proof"] = _VANDAL
def _m_syntax(fx): fx["after"] = "def already_admitted(cand:\n"
def _m_deployed_old(fx): fx["deployed_tool"] = fx["before"]
def _m_deployed_absent(fx): fx["manifest"]["deployed_paths"] = ["/nonexistent/sn"]
def _m_no_handoff(fx): fx["manifest"].update(deployed=False)
def _m_prior(fx): fx["manifest"]["prior"] = f"team/{DEAD[0]}"
def _m_advances(fx): fx["manifest"]["advances"] = "G3"
def _m_badjson(fx): fx["raw"]["manifest.json"] = "{not json"
def _m_hostile(fx): fx["raw"]["manifest.json"] = "[1, 2]"
def _m_nofile(fx): fx["raw"]["proof.py"] = None
def _m_receipts(fx): fx["raw"] = {"sprint-next.before": "\n", "sprint-next": "\n",
                                  "proof.py": "\n",
                                  "manifest.json": "{\"deployed\": false}"}


# name -> (mutation, markers that must be EXACTLY the ones raised)
_MUTANTS = {
    "fix never made": (_m_never_fixed, {"FRESH-REFUSED", "NO-FIX", "PROOF-FAILS"}),
    "over-fixed: nothing is ever refused": (_m_overfixed,
                                            {"READMISSION-ADMITTED",
                                             "PROOF-FAILS"}),
    "patch reaches outside the detector": (_m_unscoped, {"FIX-NOT-SCOPED"}),
    "pre-fix copy does not show the bug": (_m_before_clean,
                                           {"BEFORE-NOT-BUGGY", "NO-FIX",
                                            "PROOF-CANNOT-FAIL"}),
    "proof that always passes": (_m_proof_always, {"PROOF-CANNOT-FAIL"}),
    "proof with no scratch board": (_m_proof_live, {"PROOF-NOT-SCRATCH"}),
    "proof writes to the live board": (_m_vandal, {"LIVE-BOARD-TOUCHED"}),
    "patched tool does not parse": (_m_syntax, {"TOOL-UNDRIVABLE",
                                                "PROOF-FAILS"}),
    "deployed copy still has the bug": (_m_deployed_old, {"LIVE-TOOL-UNFIXED"}),
    "deployed path does not exist": (_m_deployed_absent, {"LIVE-TOOL-UNFIXED"}),
    "not deployed, nobody named": (_m_no_handoff, {"NOT-DEPLOYED-NO-HANDOFF"}),
    "one dead proposal cited": (_m_prior, {"PRIOR-NOT-CITED"}),
    "advances overstated": (_m_advances, {"ADVANCES-UNSTATED"}),
    "broken json": (_m_badjson, {"BAD-JSON"}),
    "hostile manifest": (_m_hostile, {"SCHEMA"}),
    "file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _selftest() -> int:
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []

    def case(name, fx, want):
        with tempfile.TemporaryDirectory() as td:
            root, live = _write(Path(td), fx)
            r = subprocess.run([sys.executable, __file__, str(root),
                                "--live-queue", str(live)], capture_output=True,
                               text=True, timeout=600)
        out = r.stdout + r.stderr
        got = set(marker.findall(out))
        ok = want(got) if callable(want) else got == want
        if TRACEBACK in out:
            bad.append(f"{name}: traceback")
        elif want is None and (r.returncode != 0 or got):
            bad.append(f"{name}: should be ACCEPTED, got exit {r.returncode} "
                       f"{sorted(got)}")
        elif want is not None and (r.returncode != 1 or not ok
                                   or "S10-4 gate findings: " not in out):
            bad.append(f"{name}: wrong rejection, got exit {r.returncode} "
                       f"{sorted(got)}")

    case("conforming, deployed", _fixture(), None)
    handed = _fixture()
    handed["manifest"].update(deployed=False, handoff="the tool's operator "
                              "deploys it to ~/.config/agent-deck/sprint-next")
    case("conforming, not deployed, handed off", handed, None)
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
    print(f"selftest: PASS (2 conforming builds accepted; a receipts-only "
          f"directory and {len(_MUTANTS)} mutants each rejected by exactly "
          f"their own markers - a fix never made, an over-fix that refuses "
          f"nothing, a proof that cannot fail and one that writes to the live "
          f"board among them; no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S10-4")
    ap.add_argument("root", nargs="?", default=str(HERE))
    ap.add_argument("--live-queue", default=str(HERE.parent / "QUEUE.md"))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    return run(Path(a.root), Path(a.live_queue))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S10-4 gate findings: 1")
        raise SystemExit(1)
