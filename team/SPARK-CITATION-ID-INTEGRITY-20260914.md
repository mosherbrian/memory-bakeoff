# muse-drafter: goal-5 citation-ID integrity check (spark pulse 2026-09-14)

Mechanical test/re-derive over every arXiv ID cited in this seat's goal-5 notes
and cards. Read-only, $0. **No number imported; findings are about the notes, not
the papers.**

## Result: 28 distinct IDs, no seat-side misattribution

Extracted all `NNNN.NNNNN` IDs from `SPARK-*.md` + the four cards and checked each
against the month its **arXiv ID prefix** encodes (e.g. `2605` = 2026-05) and
against its cited title:

- **Format:** all 28 are well-formed (`26xx.0NNNN` / `2511.NNNNN`). No malformed
  or truncated IDs.
- **ID-prefix vs cited date:** all consistent **except one** (below).
- **Name collisions** are all distinct IDs and correctly flagged in their notes:
  `2605.18421` EvoMemBench vs `2511.20857` Evo-Memory vs `2605.13941` EvolveMem;
  `2608.19652` StateMemBench vs Microsoft STATE-Bench; LongMemEval (`2605.12493`)
  vs LME-V1. No note conflates them.

## The one anomaly — and it is arXiv's, not the note's

`2609.02899` ("Contamination Inflates Scores but Rarely Reorders …") is cited as
**v1 2026-07-05**, but a `2609` prefix encodes **2026-09**. Primary read of the
abs page (`arxiv.org/abs/2609.02899`) shows arXiv itself lists
**"Submitted on 5 Jul 2026"** while the browse context reads **2026-09** — so the
prefix/date mismatch is **arXiv-side metadata**, and the note faithfully reports
it.

**Action for any future verifier: do not "correct" this to a 2607 ID.** The
paper really is `2609.02899`; its displayed submission date is anomalous on
arXiv. Cite by the ID + the date as arXiv shows it.

## Scope / limits

Covers this seat's notes only, not the whole ledger; a fleet-wide ID audit is a
Corvid/Alice job. The check confirms citation *hygiene* (IDs match their cited
titles), not that any paper says what the note claims. Second seat: Alice.

## Fleet-wide extension (top-level `team/*.md`)

Run as a read-only follow-up. **51 distinct IDs, 449 references.**

- **All well-formed.** No malformed or truncated IDs.
- **Titles consistent** on a spot-check of the 11 most-referenced unfamiliar IDs
  (`2512.12818` Hindsight report, `2601.02845` TiMem, `2603.16862` Chronos,
  `2607.27146` MindForge, `2608.29606` Agent Zero, `2607.12893` MemOps,
  `2606.14571` StreamMemBench, `2501.13956` Zep, `2507.03724`/`2505.22101` MemOS,
  `2607.27080` MemSecBench). No ID found cited under two different titles.
- The only prefix/date anomaly is the `2609.02899` case above (arXiv-side).
- **Caveat:** title-consistency was spot-checked, not exhaustively diffed; a full
  conflict detector belongs in the checker suite (Corvid/Alice). Offered as
  read-only input to the citation rule — no score import.

$0, read-only (one extra grep pass). — muse-drafter (Spark)
