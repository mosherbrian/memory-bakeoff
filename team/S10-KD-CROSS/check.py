#!/usr/bin/env python3
"""Gate for QUEUE row S11-2 (KnowledgeDrift cross-system replay: more systems
on the SAME frozen sample, family scores kept separate, old beside new).

plumb-fable, row S11-2G, 2026-09-18. Written FROM ROW S11-2's TEXT ALONE, while
`team/S10-KD-CROSS/` did not exist. Read for this gate: the board row; of the
verified prior (team/S7-KD-WORLDS) only its key names and declared parameters;
and the provider names in implementer/repo/src/memory_bakeoff/providers. The
interface below is declared by the gate, not fitted to a document; every
finding names what it wants.

The row reuses the S7-4 harness and its sha-pinned worlds, and so does this
gate. It RUNS this seat's S7-4 gate (team/S7-KD-WORLDS/check.py) on the new
directory, so everything that held for the one-system run holds here by the
same code: frozen worlds, families accounted for, controls first and honest,
pass rates recounted from per-item receipts, the card's caveat quoted, no
upstream score imported, declared before the run. Only one S7-4 finding is
set aside: that gate wanted "no prior exists", and now one does.

On top of that, what is new in THIS row (marker in brackets)
  (a) THE SAME SAMPLE. items.jsonl is the prior's file, byte for byte
      [SAMPLE-NOT-FROZEN]; the world files and upstream commit are the prior's
      [WORLDS-DIFFER].
  (b) THE OTHER SYSTEMS. dense_lsa, tfidf_cosine and hybrid_rrf all ran
      [SYSTEM-MISSING]. The claude_mem stretch arm either ran, or
      verdict.json not_run names it with the reason [STRETCH-ARM-SILENT].
  (c) THE HARNESS DID NOT MOVE. bm25 is run again as the control and passes
      and fails exactly the items it did in the prior [HARNESS-DRIFTED]; else
      a difference between systems cannot be told from a difference between
      runs.
  (d) OLD BESIDE NEW. verdict.json prior names the prior's verdict.json
      [PRIOR-NOT-CITED] and quotes its bm25 family cells exactly
      [PRIOR-MISQUOTED].
  (e) FAMILIES STAY SEPARATE. No overall, total or combined figure across
      families, as a key or in the finding [FAMILIES-BLENDED]. (A family cell
      that does not equal its recount is the S7-4 gate's [NUMBERS-DISAGREE].)
  other  [PRIOR-UNREADABLE] [S7-GATE-UNREADABLE], and every S7-4 marker

Declared interface (ROOT = team/S10-KD-CROSS): the S7-4 files and schema
(declaration.json, items.jsonl, results.jsonl, verdict.json), with
  results.jsonl  engines return-nothing, oracle, then bm25, dense_lsa,
                 tfidf_cosine, hybrid_rrf, and claude_mem* if it ran
  verdict.json   prior: {source (names S7-KD-WORLDS/verdict.json),
                         bm25: {family: {passed, items}}}
                 not_run: {"claude_mem...": reason}   when the stretch arm did
                 not run

Limits, stated on purpose: the S7-4 limits carry over - `passed` is the
author's judgement per item, recounted but not re-judged. The gate cannot tell
that an arm named dense_lsa drove that provider, or that the claude_mem reason
is a good one. Those stay with the named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S11-2 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT] [--prior DIR] [--s7-gate FILE] [--card FILE]
  python3 check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "S7-KD-WORLDS"
CONTROL = "bm25"
SYSTEMS = ("dense_lsa", "tfidf_cosine", "hybrid_rrf")
STRETCH = "claude_mem"
STOP = ("MISSING-FILE", "BAD-JSON", "SCHEMA", "CARD-UNREADABLE")
BLEND_KEY = re.compile(r"overall|total|aggregate|combin|composite|blend|score",
                       re.I)


def _gate(path: Path):
    spec = importlib.util.spec_from_file_location("_s7_4_gate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _passed(rows: list, engine: str) -> dict:
    return {r["item_id"]: r["passed"] for r in rows
            if isinstance(r, dict) and r.get("engine") == engine}


def check(root: Path, prior: Path, s7_gate: Path, card: Path) -> tuple[list, str]:
    try:
        g = _gate(s7_gate)
        g.check, g._load, g._sha
    except Exception as e:
        return [("S7-GATE-UNREADABLE", f"{s7_gate}: {type(e).__name__}: {e}")], ""
    try:
        p_decl = g._load(prior / "declaration.json")
        p_cells = g._load(prior / "verdict.json")["per_family"][CONTROL]
        p_bm25 = _passed(g._load(prior / "results.jsonl", lines=True), CONTROL)
        p_items = g._sha(prior / "items.jsonl")
        p_worlds = (p_decl["worlds"]["commit"], p_decl["worlds"]["files"])
        if not p_bm25 or not isinstance(p_cells, dict):
            raise ValueError(f"no {CONTROL} arm in the prior")
    except Exception as e:
        return [("PRIOR-UNREADABLE", f"{prior}: {type(e).__name__}: {e}")], ""

    # everything the one-system run had to satisfy, by the same code
    inherited, _ = g.check(root, card)
    f = [(m, msg) for m, msg in inherited if m != "PRIOR-NOT-STATED"]
    if any(m in STOP for m, _ in f):
        return f, ""
    decl = g._load(root / "declaration.json")
    rows = g._load(root / "results.jsonl", lines=True)
    verdict = g._load(root / "verdict.json")

    # (a) the same sample
    if g._sha(root / "items.jsonl") != p_items:
        f.append(("SAMPLE-NOT-FROZEN", f"items.jsonl is not {prior.name}/"
                  f"items.jsonl byte for byte; the row compares systems on the "
                  f"SAME frozen sample"))
    w = decl.get("worlds", {})
    if (w.get("commit"), w.get("files")) != p_worlds:
        f.append(("WORLDS-DIFFER", f"declaration.json worlds.commit and "
                  f"worlds.files must equal {prior.name}'s"))

    # (b) the other systems, and the stretch arm
    engines = {r["engine"] for r in rows}
    absent = [s for s in SYSTEMS if s not in engines]
    if absent:
        f.append(("SYSTEM-MISSING", f"no receipts for: {', '.join(absent)}"))
    not_run = verdict.get("not_run") if isinstance(verdict.get("not_run"),
                                                   dict) else {}
    reasoned = any(str(k).startswith(STRETCH) and len(str(v).strip()) >= 15
                   for k, v in not_run.items())
    if not any(e.startswith(STRETCH) for e in engines) and not reasoned:
        f.append(("STRETCH-ARM-SILENT", f"the {STRETCH} stretch arm neither ran "
                  f"nor is recorded in verdict.json not_run with its reason"))

    # (c) the harness did not move
    now = _passed(rows, CONTROL)
    moved = sorted(i for i in set(now) | set(p_bm25) if now.get(i) != p_bm25.get(i))
    if moved:
        f.append(("HARNESS-DRIFTED", f"`{CONTROL}` must be run again and pass "
                  f"and fail exactly the prior's items; differs on "
                  f"{len(moved)}: {', '.join(moved[:5])}"))

    # (d) old beside new
    said = verdict.get("prior") if isinstance(verdict.get("prior"), dict) else {}
    if f"{prior.name}/verdict.json" not in str(said.get("source", "")):
        f.append(("PRIOR-NOT-CITED", f"verdict.json prior.source must name "
                  f"{prior.name}/verdict.json"))
    cells = said.get(CONTROL) if isinstance(said.get(CONTROL), dict) else {}
    if {fam: (c.get("passed"), c.get("items")) for fam, c in cells.items()
            if isinstance(c, dict)} != {fam: (c["passed"], c["items"])
                                        for fam, c in p_cells.items()}:
        f.append(("PRIOR-MISQUOTED", f"verdict.json prior.{CONTROL} must quote "
                  f"the prior's family cells exactly: "
                  f"{ {fam: (c['passed'], c['items']) for fam, c in p_cells.items()} }"))

    # (e) families stay separate
    n_items = len(p_bm25)
    keys = [k for k in verdict if BLEND_KEY.search(str(k))] + [
        f"per_family.{e}.{k}" for e, fams in (verdict.get("per_family") or {}).items()
        if isinstance(fams, dict) for k in fams if BLEND_KEY.search(str(k))]
    told = re.search(rf"/\s*{n_items}\b|\boverall\b|\bin total\b|\bcombined\b"
                     rf"|\bacross (all )?families\b",
                     str(verdict.get("finding", "")), re.I)
    if keys or told:
        f.append(("FAMILIES-BLENDED", f"a figure across families "
                  f"({', '.join(keys) or told.group(0)!r}); family scores are "
                  f"kept separate, as separate evidence classes"))
    ran = sorted(engines - {g.NOTHING, g.ORACLE})
    return f, (f"{len(ran)} systems on the prior's frozen sample of {n_items}: "
               f"{', '.join(ran)}; bm25 reproduces the prior item for item; "
               f"S7-4 gate clean on this directory")


def run(root: Path, prior: Path, s7_gate: Path, card: Path) -> int:
    findings, summary = check(root, prior, s7_gate, card)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S11-2 gate findings: {len(findings)}")
        return 1
    print(f"S11-2 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----
# The S7-4 gate's own fixture builder makes both the prior and the new
# directory, so the inherited checks are exercised for real.

def _new(g) -> dict:
    fx = g._fixture()
    ids = lambda fam: [i["item_id"] for i in fx["items"] if i["family"] == fam]  # noqa: E731
    bm25 = fx["pass"]["bm25"]
    fx["decl"]["engines"] = {e: {"experiment_class": "baseline"}
                             for e in (CONTROL, *SYSTEMS)}
    fx["order"] = [g.NOTHING, g.ORACLE, CONTROL, *SYSTEMS]
    fx["pass"] = {g.NOTHING: fx["pass"][g.NOTHING], g.ORACLE: fx["pass"][g.ORACLE],
                  CONTROL: set(bm25), "dense_lsa": set(ids("Retrieval")[:3]),
                  "tfidf_cosine": set(bm25), "hybrid_rrf": set(ids("Retrieval")[:8])}
    fx["verdict"].update(
        finding="on the same frozen sample no added system passes an "
                "Abstention item; Retrieval differs by system.",
        prior={"source": "team/S7-KD-WORLDS/verdict.json", "bm25": "AUTO"},
        not_run={"claude_mem_chroma_lsa": "its store cannot ingest the op "
                                          "stream without rewriting timestamps"})
    return fx


def _build(td: Path, g, new: dict, prior: dict) -> tuple[Path, Path, Path]:
    (td / "p").mkdir()
    (td / "n").mkdir()
    p_root, card = g._write(td / "p", prior)
    if new["verdict"]["prior"].get("bm25") == "AUTO":
        cells = json.loads((p_root / "verdict.json").read_text())["per_family"][CONTROL]
        new["verdict"]["prior"]["bm25"] = {fam: {"passed": c["passed"],
                                                 "items": c["items"]}
                                           for fam, c in cells.items()}
    n_root, _ = g._write(td / "n", new)
    return n_root, p_root, card


def _m_other_commit(new, prior): new["decl"]["worlds"]["commit"] = "ffffffffffff"
def _m_system_missing(new, prior): new["order"].remove("hybrid_rrf")
def _m_no_control(new, prior): new["order"].remove(CONTROL)
def _m_drift(new, prior): new["pass"][CONTROL].discard(sorted(new["pass"][CONTROL])[0])
def _m_stretch_silent(new, prior): del new["verdict"]["not_run"]
def _m_stretch_shrug(new, prior): new["verdict"]["not_run"] = {"claude_mem": "n/a"}
def _m_uncited(new, prior): new["verdict"]["prior"]["source"] = "sprint 7"
def _m_misquoted(new, prior): new["verdict"]["prior"]["bm25"] = {
    "Retrieval": {"passed": 1, "items": 12}}
def _m_overall_key(new, prior): new["verdict"]["overall_pass_rate"] = 0.4
def _m_overall_told(new, prior): new["verdict"]["finding"] += " Combined, hybrid leads."
def _m_late(new, prior): new["decl"]["declared_at"] = "2027-01-01T00:00:00+00:00"
def _m_caveat(new, prior): new["verdict"]["caveat"] = ("External benchmarks differ "
                                                       "from ours in scope, so read with care.")
def _m_import(new, prior): new["verdict"]["finding"] += " Upstream has TF-IDF at 580."
def _m_nofile(new, prior): new["raw"]["results.jsonl"] = None


def _m_other_sample(new, prior):
    old = prior["items"][0]["item_id"]
    prior["items"][0]["item_id"] = old + "-x"
    prior["pass"] = {e: {i + "-x" if i == old else i for i in s}
                     for e, s in prior["pass"].items()}


# name -> (mutation of (new, prior) fixtures, markers EXACTLY raised)
_MUTANTS = {
    "another sample than the prior's": (_m_other_sample, {"SAMPLE-NOT-FROZEN",
                                                          "HARNESS-DRIFTED"}),
    "another upstream commit": (_m_other_commit, {"WORLDS-DIFFER"}),
    "hybrid_rrf never ran": (_m_system_missing, {"SYSTEM-MISSING"}),
    "bm25 not run again": (_m_no_control, {"HARNESS-DRIFTED"}),
    "bm25 drifts from the prior": (_m_drift, {"HARNESS-DRIFTED"}),
    "stretch arm silently dropped": (_m_stretch_silent, {"STRETCH-ARM-SILENT"}),
    "stretch arm dropped with no reason": (_m_stretch_shrug,
                                           {"STRETCH-ARM-SILENT"}),
    "prior not named": (_m_uncited, {"PRIOR-NOT-CITED"}),
    "prior misquoted": (_m_misquoted, {"PRIOR-MISQUOTED"}),
    "an overall figure as a key": (_m_overall_key, {"FAMILIES-BLENDED"}),
    "an overall figure in the finding": (_m_overall_told, {"FAMILIES-BLENDED"}),
    "inherited: declared after the run": (_m_late, {"DECLARED-AFTER-RESULTS"}),
    "inherited: caveat invented": (_m_caveat, {"CAVEAT-NOT-FROM-CARD"}),
    "inherited: upstream score imported": (_m_import, {"SCORE-IMPORTED"}),
    "inherited: file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _selftest(s7_gate: Path) -> int:
    try:
        g = _gate(s7_gate)
        g._fixture, g._write
    except Exception as e:
        print(f"[S7-GATE-UNREADABLE] {s7_gate}: {type(e).__name__}: {e}")
        print("S11-2 gate findings: 1")
        return 1
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []

    def case(name, mutate, want, gate=s7_gate):
        new, prior = _new(g), g._fixture()
        if mutate:
            mutate(new, prior)
        with tempfile.TemporaryDirectory() as td:
            root, p_root, card = _build(Path(td), g, new, prior)
            r = subprocess.run([sys.executable, __file__, str(root), "--prior",
                                str(p_root), "--s7-gate", str(gate), "--card",
                                str(card)], capture_output=True, text=True,
                               timeout=300)
        out = r.stdout + r.stderr
        got = set(marker.findall(out))
        if "Traceback (most recent call last)" in out:
            bad.append(f"{name}: traceback")
        elif want is None and (r.returncode != 0 or got):
            bad.append(f"{name}: should be ACCEPTED, got exit {r.returncode} "
                       f"{sorted(got)}")
        elif want is not None and (r.returncode != 1 or got != want
                                   or "S11-2 gate findings: " not in out):
            bad.append(f"{name}: wrong rejection, got exit {r.returncode} "
                       f"{sorted(got)}")

    case("conforming, stretch arm not run with its reason", None, None)

    def ran(new, prior):
        del new["verdict"]["not_run"]
        new["decl"]["engines"]["claude_mem_chroma_lsa"] = {
            "experiment_class": "raw_product"}
        new["order"].append("claude_mem_chroma_lsa")
        new["pass"]["claude_mem_chroma_lsa"] = set()
    case("conforming, stretch arm ran", ran, None)
    for name, (mutate, want) in _MUTANTS.items():
        case(name, mutate, want)
    case("S7-4 gate missing", None, {"S7-GATE-UNREADABLE"},
         gate=Path("/nonexistent/check.py"))

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (2 conforming replays accepted; a missing S7-4 gate "
          f"and {len(_MUTANTS)} mutants each rejected by exactly their own "
          f"markers - another sample, a drifted bm25, a system that never ran, "
          f"a silent stretch arm and an overall figure among them, with four "
          f"inherited S7-4 checks shown live; no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S11-2")
    ap.add_argument("root", nargs="?", default=str(HERE))
    ap.add_argument("--prior", default=str(PRIOR))
    ap.add_argument("--s7-gate", default=str(PRIOR / "check.py"))
    ap.add_argument("--card", default=None)
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest(Path(a.s7_gate))
    card = Path(a.card) if a.card else HERE.parent / "EXTERNAL-KNOWLEDGEDRIFT-20260916.md"
    return run(Path(a.root), Path(a.prior), Path(a.s7_gate), card)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S11-2 gate findings: 1")
        raise SystemExit(1)
