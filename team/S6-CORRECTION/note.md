# Correction: the S4-12 cross-engine zeros were a retrieval-configuration artifact

Sprint-6 row S6-1, published under Brian's approval of 2026-09-16 evening:
"publish the correction, not a ranking." Author: kiln-flash, 2026-09-17.
Written to be readable without this fleet's context. It corrects the zero
results reported by QUEUE row S4-12 on 2026-09-16, as repaired by the S4-14
re-run of the same day.

## What was reported

Row S4-12 ran two memory systems on the frozen invocation corpus (v3, sha256
`7395b7d5fc44c92a58599b74b193eabf727bbec5a81b8fac991ee66a15a369c0`) and
reported FBMR_topic 0/30 for both: `pi_lcm_store_reader` (the raw store
reader) and `claude_mem_fts5_core` (the whole prompt scored as one quoted
FTS5 phrase), with FalseFire 0/60 on each. The zeros were recorded as the
systems' measured performance on the invocation instrument and travelled
into Brian's briefing as a real result.

## Why it was wrong

The zeros came from the retrieval configuration, not measurement error.
Each arm scored a retrieval surface its vendor does not ship as the
system's search path. The pi-lcm arm read the store raw, without the
tool-level exact-then-relaxed query path that is the validated semantics —
iteration 1 had already measured raw 0.0 versus tool-level 0.2227 dynamic
Hit@3 on the conflict benchmark. The claude-mem arm scored the whole prompt
as one quoted phrase, while the product's actual search policy is chroma
semantic search. The correcting knowledge was already on record in
`team/ECOSYSTEM-MAP.md` (2026-09-13, three days before S4-12 ran) and was
not consulted; that routing failure is recorded in
`team/RETRO-4-SUMMARY.md`.

## What the corrected settings produce

The S4-14 re-run (`team/s4-14-crossengine-rerun/summary-comparison.md`;
same corpus, trigger, harness and scoring) put both systems on their
validated paths and reports, old against new:

- claude-mem on the vendor chroma policy, 90-day window disabled:
  FBMR_topic 30/30, with the window-on arm byte-identical; FirePrecision
  30/119 and NearMissFire 24/24 are the cost of a surface that brings the
  record back on every turn — full recall, low selectivity.
- pi-lcm on the tool-level path (a verbatim port of the vendor's
  relaxedVariants): FBMR_topic 7/30, FalseFire 0/60, NearMissFire 10/24.
  The exact AND query matched nothing; every one of the 23 non-empty
  derivation turns was rescued by bounded relaxation.
- bm25 (row S4-12, unchanged): FBMR_topic 25/30.

Scenario partition of the same re-run, re-measured on 2026-09-17 from the
pinned derivation log: 19 of the 60 scenarios produced at least one
non-empty derivation turn on the pi-lcm tool-level path, and the other 41
scenarios produced none. The re-run document's F4 annex originally said 37
of the 60 produced none; that count was wrong, and the document now carries
the corrected 41 alongside its own table.

## The fixture dating, explained

The stored fixture records all carry the fixed stamp 2026-09-01T00:00Z
(`RECORD_TS`, `run_crossengine.py:43`), while the evaluation clock eval_now
is pinned at 2026-08-30T12:00Z (`DEFAULT_EVAL_NOW`, `claude_mem_core.py:25`),
so the fixtures are future-dated relative to eval_now. This happened because
the two constants are independent determinism pins: RECORD_TS exists so that
every re-run sees a byte-identical store, and DEFAULT_EVAL_NOW exists so
that the vendored claude-mem 13.18.0 window policy is reproducible instead
of silently drifting with the wall clock; they were chosen at different
times, for different layers, and never reconciled with each other. The
consequence is mechanical and it bounds what the run can say about windows:
the 90-day window filter is lower-bound-only — a record is dropped only when
its stamp is older than eval_now minus 90 days — so a future-dated record
can never fall outside the window, and the window-on arm keeps exactly the
record set the window-off arm keeps, on this corpus, by construction. The
byte-identical window A/B therefore demonstrates the fixture dating, not a
measured window effect, and should be quoted only as "identical on this
corpus." What the 90-day window does to records older than its boundary
remains iteration 1's separate measured result (Hit@5 0.208 with the window
versus 0.958 without, on a different instrument), which this correction
leaves intact.

## What the review caught, and what checking arithmetic cannot do

Astra's review found both defects in the re-run document — the annex count
that contradicted the table, and the dating that was stated but never
explained — and the corrected arithmetic was verified against the pinned
data before publication. Verifying the arithmetic did not validate the
experiment: the document had passed through an author's check and a
verifier's check while disagreeing with itself about a core count for the
whole life of the result. That is the transferable finding — arithmetic
re-derivation and does-the-document-agree-with-itself checks catch different
defect classes, and either one alone certifies far less than it appears to.

## What this correction does not claim

No engine ranking is offered here and none should be inferred. With one
record per store, a surface that returns everything cannot lose, so
claude-mem's 30/30 shows coverage rather than selectivity (Astra's
sprint-5 review); a comparative result becomes publishable only once the
instrument can make indiscriminate retrieval lose, which is exactly the
control sprint-6 row S6-2 is building. Trigger FirePrecision is not
retrieval precision; they are different measures that share a name —
FirePrecision scores which fired turns were topic moments (a property of
the trigger), while retrieval precision would score retrieved records
against relevance labels (a property of retrieval). Brian's briefing
conflated the two; this note keeps them apart.

## Publication

This note is the canonical correction text; the receipt in
`publication.json` names its revision and where it was announced. The
numbers above recompute from the pinned run directories named in
`numeric-claims.json`.
