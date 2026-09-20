#!/usr/bin/env python3
"""Declared-row check for QUEUE row S4-14 (substantive companion to the row's
declared `test -f summary-comparison.md`).

Verifies, from files on disk:
  1. per-arm results exist for all three corrected arms
     (pi_lcm_store_reader_toollevel, claude_mem_chroma_lsa_no_recency,
     claude_mem_chroma_lsa) and each run records zero failures;
  2. every arm summary cites the frozen corpus v3 sha, the pinned trigger,
     and a non-empty engine pin;
  3. pin drift gate: trigger index.ts, pi-project-recall index.ts, and both
     provider adapters still hash to their pinned sha256 values;
  4. determinism spot-checks: invariant fire-log fields of T001-T003 are
     identical between each arm's full run and its detcheck re-run
     (wall-clock fields excluded);
  5. controls unchanged and separate: the S4-10/S4-12 control dirs still
     recompute to 0/180 (never) and 134/180 (always) fired, and are distinct
     from every S4-14 engine results dir;
  6. zero-demonstration rule (row term): any arm whose FBMR_topic count is 0
     must have a non-empty derivation surface recorded (evidence the harness
     got SOMETHING through the engine before the zero is a finding);
  7. summary-comparison.md exists and cites: all six arm names (3 old +
     3 new), the corpus sha, the iteration-1 anchors (0.2227, 0.208, 0.958),
     the adapter pins, and the separate control dirs.

Exit 0 iff all hold; any violation prints a named finding and exits 1.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEAM = os.path.dirname(HERE)
REPO = os.path.join(TEAM, "..", "implementer", "repo")
FROZEN_CORPUS_SHA = "7395b7d5fc44c92a58599b74b193eabf727bbec5a81b8fac991ee66a15a369c0"
PINS = {
    "extensions/pi-change-trigger/index.ts":
        "ec6d87948a48b44b536e714abc05b78968657d5abf20154d7a6059014fbbdd01",
    "extensions/pi-project-recall/index.ts":
        "9025eef540b6bbbb1364df5c6232672c0d67a8ad9b241d0208d62da39eb43c78",
    "src/memory_bakeoff/providers/pi_lcm_store_reader.py":
        "e2f87f92b5651aee6ad77764ffbd1533ba9d07300899c6977bc23a01b431d42e",
    "src/memory_bakeoff/providers/claude_mem_core.py":
        "53199f688574c9e5b037c9231d87e560b21a6103d956ddc22036ef523c8d594a",
}
OLD_ARMS = ["pi_lcm_store_reader", "claude_mem_fts5_core", "bm25"]
NEW_ARMS = ["pi_lcm_store_reader_toollevel", "claude_mem_chroma_lsa_no_recency",
            "claude_mem_chroma_lsa"]
CONTROLS = {"results-control-never-clean": (0, 180),
            "results-control-always-clean": (134, 180)}


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
    for name in NEW_ARMS:
        d = os.path.join(HERE, f"results-{name}")
        sp = os.path.join(d, "summary.json")
        if not os.path.isfile(sp):
            findings.append(f"missing results dir/summary for arm {name}: {sp}")
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

    for rel, want in PINS.items():
        p = os.path.join(REPO, rel)
        if not os.path.isfile(p):
            findings.append(f"pinned file missing: {rel}")
        elif sha256(p) != want:
            findings.append(f"pin drift: {rel} now {sha256(p)[:16]}... != pinned {want[:16]}...")

    corpus = os.path.join(TEAM, "invocation-corpus-v3-standard", "corpus.jsonl")
    if sha256(corpus) != FROZEN_CORPUS_SHA:
        findings.append(f"corpus v3 drifted from frozen sha: {sha256(corpus)}")

    sids = {f"T{i:03d}" for i in (1, 2, 3)}
    for name in NEW_ARMS:
        full = os.path.join(HERE, f"results-{name}", "results.jsonl")
        det = os.path.join(HERE, f"detcheck-{name}", "results.jsonl")
        if not (os.path.isfile(full) and os.path.isfile(det)):
            findings.append(f"{name}: determinism spot-check files missing")
            continue
        a, b = invariant_tuples(full, sids), invariant_tuples(det, sids)
        if a != b or not a:
            findings.append(f"{name}: determinism mismatch or empty ({len(a)} vs {len(b)} invariant tuples)")

    engine_dirs = {os.path.abspath(os.path.join(HERE, f"results-{n}")) for n in NEW_ARMS}
    for cname, (want_fired, want_turns) in CONTROLS.items():
        p = os.path.join(TEAM, "invocation-corpus-v3-standard", cname)
        if not os.path.isdir(p):
            findings.append(f"separate control dir missing: {p}")
            continue
        if os.path.abspath(p) in engine_dirs:
            findings.append(f"control dir collides with engine dir: {cname}")
        rp = os.path.join(p, "results.jsonl")
        if not os.path.isfile(rp):
            findings.append(f"control dir has no results.jsonl: {cname}")
            continue
        lines = [json.loads(l) for l in open(rp)]
        fired, turns = sum(1 for d in lines if d["fired"]), len(lines)
        if (fired, turns) != (want_fired, want_turns):
            findings.append(f"control {cname} changed since S4-12: {fired}/{turns} != {want_fired}/{want_turns}")

    for name in NEW_ARMS:
        s = summaries.get(name)
        if not s:
            continue
        fbmr = s.get("metrics", {}).get("FBMR_topic", {})
        surf = s.get("derivation_surface", {})
        if fbmr.get("num") == 0 and surf.get("nonempty", 0) == 0:
            findings.append(f"{name}: FBMR_topic 0 with 0/0 non-empty derivation surface "
                            f"- zero not demonstrated (row rule)")

    table = os.path.join(HERE, "summary-comparison.md")
    if not os.path.isfile(table):
        findings.append(f"summary-comparison.md missing: {table}")
    else:
        text = open(table).read()
        needles = ([FROZEN_CORPUS_SHA] + OLD_ARMS + NEW_ARMS
                   + ["0.2227", "0.208", "0.958",
                      "e2f87f92b5651aee6ad77764ffbd1533ba9d07300899c6977bc23a01b431d42e",
                      "53199f688574c9e5b037c9231d87e560b21a6103d956ddc22036ef523c8d594a",
                      "results-control-never-clean", "results-control-always-clean"])
        for needle in needles:
            if needle not in text:
                findings.append(f"summary-comparison.md missing required token: {needle[:60]}")

    for f in findings:
        print(f"FINDING: {f}")
    print(f"s4-14 check: {len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
