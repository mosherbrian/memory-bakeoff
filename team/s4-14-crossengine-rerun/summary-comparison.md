# S4-14 — cross-engine re-run on the corrected reader paths: old vs new, side by side

> **Amended 2026-09-17 (sprint-6 row S6-1; defects found by Astra's review,
> arithmetic re-check relayed by Brian):** two defects in this document are
> corrected in place, each marked inline — **F4**'s empty-scenario count (37 was
> wrong; 41 is what the table implies and what the pinned derivation log
> re-measures), and **F3** now explains the fixture dating (records stamped
> 2026-09-01 vs eval_now pinned 2026-08-30) instead of merely stating it. No
> number in the table, the controls, or the other findings changed. Companion
> check `check_s4_14.py` re-run green after the edit.

**Row:** QUEUE S4-14 (originated by Brian's ruling 2026-09-16: "the zeros suggest
misconfiguration, and iteration 1 shook these out already"). **Date:** 2026-09-16,
free window, $0, no score import, deterministic-first. **Corpus:** frozen
invocation-corpus-v3-standard/corpus.jsonl sha256
`7395b7d5fc44c92a58599b74b193eabf727bbec5a81b8fac991ee66a15a369c0` (unchanged since
S4-10 froze it). **Trigger:** unchanged pinned pi-change-trigger @`db31ea3e…`,
index.ts sha256 `ec6d8794…`. **Harness:** run_standard.py rev `e84bd58e` reused
through run_crossengine.py (S4-12) — run_scenario_topics byte-identical, sole delta
remains the topics source; S4-14's sole further deltas are the engine retrieval paths
below. **Model:** GLM-5.3-Flash local pi RPC, top_k=2, record ts fixed 2026-09-01T00:00Z.

## What changed and why

Brian's diagnosis, confirmed against the iteration-1 record before any re-run:

1. **pi-lcm:** S4-12 ran the RAW arm (`pi_lcm_store_reader` — the adapter
   deliberately does not port tool-level relaxation,
   pi_lcm_store_reader.py:20-25). Iteration 1 (P2-entry run, 2026-09-13,
   `team/P2-ENTRY-RUN.md`, second-driven `team/ASSAY-SECOND-DRIVER-P2-ENTRY-RUN.md`
   586/2631 recount) MEASURED raw 0.0 vs tool-level **0.2227** dynamic Hit@3 on the
   conflict benchmark — the tool-level path (`lcm_grep`: exact query then bounded
   relaxation, NOT `lcm_expand`) is the validated semantics. S4-14 runs
   `pi_lcm_store_reader_toollevel` (iteration-1's arm name): verbatim `relaxedVariants`
   port (pi-project-recall index.ts:121-133, @sha256
   `9025eef540b6bbbb1364df5c6232672c0d67a8ad9b241d0208d62da39eb43c78`), same port that
   produced the 0.2227 in `experiment_20260913_p2_entry/run_p2_entry.py`.
   **Declared adaptation:** the extension's relaxation gate (index.ts:347-363,
   `bounds.conversations > 1` + live-echo check) has no counterpart here — the
   invocation store holds exactly the one prior-session record and the live prompt is
   never in the store, so "reaches prior sessions" reduces to "any hit"; the gate
   ports as: exact AND query first, if empty try relaxed variants (max 6), take the
   first with any hits, else the empty exact result stands unmarked. Store adapter
   byte-identical to S4-12: pi_lcm_store_reader.py @sha256
   `e2f87f92b5651aee6ad77764ffbd1533ba9d07300899c6977bc23a01b431d42e`.
2. **claude-mem:** S4-12's `claude_mem_fts5_core` arm scores the WHOLE prompt as one
   quoted FTS5 phrase — a surface the vendor does not ship as its search path
   (claude-mem "refuses raw — no supported no-LLM raw path", external.py:564;
   `team/CORVID-PRODUCT-PATH-CENSUS.md:50`). Iteration 1 (`team/ASSAY-SECOND-DRIVER-
   CLAUDE-MEM-WINDOW.md`) measured the vendor's ACTUAL current search policy
   (chroma top-100 semantic, shared-LSA) at core Hit@5 **0.208** with the default
   90-day window vs **0.958** with the window off. S4-14 runs that policy with the
   window disabled (`claude_mem_chroma_lsa_no_recency`, the row-mandated arm) plus
   the window-on arm as A/B context. Adapter unchanged: claude_mem_core.py @sha256
   `53199f688574c9e5b037c9231d87e560b21a6103d956ddc22036ef523c8d594a` (byte-identical
   to its S4-12 pin — re-verified before the re-run).

## Old vs new (identical corpus, trigger, harness, scoring)

| arm | retrieval path | derivation surface (turns) | scenarios w/ ≥1 non-empty turn | FBMR_topic | FalseFire | NearMissFire | FirePrecision | fresh_rate | gap_rate |
|---|---|---|---|---|---|---|---|---|---|
| pi_lcm_store_reader (S4-12 old) | raw store queries, no relaxation (charter A/B raw side) | 0/180 | 0/60 | 0/30 | 0/60 | 0/24 | 0/60 | 60/60 | 0/60 |
| claude_mem_fts5_core (S4-12 old) | whole prompt as ONE quoted FTS5 phrase (strict surface) | 0/180 | 0/60 | 0/30 | 0/60 | 0/24 | 0/60 | 60/60 | 0/60 |
| bm25 (S4-12 old) | in-tree BM25 baseline (context arm) | 77/180 | 47/60 | 25/30 | 0/60 | 20/24 | 25/110 | 60/60 | 0/60 |
| pi_lcm_store_reader_toollevel (S4-14 new) | raw reader + VERBATIM relaxedVariants (lcm_grep semantics; declared single-session gate adaptation) | 23/180 | 19/60 | 7/30 | 0/60 | 10/24 | 7/79 | 60/60 | 0/60 |
| claude_mem_chroma_lsa_no_recency (S4-14 new) | vendor chroma search policy, 90-day window DISABLED (row-mandated) | 180/180 | 60/60 | 30/30 | 0/60 | 24/24 | 30/119 | 60/60 | 0/60 |
| claude_mem_chroma_lsa (S4-14 new) | vendor chroma search policy, default 90-day window (A/B context) | 180/180 | 60/60 | 30/30 | 0/60 | 24/24 | 30/119 | 60/60 | 0/60 |

Scoring: frozen S3-1 programmatic fire-log metrics, identical definitions and
stopwords across all six arms. `fresh_rate`/`gap_rate` are method-behaviour metrics
(see S4-12 summary F4); FirePrecision denominators are run-dependent by the
pre-registered S3-1 definition.

## Controls (same checks as S4-12)

The S4-10 control runs are engine-independent by construction and remain THE controls
for this harness+trigger: `team/invocation-corpus-v3-standard/results-control-never-clean/`
(0/180 fired) and `results-control-always-clean/` (134/180 fired) — recomputed from
their results.jsonl by `check_s4_14.py`, which fails if either count drifts or the dirs
collide with an engine dir. Determinism: T001-T003 invariant fire-log tuples identical
between each arm's full run and its `detcheck-<arm>` re-run (wall-clock fields excluded).

## Findings (measured)

**F1 — Brian's ruling confirmed for both engines: the S4-12 zeros were configuration
artifacts, not results.** On identical corpus, trigger, harness and scoring:

- **claude-mem** 0/30 → **30/30 FBMR_topic** once scored on the vendor's actual search
  policy (chroma semantic, shared-LSA). The old `claude_mem_fts5_core` arm measured a
  whole-prompt quoted-phrase surface the vendor does not ship. NearMiss 24/24 and
  FirePrecision 30/119: with the record surfacing on every turn, every near-miss also
  fires — the surface is a firehose, so recall is full and precision is the cost.
- **pi-lcm** 0/30 → **7/30 FBMR_topic** on the tool-level path. The exact AND query
  matched 0/180 turns; all 23 non-empty surface turns are relaxation-rescued (max-6
  bounded variants, verbatim port). Fires come from two mechanisms, both visible in the
  fire log: single content tokens (`deploy` rescues T031/T033/T035/T037/T039; fires
  match token `deploy`) and stop-token rescues that still admit the record, whose
  genuine tokens then match (`mode` rescues T021/T027; fires match `billing-100`,
  `service`). NearMiss rises 0/24 → 10/24 — the honest cost of the same stop-token
  surfaces. FalseFire stays 0/60 everywhere, stale/anachronism 0 everywhere.

**F2 — The relaxation budget is the pi-lcm finding.** Rescued-variant frequency:
`to`×10, `mode`×4, `deploy`×4, `101.`–`109.`×1 each. On 10-word prompts the 6-attempt
budget is spent on leading trailing-drop windows (which contain stop-words absent from
the record) before any single-token attempt; the single tokens that do fire are the
prompt's LAST words (the port tries them last-first), so rescue skews to sentence-final
tokens. This is the verbatim vendor behavior (same port that measured 0.2227 on the
conflict benchmark, where queries are shorter and vocabulary is shared) — it is a real
property of the tool on long natural prompts, now measured on a second instrument.

**F3 — The 90-day window is a non-factor on THIS corpus — by construction of the
fixture dating, not by measurement.** Window-on and window-off chroma arms returned
byte-identical metrics (30/30, 30/119, 24/24). **[Corrected/explained 2026-09-17,
S6-1 defect (b):]** every record carries the fixed stamp `RECORD_TS =
2026-09-01T00:00Z` (`run_crossengine.py:43`), while the evaluation clock is pinned
`DEFAULT_EVAL_NOW = 2026-08-30T12:00Z` (`claude_mem_core.py:25`, kept explicit "so
the 90-day policy is reproducible instead of silently drifting"). The two constants
are independent determinism pins — one freezes every record's age so a re-run sees an
identical store, the other freezes the vendored claude-mem 13.18.0 policy clock — set
at different times for different layers and never reconciled, so the fixtures are
future-dated relative to eval_now. The consequence is mechanical: the window filter
is lower-bound-only (`claude_mem_core.py:243` drops a record only when its stamp is
OLDER than `eval_now − 90d`), so a future-dated record can never fall outside the
window and window-on keeps exactly the set window-off keeps — on this corpus, by
construction. The byte-identical A/B therefore demonstrates the dating, not a window
effect; cite it as "identical on this corpus" and nothing more. What the 90-day
window does to records older than its boundary remains iteration 1's measured result
on its own instrument (0.208 vs 0.958 Hit@5, a 0.75 cost), unchanged by this
correction. Row-mandated arm (window-off) stands as primary; the A/B is reported so
nobody cites the window as a live confound.

**F4 — Zero-demonstration annex (row rule).** No corrected arm scores zero, so the
rule's burden is discharged with evidence rather than argument: the pi tool-level
empty scenarios number **41 of 60** **[corrected 2026-09-17, S6-1 defect (a): this
annex originally said 37, contradicting the table's own 19/60 with ≥1 non-empty
turn; re-measured 2026-09-17 from
`results-pi_lcm_store_reader_toollevel/topics-derivation.jsonl`: 19 scenarios with
≥1 non-empty derivation turn, 41 with none, 23 non-empty turns of 180]** and the
emptiness is demonstrated turn-by-turn in
`results-pi_lcm_store_reader_toollevel/topics-derivation.jsonl` — every turn carries
`tool_level = {exact_nonempty: false, relaxed_with: null, attempts: N}` (N = variants
tried), i.e. the harness demonstrably got SOMETHING on 23 turns and demonstrably got
an audited empty on the rest. The old strict arms' 0/180 surfaces are retained for
contrast in the table above.

**F5 — Reading, honestly.** "Which engine detects moments" now has a first real
cross-engine answer at $0: claude-mem's semantic policy saturates the invocation
instrument (30/30, with precision 30/119 and near-miss 24/24 as the price), pi-lcm's
lexical grep+relaxation catches 7/30 with zero false fires, bm25 sits between at 25/30
(S4-12, unchanged). The instrument (single-record store, top_k=2 topics surface) favors
semantic surfaces; the pi-lcm number is a floor for the grep path, not a ceiling for
the product (its expand/summarize surfaces are out of this row's scope).

## Iteration-1 anchors (for provenance; NOT same-instrument numbers)

| anchor | value | instrument | source |
|---|---|---|---|
| pi-lcm tool-level | dynamic Hit@3 **0.2227** (raw 0.0) | conflict benchmark, heldout 27 (n=2,631) | P2-ENTRY-RUN.md; ASSAY-SECOND-DRIVER-P2-ENTRY-RUN.md |
| claude-mem window ON | core Hit@5 **0.208** | controlled core5 (24 scored) | ASSAY-SECOND-DRIVER-CLAUDE-MEM-WINDOW.md |
| claude-mem window OFF | core Hit@5 **0.958** | same | same |

These anchors live on different instruments than the invocation corpus; they travel as
path validation (which retrieval semantics is the real system), not as comparable scores.

