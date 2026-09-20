#!/usr/bin/env python3
"""S4-12 cross-engine invocation measurement on the frozen corpus v3 standard tier.

Per team/QUEUE.md row S4-12: run the frozen standard tier `controlled_core`
across >=2 locally-runnable engines at $0, deterministic-first, fire-log
programmatic scoring, no score import.

Protocol (per team/RESEARCH-INVOCATION-SURFACE-AUDIT.md implication 3 and
team/DESIGN-INVOCATION-BENCHMARK.md Addendum A):
  - The harness trigger is FIXED: canonical pi-change-trigger, pinned commit
    db31ea3e0138083bfd136233131f575f0640e9b5, index.ts sha256 ec6d8794... .
    It is the only fair cross-system arm (harness_trigger == controlled_core).
  - The ENGINES differ only in the topic set the trigger sees: for each
    scenario the engine ingests the scenario's records (raw mode) and its own
    stored surface is derived by querying the ENGINE with each turn's prompt;
    the retrieved stored-record texts become the trigger's topics file.
    Empty retrieval -> empty topics -> the trigger cannot fire on `topic`:
    an honest zero, never imputed.
  - Scoring is programmatic from the fire log with the S3-1 shipping metric
    definitions (reused verbatim from run_standard.py).
  - fail-closed: the corpus sha256 must equal the frozen S4-10 value or the
    run aborts before spawning anything.

Usage: run_crossengine.py --engine NAME --out DIR [--scenarios T001,T002]
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
TEAM = os.path.dirname(HERE)
V3 = os.path.join(TEAM, "invocation-corpus-v3-standard")
sys.path.insert(0, V3)
sys.path.insert(0, os.path.join(TEAM, "..", "implementer", "repo", "src"))

import run_standard  # frozen v3 harness: metrics(), load_stopwords(), constants

CORPUS = os.path.join(V3, "corpus.jsonl")
FROZEN_CORPUS_SHA = "7395b7d5fc44c92a58599b74b193eabf727bbec5a81b8fac991ee66a15a369c0"
RECORD_TS = datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc)  # fixed; declared in artifact
TOP_K = 2

ENGINES = {
    # name -> (module, class, experiment_class, pin string)
    "claude_mem_fts5_core": (
        "memory_bakeoff.providers.claude_mem_core", "ClaudeMemFTS5CoreProvider",
        "controlled_core",
        "claude-mem @fa6a1e9ec12d23f98326a9b26e243acb0819e105 (Apache-2.0; CLAIMS-LEDGER row 10) "
        "+ adapter sha256 53199f688574c9e5b037c9231d87e560b21a6103d956ddc22036ef523c8d594a"),
    "pi_lcm_store_reader": (
        "memory_bakeoff.providers.pi_lcm_store_reader", "PiLcmStoreReaderProvider",
        "controlled_core",
        "pi-project-recall ported store queries (in-tree) + pi-lcm schema; receipt "
        "docs/PORTFOLIO-P1-ADAPTER-RECEIPTS.md rows 1-2 (12/12); adapter sha256 "
        "e2f87f92b5651aee6ad77764ffbd1533ba9d07300899c6977bc23a01b431d42e"),
    "bm25": (
        "memory_bakeoff.providers.bm25", "BM25Provider",
        "baseline",
        "in-tree BM25 baseline (baseline class, context arm only); adapter "
        "src/memory_bakeoff/providers/bm25.py at canonical repo commit be2bfa9"),
}


def make_record(scen):
    from memory_bakeoff.models import MemoryRecord
    r = scen["records"][0]
    return MemoryRecord(id=r["id"], text=r["content"], timestamp=RECORD_TS,
                        session_id=f"sess-{scen['scenario_id']}")


def query_case(scen, turn):
    from memory_bakeoff.models import QueryCase
    return QueryCase(id=f"{scen['scenario_id']}-t{turn['turn']}",
                     category=turn["type"], query=turn["text"],
                     relevant_ids=(), prohibited_ids=())


def derive_topics(engine, scen):
    """Query the ENGINE with each turn prompt; retrieved stored texts are the
    engine's topic surface. Returns (recs_for_trigger, evidence)."""
    seen, recs, turns_ev = {}, [], []
    for turn in scen["turns"]:
        res = engine.retrieve(query_case(scen, turn), top_k=TOP_K)
        items = [{"record_id": it.record_id, "text": it.text} for it in res.items]
        for it in res.items:
            if it.text not in seen:
                seen[it.text] = True
                recs.append({"summary": it.text})
        turns_ev.append({"turn": turn["turn"], "type": turn["type"],
                         "query": turn["text"], "retrieved": items})
    return recs, turns_ev


