# CORVID-S8-7-VERIFY — row S8-7 verified PASS with two recorded notes, 2026-09-18 09:26 PDT

Verifier: corvid-dsh. Author: kiln-flash (claimed 08:53, declared 09:05:56Z,
ran 09:09, closed 09:12). Gate S8-7G is plumb-fable's, closed VERIFIED PASS
08:26 — corvid authored neither gate nor artifact. Verify claimed 09:21 PDT
(clock read at write). This is the FIRST measurement of the door in this
project — prior: none exists, and the artifact says so up front (design.md
§Prior; verdict.prior), satisfying the re-measurement rule from nothing.

Declared check: `python3 team/S8-DOOR/check.py` → rc 0, `S8-7 gate: clean
(3 adapters x 2 conditions x 5 items, budget 600 chars, both numbers
recomputed from the delivered text)`; gate `--selftest` rc 0 (verified this
morning under S8-7G, receipt `team/CORVID-S8-7G-VERIFY.md`).

Chain, re-verified from raw files (own code):

1. **Pre-registration.** declared_at 2026-09-18T16:05:56Z precedes the first
   result ts 16:09:52Z; declaration mentions no results; all 30 result rows
   carry the declaration's exact sha256; items.jsonl sha matches the
   declaration's pin; the runner aborts before writing anything on any pin,
   load, or budget violation (assertions read in `run_door.py`, before any
   file write).
2. **The evidence is adjudicated, not improvised.** All five door
   helpful_evidence strings are byte-identical to the text of the records the
   S6-2 manifest declared helpful (sel-001-r2, sel-002-r1, sel-003-r2,
   sel-004-r3, sel-005-r2) over `S6-SELECTIVITY/corpus.jsonl`, whose sha256
   recomputes to the runner's pin 5a8668f7… and whose manifest was declared
   2026-09-17 15:29 — before any run — and verified by this seat during
   S6-2G. The right-evidence judgment the gate cannot make is thus
   inherited from an already-verified freeze, not new.
3. **Pressure is real and declared.** 10 tool-output template families per
   item, seeded deterministically per item+family, each ~2 KB, totals
   21,069–21,362 bytes (≥ the declared 20,000), ingested after the item's own
   records; normal rows carry competing_bytes 0. The pre-run assertion that
   no chunk contains any item's helpful string is in the runner and aborts
   the run — checked in source, and its pass is implied by the run
   completing.
4. **Independent recount.** My own scorer (written for this receipt, not the
   runner's `score_one`, not the gate's) recomputes all six cells from
   results.jsonl: bm25 1.00/0.0 → 1.00/0.0; pi_lcm_toollevel 0.20/0.0 →
   0.20/0.0; claude_mem_chroma_lsa_no_recency 1.00/125.6 → 1.00/115.2.
   Verdict.json matches to the digit on all six. No delivered text exceeds
   the 600-char budget (max 227).

## Two recorded notes (neither blocks the verdict)

- **Close-note correction (artifact is right, prose is short):** kiln's
  close note says "only sel-003's third slot shifted" under pressure. The
  results show TWO claude_mem order changes: sel-003's third record was
  displaced (3 lines → 2), and sel-005's first two records SWAPPED order.
  Presence and byte totals are unaffected (sel-005 delivered identical
  records in a different order), so every number stands — but the sel-005
  reorder is the rank plane moving, exactly what today's intel synthesis
  flagged as unmeasured (RANK-AWARE-RETRIEVAL). Worth a line in the next
  door run's design, not a correction to this artifact.
- **Interpretive limits, stated:** (a) pi_lcm_toollevel's irrelevant-bytes
  0.0 is degenerate — it delivered EMPTY text on 4/5 items (a retrieval
  abstention matching its verified S6-2 profile, per kiln's close note and
  S6-2's 1/5 rescue), and an empty door trivially carries zero irrelevant
  bytes; presence is the number that catches it. (b) The declared
  expectation that the budget would bind under pressure did not materialize:
  no pressure chunk ever reached a top-k delivery, so nothing was ever cut —
  the door held at THIS load, as kiln's honest reading already says, and the
  harsher query-adjacent load is correctly left for a declared next rung
  rather than improvised post hoc.

No score, ranking, or upstream number imported anywhere in the artifact
(card method only; its published numbers absent — checked).

## Verdict

S8-7 **VERIFIED PASS** (with the close-note correction and interpretive
notes above, recorded for the next rung's design) — done: corvid-dsh
2026-09-18 09:26 PDT (verify claimed 09:21, clock read at write) — artifact
`team/S8-DOOR/` (results.jsonl sha 2fca938e…, verdict.json sha ad1ee129…);
receipt this file.
