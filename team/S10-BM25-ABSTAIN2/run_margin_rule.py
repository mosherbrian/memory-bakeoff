#!/usr/bin/env python3
"""S11-1 runner: bm25 abstention under a declared score-margin rule
(queue row S11-1, kiln-flash 2026-09-18).

Emits the interface the verified S11-1 gate (check.py, authored from the row
text alone) declares: declaration.json (pre-run), results.jsonl (control arm
`bm25-nofilter` first, then `bm25-margin`), verdict.json (both sides, the
grid, both priors, and the verdict the declared rule gives).

The mechanism is NOT a token filter: the margin arm scores the same tokens
the control scores, and abstains when the top score's clearance over the
case store's score distribution — z = (max - mean) / pstdev, 0 when all
equal — falls under the threshold fixed in declaration.json before any run.
The corpus is S6-SELECTIVITY's frozen bytes, read in place and pinned by
sha256; the control must reproduce S6's bm25 retrieval case for case or the
run dies before the mechanism arm scores anything.

$0, local, no LLM, no score import.
"""
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = Path("/var/home/bmosher/memory-bake-off/team")
REPO = Path("/var/home/bmosher/memory-bake-off/implementer/repo")
S6 = TEAM / "S6-SELECTIVITY"
S7 = TEAM / "S7-BM25-PREFILTER"
for p in (str(REPO / "src"), str(TEAM / "s4-14-crossengine"),
          str(TEAM / "s4-12-crossengine")):
    if p not in sys.path:
        sys.path.insert(0, p)

# This seat's shell runs HOME-isolated; the providers package imports numpy
# (via the dense module) at __init__, so the user site is added explicitly.
USER_SITE = "/var/home/bmosher/.local/lib/python3.14/site-packages"
if USER_SITE not in sys.path:
    sys.path.append(USER_SITE)

from memory_bakeoff.models import MemoryRecord, QueryCase  # noqa: E402
from memory_bakeoff.providers.bm25 import BM25Provider, tokenize  # noqa: E402
from run_crossengine import RECORD_TS  # noqa: E402  (the S4-12/S4-14 fixed stamp)

# ---- pins (the same revisions the S7-1 row recorded; verified live) ----
BM25_PY_SHA = "259b15dcc7fc8397aa45884190d9b5afdbba2f82094267889218da892a124f9b"
CORPUS_SHA = "5a8668f73383ea1acc4806a31df9240cc0eb9186a7be69385a8f23e8be2024be"
MANIFEST_SHA = "d2d189128088f6b938e3c53e583026525446bf27ee6c098bc4526a099ab49561"

THRESHOLD = 1.0
GRID = [0.5, 1.0, 1.5]
RULE = {"works_if_abstain_correct_at_least": 1, "and_retrievals_lost_at_most": 0}

GATE = HERE / "check.py"
S7_GATE = S7 / "check.py"


