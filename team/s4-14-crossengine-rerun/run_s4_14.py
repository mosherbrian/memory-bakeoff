#!/usr/bin/env python3
"""S4-14 cross-engine re-run on the corrected reader paths (Brian ruling
2026-09-16: S4-12's zeros suggest misconfiguration; iteration 1 shook these
out already).

Sole deltas vs the S4-12 protocol (team/s4-12-crossengine/run_crossengine.py,
reused here by import for make_record/query_case/run_scenario_topics/constants
so the harness, trigger pin, corpus gate, RECORD_TS and TOP_K are
byte-identical):

  - pi-lcm: the TOOL-LEVEL path (pi_lcm_store_reader_toollevel, iteration-1's
    arm name) instead of the raw store reader. relaxed_variants is the
    verbatim port from extensions/pi-project-recall/index.ts:115-133
    (progressive trailing-term drop keeping >= 2 terms, then single tokens
    last-first, MAX_RELAXATION_ATTEMPTS = 6) as validated by
    implementer/repo/scripts/experiment_20260913_p2_entry/run_p2_entry.py
    (tool_level_retrieve + relaxed_variants, dynamic Hit@3 0.2227 vs raw 0.0).
    DECLARED ADAPTATION: the extension's relaxation gate
    (index.ts:347-363, `bounds.conversations > 1` + liveOnly) has no
    counterpart on the invocation store - the store holds exactly the one
    prior-session record per scenario and the live prompt is never in the
    store, so the live-echo failure mode cannot occur and "reaches prior
    sessions" reduces to "any hit". The gate therefore ports as: exact AND
    query first; if empty, try relaxed variants and take the first with any
    hits; if all fail, the exact (empty) result stands unmarked.
  - claude-mem: the vendor's ACTUAL current search policy arm
    (claude_mem_chroma_lsa: top-100 semantic candidates via shared-LSA,
    default 90-day recency) and its window-disabled ablation
    (claude_mem_chroma_lsa_no_recency) - the pairing iteration 1 measured at
    core Hit@5 0.208 vs 0.958 (ASSAY-SECOND-DRIVER-CLAUDE-MEM-WINDOW.md).
    S4-12's claude_mem_fts5_core arm scored the whole prompt as ONE quoted
    phrase - a strict surface the vendor does not ship as its search path
    (external.py:564: claude-mem "refuses raw"; its search policy is the
    chroma one). Both chroma classes run unchanged from
    memory_bakeoff.providers.claude_mem_core @ 53199f688574c9e5b037c9231d87e
    560b21a6103d956ddc22036ef523c8d594a.

Zero-finding rule (row term): if a system still scores zero, the derivation
log + summary must demonstrate whether ANY non-empty retrieval occurred
through the harness; exact-vs-relaxed counts are recorded per arm.

Usage: run_s4_14.py --arm NAME --out DIR [--scenarios T001,T002] [--tag det]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEAM = os.path.dirname(HERE)
S412 = os.path.join(TEAM, "s4-12-crossengine")
V3 = os.path.join(TEAM, "invocation-corpus-v3-standard")
REPO = os.path.join(TEAM, "..", "implementer", "repo")
sys.path.insert(0, S412)
sys.path.insert(0, V3)
sys.path.insert(0, os.path.join(REPO, "src"))

import run_standard  # frozen v3 harness (metrics/load_stopwords/PI/MODEL/...)
from run_crossengine import (  # S4-12 runner, reused verbatim
    CORPUS, FROZEN_CORPUS_SHA, RECORD_TS, TOP_K,
    make_record, query_case, run_scenario_topics, time_done,
)

from memory_bakeoff.models import QueryCase
from memory_bakeoff.providers.pi_lcm_store_reader import PiLcmStoreReaderProvider
from memory_bakeoff.providers.claude_mem_core import (
    ClaudeMemChromaLSAProvider,
    ClaudeMemChromaLSANoRecencyProvider,
)

MAX_RELAXATION_ATTEMPTS = 6  # verbatim from extensions/pi-project-recall


def relaxed_variants(query: str) -> list:
    """Verbatim port of extensions/pi-project-recall/index.ts:121-133
    relaxedVariants (same port iteration 1 validated)."""
    tokens = [t for t in query.split() if t]
    variants = []
    for keep in range(len(tokens) - 1, 1, -1):
        if len(variants) >= MAX_RELAXATION_ATTEMPTS:
            break
        variants.append(" ".join(tokens[:keep]))
    for i in range(len(tokens) - 1, -1, -1):
        if len(variants) >= MAX_RELAXATION_ATTEMPTS:
            break
        variants.append(tokens[i])
    return variants


class PiLcmToolLevelProvider:
    """pi_lcm_store_reader_toollevel: the raw store reader wrapped in the
    tool's exact-then-bounded-relaxation query behavior (declared adaptation
    above). Everything else (store schema, queries, ordering) is the
    unchanged PiLcmStoreReaderProvider @ e2f87f92... ."""

    name = "pi_lcm_store_reader_toollevel"

    def __init__(self):
        self.inner = PiLcmStoreReaderProvider()

    def probe(self):
        p = self.inner.probe()
        from memory_bakeoff.models import ProviderProbe
        return ProviderProbe(self.name, p.available,
                             p.reason + " + tool-level relaxation (verbatim "
                             "relaxedVariants port, max 6 attempts)", p.capabilities)

    def reset(self):
        self.inner.reset()

    def close(self):
        self.inner.close()

    def ingest(self, records, mode="raw"):
        self.inner.ingest(records, mode=mode)

    def retrieve(self, case: QueryCase, top_k: int = 5):
        exact = self.inner.retrieve(case, top_k=top_k)
        if exact.items:
            exact.raw["tool_level"] = {"exact_nonempty": True, "relaxed_with": None,
                                       "attempts": 0}
            return exact
        attempts = 0
        for variant in relaxed_variants(case.query):
            attempts += 1
            r = self.inner.retrieve(
                QueryCase(id=case.id, category=case.category, query=variant,
                          relevant_ids=(), prohibited_ids=()),
                top_k=top_k)
            if r.items:
                r.raw["tool_level"] = {"exact_nonempty": False, "relaxed_with": variant,
                                       "attempts": attempts}
                return r
        exact.raw["tool_level"] = {"exact_nonempty": False, "relaxed_with": None,
                                   "attempts": attempts}
        return exact


ARMS = {
    # name -> (factory, experiment_class, pin string)
    "pi_lcm_store_reader_toollevel": (
        PiLcmToolLevelProvider, "controlled_core",
        "pi-project-recall ported store queries (in-tree) + VERBATIM tool-level "
        "relaxation (relaxedVariants, index.ts:121-133 @ sha256 9025eef540b6bbbb); "
        "same port validated by experiment_20260913_p2_entry/run_p2_entry.py "
        "(dynamic Hit@3 0.2227 tool-level vs 0.0 raw); adapter "
        "pi_lcm_store_reader.py sha256 e2f87f92b5651aee6ad77764ffbd1533ba9d07300899c6977bc23a01b431d42e"),
    "claude_mem_chroma_lsa": (
        ClaudeMemChromaLSAProvider, "controlled_core",
        "claude-mem @fa6a1e9ec12d23f98326a9b26e243acb0819e105 chroma search policy "
        "(top-100 semantic, DEFAULT 90-day recency) with shared-LSA vectors; "
        "iteration-1 pairing arm (core Hit@5 0.208 with window); adapter "
        "claude_mem_core.py sha256 53199f688574c9e5b037c9231d87e560b21a6103d956ddc22036ef523c8d594a"),
    "claude_mem_chroma_lsa_no_recency": (
        ClaudeMemChromaLSANoRecencyProvider, "controlled_core",
        "claude-mem @fa6a1e9ec12d23f98326a9b26e243acb0819e105 chroma search policy, "
        "implicit 90-day recency DISABLED (row-mandated arm; iteration-1 pairing "
        "measured core Hit@5 0.958 window-off); adapter claude_mem_core.py sha256 "
        "53199f688574c9e5b037c9231d87e560b21a6103d956ddc22036ef523c8d594a"),
}

TRIGGER_PIN = ("pi-change-trigger @db31ea3e0138083bfd136233131f575f0640e9b5 "
               "index.ts sha256 ec6d87948a48b44b536e714abc05b78968657d5abf20154d7a6059014fbbdd01")


def derive_topics_s14(engine, scen):
    """Identical query protocol to run_crossengine.derive_topics (engine
    retrieved texts -> trigger topics, top_k=2), plus per-turn tool-level
    bookkeeping for the zero-demonstration rule."""
    seen, recs, turns_ev = {}, [], []
    stats = {"turns": 0, "nonempty": 0, "exact_nonempty": 0, "relaxed": 0}
    for turn in scen["turns"]:
        res = engine.retrieve(query_case(scen, turn), top_k=TOP_K)
        stats["turns"] += 1
        tl = res.raw.get("tool_level") if isinstance(res.raw, dict) else None
        if res.items:
            stats["nonempty"] += 1
            if tl:
                stats["exact_nonempty"] += 1 if tl.get("exact_nonempty") else 0
                stats["relaxed"] += 0 if tl.get("exact_nonempty") else 1
        items = [{"record_id": it.record_id, "text": it.text} for it in res.items]
        for it in res.items:
            if it.text not in seen:
                seen[it.text] = True
                recs.append({"summary": it.text})
        turns_ev.append({"turn": turn["turn"], "type": turn["type"],
                         "query": turn["text"], "retrieved": items,
                         "tool_level": tl})
    return recs, turns_ev, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--scenarios", default=None, help="comma list; default all 60")
    ap.add_argument("--tag", default="", help="run tag (e.g. det for determinism spot-check)")
    args = ap.parse_args()

    import hashlib
    sha = hashlib.sha256(open(CORPUS, "rb").read()).hexdigest()
    if sha != FROZEN_CORPUS_SHA:
        sys.exit(f"FATAL: corpus sha {sha} != frozen {FROZEN_CORPUS_SHA}; aborting")

    factory, exp_class, pin = ARMS[args.arm]
    engine = factory()
    probe = engine.probe()
    if not probe.available:
        sys.exit(f"FATAL: arm {args.arm} probe unavailable: {probe.reason}")

    scenarios = [json.loads(l) for l in open(CORPUS) if l.strip()]
    if args.scenarios:
        want = set(args.scenarios.split(","))
        scenarios = [s for s in scenarios if s["scenario_id"] in want]

    outdir = os.path.abspath(args.out)
    os.makedirs(outdir, exist_ok=True)
    deriv_path = os.path.join(outdir, "topics-derivation.jsonl")
    stop = run_standard.load_stopwords()

    results, failures = [], []
    agg = {"turns": 0, "nonempty": 0, "exact_nonempty": 0, "relaxed": 0}
    for sc in scenarios:
        sid = sc["scenario_id"]
        workdir = os.path.join(outdir, sid)
        os.makedirs(workdir, exist_ok=True)
        recs = []
        try:
            engine.ingest([make_record(sc)], mode="raw")
            recs, turns_ev, stats = derive_topics_s14(engine, sc)
            for k in agg:
                agg[k] += stats[k]
            with open(deriv_path, "a") as f:
                f.write(json.dumps({"scenario": sid, "turns": turns_ev,
                                    "n_topic_entries": len(recs)}, sort_keys=True) + "\n")
            adir, topics, firelog = run_standard.make_agent_dir(workdir, "system")
            lines = run_scenario_topics(sc, adir, topics, firelog, recs)
            for turn, line in zip(sc["turns"], lines):
                results.append((sid, turn["type"], line))
        except Exception as e:
            failures.append(f"{sid}: {e}")
        finally:
            if hasattr(engine, "close"):
                engine.close()
        print(f"[{sid}] {len(recs) if recs else 0} topics, {time_done():.0f}s", flush=True)

    summary = run_standard.metrics(scenarios, results, stop)
    with open(os.path.join(outdir, "results.jsonl"), "w") as f:
        for sid, ttype, line in results:
            f.write(json.dumps({"scenario": sid, "turn_type": ttype, **line}) + "\n")
    out = {
        "row": "S4-14", "arm": args.arm, "tag": args.tag,
        "experiment_class": exp_class, "engine_pin": pin,
        "corpus": "invocation-corpus-v3-standard/corpus.jsonl",
        "corpus_sha256": sha, "trigger_pin": TRIGGER_PIN,
        "harness": ("run_standard.py rev e84bd58e via run_crossengine.py reuse "
                    "(run_scenario_topics copied with sole delta: topics source); "
                    "sole S4-14 deltas: pi-lcm tool-level relaxation (declared "
                    "adaptation: single-prior-session store -> exact-empty gate), "
                    "claude-mem chroma policy arms"),
        "model": run_standard.MODEL, "top_k": TOP_K,
        "record_timestamp": RECORD_TS.isoformat(),
        "derivation_surface": agg,
        "n_scenarios": len(scenarios), "n_turns": len(results),
        "failures": failures,
        "metrics": {k: {"num": v[0], "den": v[1]} for k, v in summary.items()},
    }
    with open(os.path.join(outdir, "summary.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(json.dumps({"arm": args.arm, "tag": args.tag, "metrics": out["metrics"],
                      "derivation_surface": agg, "failures": failures}, indent=1))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
