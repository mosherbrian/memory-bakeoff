#!/usr/bin/env python3
"""Declared check for QUEUE row S4-12 (executable, exit-code gated).

Verifies, from files on disk:
  1. per-engine results exist for BOTH controlled_core engines
     (claude_mem_fts5_core, pi_lcm_store_reader) and each run has zero
     failures recorded in summary.json;
  2. every engine summary cites the frozen corpus v3 sha256 and the pinned
     trigger (commit + index.ts sha);
  3. the pinned trigger file on disk still hashes to the pinned sha;
  4. the frozen corpus on disk still hashes to the S4-10 sha;
  5. determinism spot-checks: for each controlled_core engine, the invariant
     fire-log fields of scenarios T001-T003 are identical between the full run
     and the re-run;
  6. controls are separate: the S4-10 control run dirs exist and are distinct
     from every engine results dir;
  7. the summary table v1 exists and names both controlled_core engines, the
     corpus sha, both engine pins, and the separate control dirs.

Exit 0 iff all hold; any violation prints a named finding and exits 1.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEAM = os.path.dirname(HERE)
FROZEN_CORPUS_SHA = "7395b7d5fc44c92a58599b74b193eabf727bbec5a81b8fac991ee66a15a369c0"
TRIGGER_TS = "/var/home/bmosher/memory-bake-off/implementer/repo/extensions/pi-change-trigger/index.ts"
TRIGGER_SHA = "ec6d87948a48b44b536e714abc05b78968657d5abf20154d7a6059014fbbdd01"
CONTROLLED = ["claude_mem_fts5_core", "pi_lcm_store_reader"]
CONTEXT = ["bm25"]
CONTROLS = ["results-control-never-clean", "results-control-always-clean"]


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def invariant_tuples(results_path, sids):
    out = []
    for line in open(results_path):
        d = json.loads(line)
        if d["scenario"] in sids:
            out.append((d["scenario"], d["turn_type"], d["fired"],
                        tuple(sorted(d["reasons"])), tuple(sorted(d["matched_tokens"]))))
    return sorted(out)


def main():
    findings = []

    summaries = {}
    for name in CONTROLLED + CONTEXT:
        d = os.path.join(HERE, f"results-{name}")
        sp = os.path.join(d, "summary.json")
        if not os.path.isfile(sp):
            findings.append(f"missing results dir/summary for {name}: {sp}")
            continue
        s = json.load(open(sp))
        summaries[name] = s
        if s.get("failures"):
            findings.append(f"{name}: run recorded failures: {s['failures']}")
        if s.get("corpus_sha256") != FROZEN_CORPUS_SHA:
            findings.append(f"{name}: summary cites corpus sha {s.get('corpus_sha256')}")
        if "db31ea3e0138083bfd136233131f575f0640e9b5" not in s.get("trigger_pin", ""):
            findings.append(f"{name}: summary does not cite pinned trigger commit")
        if not s.get("engine_pin"):
            findings.append(f"{name}: summary lacks engine pin")
        if not os.path.isfile(os.path.join(d, "results.jsonl")):
            findings.append(f"{name}: results.jsonl missing")

    for name in CONTROLLED:
        if name not in summaries:
            findings.append(f"controlled_core engine {name} has no results - row cannot be done")

    if sha256(TRIGGER_TS) != TRIGGER_SHA:
        findings.append(f"trigger index.ts drifted from pin: {sha256(TRIGGER_TS)}")
    corpus = os.path.join(TEAM, "invocation-corpus-v3-standard", "corpus.jsonl")
    if sha256(corpus) != FROZEN_CORPUS_SHA:
        findings.append(f"corpus v3 drifted from frozen sha: {sha256(corpus)}")

    for name in CONTROLLED:
        full = os.path.join(HERE, f"results-{name}", "results.jsonl")
        det = os.path.join(HERE, f"detcheck-{name}", "results.jsonl")
        if not (os.path.isfile(full) and os.path.isfile(det)):
            findings.append(f"{name}: determinism spot-check files missing")
            continue
        sids = {f"T{i:03d}" for i in (1, 2, 3)}
        a, b = invariant_tuples(full, sids), invariant_tuples(det, sids)
        if a != b or not a:
            findings.append(f"{name}: determinism mismatch or empty ({len(a)} vs {len(b)} invariant tuples)")

    engine_dirs = {os.path.join(HERE, f"results-{n}") for n in summaries}
    for c in CONTROLS:
        p = os.path.join(TEAM, "invocation-corpus-v3-standard", c)
        if not os.path.isdir(p):
            findings.append(f"separate control dir missing: {p}")
        elif p in engine_dirs:
            findings.append(f"control dir collides with engine dir: {p}")

    table = os.path.join(TEAM, "S4-12-CROSSENGINE-SUMMARY-v1.md")
    if not os.path.isfile(table):
        findings.append(f"summary table v1 missing: {table}")
    else:
        text = open(table).read()
        for needle in ([FROZEN_CORPUS_SHA] + CONTROLLED
                       + ["53199f688574c9e5b037c9231d87e560b21a6103d956ddc22036ef523c8d594a",
                          "e2f87f92b5651aee6ad77764ffbd1533ba9d07300899c6977bc23a01b431d42e",
                          "results-control-never-clean", "results-control-always-clean"]):
            if needle not in text:
                findings.append(f"summary table does not cite required token: {needle[:60]}")

    for f in findings:
        print(f"FINDING: {f}")
    print(f"s4-12 check: {len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
