#!/usr/bin/env python3
"""S6-2 selectivity diagnostic runner (queue row S6-2, kiln-flash 2026-09-17).

Enforces the row's chain of custody in code:
  corpus.jsonl (frozen on disk) -> manifest.json (declared_at BEFORE any run,
  pins corpus sha256) -> CONTROL rows first (return-nothing, return-everything,
  bm25, oracle) -> frozen decision rule (gap > separation_margin, else STOP
  with no engine rows) -> engine rows only on continue, each carrying its
  adaptation labels.

Arm semantics are the ones pre-declared in design.md. $0, local, no LLM,
no score import.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = HERE.parent
REPO = (TEAM / ".." / "implementer" / "repo").resolve()
for p in (str(TEAM / "s4-14-crossengine-rerun"), str(TEAM / "s4-12-crossengine"),
          str(REPO / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from run_crossengine import RECORD_TS  # the S4-12/S4-14 fixed stamp, reused verbatim
from run_s4_14 import PiLcmToolLevelProvider  # noqa: E402 (module-level path setup)
from memory_bakeoff.models import MemoryRecord, QueryCase
from memory_bakeoff.providers.bm25 import BM25Provider
from memory_bakeoff.providers.claude_mem_core import ClaudeMemChromaLSANoRecencyProvider

MARGIN = 0.25          # pre-declared in design.md; mirrored in the manifest
TRUNCATION = None      # null: "everything" = the whole 4-record store
ENGINE_TOPK = {"pi_lcm_toollevel_sel": 5, "claude_mem_chroma_lsa_no_recency_sel": 3}
ENGINE_ADAPTATIONS = {
    "pi_lcm_toollevel_sel": [
        "store: 4 records per case instead of 1",
        "single-session relaxation gate port (S4-14 declared adaptation)",
        "record ts fixed 2026-09-01T00:00Z, uniform age, no time behaviour in scope",
    ],
    "claude_mem_chroma_lsa_no_recency_sel": [
        "store: 4 records per case instead of 1",
        "top-3 semantic neighbours - vendor policy has no abstention threshold",
        "90-day window disabled (S4-14 row-mandated primary)",
        "record ts fixed 2026-09-01T00:00Z, window behaviour out of scope per S6-1 note",
    ],
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f1(helpful: set, got: set) -> float:
    if not helpful:
        return 0.0 if got else 1.0
    tp = len(helpful & got)
    return 2 * tp / (len(helpful) + len(got)) if tp else 0.0


def records_for(case):
    return [MemoryRecord(id=r["id"], text=r["text"], timestamp=RECORD_TS,
                         session_id=f"sess-{case['case_id']}") for r in case["store"]]


def query_for(case):
    return QueryCase(id=case["case_id"], category=case["expect"], query=case["query"],
                     relevant_ids=(), prohibited_ids=())


def ids_from(result, text_to_id):
    out = []
    for it in result.items:
        rid = it.record_id if getattr(it, "record_id", None) else text_to_id.get(it.text)
        out.append(rid if rid else it.text)
    return out


def main() -> int:
    cases = [json.loads(l) for l in (HERE / "corpus.jsonl").read_text().splitlines() if l.strip()]

    # ---- manifest first: the declaration exists before ANY run ----
    corpus_sha = sha(HERE / "corpus.jsonl")
    declared_at = now()
    helpful = {"sel-001": ["sel-001-r2"], "sel-002": ["sel-002-r1"],
               "sel-003": ["sel-003-r2"], "sel-004": ["sel-004-r3"],
               "sel-005": ["sel-005-r2"], "sel-006": [], "sel-007": [],
               "sel-008": [], "sel-009": [], "sel-010": []}
    manifest = {"declared_at": declared_at, "corpus_sha256": corpus_sha,
                "truncation": TRUNCATION, "separation_margin": MARGIN,
                "helpful": helpful,
                "declares": "which records should help per case, written before any run"}
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    msha = sha(HERE / "manifest.json")
    print(f"manifest declared at {declared_at} sha {msha[:12]}...")

    rows = []

    def add(arm, case, ids, adaptations=None):
        row = {"ts": now(), "arm": arm, "case_id": case["case_id"],
               "retrieved_ids": ids, "manifest_sha256": msha}
        if adaptations is not None:
            row["adaptations"] = adaptations
        rows.append(row)

    text_to_id = {c["case_id"]: {r["text"]: r["id"] for r in c["store"]} for c in cases}

    # ---- controls first, in the declared arm order, each covering every case ----
    for c in cases:                                    # return-nothing
        add("return-nothing", c, [])
    for c in cases:                                    # return-everything
        add("return-everything", c, [r["id"] for r in c["store"]])
    bm25_scores = {}
    eng = BM25Provider()
    for c in cases:                                    # bm25: top-1 iff score > 0
        eng.ingest(records_for(c))
        res = eng.retrieve(query_for(c), top_k=1)
        got = [it.record_id for it in res.items]
        add("bm25", c, got)
        bm25_scores[c["case_id"]] = got
    for c in cases:                                    # oracle: exactly the helpful set
        add("oracle", c, list(helpful[c["case_id"]]))

    score = {}
    for arm in ("bm25", "return-everything"):
        got_by_case = {r["case_id"]: set(r["retrieved_ids"])
                       for r in rows if r["arm"] == arm}
        score[arm] = sum(f1(set(helpful[k]), got_by_case[k]) for k in helpful) / len(helpful)
    gap = score["bm25"] - score["return-everything"]
    detail = (f"bm25 {score['bm25']:.3f} vs return-everything "
              f"{score['return-everything']:.3f}, gap {gap:.3f}, margin {MARGIN}")
    print(detail)

    decision = {"rule": "continue iff mean-setF1(bm25) - mean-setF1(return-everything) "
                        "> separation_margin (design.md, declared before the runs)",
                "bm25_mean_setf1": round(score["bm25"], 4),
                "return_everything_mean_setf1": round(score["return-everything"], 4),
                "gap": round(gap, 4), "separation_margin": MARGIN}

    if gap > MARGIN:
        decision["verdict"] = "continue"
        decision["finding"] = (f"controls separate selective retrieval from the firehose "
                               f"({detail}); engines run after the controls")
        # ---- engines, after every control row, adaptations labelled ----
        engine = PiLcmToolLevelProvider()
        for c in cases:
            engine.reset()
            engine.ingest(records_for(c))
            res = engine.retrieve(query_for(c), top_k=ENGINE_TOPK["pi_lcm_toollevel_sel"])
            add("pi_lcm_toollevel_sel", c, ids_from(res, text_to_id[c["case_id"]]),
                ENGINE_ADAPTATIONS["pi_lcm_toollevel_sel"])
        engine.close()

        engine = ClaudeMemChromaLSANoRecencyProvider()
        for c in cases:
            engine.ingest(records_for(c))
            res = engine.retrieve(query_for(c),
                                  top_k=ENGINE_TOPK["claude_mem_chroma_lsa_no_recency_sel"])
            add("claude_mem_chroma_lsa_no_recency_sel", c,
                ids_from(res, text_to_id[c["case_id"]]),
                ENGINE_ADAPTATIONS["claude_mem_chroma_lsa_no_recency_sel"])
        engine.close()
    else:
        decision["verdict"] = "stop"
        decision["finding"] = (f"return-everything is indistinguishable from selective "
                               f"retrieval under the frozen rule ({detail}); the "
                               f"instrument cannot separate a firehose, so no engine ran")

    (HERE / "results.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows))
    (HERE / "decision.json").write_text(json.dumps(decision, indent=1) + "\n")

    engine_means = {}
    for r in rows:
        if r["arm"] not in score and r["arm"] not in ("return-nothing", "oracle"):
            engine_means.setdefault(r["arm"], []).append(
                f1(set(helpful[r["case_id"]]), set(r["retrieved_ids"])))
    for arm, vals in engine_means.items():
        print(f"{arm}: mean set-F1 {sum(vals) / len(vals):.3f} over {len(vals)} cases")
    print(f"verdict: {decision['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
