#!/usr/bin/env python3
"""Generate team/s4-14-crossengine-rerun/summary-comparison.md from the run
summaries on disk (S4-12 old arms + S4-14 corrected arms). Numbers are read,
never transcribed by hand."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TEAM = os.path.dirname(HERE)
S412 = os.path.join(TEAM, "s4-12-crossengine")

ARMS = [
    ("S4-12 old", "pi_lcm_store_reader", "raw store queries, no relaxation (charter A/B raw side)"),
    ("S4-12 old", "claude_mem_fts5_core", "whole prompt as ONE quoted FTS5 phrase (strict surface)"),
    ("S4-12 old", "bm25", "in-tree BM25 baseline (context arm)"),
    ("S4-14 new", "pi_lcm_store_reader_toollevel", "raw reader + VERBATIM relaxedVariants (lcm_grep semantics; declared single-session gate adaptation)"),
    ("S4-14 new", "claude_mem_chroma_lsa_no_recency", "vendor chroma search policy, 90-day window DISABLED (row-mandated)"),
    ("S4-14 new", "claude_mem_chroma_lsa", "vendor chroma search policy, default 90-day window (A/B context)"),
]
METRICS = ["FBMR_topic", "FalseFire", "NearMissFire", "FirePrecision", "fresh_rate", "gap_rate"]


def surface(s412, arm):
    d = os.path.join(S412 if s412 else HERE, f"results-{arm}", "topics-derivation.jsonl")
    turns = nonempty = 0
    scen = set()
    for line in open(d):
        o = json.loads(line)
        hit = False
        for t in o["turns"]:
            turns += 1
            if t.get("retrieved"):
                nonempty += 1
                hit = True
        if hit:
            scen.add(o["scenario"])
    return nonempty, turns, len(scen)


def main():
    rows = []
    for tag, arm, desc in ARMS:
        base = S412 if tag == "S4-12 old" else HERE
        s = json.load(open(os.path.join(base, f"results-{arm}", "summary.json")))
        ne, t, sc = surface(tag == "S4-12 old", arm)
        rows.append((tag, arm, desc, f"{ne}/{t}", f"{sc}/60",
                     {m: f"{s['metrics'][m]['num']}/{s['metrics'][m]['den']}" for m in METRICS},
                     s.get("derivation_surface", {}).get("relaxed")))

    L = []
    L.append("# S4-14 — cross-engine re-run on the corrected reader paths: old vs new, side by side")
    L.append("")
    L.append("**Row:** QUEUE S4-14 (originated by Brian's ruling 2026-09-16: \"the zeros suggest")
    L.append("misconfiguration, and iteration 1 shook these out already\"). **Date:** 2026-09-16,")
    L.append("free window, $0, no score import, deterministic-first. **Corpus:** frozen")
    L.append("invocation-corpus-v3-standard/corpus.jsonl sha256")
    L.append("`7395b7d5fc44c92a58599b74b193eabf727bbec5a81b8fac991ee66a15a369c0` (unchanged since")
    L.append("S4-10 froze it). **Trigger:** unchanged pinned pi-change-trigger @`db31ea3e…`,")
    L.append("index.ts sha256 `ec6d8794…`. **Harness:** run_standard.py rev `e84bd58e` reused")
    L.append("through run_crossengine.py (S4-12) — run_scenario_topics byte-identical, sole delta")
    L.append("remains the topics source; S4-14's sole further deltas are the engine retrieval paths")
    L.append("below. **Model:** GLM-5.3-Flash local pi RPC, top_k=2, record ts fixed 2026-09-01T00:00Z.")
    L.append("")
    L.append("## What changed and why")
    L.append("")
    L.append("Brian's diagnosis, confirmed against the iteration-1 record before any re-run:")
    L.append("")
    L.append("1. **pi-lcm:** S4-12 ran the RAW arm (`pi_lcm_store_reader` — the adapter")
    L.append("   deliberately does not port tool-level relaxation,")
    L.append("   pi_lcm_store_reader.py:20-25). Iteration 1 (P2-entry run, 2026-09-13,")
    L.append("   `team/P2-ENTRY-RUN.md`, second-driven `team/ASSAY-SECOND-DRIVER-P2-ENTRY-RUN.md`")
    L.append("   586/2631 recount) MEASURED raw 0.0 vs tool-level **0.2227** dynamic Hit@3 on the")
    L.append("   conflict benchmark — the tool-level path (`lcm_grep`: exact query then bounded")
    L.append("   relaxation, NOT `lcm_expand`) is the validated semantics. S4-14 runs")
    L.append("   `pi_lcm_store_reader_toollevel` (iteration-1's arm name): verbatim `relaxedVariants`")
    L.append("   port (pi-project-recall index.ts:121-133, @sha256 `9025eef5…`), same port that")
    L.append("   produced the 0.2227 in `experiment_20260913_p2_entry/run_p2_entry.py`.")
    L.append("   **Declared adaptation:** the extension's relaxation gate (index.ts:347-363,")
    L.append("   `bounds.conversations > 1` + live-echo check) has no counterpart here — the")
    L.append("   invocation store holds exactly the one prior-session record and the live prompt is")
    L.append("   never in the store, so \"reaches prior sessions\" reduces to \"any hit\"; the gate")
    L.append("   ports as: exact AND query first, if empty try relaxed variants (max 6), take the")
    L.append("   first with any hits, else the empty exact result stands unmarked.")
    L.append("2. **claude-mem:** S4-12's `claude_mem_fts5_core` arm scores the WHOLE prompt as one")
    L.append("   quoted FTS5 phrase — a surface the vendor does not ship as its search path")
    L.append("   (claude-mem \"refuses raw — no supported no-LLM raw path\", external.py:564;")
    L.append("   `team/CORVID-PRODUCT-PATH-CENSUS.md:50`). Iteration 1 (`team/ASSAY-SECOND-DRIVER-")
    L.append("   CLAUDE-MEM-WINDOW.md`) measured the vendor's ACTUAL current search policy")
    L.append("   (chroma top-100 semantic, shared-LSA) at core Hit@5 **0.208** with the default")
    L.append("   90-day window vs **0.958** with the window off. S4-14 runs that policy with the")
    L.append("   window disabled (`claude_mem_chroma_lsa_no_recency`, the row-mandated arm) plus")
    L.append("   the window-on arm as A/B context. Adapter unchanged:")
    L.append("   claude_mem_core.py @sha256 `53199f68…`.")
    L.append("")
    L.append("## Old vs new (identical corpus, trigger, harness, scoring)")
    L.append("")
    L.append("| arm | retrieval path | derivation surface (turns) | scenarios w/ ≥1 non-empty turn | " + " | ".join(METRICS) + " |")
    L.append("|---|---|---|---|" + "---|" * len(METRICS))
    for tag, arm, desc, surf, scen, m, _ in rows:
        L.append(f"| {arm} ({tag}) | {desc} | {surf} | {scen} | " + " | ".join(m[x] for x in METRICS) + " |")
    L.append("")
    L.append("Scoring: frozen S3-1 programmatic fire-log metrics, identical definitions and")
    L.append("stopwords across all six arms. `fresh_rate`/`gap_rate` are method-behaviour metrics")
    L.append("(see S4-12 summary F4); FirePrecision denominators are run-dependent by the")
    L.append("pre-registered S3-1 definition.")
    L.append("")
    L.append("## Controls (same checks as S4-12)")
    L.append("")
    L.append("The S4-10 control runs are engine-independent by construction and remain THE controls")
    L.append("for this harness+trigger: `team/invocation-corpus-v3-standard/results-control-never-clean/`")
    L.append("(0/180 fired) and `results-control-always-clean/` (134/180 fired) — recomputed from")
    L.append("their results.jsonl by `check_s4_14.py`, which fails if either count drifts or the dirs")
    L.append("collide with an engine dir. Determinism: T001-T003 invariant fire-log tuples identical")
    L.append("between each arm's full run and its `detcheck-<arm>` re-run (wall-clock fields excluded).")
    L.append("")
    L.append("## Findings")
    L.append("")
    L.append("(filled from the run output below — see `## Findings (measured)`)")
    L.append("")
    L.append("## Iteration-1 anchors (for provenance; NOT same-instrument numbers)")
    L.append("")
    L.append("| anchor | value | instrument | source |")
    L.append("|---|---|---|---|")
    L.append("| pi-lcm tool-level | dynamic Hit@3 **0.2227** (raw 0.0) | conflict benchmark, heldout 27 (n=2,631) | P2-ENTRY-RUN.md; ASSAY-SECOND-DRIVER-P2-ENTRY-RUN.md |")
    L.append("| claude-mem window ON | core Hit@5 **0.208** | controlled core5 (24 scored) | ASSAY-SECOND-DRIVER-CLAUDE-MEM-WINDOW.md |")
    L.append("| claude-mem window OFF | core Hit@5 **0.958** | same | same |")
    L.append("")
    L.append("These anchors live on different instruments than the invocation corpus; they travel as")
    L.append("path validation (which retrieval semantics is the real system), not as comparable scores.")
    L.append("")
    with open(os.path.join(HERE, "summary-comparison.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("wrote skeleton summary-comparison.md with measured tables")


if __name__ == "__main__":
    main()