def load_gate(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem + "_imp", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def die(msg: str) -> None:
    print(f"FATAL: {msg}", flush=True)
    raise SystemExit(1)


def records_for(case):
    return [MemoryRecord(id=r["id"], text=r["text"], timestamp=RECORD_TS,
                         session_id=f"sess-{case['case_id']}") for r in case["store"]]


def query_for(case):
    return QueryCase(id=case["case_id"], category=case["expect"],
                     query=case["query"], relevant_ids=(), prohibited_ids=())


def main() -> int:
    # ---- pins verified live, before anything runs ----
    if sha(REPO / "src" / "memory_bakeoff" / "providers" / "bm25.py") != BM25_PY_SHA:
        die("bm25.py is not the pinned revision")
    if sha(S6 / "corpus.jsonl") != CORPUS_SHA:
        die("S6 corpus.jsonl does not match its pinned sha")
    if sha(S6 / "manifest.json") != MANIFEST_SHA:
        die("S6 manifest.json does not match its pinned sha")

    g11 = load_gate(GATE)      # the verified S11-1 gate: zscore + sides
    g7 = load_gate(S7_GATE)    # the verified S7-1 gate: corpus + scoring
    cases, helpful, s6_got = g7._prior(S6)
    corpus = g7._load(S6 / "corpus.jsonl", lines=True)
    by_id = {c["case_id"]: c for c in corpus}
    if set(cases) != set(by_id):
        die("corpus and re-derived case set disagree")

    # ---- declaration first: byte-final before ANY retrieval ----
    # (wording constraint, enforced by the gate: a pre-run declaration says
    # nothing about outcomes and names no token list)
    declaration = {
        "declared_at": now(),
        "mechanism": "score-margin",
        "margin": "zscore-top-vs-case-scores",
        "threshold": THRESHOLD,
        "threshold_grid": GRID,
        "corpus_sha256": sha(S6 / "corpus.jsonl"),
        "manifest_sha256": sha(S6 / "manifest.json"),
        "rule": dict(RULE),
        "preregistration": (
            "the margin is the top score's clearance over the case store's "
            "score distribution: z = (max - mean) / pstdev, 0 when all equal. "
            "With four-record stores the z range tops at sqrt(3) = 1.732 (one "
            "record dominating three equal lows), so the primary threshold "
            "1.0 — the top score one population-SD clear of the store mean — "
            "is fixed before any run, with 0.5 and 1.5 declared as "
            "sensitivity data, never a menu. The rule demands BOTH sides: at "
            "least one irrelevant query rejected AND no useful retrieval "
            "lost; the refuted token-filter row (S7-BM25-PREFILTER) rejected "
            "nothing and lost a retrieval, so a second mechanism must do "
            "better on both sides or it is honestly refuted too. The "
            "mechanism arm scores the same tokens the control scores — no "
            "query or document token is touched — so the only question is "
            "whether the shape of the score distribution separates the "
            "no-subject cases from the real ones"),
    }
    (HERE / "declaration.json").write_text(json.dumps(declaration, indent=1) + "\n")
    dsha = sha(HERE / "declaration.json")
    print(f"declaration written at {declaration['declared_at']} sha {dsha[:12]}...")

    # ---- control arm first: the pinned bm25, tokens untouched ----
    rows, control_ids = [], {}
    for c in corpus:
        cid = c["case_id"]
        eng = BM25Provider()
        eng.ingest(records_for(c))
        res = eng.retrieve(query_for(c), top_k=1)
        got = [it.record_id for it in res.items]
        eng.close()
        control_ids[cid] = got
        rows.append({"ts": now(), "arm": "bm25-nofilter", "case_id": cid,
                     "retrieved_ids": got, "query_tokens": tokenize(c["query"]),
                     "declaration_sha256": dsha})
    drift = sorted(c for c in cases if set(control_ids[c]) != set(s6_got[c]))
    if drift:
        die(f"control differs from S6's bm25 retrieval on {', '.join(drift)}: "
            f"the harness has moved; nothing further runs")
    print(f"control reproduces S6's bm25 retrieval on all {len(cases)} cases")

    # ---- margin arm: same tokens, whole-store scores, declared rule ----
    scores_by_case = {}
    for c in corpus:
        cid = c["case_id"]
        eng = BM25Provider()
        eng.ingest(records_for(c))
        res = eng.retrieve(query_for(c), top_k=len(c["store"]))
        eng.close()
        store_ids = {r["id"] for r in c["store"]}
        got_ids = {it.record_id: it.score for it in res.items
                   if it.record_id in store_ids}
        scores = {r["id"]: float(got_ids.get(r["id"], 0.0)) for r in c["store"]}
        z = g11.zscore(scores)
        abstained = z < THRESHOLD
        scores_by_case[cid] = scores
        rows.append({"ts": now(), "arm": "bm25-margin", "case_id": cid,
                     "retrieved_ids": [] if abstained else list(control_ids[cid]),
                     "query_tokens": tokenize(c["query"]),
                     "declaration_sha256": dsha, "scores": scores,
                     "abstained": abstained})
        print(f"  {cid}: z={z:.3f} -> {'abstain' if abstained else 'retrieve'}")

    (HERE / "results.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows))

    # ---- verdict: both priors as the gate recomputes them, both sides ----
    s7_got = {r["case_id"]: list(r["retrieved_ids"])
              for r in g7._load(S7 / "results.jsonl", lines=True)
              if r.get("arm") == "bm25-prefilter"}
    was = {"s6": g7._score(cases, helpful, s6_got),
           "prefilter": g7._score(cases, helpful, s7_got)}
    rerun = g11.sides(cases, helpful, control_ids, scores_by_case, THRESHOLD)
    grid = [dict(threshold=t,
                 **g11.sides(cases, helpful, control_ids, scores_by_case, t))
            for t in GRID]
    works = (rerun["abstain_correct"] >= RULE["works_if_abstain_correct_at_least"]
             and rerun["retrievals_lost"] <= RULE["and_retrievals_lost_at_most"])
    verdict = {
        "verdict": "mechanism-works" if works else "mechanism-fails",
        "finding": (
            f"at the declared threshold {THRESHOLD} the margin rule rejects "
            f"{rerun['abstain_correct']} of the 5 irrelevant queries and loses "
            f"{rerun['retrievals_lost']} useful retrievals; both sides are "
            f"reported because rejections alone hide what was lost. The grid "
            f"is data: " + "; ".join(
                f"z-threshold {t} rejects {e['abstain_correct']}, loses "
                f"{e['retrievals_lost']}" for t, e in zip(GRID, grid)) +
            f". The verdict is the declared rule's output (at least "
            f"{RULE['works_if_abstain_correct_at_least']} rejection and at "
            f"most {RULE['and_retrievals_lost_at_most']} lost), not a "
            f"judgement call"),
        "headline_threshold": THRESHOLD,
        "prior": {
            "s6": {"source": "team/S6-SELECTIVITY/results.jsonl",
                   "retrieve_correct": was["s6"]["retrieve_correct"],
                   "abstain_correct": was["s6"]["abstain_correct"]},
            "prefilter": {"source": "team/S7-BM25-PREFILTER/verdict.json",
                          "retrieve_correct": was["prefilter"]["retrieve_correct"],
                          "abstain_correct": was["prefilter"]["abstain_correct"]},
        },
        "rerun": {"abstain_correct": rerun["abstain_correct"],
                  "retrievals_lost": rerun["retrievals_lost"]},
        "grid": grid,
    }
    (HERE / "verdict.json").write_text(json.dumps(verdict, indent=1) + "\n")
    for e in grid:
        print(f"grid {e['threshold']}: abstain_correct "
              f"{e['abstain_correct']}, retrievals_lost {e['retrievals_lost']}")
    print(f"verdict: {verdict['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
