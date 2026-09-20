#!/usr/bin/env python3
"""Gate for QUEUE row S11-1 (bm25 abstention, second declared configuration: a
score-margin rule, both sides measured).

plumb-fable, row S11-1G, 2026-09-18. Written FROM ROW S11-1's TEXT ALONE, while
`team/S10-BM25-ABSTAIN2/` did not exist. Read for this gate: the board row and
the two priors it names (team/S6-SELECTIVITY, team/S7-BM25-PREFILTER), through
this seat's own S7-1 gate. The interface below is declared by the gate, not
fitted to a document; every finding names what it wants.

The row reuses the S7-1 harness, and so does this gate: corpus loading and the
scoring of a case are IMPORTED from team/S7-BM25-PREFILTER/check.py, so the
prior cells and the new ones come from one definition.

This gate is an INSTRUMENT. Every mechanism row carries the bm25 scores over
the case's store. From those the gate recomputes the margin, the abstention
decision at the declared threshold, both sides of the result, and the whole
sensitivity grid. Nothing in verdict.json is taken on trust.

Declared interface (ROOT = team/S10-BM25-ABSTAIN2)
  declaration.json  {declared_at (ISO), mechanism: "score-margin",
                    margin: "zscore-top-vs-case-scores", threshold,
                    threshold_grid: [at least 3 values, threshold among them],
                    corpus_sha256, manifest_sha256 (the S6-SELECTIVITY files),
                    rule: {works_if_abstain_correct_at_least: N >= 1,
                           and_retrievals_lost_at_most: M >= 0}}
                    No stopword list. No mention of results.
  results.jsonl     IN RUN ORDER: {ts, arm, case_id, retrieved_ids,
                    query_tokens, declaration_sha256}. Arm `bm25-nofilter`
                    (control) then `bm25-margin`, whose rows add
                    scores: {record id: bm25 score, for the whole store} and
                    abstained: bool.
  verdict.json      {verdict: "mechanism-works" | "mechanism-fails", finding,
                    headline_threshold,
                    prior: {s6: {source, retrieve_correct, abstain_correct},
                            prefilter: {source, retrieve_correct,
                                        abstain_correct}},
                    rerun: {abstain_correct, retrievals_lost},
                    grid: [{threshold, abstain_correct, retrievals_lost}]}

The rule, fixed here so it can be recomputed
  margin   z = (top score - mean of the store's scores) / their population
           standard deviation; 0 when all scores are equal
  abstain  when z < threshold; then nothing is retrieved. Otherwise the
           control's retrieval stands.
  abstain_correct   abstain cases with nothing retrieved
  retrievals_lost   retrieve cases the control gets right and the mechanism
                    does not

What the row turns on (marker in brackets)
  (a) A DIFFERENT MECHANISM, not a token filter. mechanism and margin are the
      declared ones [MECHANISM-UNDECLARED]; no stopword list, and the
      mechanism arm scores the same tokens as the control
      [TOKEN-FILTER-AGAIN].
  (b) THRESHOLD FIXED BEFORE ANY RUN. Threshold and grid declared
      [THRESHOLD-UNDECLARED]; declared_at precedes every row
      [DECLARED-AFTER-RESULTS]; the declaration says nothing of results
      [DECLARATION-REFERENCES-RESULTS]; every row embeds its sha256
      [RESULTS-NOT-BOUND]; the headline is the DECLARED threshold and nothing
      is called best, optimal or tuned [THRESHOLD-PICKED-POST-RUN].
  (c) THE RULE REALLY RAN. Scores cover the whole store [SCORES-INCOMPLETE]
      and agree with the control's top hit [SCORES-INCONSISTENT]; each row's
      abstained flag and retrieval are what the rule gives at the declared
      threshold [RULE-NOT-APPLIED].
  (d) BOTH SIDES. rerun carries abstain_correct AND retrievals_lost
      [SIDE-MISSING], as recomputed [NUMBERS-DISAGREE], nothing blended
      [BLENDED-SCORE]; the grid holds every declared threshold
      [GRID-INCOMPLETE] with both sides as recomputed [GRID-DISAGREES].
  (e) SAME CORPUS, control first. Corpus and manifest are S6's bytes
      [CORPUS-NOT-FROZEN]; the control runs first [CONTROL-NOT-FIRST] and
      reproduces S6's bm25 retrieval [CONTROL-NOT-REPRODUCED]; both arms cover
      every case once [ARM-MISSING] [ARM-INCOMPLETE].
  (f) OLD VS NEW. Both priors are named [PRIOR-NOT-CITED] and quoted as the
      gate recomputes them from their own result files [PRIOR-MISQUOTED].
  (g) The verdict the declared rule gives [RULE-UNDECLARED]
      [VERDICT-CONTRADICTS-RULE] [VERDICT-INVALID] [VERDICT-NO-FINDING].
      `mechanism-fails` is a PASS: a second honest refutation is a result.
  other  [MISSING-FILE] [BAD-JSON] [SCHEMA] [PRIOR-UNREADABLE]
         [S7-GATE-UNREADABLE]

Limits, stated on purpose: scores are what the harness wrote down; the gate
checks them against the control's top hit, not against bm25 itself. With four
records in a store a z-score cannot pass 1.73, so the grid is narrow by
construction; whether this margin is a GOOD abstention signal stays with the
named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S11-1 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT] [--s6 DIR] [--s7 DIR] [--s7-gate FILE]
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
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, pstdev

HERE = Path(__file__).resolve().parent
FILES = ("declaration.json", "results.jsonl", "verdict.json")
CONTROL, MARGIN = "bm25-nofilter", "bm25-margin"
MECHANISM, MARGIN_DEF = "score-margin", "zscore-top-vs-case-scores"
VERDICTS = ("mechanism-works", "mechanism-fails")
SIDES = ("abstain_correct", "retrievals_lost")
BLEND = re.compile(r"score|overall|blend|combin|composite|index|grade", re.I)
PICKED = re.compile(r"\b(best|optimal|optimum|tuned|chosen|selected)\b", re.I)


def _gate(path: Path):
    spec = importlib.util.spec_from_file_location("_s7_1_gate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def zscore(scores: dict) -> float:
    vals = list(scores.values())
    sd = pstdev(vals) if len(vals) > 1 else 0.0
    return (max(vals) - mean(vals)) / sd if sd else 0.0


def sides(cases: dict, helpful: dict, control: dict, scores: dict, t: float) -> dict:
    """Both sides of the rule at threshold t, from the scores alone."""
    got = {c: [] if zscore(scores[c]) < t else control[c] for c in cases}
    right = lambda ids, c: helpful[c] <= set(ids)  # noqa: E731
    return {"abstain_correct": sum(1 for c, v in cases.items()
                                   if v["expect"] == "abstain" and not got[c]),
            "retrievals_lost": sum(1 for c, v in cases.items()
                                   if v["expect"] == "retrieve"
                                   and right(control[c], c)
                                   and not right(got[c], c))}


def _schema(g, decl, rows, verdict) -> list[tuple[str, str]]:
    f: list[tuple[str, str]] = []
    if not isinstance(decl, dict):
        return [("SCHEMA", "declaration.json must be an object")]
    if g._ts(decl.get("declared_at")) is None:
        f.append(("SCHEMA", "declaration.json needs declared_at (ISO time)"))
    if decl.get("mechanism") != MECHANISM or decl.get("margin") != MARGIN_DEF:
        f.append(("MECHANISM-UNDECLARED", f"declaration.json needs mechanism: "
                  f"\"{MECHANISM}\" and margin: \"{MARGIN_DEF}\", the rule this "
                  f"gate recomputes"))
    grid = decl.get("threshold_grid")
    if not (_num(decl.get("threshold")) and isinstance(grid, list)
            and len(grid) >= 3 and all(_num(t) for t in grid)
            and len(set(grid)) == len(grid) and decl["threshold"] in grid):
        f.append(("THRESHOLD-UNDECLARED", "declaration.json needs threshold (a "
                  "number) and threshold_grid: at least 3 distinct numbers "
                  "with the threshold among them, fixed before any run"))
    for k in ("corpus_sha256", "manifest_sha256"):
        if not isinstance(decl.get(k), str):
            f.append(("SCHEMA", f"declaration.json needs {k}"))
    rule = decl.get("rule") if isinstance(decl.get("rule"), dict) else {}
    if not (_int(rule.get("works_if_abstain_correct_at_least"))
            and rule["works_if_abstain_correct_at_least"] >= 1
            and _int(rule.get("and_retrievals_lost_at_most"))
            and rule["and_retrievals_lost_at_most"] >= 0):
        f.append(("RULE-UNDECLARED", "declaration.json needs rule: "
                  "{works_if_abstain_correct_at_least: N >= 1, "
                  "and_retrievals_lost_at_most: M >= 0}, fixed before the run"))
    if not isinstance(rows, list) or not rows or not all(
            isinstance(r, dict) and g._ts(r.get("ts"))
            and isinstance(r.get("arm"), str) and isinstance(r.get("case_id"), str)
            and g._strs(r.get("retrieved_ids")) and g._strs(r.get("query_tokens"))
            and isinstance(r.get("declaration_sha256"), str)
            and (r["arm"] != MARGIN or (
                isinstance(r.get("abstained"), bool)
                and isinstance(r.get("scores"), dict) and r["scores"]
                and all(_num(v) for v in r["scores"].values())))
            for r in rows):
        f.append(("SCHEMA", f"results.jsonl rows need ts, arm, case_id, "
                  f"retrieved_ids, query_tokens, declaration_sha256; `{MARGIN}` "
                  f"rows add scores: {{record id: number}} and abstained: bool"))
    if not isinstance(verdict, dict):
        return f + [("SCHEMA", "verdict.json must be an object")]
    if verdict.get("verdict") not in VERDICTS:
        f.append(("VERDICT-INVALID", f"verdict.json verdict must be one of "
                  f"{' / '.join(VERDICTS)}"))
    if not isinstance(verdict.get("finding"), str) \
            or len(verdict["finding"].strip()) < 20:
        f.append(("VERDICT-NO-FINDING", "verdict.json needs finding: a sentence"))
    prior = verdict.get("prior")
    if not (isinstance(prior, dict) and all(
            isinstance(prior.get(k), dict)
            and _int(prior[k].get("retrieve_correct"))
            and _int(prior[k].get("abstain_correct")) for k in ("s6", "prefilter"))):
        f.append(("SCHEMA", "verdict.json needs prior: {s6, prefilter}, each "
                  "{source, retrieve_correct, abstain_correct}"))
    if not isinstance(verdict.get("rerun"), dict) or not isinstance(
            verdict.get("grid"), list):
        f.append(("SCHEMA", "verdict.json needs rerun: {...} and grid: [...]"))
    return f


def check(root: Path, s6: Path, s7: Path, s7_gate: Path) -> tuple[list, str]:
    try:
        g = _gate(s7_gate)
        g._prior, g._score, g._sha, g._ts, g._load, g._strs
    except Exception as e:
        return [("S7-GATE-UNREADABLE", f"{s7_gate}: {type(e).__name__}: {e}")], ""
    try:
        cases, helpful, s6_got = g._prior(s6)
        s7_got = {r["case_id"]: list(r["retrieved_ids"])
                  for r in g._load(s7 / "results.jsonl", lines=True)
                  if r.get("arm") == "bm25-prefilter"}
        if set(s7_got) != set(cases):
            raise ValueError("no complete bm25-prefilter arm")
        was = {"s6": g._score(cases, helpful, s6_got),
               "prefilter": g._score(cases, helpful, s7_got)}
    except Exception as e:
        return [("PRIOR-UNREADABLE", f"{s6} / {s7}: {type(e).__name__}: {e}")], ""
    missing = [n for n in FILES if not (root / n).is_file()]
    if missing:
        return [("MISSING-FILE", f"{root}/{n}") for n in missing], ""
    try:
        decl = g._load(root / "declaration.json")
        rows = g._load(root / "results.jsonl", lines=True)
        verdict = g._load(root / "verdict.json")
    except ValueError as e:
        return [("BAD-JSON", str(e))], ""
    f = _schema(g, decl, rows, verdict)
    if f:
        return f, ""

    # (a) (b) a different mechanism, declared before any run
    decl_text = (root / "declaration.json").read_text(encoding="utf-8",
                                                      errors="replace")
    if re.search(r"result", decl_text, re.I):
        f.append(("DECLARATION-REFERENCES-RESULTS", "declaration.json mentions "
                  "results; a declaration written before the run has nothing "
                  "to say about them"))
    if re.search(r"stop_?words?", decl_text, re.I):
        f.append(("TOKEN-FILTER-AGAIN", "declaration.json carries a stopword "
                  "list; the token filter is the refuted mechanism"))
    sha = g._sha(root / "declaration.json")
    unbound = sum(1 for r in rows if r["declaration_sha256"] != sha)
    if unbound:
        f.append(("RESULTS-NOT-BOUND", f"{unbound} of {len(rows)} rows do not "
                  f"carry the sha256 of declaration.json as it stands "
                  f"({sha[:12]}): the threshold moved after the run, or the "
                  f"run never read it"))
    first = min(g._ts(r["ts"]) for r in rows)
    if g._ts(decl["declared_at"]) >= first:
        f.append(("DECLARED-AFTER-RESULTS", f"declared_at {decl['declared_at']} "
                  f"is not before the first row {first.isoformat()}"))
    if decl["corpus_sha256"] != g._sha(s6 / "corpus.jsonl") or \
            decl["manifest_sha256"] != g._sha(s6 / "manifest.json"):
        f.append(("CORPUS-NOT-FROZEN", f"corpus_sha256 and manifest_sha256 must "
                  f"be the sha256 of {s6.name}/corpus.jsonl and manifest.json"))

    # (e) both arms, control first and reproducing
    arm: dict[str, dict] = {}
    for name in (CONTROL, MARGIN):
        mine = [r for r in rows if r["arm"] == name]
        if not mine:
            f.append(("ARM-MISSING", f"results.jsonl has no `{name}` rows"))
            continue
        seen = Counter(r["case_id"] for r in mine)
        if set(seen) != set(cases) or max(seen.values()) > 1:
            f.append(("ARM-INCOMPLETE", f"`{name}` must hold each of the "
                      f"{len(cases)} cases exactly once"))
            continue
        arm[name] = {r["case_id"]: r for r in mine}
    if len(arm) < 2:
        return f, ""
    order = [r["arm"] for r in rows]
    if len(order) - 1 - order[::-1].index(CONTROL) > order.index(MARGIN):
        f.append(("CONTROL-NOT-FIRST", f"every `{CONTROL}` row must come before "
                  f"the first `{MARGIN}` row"))
    control = {c: arm[CONTROL][c]["retrieved_ids"] for c in cases}
    drift = sorted(c for c in cases if set(control[c]) != set(s6_got[c]))
    if drift:
        f.append(("CONTROL-NOT-REPRODUCED", f"`{CONTROL}` differs from "
                  f"{s6.name}'s bm25 retrieval on {', '.join(drift)}"))
    filtered = sorted(c for c in cases if arm[MARGIN][c]["query_tokens"]
                      != arm[CONTROL][c]["query_tokens"])
    if filtered:
        f.append(("TOKEN-FILTER-AGAIN", f"`{MARGIN}` scores other tokens than "
                  f"the control on {', '.join(filtered)}; this mechanism may "
                  f"not touch the query"))

    # (c) the rule really ran
    scores = {c: arm[MARGIN][c]["scores"] for c in cases}
    partial = sorted(c for c in cases if set(scores[c]) != cases[c]["store"])
    if partial:
        f.append(("SCORES-INCOMPLETE", f"scores must cover the whole store, no "
                  f"more, no less: {', '.join(partial)}"))
        return f, ""
    odd = sorted(c for c in cases if control[c]
                 and scores[c][control[c][0]] < max(scores[c].values()))
    if odd:
        f.append(("SCORES-INCONSISTENT", f"the control's top hit is not the "
                  f"top score on {', '.join(odd)}"))
    t = decl["threshold"]
    unruly = sorted(c for c in cases if (
        arm[MARGIN][c]["abstained"] != (zscore(scores[c]) < t)
        or set(arm[MARGIN][c]["retrieved_ids"]) != (
            set() if zscore(scores[c]) < t else set(control[c]))))
    if unruly:
        f.append(("RULE-NOT-APPLIED", f"at the declared threshold {t} the rule "
                  f"gives another abstention or retrieval than the row records "
                  f"on {', '.join(unruly)} (z = "
                  f"{', '.join(f'{zscore(scores[c]):.3f}' for c in unruly)})"))

    # (d) both sides, and the grid, as recomputed
    real = sides(cases, helpful, control, scores, t)
    rerun = verdict["rerun"]
    lacking = [s for s in SIDES if not _int(rerun.get(s))]
    if lacking:
        f.append(("SIDE-MISSING", f"verdict.json rerun needs BOTH "
                  f"{' and '.join(SIDES)}; missing: {', '.join(lacking)}. "
                  f"Rejections alone hide what was lost"))
    elif any(rerun[s] != real[s] for s in SIDES):
        f.append(("NUMBERS-DISAGREE", f"verdict.json rerun is not the "
                  f"recomputation at threshold {t}: {real}"))
    blended = sorted(k for k in rerun if BLEND.search(str(k)))
    if blended:
        f.append(("BLENDED-SCORE", f"rerun.{', rerun.'.join(blended)}: report "
                  f"the two sides and nothing that blends them"))
    said = {e.get("threshold"): e for e in verdict["grid"] if isinstance(e, dict)}
    absent = [x for x in decl["threshold_grid"] if x not in said]
    if absent:
        f.append(("GRID-INCOMPLETE", f"verdict.json grid lacks declared "
                  f"thresholds: {absent}"))
    wrong = [x for x in decl["threshold_grid"] if x in said and any(
        said[x].get(s) != sides(cases, helpful, control, scores, x)[s]
        for s in SIDES)]
    if wrong:
        f.append(("GRID-DISAGREES", f"verdict.json grid is not the "
                  f"recomputation at thresholds {wrong}"))
    picked = PICKED.search(verdict["finding"]) or next(
        (k for k in verdict if PICKED.search(str(k).replace("_", " "))), None)
    if verdict.get("headline_threshold") != t or picked:
        f.append(("THRESHOLD-PICKED-POST-RUN", f"headline_threshold must be the "
                  f"declared {t}, and nothing may be called best, optimal, "
                  f"tuned or chosen; the grid is data, not a menu"))

    # (f) old vs new
    sources = {"s6": f"{s6.name}/results.jsonl", "prefilter": f"{s7.name}/verdict.json"}
    for k, src in sources.items():
        p = verdict["prior"][k]
        if src not in str(p.get("source", "")):
            f.append(("PRIOR-NOT-CITED", f"verdict.json prior.{k}.source must "
                      f"name {src}"))
        if (p["retrieve_correct"], p["abstain_correct"]) != (
                was[k]["retrieve_correct"], was[k]["abstain_correct"]):
            f.append(("PRIOR-MISQUOTED", f"verdict.json prior.{k} is not the "
                      f"prior as recomputed: retrieve_correct "
                      f"{was[k]['retrieve_correct']}, abstain_correct "
                      f"{was[k]['abstain_correct']}"))

    # (g) the verdict the rule gives
    rule = decl["rule"]
    works = (real["abstain_correct"] >= rule["works_if_abstain_correct_at_least"]
             and real["retrievals_lost"] <= rule["and_retrievals_lost_at_most"])
    rightful = VERDICTS[0] if works else VERDICTS[1]
    if verdict["verdict"] != rightful:
        f.append(("VERDICT-CONTRADICTS-RULE", f"{real} under the declared rule "
                  f"{rule} gives {rightful}"))
    return f, (f"{rightful} at declared threshold {t}: {real}; grid of "
               f"{len(decl['threshold_grid'])} recomputed; priors s6 "
               f"{was['s6']['retrieve_correct']}/{was['s6']['abstain_correct']}, "
               f"prefilter {was['prefilter']['retrieve_correct']}/"
               f"{was['prefilter']['abstain_correct']} (retrieve/abstain)")


def run(root: Path, s6: Path, s7: Path, s7_gate: Path) -> int:
    findings, summary = check(root, s6, s7, s7_gate)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S11-1 gate findings: {len(findings)}")
        return 1
    print(f"S11-1 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_T0 = datetime(2026, 9, 19, 17, 0, tzinfo=timezone.utc)
# case -> (expect, helpful, s6 bm25 ids, s7 prefilter ids, scores r1..r4)
_Q = {"c1": ("retrieve", ["c1-r1"], ["c1-r1"], ["c1-r1"], [9.0, 1.0, 1.0, 1.0]),
      "c2": ("retrieve", ["c2-r1"], ["c2-r1"], [], [9.0, 1.0, 1.0, 1.0]),
      "c3": ("abstain", [], ["c3-r1"], ["c3-r1"], [2.2, 2.1, 2.0, 1.9]),
      "c4": ("abstain", [], ["c4-r1"], ["c4-r1"], [2.2, 2.1, 2.0, 1.9])}
_GRID = [1.0, 1.6, 1.74]


def _fixture(threshold: float = 1.6) -> dict:
    """z is 1.732 on the retrieve cases and 1.342 on the abstain cases, so 1.6
    separates them, 1.0 abstains on nothing and 1.74 on everything."""
    works = threshold == 1.6
    fx = {
        "decl": {"declared_at": _T0.isoformat(), "mechanism": MECHANISM,
                 "margin": MARGIN_DEF, "threshold": threshold,
                 "threshold_grid": list(_GRID), "corpus_sha256": "AUTO",
                 "manifest_sha256": "AUTO",
                 "rule": {"works_if_abstain_correct_at_least": 1,
                          "and_retrievals_lost_at_most": 0}},
        "rows": [], "raw": {}, "after": None,
        "verdict": {
            "verdict": VERDICTS[0 if works else 1],
            "finding": "the top score stands clear of the store on the retrieve "
                       "cases and not on the abstain cases at the declared "
                       "threshold." if works else
                       "at the declared threshold the margin rule rejects no "
                       "irrelevant query; a second mechanism refuted.",
            "headline_threshold": threshold,
            "prior": {"s6": {"source": "team/S6-SELECTIVITY/results.jsonl",
                             "retrieve_correct": 2, "abstain_correct": 0},
                      "prefilter": {"source": "team/S7-BM25-PREFILTER/verdict.json",
                                    "retrieve_correct": 1, "abstain_correct": 0}},
            "rerun": {"abstain_correct": 2 if works else 0, "retrievals_lost": 0},
            "grid": [{"threshold": 1.0, "abstain_correct": 0, "retrievals_lost": 0},
                     {"threshold": 1.6, "abstain_correct": 2, "retrievals_lost": 0},
                     {"threshold": 1.74, "abstain_correct": 2,
                      "retrievals_lost": 2}]},
    }
    for name in (CONTROL, MARGIN):
        for c, (_, _, got, _, sc) in _Q.items():
            row = {"arm": name, "case_id": c, "query_tokens": ["which", "port"],
                   "retrieved_ids": list(got)}
            if name == MARGIN:
                scores = {f"{c}-r{i + 1}": s for i, s in enumerate(sc)}
                gone = zscore(scores) < threshold
                row.update(scores=scores, abstained=gone,
                           retrieved_ids=[] if gone else list(got))
            fx["rows"].append(row)
    return fx


def _write(td: Path, fx: dict, g) -> tuple[Path, Path, Path]:
    s6, s7 = td / "S6-SELECTIVITY", td / "S7-BM25-PREFILTER"
    root = td / "S10-BM25-ABSTAIN2"
    for d in (s6, s7, root):
        d.mkdir()
    (s6 / "corpus.jsonl").write_text("".join(json.dumps({
        "case_id": c, "query": "which port", "expect": q[0],
        "store": [{"id": f"{c}-r{i}", "text": "x"} for i in (1, 2, 3, 4)]}) + "\n"
        for c, q in _Q.items()))
    (s6 / "manifest.json").write_text(json.dumps(
        {"helpful": {c: q[1] for c, q in _Q.items()}}))
    (s6 / "results.jsonl").write_text("".join(json.dumps(
        {"arm": "bm25", "case_id": c, "retrieved_ids": q[2]}) + "\n"
        for c, q in _Q.items()))
    (s7 / "results.jsonl").write_text("".join(json.dumps(
        {"arm": "bm25-prefilter", "case_id": c, "retrieved_ids": q[3]}) + "\n"
        for c, q in _Q.items()))
    decl = fx["decl"]
    for k, name in (("corpus_sha256", "corpus.jsonl"),
                    ("manifest_sha256", "manifest.json")):
        if decl.get(k) == "AUTO":
            decl[k] = g._sha(s6 / name)
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))
    sha = g._sha(root / "declaration.json")
    out = []
    for i, r in enumerate(fx["rows"], 1):
        r = dict(r)
        r.setdefault("ts", (_T0 + timedelta(seconds=i)).isoformat())
        r.setdefault("declaration_sha256", sha)
        out.append(json.dumps(r) + "\n")
    (root / "results.jsonl").write_text("".join(out))
    (root / "verdict.json").write_text(json.dumps(fx["verdict"]))
    if fx["after"]:
        fx["after"](root, decl)
    for name, text in fx["raw"].items():
        if text is None:
            (root / name).unlink()
        else:
            (root / name).write_text(text)
    return root, s6, s7


def _margin(fx, case):
    return next(r for r in fx["rows"] if r["arm"] == MARGIN and r["case_id"] == case)


def _after_threshold(root, decl):  # the threshold moved once numbers were seen
    decl["threshold"] = 1.74
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))


def _m_late(fx): fx["decl"]["declared_at"] = (_T0 + timedelta(hours=1)).isoformat()
def _m_refs(fx): fx["decl"]["note"] = "threshold read off results.jsonl"
def _m_stopwords(fx): fx["decl"]["stopwords"] = ["what", "the"]
def _m_tokens(fx): _margin(fx, "c3")["query_tokens"] = ["port"]
def _m_mechanism(fx): fx["decl"]["mechanism"] = "token-filter-v2"
def _m_nothreshold(fx): del fx["decl"]["threshold"]
def _m_grid_small(fx): fx["decl"]["threshold_grid"] = [1.6]
def _m_off_grid(fx): fx["decl"]["threshold_grid"] = [1.0, 1.5, 1.74]
def _m_norule(fx): del fx["decl"]["rule"]
def _m_corpus(fx): fx["decl"]["corpus_sha256"] = "0" * 64
def _m_best(fx): fx["verdict"]["best_threshold"] = 1.6
def _m_tuned(fx): fx["verdict"]["finding"] += " 1.6 is the optimal setting."
def _m_partial_scores(fx): _margin(fx, "c1")["scores"].pop("c1-r4")
def _m_odd_scores(fx): _margin(fx, "c1")["scores"].update({"c1-r1": 1.0, "c1-r2": 9.0})
def _m_drift(fx): fx["rows"][2]["retrieved_ids"] = ["c3-r2"]
def _m_order(fx): fx["rows"].reverse()
def _m_noarm(fx): fx["rows"] = [r for r in fx["rows"] if r["arm"] == MARGIN]
def _m_short(fx): fx["rows"].pop()
def _m_one_side(fx): del fx["verdict"]["rerun"]["retrievals_lost"]
def _m_numbers(fx): fx["verdict"]["rerun"]["abstain_correct"] = 1
def _m_blended(fx): fx["verdict"]["rerun"]["abstention_score"] = 0.9
def _m_grid_gap(fx): fx["verdict"]["grid"].pop()
def _m_grid_wrong(fx): fx["verdict"]["grid"][2]["retrievals_lost"] = 0
def _m_prior_uncited(fx): fx["verdict"]["prior"]["prefilter"]["source"] = "sprint 7"
def _m_prior_wrong(fx): fx["verdict"]["prior"]["prefilter"]["retrieve_correct"] = 2
def _m_flip(fx): fx["verdict"]["verdict"] = VERDICTS[1]
def _m_maybe(fx): fx["verdict"]["verdict"] = "promising"
def _m_nofinding(fx): fx["verdict"]["finding"] = ""
def _m_badjson(fx): fx["raw"]["verdict.json"] = "{not json"
def _m_hostile(fx): fx["raw"]["results.jsonl"] = "[1, 2]\n\"x\"\nnull\n"
def _m_nofile(fx): fx["raw"]["declaration.json"] = None
def _m_receipts(fx): fx["raw"] = {n: "{}\n" for n in FILES}


def _m_moved(fx):
    fx["after"] = _after_threshold


def _m_headline_moved(fx):  # the grid used as a menu
    fx["verdict"]["headline_threshold"] = 1.74


def _m_unruly(fx):  # the row says it abstained; the scores say it would not
    _margin(fx, "c1").update(abstained=True, retrieved_ids=[])
    fx["verdict"]["rerun"]["retrievals_lost"] = 1


# name -> (mutation, markers that must be EXACTLY the ones raised)
_MUTANTS = {
    "declared after the run": (_m_late, {"DECLARED-AFTER-RESULTS"}),
    "declaration references results": (_m_refs,
                                       {"DECLARATION-REFERENCES-RESULTS"}),
    "threshold moved after the run": (_m_moved, {"RESULTS-NOT-BOUND",
                                                 "RULE-NOT-APPLIED",
                                                 "NUMBERS-DISAGREE",
                                                 "THRESHOLD-PICKED-POST-RUN",
                                                 "VERDICT-CONTRADICTS-RULE"}),
    "a stopword list again": (_m_stopwords, {"TOKEN-FILTER-AGAIN"}),
    "mechanism arm filters tokens": (_m_tokens, {"TOKEN-FILTER-AGAIN"}),
    "another mechanism named": (_m_mechanism, {"MECHANISM-UNDECLARED"}),
    "no threshold": (_m_nothreshold, {"THRESHOLD-UNDECLARED"}),
    "grid of one": (_m_grid_small, {"THRESHOLD-UNDECLARED"}),
    "threshold not on its grid": (_m_off_grid, {"THRESHOLD-UNDECLARED"}),
    "no verdict rule": (_m_norule, {"RULE-UNDECLARED"}),
    "other corpus": (_m_corpus, {"CORPUS-NOT-FROZEN"}),
    "headline moved to another grid point": (_m_headline_moved,
                                             {"THRESHOLD-PICKED-POST-RUN"}),
    "a best threshold reported": (_m_best, {"THRESHOLD-PICKED-POST-RUN"}),
    "finding calls a setting optimal": (_m_tuned, {"THRESHOLD-PICKED-POST-RUN"}),
    "scores for part of the store": (_m_partial_scores, {"SCORES-INCOMPLETE"}),
    "scores disagree with the control": (_m_odd_scores, {"SCORES-INCONSISTENT"}),
    "row abstains against its scores": (_m_unruly, {"RULE-NOT-APPLIED",
                                                    "NUMBERS-DISAGREE"}),
    "control drifts from S6": (_m_drift, {"CONTROL-NOT-REPRODUCED",
                                          "SCORES-INCONSISTENT"}),
    "control after the mechanism": (_m_order, {"CONTROL-NOT-FIRST"}),
    "no control arm": (_m_noarm, {"ARM-MISSING"}),
    "a case dropped": (_m_short, {"ARM-INCOMPLETE"}),
    "rejections only, losses unreported": (_m_one_side, {"SIDE-MISSING"}),
    "rerun numbers wrong": (_m_numbers, {"NUMBERS-DISAGREE"}),
    "a blended score": (_m_blended, {"BLENDED-SCORE"}),
    "a grid point missing": (_m_grid_gap, {"GRID-INCOMPLETE"}),
    "grid hides the losses": (_m_grid_wrong, {"GRID-DISAGREES"}),
    "prior not named": (_m_prior_uncited, {"PRIOR-NOT-CITED"}),
    "prior misquoted": (_m_prior_wrong, {"PRIOR-MISQUOTED"}),
    "verdict against the rule": (_m_flip, {"VERDICT-CONTRADICTS-RULE"}),
    "verdict not in vocabulary": (_m_maybe, {"VERDICT-INVALID"}),
    "no finding": (_m_nofinding, {"VERDICT-NO-FINDING"}),
    "broken json": (_m_badjson, {"BAD-JSON"}),
    "hostile results": (_m_hostile, {"SCHEMA"}),
    "file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _selftest(s7_gate: Path) -> int:
    try:
        g = _gate(s7_gate)
    except Exception as e:
        print(f"[S7-GATE-UNREADABLE] {s7_gate}: {type(e).__name__}: {e}")
        print("S11-1 gate findings: 1")
        return 1
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []

    def case(name, fx, want, gate=s7_gate):
        with tempfile.TemporaryDirectory() as td:
            root, s6, s7 = _write(Path(td), fx, g)
            r = subprocess.run([sys.executable, __file__, str(root), "--s6",
                                str(s6), "--s7", str(s7), "--s7-gate", str(gate)],
                               capture_output=True, text=True, timeout=120)
        out = r.stdout + r.stderr
        got = set(marker.findall(out))
        ok = want(got) if callable(want) else got == want
        if "Traceback (most recent call last)" in out:
            bad.append(f"{name}: traceback")
        elif want is None and (r.returncode != 0 or got):
            bad.append(f"{name}: should be ACCEPTED, got exit {r.returncode} "
                       f"{sorted(got)}")
        elif want is not None and (r.returncode != 1 or not ok
                                   or "S11-1 gate findings: " not in out):
            bad.append(f"{name}: wrong rejection, got exit {r.returncode} "
                       f"{sorted(got)}")

    case("conforming, mechanism works", _fixture(), None)
    case("conforming, honestly refuted", _fixture(threshold=1.0), None)
    receipts = _fixture()
    _m_receipts(receipts)
    case("receipts only: all files present, no substance", receipts,
         lambda got: len(got) >= 3 and "MISSING-FILE" not in got)
    for name, (mutate, want) in _MUTANTS.items():
        fx = _fixture()
        mutate(fx)
        case(name, fx, want)
    case("S7-1 gate missing", _fixture(), {"S7-GATE-UNREADABLE"},
         gate=Path("/nonexistent/check.py"))
    if abs(zscore({"a": 9.0, "b": 1.0, "c": 1.0, "d": 1.0}) - 3 ** 0.5) > 1e-9 \
            or zscore({"a": 2.0, "b": 2.0}) != 0.0:
        bad.append("zscore: wrong on the two reference stores")

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (2 conforming runs accepted, one an honest "
          f"refutation; a receipts-only directory, a missing S7-1 gate and "
          f"{len(_MUTANTS)} mutants each rejected by exactly their own markers "
          f"- a threshold moved after the run, a headline moved along the "
          f"grid, a token filter again and losses left unreported among them; "
          f"no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S11-1")
    ap.add_argument("root", nargs="?", default=str(HERE))
    ap.add_argument("--s6", default=str(HERE.parent / "S6-SELECTIVITY"))
    ap.add_argument("--s7", default=str(HERE.parent / "S7-BM25-PREFILTER"))
    ap.add_argument("--s7-gate",
                    default=str(HERE.parent / "S7-BM25-PREFILTER" / "check.py"))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest(Path(a.s7_gate))
    return run(Path(a.root), Path(a.s6), Path(a.s7), Path(a.s7_gate))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S11-1 gate findings: 1")
        raise SystemExit(1)