def run_scenario_topics(scen, adir, topics_path, firelog_path, recs):
    """Copied from run_standard.py run_scenario rev
    e84bd58e1ff8e8162406d33265c93cfcdcea0d61b0600fe0650dc6b3b5b00c0f.
    Sole delta: the topics file is written from `recs` (the engine-derived
    topic surface) instead of the corpus record summaries. Everything else -
    pi spawn flags, RPC order, abort timing, wait_line, timeouts - is
    byte-identical."""
    import select
    import subprocess
    import time

    with open(topics_path, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    env = dict(os.environ, PI_CODING_AGENT_DIR=adir)
    proc = subprocess.Popen(
        [run_standard.PI, "--mode", "rpc", "--no-session", "--model", run_standard.MODEL],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, env=env, text=True, bufsize=1,
        cwd=os.path.dirname(adir))

    def rpc(cmd):
        proc.stdin.write(json.dumps(cmd) + "\n"); proc.stdin.flush()

    def wait_line(n):
        deadline = time.time() + run_standard.LINE_TIMEOUT
        while time.time() < deadline:
            if proc.poll() is not None:
                raise RuntimeError(f"rpc died rc={proc.returncode}")
            if os.path.isfile(firelog_path) and sum(1 for _ in open(firelog_path)) >= n:
                return
            r, _, _ = select.select([proc.stdout], [], [], 0.5)
            if not r:
                continue
            line = proc.stdout.readline()
            if not line:
                raise RuntimeError("rpc stdout closed early")
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "response" and not ev.get("success"):
                raise RuntimeError(f"command rejected: {ev}")
        raise RuntimeError(f"no firelog line {n} in {run_standard.LINE_TIMEOUT}s")

    try:
        turns = scen["turns"]
        for i, turn in enumerate(turns, 1):
            rpc({"id": f"p{i}", "type": "prompt", "message": turn["text"]})
            wait_line(i)
            if i < len(turns):
                rpc({"type": "abort"}); time.sleep(2)
    finally:
        try: proc.stdin.close()
        except Exception: pass
        proc.terminate()
        try: proc.wait(timeout=10)
        except subprocess.TimeoutExpired: proc.kill()
    return [json.loads(l) for l in open(firelog_path) if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", required=True, choices=sorted(ENGINES))
    ap.add_argument("--out", required=True)
    ap.add_argument("--scenarios", default=None, help="comma list; default all 60")
    ap.add_argument("--tag", default="", help="run tag for determinism spot-checks")
    args = ap.parse_args()

    sha = hashlib.sha256(open(CORPUS, "rb").read()).hexdigest()
    if sha != FROZEN_CORPUS_SHA:
        sys.exit(f"FATAL: corpus sha {sha} != frozen {FROZEN_CORPUS_SHA}; aborting")

    mod_name, cls_name, exp_class, pin = ENGINES[args.engine]
    module = __import__(mod_name, fromlist=[cls_name])
    engine = getattr(module, cls_name)()
    probe = engine.probe()
    if not probe.available:
        sys.exit(f"FATAL: engine {args.engine} probe unavailable: {probe.reason}")

    scenarios = [json.loads(l) for l in open(CORPUS) if l.strip()]
    if args.scenarios:
        want = set(args.scenarios.split(","))
        scenarios = [s for s in scenarios if s["scenario_id"] in want]

    outdir = os.path.abspath(args.out)
    os.makedirs(outdir, exist_ok=True)
    deriv_path = os.path.join(outdir, "topics-derivation.jsonl")
    stop = run_standard.load_stopwords()

    results, failures = [], []
    for sc in scenarios:
        sid = sc["scenario_id"]
        workdir = os.path.join(outdir, sid)
        os.makedirs(workdir, exist_ok=True)
        recs = []
        try:
            engine.ingest([make_record(sc)], mode="raw")
            recs, turns_ev = derive_topics(engine, sc)
            with open(deriv_path, "a") as f:
                f.write(json.dumps({"scenario": sid, "turns": turns_ev,
                                    "n_topic_entries": len(recs)}, sort_keys=True) + "\n")
            adir, topics, firelog = run_standard.make_agent_dir(workdir, "system")
            lines = run_scenario_topics(sc, adir, topics, firelog, recs)
            for turn, line in zip(sc["turns"], lines):
                results.append((sid, turn["type"], line))
        except Exception as e:
            failures.append(f"{sid}: {e}")
        print(f"[{sid}] {len(recs) if recs else 0} topics, "
              f"{time_done():.0f}s", flush=True)

    summary = run_standard.metrics(scenarios, results, stop)
    with open(os.path.join(outdir, "results.jsonl"), "w") as f:
        for sid, ttype, line in results:
            f.write(json.dumps({"scenario": sid, "turn_type": ttype, **line}) + "\n")
    out = {
        "row": "S4-12", "engine": args.engine, "experiment_class": exp_class,
        "engine_pin": pin, "tag": args.tag,
        "corpus": "invocation-corpus-v3-standard/corpus.jsonl",
        "corpus_sha256": sha,
        "trigger_pin": "pi-change-trigger @db31ea3e0138083bfd136233131f575f0640e9b5 "
                       "index.ts sha256 ec6d87948a48b44b536e714abc05b78968657d5abf20154d7a6059014fbbdd01",
        "harness": f"run_standard.py rev e84bd58e (metrics/load_stopwords reused; "
                   f"run_scenario copied with sole delta: topics source)",
        "model": run_standard.MODEL, "top_k": TOP_K, "record_timestamp": RECORD_TS.isoformat(),
        "n_scenarios": len(scenarios), "n_turns": len(results),
        "failures": failures,
        "metrics": {k: {"num": v[0], "den": v[1]} for k, v in summary.items()},
    }
    with open(os.path.join(outdir, "summary.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))
    return 1 if failures else 0


_start = None
def time_done():
    import time
    global _start
    if _start is None:
        _start = time.time()
    return time.time() - _start


if __name__ == "__main__":
    sys.exit(main())
