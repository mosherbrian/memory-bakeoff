#!/usr/bin/env python3
"""Gate for QUEUE row S6-3 (make the roadmap govern the work; reconcile the
charter; propose ONE experiment; populate Phase F).

plumb-fable, row S6-3G, 2026-09-17. Written FROM ROW S6-3's TEXT ALONE, before
any S6-3 artifact existed (`team/S6-ROADMAP/` was absent). The interface below is
declared by the gate, not fitted to a document; every finding names what it
wants, so the author can conform without reading this source.

Declared interface
  evidence.json
    roadmap      path of the roadmap the commitments come from
    commitments  [{id, quote, promised, artifact, status, next_decision}]
                 quote  = >= 4 words VERBATIM from the roadmap file
                 status = supported | in-progress | not-evidenced-here | never-done
                 artifact = a path that resolves, or null for the two absent states
    charter      [{section, state: live|superseded, superseded_by}]
                 section = text found in team/PORTFOLIO-CHARTER-draft.md
    phase_f      {options: {adopt, compose, build: {assessment, evidence: [paths]}},
                  deciding_uncertainty: "<one sentence>"}
  map.md         one line per commitment, carrying its id and its status
  next-experiment.json  {status: "proposed-not-built", question, baseline,
                 stopping_rule}; some field names G4
  review.json    {reviewer, author, verdict}

The distinctions the row is FOR (marker in brackets):
  a line each   every commitment has a map.md line with its id and its status,
                and the map agrees with evidence.json [COMMITMENT-WITHOUT-LINE]
                [MAP-STATUS-DISAGREES]; all four fields are filled
                [COMMITMENT-INCOMPLETE]; the commitment is a real one
                [QUOTE-NOT-IN-ROADMAP].
  two absences  "not evidenced here" and "never done" are separate values. An
                absent-ish value (null, unknown, missing, n/a ...) is rejected
                [STATUS-COLLAPSED]; a status must agree with its artifact
                [STATUS-CONTRADICTS-ARTIFACT]; a map line may not carry both
                absent states [ABSENT-STATES-COLLAPSED]; map.md defines both
                terms [LEGEND-MISSING].
  superseded    each superseded charter section names WHAT supersedes it;
                "stale" is not an answer [SUPERSEDED-BY-WHAT]; the section is
                real [CHARTER-SECTION-UNKNOWN]; at least one section is
                reconciled [NO-SUPERSEDED-SECTIONS]; map.md addresses the live
                arrangement the row lists [LIVE-ARRANGEMENT-MISSING].
  experiment    ONE [EXPERIMENT-NOT-ONE], with a baseline
                [EXPERIMENT-NO-BASELINE] and a stopping rule that is a rule
                [EXPERIMENT-NO-STOPPING-RULE], tied to G4 [EXPERIMENT-NOT-G4],
                marked proposed-not-built [EXPERIMENT-NOT-MARKED-PROPOSED] and
                carrying no results [EXPERIMENT-BUILT].
  Phase F       adopt / compose / build each assessed [PHASE-F-MATRIX], from
                evidence that already exists [ARTIFACT-UNRESOLVED], with ONE
                deciding uncertainty, a sentence and not a list
                [PHASE-F-UNCERTAINTY], and an entry in map.md
                [PHASE-F-NOT-IN-MAP].
  other         [MISSING-FILE] [BAD-JSON] [SCHEMA] [ROADMAP-UNRESOLVED]
                [CHARTER-UNRESOLVED] [REVIEW-INCOMPLETE] [REVIEW-NOT-INDEPENDENT]

Limit, stated on purpose: the gate proves every listed commitment is real and
every cited artifact EXISTS. It cannot prove the list is COMPLETE, nor that an
artifact SUPPORTS its claim; both stay with the named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S6-3 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT]      # ROOT defaults to this directory
  python3 check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

FILES = ("map.md", "evidence.json", "next-experiment.json", "review.json")
CHARTER = "PORTFOLIO-CHARTER-draft.md"
PRESENT = ("supported", "in-progress")
ABSENT = ("not-evidenced-here", "never-done")
OPTIONS = ("adopt", "compose", "build")
PLACEHOLDER = re.compile(
    r"^(?:|tbd|todo|pending|n/?a|none|null|unknown|missing|absent|\?+|-+|x+)$", re.I)
STALE_ONLY = re.compile(
    r"^(?:it is |is |now )?(?:stale|outdated|out of date|obsolete|old|superseded"
    r"|deprecated|no longer (?:true|applies|valid))\.?$", re.I)
RULE_WORD = re.compile(r"\b(?:stop|halt|abandon|end|if|when|until|unless|after)\b", re.I)
LIVE = {  # the live arrangement the row tells the author to reconcile against
    "three seats": r"\b(?:three|3)\s+seats?\b",
    "one request in flight": r"\b(?:one|single|1)\s+request\b",
    "free window ending 2026-09-20": r"2026-09-20",
    "OpenCode Go budget": r"opencode\s*go",
}


def _text(v, min_words: int = 1):
    ok = (isinstance(v, str) and not PLACEHOLDER.match(v.strip())
          and len(v.split()) >= min_words)
    return v.strip() if ok else None


def _norm(s: str) -> str:
    return " ".join(re.sub(r"[*_`]", "", s).lower().split())


def _status_re(status: str) -> re.Pattern:
    return re.compile(r"(?<![\w-])" + status.replace("-", r"[- ]") + r"(?![\w-])", re.I)


def _resolve(root: Path, ref):
    if not isinstance(ref, str) or PLACEHOLDER.match(ref.strip()):
        return None
    rel = ref.split("#")[0].strip().strip("`")
    for base in (root, root.parent, root.parent.parent):
        for p in (base / rel, base / rel.removeprefix("team/")):
            if p.exists():
                return p
    return None


def _read_json(root: Path, name: str, findings: list):
    try:
        return json.loads((root / name).read_text(encoding="utf-8", errors="replace"))
    except ValueError as e:
        findings.append(("BAD-JSON", f"{name}: {e}"))
        return None


def _check_commitments(root: Path, ev: dict, map_text: str, add) -> None:
    roadmap = _resolve(root, ev.get("roadmap"))
    if roadmap is None or not roadmap.is_file():
        add("ROADMAP-UNRESOLVED", f"evidence.json roadmap {ev.get('roadmap')!r} "
            "does not resolve to a file")
    road = _norm(roadmap.read_text(encoding="utf-8", errors="replace")) \
        if roadmap and roadmap.is_file() else None
    items = ev.get("commitments")
    if not (isinstance(items, list) and items and all(isinstance(c, dict) for c in items)):
        return add("SCHEMA", "evidence.json: commitments must be a non-empty list of objects")
    lines = map_text.splitlines()
    seen = set()
    for i, c in enumerate(items):
        cid = _text(c.get("id"))
        if cid is None or cid in seen:
            add("SCHEMA", f"commitment #{i}: id missing or duplicated ({c.get('id')!r})")
            continue
        seen.add(cid)
        lack = [k for k in ("promised", "next_decision") if _text(c.get(k), 2) is None]
        if lack:
            add("COMMITMENT-INCOMPLETE", f"{cid}: {', '.join(lack)} empty or placeholder")
        q = _text(c.get("quote"), 4)
        if q is None or (road is not None and _norm(q) not in road):
            add("QUOTE-NOT-IN-ROADMAP", f"{cid}: quote must be >= 4 words verbatim from "
                f"the roadmap file, got {c.get('quote')!r}")

        status = _norm(c["status"]).replace(" ", "-") if isinstance(c.get("status"), str) else None
        if status not in PRESENT + ABSENT:
            add("STATUS-COLLAPSED", f"{cid}: status {c.get('status')!r} is not one of "
                f"{' | '.join(PRESENT + ABSENT)}; 'not evidenced here' and 'never done' "
                "are separate values, not one absent-ish state")
            continue
        art = c.get("artifact")
        if status in ABSENT and art is not None:
            add("STATUS-CONTRADICTS-ARTIFACT", f"{cid}: status {status} but artifact {art!r} is cited")
        elif status in PRESENT and _resolve(root, art) is None:
            add("STATUS-CONTRADICTS-ARTIFACT" if art is None else "ARTIFACT-UNRESOLVED",
                f"{cid}: status {status} needs an artifact that exists, got {art!r}")

        mine = [l for l in lines
                if re.search(r"(?<![\w-])" + re.escape(cid) + r"(?![\w-])", l)]
        if not mine:
            add("COMMITMENT-WITHOUT-LINE", f"{cid}: no line in map.md carries this id")
        elif not any(_status_re(status).search(l) for l in mine):
            add("MAP-STATUS-DISAGREES", f"{cid}: evidence.json says {status}; no map.md "
                "line for it says the same")
        elif any(all(_status_re(s).search(l) for s in ABSENT) for l in mine):
            add("ABSENT-STATES-COLLAPSED", f"{cid}: its map.md line carries both absent states")
    for s in ABSENT:
        if not _status_re(s).search(map_text):
            add("LEGEND-MISSING", f"map.md never uses or defines {s.replace('-', ' ')!r}; "
                "the legend must define both absent states")


def _check_charter(root: Path, ev: dict, map_text: str, add) -> None:
    path = root.parent / CHARTER
    if not path.is_file():
        return add("CHARTER-UNRESOLVED", f"{path} not found")
    charter = _norm(path.read_text(encoding="utf-8", errors="replace"))
    rows = ev.get("charter")
    if not (isinstance(rows, list) and rows and all(isinstance(r, dict) for r in rows)):
        return add("SCHEMA", "evidence.json: charter must be a non-empty list of "
                   "{section, state, superseded_by}")
    superseded = 0
    for i, r in enumerate(rows):
        sec = _text(r.get("section"))
        if sec is None or _norm(sec) not in charter:
            add("CHARTER-SECTION-UNKNOWN", f"charter #{i}: section {r.get('section')!r} "
                f"is not text found in {CHARTER}")
        if r.get("state") not in ("live", "superseded"):
            add("SCHEMA", f"charter #{i}: state must be live or superseded")
        elif r["state"] == "superseded":
            superseded += 1
            by = _text(r.get("superseded_by"), 2)
            if by is None or STALE_ONLY.match(by) or (sec and _norm(by) == _norm(sec)):
                add("SUPERSEDED-BY-WHAT", f"charter section {r.get('section')!r}: "
                    f"superseded_by {r.get('superseded_by')!r} says it is stale, not WHAT "
                    "supersedes it")
    if not superseded:
        add("NO-SUPERSEDED-SECTIONS", "no charter section is marked superseded; the row "
            "lists four live facts the draft predates")
    lack = [k for k, pat in LIVE.items() if not re.search(pat, map_text, re.I)]
    if lack:
        add("LIVE-ARRANGEMENT-MISSING", "map.md does not address: " + "; ".join(lack))


def _check_phase_f(root: Path, ev: dict, map_text: str, add) -> None:
    pf = ev.get("phase_f")
    opts = pf.get("options") if isinstance(pf, dict) else None
    if not isinstance(opts, dict):
        return add("PHASE-F-MATRIX", "evidence.json: phase_f.options must hold "
                   + " / ".join(OPTIONS))
    cited = 0
    for name in OPTIONS:
        o = opts.get(name)
        if not (isinstance(o, dict) and _text(o.get("assessment"), 3)
                and isinstance(o.get("evidence"), list)):
            add("PHASE-F-MATRIX", f"phase_f.options.{name} needs an assessment and an "
                "evidence list")
            continue
        for ref in o["evidence"]:
            cited += 1
            if _resolve(root, ref) is None:
                add("ARTIFACT-UNRESOLVED", f"phase_f.options.{name}: {ref!r} does not exist")
    if not cited:
        add("PHASE-F-MATRIX", "Phase F cites no evidence at all; the row says populate "
            "it from evidence that already exists")
    u = pf.get("deciding_uncertainty")
    if _text(u, 5) is None or "uncertainties" in pf:
        add("PHASE-F-UNCERTAINTY", "phase_f.deciding_uncertainty must be ONE sentence "
            f"(a string, >= 5 words, no list), got {u!r}")
    if not any(re.search(r"phase\s*f\b", l, re.I) and re.search(r"uncertaint", l, re.I)
               for l in re.split(r"\n\s*\n", map_text)):
        add("PHASE-F-NOT-IN-MAP", "map.md has no Phase F entry naming the uncertainty")


def _check_experiment(ex, add) -> None:
    if not isinstance(ex, dict) or any(
            isinstance(ex.get(k), list) for k in ("experiments", "proposals", "options")):
        return add("EXPERIMENT-NOT-ONE", "next-experiment.json must be ONE experiment "
                   "object, not a list of candidates")
    if not (isinstance(ex.get("status"), str)
            and _norm(ex["status"]).replace(" ", "-") == "proposed-not-built"):
        add("EXPERIMENT-NOT-MARKED-PROPOSED", f"status must be \"proposed-not-built\", "
            f"got {ex.get('status')!r}")
    built = [k for k in ("results", "result", "outcome", "measured", "built_at", "run_id")
             if ex.get(k)]
    if built:
        add("EXPERIMENT-BUILT", f"carries {built}: the row says propose it, do not build it")
    if _text(ex.get("question"), 4) is None:
        add("SCHEMA", "next-experiment.json: question missing")
    if _text(ex.get("baseline"), 3) is None:
        add("EXPERIMENT-NO-BASELINE", f"baseline is {ex.get('baseline')!r}")
    rule = _text(ex.get("stopping_rule"), 4)
    if rule is None or not RULE_WORD.search(rule):
        add("EXPERIMENT-NO-STOPPING-RULE", f"stopping_rule must state a condition "
            f"(stop if / when / until ...), got {ex.get('stopping_rule')!r}")
    if not re.search(r"\bG4\b", json.dumps(ex)):
        add("EXPERIMENT-NOT-G4", "no field ties the experiment to the G4 material outcome")


def _check_review(obj, add) -> None:
    def s(*keys):
        for k in keys:
            v = _text(obj.get(k)) if isinstance(obj, dict) else None
            if v:
                return v
    who, author = s("reviewer", "verifier", "reviewed_by"), s("author")
    if not (who and author and s("verdict", "status", "result")):
        add("REVIEW-INCOMPLETE", "review.json needs reviewer, author and verdict")
    elif who.lower() == author.lower():
        add("REVIEW-NOT-INDEPENDENT", f"reviewer and author are both {who!r}")


def check(root: Path) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    add = lambda marker, msg: findings.append((marker, msg))
    missing = [f for f in FILES
               if not (root / f).is_file() or not (root / f).stat().st_size]
    for f in missing:
        add("MISSING-FILE", f"{f} (absent or empty)")
    if "review.json" not in missing:
        obj = _read_json(root, "review.json", findings)
        if obj is not None:
            _check_review(obj, add)
    if "next-experiment.json" not in missing:
        obj = _read_json(root, "next-experiment.json", findings)
        if obj is not None:
            _check_experiment(obj, add)
    if "evidence.json" in missing or "map.md" in missing:
        return findings
    ev = _read_json(root, "evidence.json", findings)
    if ev is None:
        return findings
    if not isinstance(ev, dict):
        add("SCHEMA", "evidence.json must be an object")
        return findings
    map_text = (root / "map.md").read_text(encoding="utf-8", errors="replace")
    _check_commitments(root, ev, map_text, add)
    _check_charter(root, ev, map_text, add)
    _check_phase_f(root, ev, map_text, add)
    return findings


# ---- selftest: the gate must be able to fail, and able to pass ----

_ROADMAP = ("# Roadmap\n\n## Phase B\nWe will publish a frozen retrieval benchmark with "
            "hidden tests.\n\n## Phase C\nWe will compare three engines on the same frozen "
            "corpus.\n\n## Phase D\nWe will run a long-horizon drift study across sessions.\n")
_CHARTER = ("# Portfolio charter (draft)\n\n## Staffing\nNine seats work in parallel.\n\n"
            "## Goals\nFrozen goals G1 to G4.\n")
_MAP = """# Evidence map

