#!/usr/bin/env python3
"""Gate for QUEUE row S10-2 (rank-aware retrieval diagnostics: surface MRR,
add nDCG, alongside presence, each its own number).

plumb-fable, row S10-2G, 2026-09-18. Written FROM ROW S10-2's TEXT ALONE, while
`team/S9-RANK-DIAG/` did not exist. Read for this gate: the board row and the
prior it names, implementer/repo/src/memory_bakeoff/metrics.py (how reciprocal
rank and MRR are defined today). The interface below is declared by the gate,
not fitted to a document; every finding names what it wants.

This gate is an INSTRUMENT in three places. The row says the build SURFACES
the repo's reciprocal rank and does not re-derive it, so the gate computes MRR
and presence by calling the real metrics.score_case, not a copy. It recomputes
nDCG by the one definition fixed below. And it DRIVES the build's tool: it
runs diag.py on the artifact's own rankings and on a gate-written probe where
the top two records are swapped - the case the row cites - and checks that
presence stays put while MRR and nDCG move.

Declared interface (ROOT = team/S9-RANK-DIAG)
  rankings.jsonl  one row per adapter, condition and case: {adapter,
                  condition, case_id, category ("negative" or any other),
                  relevant_ids: [ids], ranked_ids: [ids, best first]}
  diag.py         the reporting-path tool. `python3 diag.py RANKINGS --k K`
                  prints {"per_adapter": {adapter: {condition: {mrr, ndcg,
                  presence}}}}. It imports memory_bakeoff.metrics (the gate
                  runs it with the repo source on PYTHONPATH). No LLM, no
                  network.
  report.json     {k, ndcg_definition: "binary-gain-log2", prior (names
                  metrics.py and an earlier report that carried MRR),
                  per_adapter: as diag.py prints it}

The numbers, fixed here so they can be recomputed (positives only, as
metrics.aggregate does: cases whose category is not "negative")
  mrr       mean of metrics.score_case(...).reciprocal_rank
  presence  mean of metrics.score_case(...).hit_at_k
  ndcg      binary gain, DCG@k = sum 1/log2(rank+1) over relevant ids in the
            top k, each id counted once; divided by the ideal DCG for
            min(|relevant|, k) hits

What the row turns on (marker in brackets)
  (a) SURFACED, not re-derived. diag.py imports memory_bakeoff.metrics
      [METRICS-REDERIVED]; it runs [DIAG-BROKEN]; report.json is what diag.py
      prints for rankings.jsonl [DIAG-DISAGREES]; no LLM or network
      [LLM-OR-NETWORK].
  (b) RANK-SENSITIVE. On the gate's swap probe diag.py gives equal presence
      and lower MRR and nDCG for the swapped arm, to the recomputed values
      [DIAG-BLIND-TO-RANK]. A tool that reports presence under another name
      fails here.
  (c) EXTENDED with nDCG, under the declared definition [NDCG-UNDECLARED].
  (d) ITS OWN NUMBER, never blended. Every cell carries mrr, ndcg and presence
      [NUMBER-MISSING], nothing that blends them [BLENDED-SCORE], and each
      equals the recomputation [NUMBERS-DISAGREE].
  (e) Enough to read: at least one adapter and five positive cases per cell
      [TOO-FEW-CASES]; one row per adapter, condition and case
      [RANKING-DUPLICATED]; the prior cited, as the re-measurement rule asks
      [PRIOR-NOT-CITED].
  other  [MISSING-FILE] [BAD-JSON] [SCHEMA] [METRICS-UNREADABLE]

Limits, stated on purpose: ranked_ids are what the build wrote down; the gate
cannot see the adapters rank. It checks that a reporting tool exists and is
rank-sensitive, not that a given sprint report calls it. That stays with the
named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S10-2 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT] [--repo-src DIR]
  python3 check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parent
REPO_SRC = HERE.parent.parent / "implementer" / "repo" / "src"
FILES = ("rankings.jsonl", "diag.py", "report.json")
NUMBERS = ("mrr", "ndcg", "presence")
NDCG = "binary-gain-log2"
PRIORS = ("RESEARCH-Q1.2-ISOLATION-RESULT", "COLDREAD-20260912-scoreboard")
MIN_POSITIVES = 5
BLEND = re.compile(r"score|overall|blend|combin|composite|total|index|grade",
                   re.I)
USES_METRICS = re.compile(r"^\s*(from\s+memory_bakeoff(\.metrics)?\s+import|"
                          r"import\s+memory_bakeoff)", re.M)
NETWORK = re.compile(r"^\s*(import|from)\s+(anthropic|openai|requests|httpx|"
                     r"aiohttp|socket|urllib|http)\b|api_key|/v1/(chat|messages)",
                     re.I | re.M)


def _load(path: Path, lines: bool = False):
    text = path.read_text(encoding="utf-8", errors="replace")
    if lines:
        return [json.loads(l) for l in text.splitlines() if l.strip()]
    return json.loads(text)


def _metrics(repo_src: Path):
    sys.path.insert(0, str(repo_src))
    from memory_bakeoff.metrics import score_case
    from memory_bakeoff.models import QueryCase, RetrievalItem, RetrievalResult
    return score_case, QueryCase, RetrievalItem, RetrievalResult


def _ndcg(relevant: set, ranked: list, k: int) -> float:
    seen, dcg = set(), 0.0
    for rank, rid in enumerate(ranked[:k], 1):
        if rid in relevant and rid not in seen:
            seen.add(rid)
            dcg += 1 / math.log2(rank + 1)
    ideal = sum(1 / math.log2(r + 1) for r in range(1, min(len(relevant), k) + 1))
    return dcg / ideal if ideal else 0.0


def recompute(m, rows: list, k: int) -> dict:
    score_case, QueryCase, RetrievalItem, RetrievalResult = m
    cells: dict = {}
    for r in rows:
        if r["category"] == "negative":
            continue
        got = score_case(
            QueryCase(r["case_id"], r["category"], "", tuple(r["relevant_ids"])),
            RetrievalResult([RetrievalItem(i, "") for i in r["ranked_ids"]], 0.0),
            k)
        cells.setdefault(r["adapter"], {}).setdefault(r["condition"], []).append(
            (got.reciprocal_rank, _ndcg(set(r["relevant_ids"]), r["ranked_ids"], k),
             got.hit_at_k))
    return {a: {c: dict(zip(NUMBERS, (mean(col) for col in zip(*v))), n=len(v))
                for c, v in conds.items()} for a, conds in cells.items()}


def _cell_ok(cell) -> bool:
    return isinstance(cell, dict) and all(
        isinstance(cell.get(n), (int, float)) and not isinstance(cell.get(n), bool)
        for n in NUMBERS)


def _differs(said, real: dict) -> list[str]:
    """Cells of `said` that are absent or not the recomputed numbers."""
    out = []
    said = said if isinstance(said, dict) else {}
    for a in sorted(set(said) | set(real)):
        conds = said.get(a) if isinstance(said.get(a), dict) else {}
        for c in sorted(set(conds) | set(real.get(a, {}))):
            cell, want = conds.get(c), real.get(a, {}).get(c)
            if want is None or not _cell_ok(cell) or any(
                    abs(cell[n] - want[n]) >= 0.0006 for n in NUMBERS):
                out.append(f"{a}/{c}")
    return out


def _run_diag(diag: Path, rankings: Path, k: int, repo_src: Path):
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(
        [str(repo_src), os.environ.get("PYTHONPATH", "")]).rstrip(os.pathsep))
    try:
        p = subprocess.run([sys.executable, str(diag), str(rankings), "--k",
                            str(k)], capture_output=True, text=True, timeout=120,
                           env=env)
        return json.loads(p.stdout)["per_adapter"] if p.returncode == 0 else None
    except Exception:
        return None


_PROBE = [{"adapter": arm, "condition": "probe", "case_id": f"p{i}",
           "category": "exact", "relevant_ids": [f"r{i}"],
           "ranked_ids": [f"r{i}", f"x{i}", f"y{i}"] if arm == "in-order"
           else [f"x{i}", f"r{i}", f"y{i}"]}
          for arm in ("in-order", "top-two-swapped") for i in range(5)]


def check(root: Path, repo_src: Path) -> tuple[list[tuple[str, str]], str]:
    try:
        m = _metrics(repo_src)
    except Exception as e:
        return [("METRICS-UNREADABLE", f"{repo_src}: {type(e).__name__}: {e}")], ""
    missing = [n for n in FILES if not (root / n).is_file()]
    if missing:
        return [("MISSING-FILE", f"{root}/{n}") for n in missing], ""
    try:
        rows = _load(root / "rankings.jsonl", lines=True)
        report = _load(root / "report.json")
    except ValueError as e:
        return [("BAD-JSON", str(e))], ""
    f: list[tuple[str, str]] = []
    if not (isinstance(rows, list) and rows and all(
            isinstance(r, dict) and all(isinstance(r.get(x), str) and r[x]
                                        for x in ("adapter", "condition",
                                                  "case_id", "category"))
            and all(isinstance(r.get(x), list) and all(isinstance(i, str)
                                                       for i in r[x])
                    for x in ("relevant_ids", "ranked_ids")) for r in rows)):
        f.append(("SCHEMA", "rankings.jsonl needs {adapter, condition, case_id, "
                  "category, relevant_ids: [ids], ranked_ids: [ids]} per line"))
    k = report.get("k") if isinstance(report, dict) else None
    if not (isinstance(k, int) and not isinstance(k, bool) and k >= 1):
        f.append(("SCHEMA", "report.json needs k: a whole number >= 1, and "
                  "per_adapter"))
    if f:
        return f, ""

    # (c) (e) declared, cited, enough to read
    if report.get("ndcg_definition") != NDCG:
        f.append(("NDCG-UNDECLARED", f"report.json needs ndcg_definition: "
                  f"\"{NDCG}\", the definition this gate recomputes"))
    prior = json.dumps(report.get("prior", ""))
    if "metrics.py" not in prior or not any(p in prior for p in PRIORS):
        f.append(("PRIOR-NOT-CITED", f"report.json prior must name metrics.py "
                  f"and an earlier report that carried MRR "
                  f"({' or '.join(PRIORS)})"))
    dup = [k_ for k_, n in Counter((r["adapter"], r["condition"], r["case_id"])
                                   for r in rows).items() if n > 1]
    if dup:
        f.append(("RANKING-DUPLICATED", f"{len(dup)} adapter/condition/case "
                  f"combinations appear twice, e.g. {'/'.join(dup[0])}"))
    real = recompute(m, rows, k)
    thin = sorted(f"{a}/{c}" for a, conds in real.items()
                  for c, cell in conds.items() if cell["n"] < MIN_POSITIVES)
    if not real or thin:
        f.append(("TOO-FEW-CASES", f"each adapter and condition needs at least "
                  f"{MIN_POSITIVES} positive cases"
                  + (f"; short: {', '.join(thin)}" if thin else "")))

    # (d) its own number, never blended, as recomputed
    said = report.get("per_adapter")
    cells = [(f"{a}/{c}", cell) for a, conds in (said or {}).items()
             if isinstance(conds, dict) for c, cell in conds.items()] \
        if isinstance(said, dict) else []
    lacking = sorted(n for n, cell in cells if not _cell_ok(cell))
    if not cells or lacking:
        f.append(("NUMBER-MISSING", f"every cell needs {', '.join(NUMBERS)}, "
                  f"each its own number"
                  + (f"; incomplete: {', '.join(lacking)}" if lacking else "")))
    blended = sorted({f"{n}.{key}" for n, cell in cells if isinstance(cell, dict)
                      for key in cell if BLEND.search(str(key))}
                     | {str(key) for key in report if BLEND.search(str(key))})
    if blended:
        f.append(("BLENDED-SCORE", f"{', '.join(blended)} - rank measures are "
                  f"reported beside presence, never folded into a score"))
    wrong = [n for n in _differs(said, real) if n not in lacking]
    if wrong:
        f.append(("NUMBERS-DISAGREE", f"report.json differs from the "
                  f"recomputation (MRR and presence by metrics.score_case) on: "
                  f"{', '.join(wrong[:6])}"))

    # (a) (b) the tool, driven
    code = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                     for p in sorted(root.glob("*.py")) if p.name != "check.py")
    if not USES_METRICS.search((root / "diag.py").read_text(
            encoding="utf-8", errors="replace")):
        f.append(("METRICS-REDERIVED", "diag.py does not import "
                  "memory_bakeoff.metrics; the row surfaces the repo's "
                  "reciprocal rank, it does not re-derive it"))
    hit = NETWORK.search(code)
    if hit:
        f.append(("LLM-OR-NETWORK", f"build code reaches for a model or the "
                  f"network ({hit.group(0).strip()!r})"))
    out = _run_diag(root / "diag.py", root / "rankings.jsonl", k, repo_src)
    if out is None:
        f.append(("DIAG-BROKEN", "`python3 diag.py rankings.jsonl --k K` did "
                  "not exit 0 with {\"per_adapter\": ...} on stdout"))
        return f, ""
    if _differs(said, {a: {c: out[a][c] for c in out[a] if _cell_ok(out[a][c])}
                       for a in out if isinstance(out[a], dict)}) or \
            _differs(out, {a: {c: v for c, v in conds.items()}
                           for a, conds in (said or {}).items()
                           if isinstance(conds, dict)
                           and all(_cell_ok(v) for v in conds.values())}):
        f.append(("DIAG-DISAGREES", "report.json is not what diag.py prints "
                  "for rankings.jsonl; the report must come from the tool"))
    with tempfile.TemporaryDirectory() as td:
        probe = Path(td) / "probe.jsonl"
        probe.write_text("".join(json.dumps(r) + "\n" for r in _PROBE))
        got = _run_diag(root / "diag.py", probe, 3, repo_src)
    if got is None or _differs(got, recompute(m, _PROBE, 3)):
        f.append(("DIAG-BLIND-TO-RANK", "on the gate's probe (same records, "
                  "top two swapped) diag.py must give presence 1.0 for both "
                  "arms, MRR 1.0 against 0.5 and nDCG 1.0 against 0.631"))
    return f, (f"{len(real)} adapters, {sum(len(c) for c in real.values())} "
               f"cells; MRR and presence by metrics.score_case, nDCG "
               f"recomputed; diag.py driven and rank-sensitive")


def run(root: Path, repo_src: Path) -> int:
    findings, summary = check(root, repo_src)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S10-2 gate findings: {len(findings)}")
        return 1
    print(f"S10-2 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_DIAG = '''import argparse, json, math
from statistics import mean
from memory_bakeoff.metrics import score_case
from memory_bakeoff.models import QueryCase, RetrievalItem, RetrievalResult

ap = argparse.ArgumentParser()
ap.add_argument("rankings")
ap.add_argument("--k", type=int, default=5)
a = ap.parse_args()


def ndcg(relevant, ranked, k):
    seen, dcg = set(), 0.0
    for rank, rid in enumerate(ranked[:k], 1):
        if rid in relevant and rid not in seen:
            seen.add(rid)
            dcg += 1 / math.log2(rank + 1)
    ideal = sum(1 / math.log2(r + 1) for r in range(1, min(len(relevant), k) + 1))
    return dcg / ideal if ideal else 0.0


cells = {}
for line in open(a.rankings):
    if not line.strip():
        continue
    r = json.loads(line)
    if r["category"] == "negative":
        continue
    got = score_case(QueryCase(r["case_id"], r["category"], "",
                               tuple(r["relevant_ids"])),
                     RetrievalResult([RetrievalItem(i, "") for i in
                                      r["ranked_ids"]], 0.0), a.k)
    cells.setdefault(r["adapter"], {}).setdefault(r["condition"], []).append(
        (RANK_MEASURE, ndcg(set(r["relevant_ids"]), r["ranked_ids"], a.k),
         got.hit_at_k))
print(json.dumps({"per_adapter": {ad: {c: dict(zip(("mrr", "ndcg", "presence"),
      (mean(col) for col in zip(*v)))) for c, v in conds.items()}
      for ad, conds in cells.items()}}))
'''
_GOOD_DIAG = _DIAG.replace("RANK_MEASURE", "got.reciprocal_rank")
_BLIND_DIAG = _DIAG.replace("RANK_MEASURE", "got.hit_at_k").replace(
    "ndcg(set(r[\"relevant_ids\"]), r[\"ranked_ids\"], a.k)", "got.hit_at_k")
_REDERIVED = _GOOD_DIAG.replace(
    "from memory_bakeoff.metrics import score_case",
    "import importlib\nscore_case = importlib.import_module("
    "'memory_bakeoff' + '.metrics').score_case")


def _fixture() -> dict:
    rows = []
    for adapter in ("bm25", "claude_mem"):
        for cond in ("normal", "pressure"):
            for i in range(5):
                ranked = [f"r{i}", f"x{i}", f"y{i}"]
                if adapter == "claude_mem" and cond == "pressure" and i == 4:
                    ranked = [f"x{i}", f"r{i}", f"y{i}"]  # the row's swap
                rows.append({"adapter": adapter, "condition": cond,
                             "case_id": f"sel-{i:03d}", "category": "exact",
                             "relevant_ids": [f"r{i}"], "ranked_ids": ranked})
            rows.append({"adapter": adapter, "condition": cond,
                         "case_id": "sel-neg", "category": "negative",
                         "relevant_ids": [], "ranked_ids": []})
    return {"rows": rows, "diag": _GOOD_DIAG, "extra_py": {}, "raw": {},
            "patch": None,
            "report": {"k": 3, "ndcg_definition": NDCG,
                       "prior": "implementer/repo/src/memory_bakeoff/metrics.py "
                                "computes reciprocal rank and MRR; reported in "
                                "team/RESEARCH-Q1.2-ISOLATION-RESULT",
                       "per_adapter": "AUTO"}}


def _write(td: Path, fx: dict, m) -> Path:
    root = td / "S9-RANK-DIAG"
    root.mkdir()
    (root / "rankings.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in fx["rows"]))
    (root / "diag.py").write_text(fx["diag"])
    report = fx["report"]
    if report.get("per_adapter") == "AUTO":
        real = recompute(m, fx["rows"], report["k"])
        report["per_adapter"] = {a: {c: {n: cell[n] for n in NUMBERS}
                                     for c, cell in conds.items()}
                                 for a, conds in real.items()}
    if fx["patch"]:
        fx["patch"](report)
    (root / "report.json").write_text(json.dumps(report))
    for name, text in {**fx["extra_py"], **fx["raw"]}.items():
        if text is None:
            (root / name).unlink()
        else:
            (root / name).write_text(text)
    return root


def _m_blind(fx):  # presence under another name: the row's whole complaint
    fx["diag"] = _BLIND_DIAG
    fx["patch"] = lambda rep: [cell.update(mrr=cell["presence"],
                                           ndcg=cell["presence"])
                               for conds in rep["per_adapter"].values()
                               for cell in conds.values()]


def _m_rederived(fx): fx["diag"] = _REDERIVED
def _m_crash(fx): fx["diag"] = "raise RuntimeError('boom')\n"
def _m_llm(fx): fx["extra_py"]["judge.py"] = "import openai\n"
def _m_hand_edited(fx): fx["patch"] = lambda rep: rep["per_adapter"]["bm25"][
    "normal"].update(mrr=0.9)
def _m_no_ndcg(fx): fx["patch"] = lambda rep: [
    cell.pop("ndcg") for conds in rep["per_adapter"].values()
    for cell in conds.values()]
def _m_blended(fx): fx["patch"] = lambda rep: rep["per_adapter"]["bm25"][
    "normal"].update(retrieval_score=0.95)
def _m_undeclared(fx): fx["report"]["ndcg_definition"] = "standard"
def _m_prior(fx): fx["report"]["prior"] = "a new measure"
def _m_half_prior(fx): fx["report"]["prior"] = "metrics.py computes it"
def _m_few(fx): fx["rows"] = [r for r in fx["rows"]
                              if r["case_id"] in ("sel-000", "sel-001", "sel-neg")]
def _m_dup(fx): fx["rows"].append(dict(fx["rows"][0]))
def _m_badjson(fx): fx["raw"]["report.json"] = "{not json"
def _m_hostile(fx): fx["raw"]["rankings.jsonl"] = "[1, 2]\n\"x\"\nnull\n"
def _m_nofile(fx): fx["raw"]["diag.py"] = None
def _m_receipts(fx): fx["raw"] = {"rankings.jsonl": "{}\n", "report.json": "{}\n",
                                  "diag.py": "\n"}


# name -> (mutation, markers that must be EXACTLY the ones raised)
_MUTANTS = {
    "diag reports presence as MRR and nDCG": (_m_blind, {"NUMBERS-DISAGREE",
                                                        "DIAG-BLIND-TO-RANK"}),
    "metrics.py not imported": (_m_rederived, {"METRICS-REDERIVED"}),
    "diag crashes": (_m_crash, {"METRICS-REDERIVED", "DIAG-BROKEN"}),
    "a model judge beside the tool": (_m_llm, {"LLM-OR-NETWORK"}),
    "report edited by hand": (_m_hand_edited, {"NUMBERS-DISAGREE",
                                               "DIAG-DISAGREES"}),
    "nDCG absent": (_m_no_ndcg, {"NUMBER-MISSING", "DIAG-DISAGREES"}),
    "a blended score in a cell": (_m_blended, {"BLENDED-SCORE"}),
    "nDCG definition not declared": (_m_undeclared, {"NDCG-UNDECLARED"}),
    "no prior cited": (_m_prior, {"PRIOR-NOT-CITED"}),
    "prior names metrics.py only": (_m_half_prior, {"PRIOR-NOT-CITED"}),
    "two positive cases": (_m_few, {"TOO-FEW-CASES"}),
    "a ranking twice": (_m_dup, {"RANKING-DUPLICATED"}),
    "broken json": (_m_badjson, {"BAD-JSON"}),
    "hostile rankings": (_m_hostile, {"SCHEMA"}),
    "file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _selftest(repo_src: Path) -> int:
    try:
        m = _metrics(repo_src)
    except Exception as e:
        print(f"[METRICS-UNREADABLE] {repo_src}: {type(e).__name__}: {e}")
        print("S10-2 gate findings: 1")
        return 1
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []

    def case(name, fx, want, src=repo_src):
        with tempfile.TemporaryDirectory() as td:
            r = subprocess.run([sys.executable, __file__,
                                str(_write(Path(td), fx, m)), "--repo-src",
                                str(src)], capture_output=True, text=True,
                               timeout=300)
        out = r.stdout + r.stderr
        got = set(marker.findall(out))
        ok = want(got) if callable(want) else got == want
        if "Traceback (most recent call last)" in out:
            bad.append(f"{name}: traceback")
        elif want is None and (r.returncode != 0 or got):
            bad.append(f"{name}: should be ACCEPTED, got exit {r.returncode} "
                       f"{sorted(got)}")
        elif want is not None and (r.returncode != 1 or not ok
                                   or "S10-2 gate findings: " not in out):
            bad.append(f"{name}: wrong rejection, got exit {r.returncode} "
                       f"{sorted(got)}")

    case("conforming", _fixture(), None)
    receipts = _fixture()
    _m_receipts(receipts)
    case("receipts only: all files present, no substance", receipts,
         lambda got: bool(got) and "MISSING-FILE" not in got)
    for name, (mutate, want) in _MUTANTS.items():
        fx = _fixture()
        mutate(fx)
        case(name, fx, want)
    case("metrics.py unreachable", _fixture(), {"METRICS-UNREADABLE"},
         src=Path("/nonexistent/src"))
    # the row's own example, on the gate's own arithmetic
    cells = recompute(m, _fixture()["rows"], 3)["claude_mem"]
    if not (cells["normal"]["presence"] == cells["pressure"]["presence"] == 1.0
            and cells["pressure"]["mrr"] < cells["normal"]["mrr"]
            and cells["pressure"]["ndcg"] < cells["normal"]["ndcg"]):
        bad.append(f"recompute: a top-two swap must move MRR and nDCG and "
                   f"leave presence, got {cells}")

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (the conforming build accepted; a receipts-only "
          f"directory, an unreachable metrics.py and {len(_MUTANTS)} mutants "
          f"each rejected by exactly their own markers - a tool that reports "
          f"presence as MRR among them; the swap moves MRR and nDCG and "
          f"leaves presence; no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S10-2")
    ap.add_argument("root", nargs="?", default=str(HERE))
    ap.add_argument("--repo-src", default=str(REPO_SRC))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest(Path(a.repo_src))
    return run(Path(a.root), Path(a.repo_src))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S10-2 gate findings: 1")
        raise SystemExit(1)