Legend: `not evidenced here` = the brief did not hold the record, it may exist
elsewhere. `never done` = we looked and the work was not started.

| id | promised | artifact | status | next decision |
|---|---|---|---|---|
| RM-B1 | frozen benchmark | proof/bench.md | supported | publish or hold |
| RM-C1 | engine comparison | - | not evidenced here | ask Brian for the full record |
| RM-D1 | drift study | - | never done | schedule or drop |

## Charter reconciliation
The live arrangement is three seats with one request in flight; the free window
ends 2026-09-20 and the OpenCode Go budget applies after it.

## Phase F (adopt / compose / build)
The one uncertainty that would change the answer: whether an adopted engine can
pass the abstention control.
"""
_EVIDENCE = {
    "roadmap": "ROADMAP.md",
    "commitments": [
        {"id": "RM-B1", "quote": "publish a frozen retrieval benchmark",
         "promised": "a frozen benchmark", "artifact": "proof/bench.md",
         "status": "supported", "next_decision": "publish or hold"},
        {"id": "RM-C1", "quote": "compare three engines on the same frozen corpus",
         "promised": "an engine comparison", "artifact": None,
         "status": "not-evidenced-here", "next_decision": "ask Brian for the record"},
        {"id": "RM-D1", "quote": "run a long-horizon drift study",
         "promised": "a drift study", "artifact": None,
         "status": "never-done", "next_decision": "schedule or drop"}],
    "charter": [
        {"section": "Staffing", "state": "superseded",
         "superseded_by": "POLICY.md three-seat arrangement of 2026-09-16"},
        {"section": "Goals", "state": "live", "superseded_by": None}],
    "phase_f": {
        "options": {
            "adopt": {"assessment": "one engine passes coverage only",
                      "evidence": ["proof/bench.md"]},
            "compose": {"assessment": "bm25 plus a trigger is untested", "evidence": []},
            "build": {"assessment": "no evidence supports building yet", "evidence": []}},
        "deciding_uncertainty": "whether an adopted engine can pass the abstention control"},
}
_EXPERIMENT = {"status": "proposed-not-built",
               "question": "Does selective retrieval change the G4 material outcome?",
               "baseline": "bm25 on the frozen diagnostic",
               "stopping_rule": "stop if the gap to bm25 is under the declared margin "
                                "after one run"}
_REVIEW = {"reviewer": "corvid-dsh", "author": "kiln-flash", "verdict": "pass"}


def _fixture() -> dict:
    return copy.deepcopy({"map": _MAP, "evidence": _EVIDENCE, "experiment": _EXPERIMENT,
                          "review": _REVIEW, "charter": _CHARTER})


def _write(base: Path, fx: dict) -> Path:
    """Lays out base/team/{charter, ROADMAP.md, S6-ROADMAP/...}; returns the gate root."""
    root = base / "team" / "S6-ROADMAP"
    (root / "proof").mkdir(parents=True)
    (root / "proof" / "bench.md").write_text("benchmark receipt\n")
    (root.parent / "ROADMAP.md").write_text(_ROADMAP)
    if fx["charter"] is not None:
        (root.parent / CHARTER).write_text(fx["charter"])
    (root / "map.md").write_text(fx["map"], encoding="utf-8")
    for name, key in (("evidence.json", "evidence"), ("next-experiment.json", "experiment"),
                      ("review.json", "review")):
        v = fx[key]
        (root / name).write_text(v if isinstance(v, str) else json.dumps(v), encoding="utf-8")
    return root


def _c(i, **kw):
    return lambda fx: fx["evidence"]["commitments"][i].update(kw)


def _map(old, new):
    return lambda fx: fx.update(map=fx["map"].replace(old, new))


def _ex(**kw):
    return lambda fx: fx["experiment"].update(kw)


# one defect each, so every check is shown to fail on its own
_MUTANTS = {
    "STATUS-COLLAPSED": _c(1, status="missing"),
    "STATUS-CONTRADICTS-ARTIFACT": _c(2, artifact="proof/bench.md"),
    "ABSENT-STATES-COLLAPSED": _map("| not evidenced here |",
                                    "| not evidenced here / never done |"),
    "MAP-STATUS-DISAGREES": _map("| - | not evidenced here |", "| - | never done |"),
    "COMMITMENT-WITHOUT-LINE": _map("| RM-D1 | drift study | - | never done | "
                                    "schedule or drop |\n", ""),
    "LEGEND-MISSING": lambda fx: (
        fx["evidence"]["commitments"].pop(),
        fx.update(map=re.sub(r"(?i)never done", "skipped", fx["map"])
                  .replace("| RM-D1 |", "| RM-X |"))),
    "COMMITMENT-INCOMPLETE": _c(0, next_decision="TBD"),
    "QUOTE-NOT-IN-ROADMAP": _c(0, quote="ship a product nobody promised"),
    "ARTIFACT-UNRESOLVED": _c(0, artifact="proof/nowhere.md"),
    "ROADMAP-UNRESOLVED": lambda fx: fx["evidence"].update(roadmap="NOPE.md"),
    "SUPERSEDED-BY-WHAT": lambda fx: fx["evidence"]["charter"][0].update(superseded_by="stale"),
    "CHARTER-SECTION-UNKNOWN": lambda fx: fx["evidence"]["charter"][0].update(
        section="Section 99 that is not there"),
    "NO-SUPERSEDED-SECTIONS": lambda fx: fx["evidence"]["charter"].pop(0),
    "CHARTER-UNRESOLVED": lambda fx: fx.update(charter=None),
    "LIVE-ARRANGEMENT-MISSING": _map("OpenCode Go budget", "paid budget"),
    "EXPERIMENT-NOT-MARKED-PROPOSED": _ex(status="ready"),
    "EXPERIMENT-BUILT": _ex(results={"gap": 0.2}),
    "EXPERIMENT-NO-BASELINE": lambda fx: fx["experiment"].pop("baseline"),
    "EXPERIMENT-NO-STOPPING-RULE": _ex(stopping_rule="we will see how it goes"),
    "EXPERIMENT-NOT-G4": _ex(question="Does selective retrieval change anything at all?"),
    "EXPERIMENT-NOT-ONE": lambda fx: fx.update(experiment=[_EXPERIMENT, _EXPERIMENT]),
    "PHASE-F-MATRIX": lambda fx: fx["evidence"]["phase_f"]["options"].pop("compose"),
    "PHASE-F-UNCERTAINTY": lambda fx: fx["evidence"]["phase_f"].update(
        deciding_uncertainty=["cost", "latency", "abstention"]),
    "PHASE-F-NOT-IN-MAP": _map("## Phase F (adopt / compose / build)", "## Later"),
    "REVIEW-NOT-INDEPENDENT": lambda fx: fx["review"].update(reviewer="kiln-flash"),
    "BAD-JSON": lambda fx: fx.update(evidence="{not json"),
}
_MARKER = re.compile(r"S6-3 gate findings: [1-9]")


def _selftest() -> int:
    fails: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        def root(name, *edits):
            fx = _fixture()
            for e in edits:
                e(fx)
            return _write(Path(td) / name, fx)

        good = root("good")
        got = check(good)
        if got:
            fails.append(f"conforming fixture REJECTED: {got}")

        for marker, edit in _MUTANTS.items():
            got = {m for m, _ in check(root(marker, edit))}
            if marker not in got:
                fails.append(f"mutant for [{marker}] was ACCEPTED or mis-named: {sorted(got)}")

        for f in FILES:  # every declared file is required, one at a time
            d = root(f"no-{f}")
            (d / f).unlink()
            if ("MISSING-FILE", f"{f} (absent or empty)") not in check(d):
                fails.append(f"fixture without {f} was ACCEPTED")

        # the file-counting failure the row names: right names, no distinctions
        hollow = root("hollow", lambda fx: fx.update(
            map="# map\n", evidence={}, experiment={}, review={}))
        if len({m for m, _ in check(hollow)}) < 5:
            fails.append(f"four hollow files were nearly ACCEPTED: {check(hollow)}")

        # the real command line, both ways, plus a root that tries to crash it
        bad = root("bad", _c(1, status="unknown"), _ex(status="built"))
        crash = root("crash", lambda fx: fx.update(
            evidence={"commitments": [1, None], "charter": "x", "phase_f": [],
                      "roadmap": 7}, experiment="7", review="[]"))
        (crash / "map.md").unlink()
        (crash / "map.md").mkdir()
        for label, d, want in (("clean", good, 0), ("dirty", bad, 1), ("hollow", hollow, 1),
                               ("hostile", crash, 1)):
            p = subprocess.run([sys.executable, str(Path(__file__).resolve()), str(d)],
                               capture_output=True, text=True, timeout=60)
            text = p.stdout + p.stderr
            if p.returncode != want:
                fails.append(f"CLI [{label}]: exit {p.returncode}, expected {want}")
            if "Traceback (most recent call last)" in text or "GATE-ERROR" in text:
                fails.append(f"CLI [{label}]: crash instead of a verdict :: {text[-160:]}")
            if bool(_MARKER.search(text)) != bool(want):
                fails.append(f"CLI [{label}]: finding marker "
                             f"{'absent' if want else 'printed on a clean root'}")
    for f in fails:
        print(f"[SELFTEST-FAIL] {f}")
    if fails:
        print(f"S6-3 gate selftest findings: {len(fails)}")
        return 1
    print(f"selftest: PASS (conforming fixture accepted; {len(_MUTANTS)} single-defect "
          f"mutants, {len(FILES)} missing-file roots, four hollow files, and the dirty and "
          "hostile CLI roots all rejected by name, no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S6-3")
    ap.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    findings = check(Path(a.root).resolve())
    for marker, detail in findings:
        print(f"[{marker}] {detail}")
    if findings:
        print(f"S6-3 gate findings: {len(findings)}")
        return 1
    print("S6-3 gate: clean")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as e:  # a crash must still read as a finding, not a trace
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S6-3 gate findings: 1")
        raise SystemExit(1)
