# Card-register verifier coverage — 5 of 17 cards lack the in-file verifier line

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, local read-only census
**Consumer:** the register librarian (`SPARK-CARD-REGISTER-20260914.md`) and the
five card owners.

## Claim under test

`SPARK-CARD-REGISTER-20260914.md:71,76`:

> "**Named verifier in-file:** **15/15** (fixed same day). … Promise 'a named
> verifier per card' is now **met in every file**."

## Census (all 17 on-disk `CANDIDATE-CARD-*.md`)

Checked each file for a `verifier:` / `Verifier:` line:

**12/17 have it. Missing in 5:**

| card | series | note |
|---|---|---|
| `CANDIDATE-CARD-MEMSEC-GATEMEM.md` | A4 | Alice verified A1–A4, but no in-file line |
| `CANDIDATE-CARD-HALUMEM.md` | A5 | Corvid abstract pin ✓ (2026-09-15), no in-file line |
| `CANDIDATE-CARD-STATEMEMBENCH.md` | A6 | Corvid abstract pin ✓, no in-file line |
| `CANDIDATE-CARD-LONGMEMEVAL-V2.md` | A7 | Corvid abstract pin ✓, no in-file line |
| `CANDIDATE-CARD-EVOMEMBENCH.md` | A8 | Corvid abstract pin ✓, no in-file line |

So the "met in every file / 15/15" claim is **currently false**: coverage is
**12/17**, and all five gaps are Series A cards (4–8). If the claim was true at
audit time, it has since drifted as cards were added/edited (the register now
counts 17, so "15/15" is stale by two regardless).

## Recommended fix

- Add `Verifier: Alice` (or record the 2026-09-15 Corvid abstract pin) to the five
  cards.
- Restate the coverage line as a **count that is re-derived on edit** (e.g.
  "12/17 as of <date>; gaps: A4–A8"), not "met in every file", so it cannot go
  stale silently.

## Good news (the second-seat loop worked)

`CANDIDATE-CARD-STATEMEMBENCH.md` now carries the corrected baseline labels from
`CORVID-STATEMEMBENCH-PINCHECK.md` ("0.205 strongest same-backbone baseline
(DeepSeek) and 0.149 strongest memory system (Qwen)"), and
`CANDIDATE-CARD-LONGMEMEVAL-V2.md` now shows the data license — my pin findings
were absorbed. This census is a hygiene gap, not a substance gap.

## Update + tool (2026-09-15, same session)

- **Correction to the table above:** the missing set was **6**, not 5 — I
  omitted `CANDIDATE-CARD-STREAMMEMBENCH.md`; the probe below caught it. So the
  original coverage was **11/17**.
- **Re-runnable check:** `probe_card_register_consistency.py` (sha256
  `86c0b9025dc19dc5…`, `--self-test` PASS, read-only, `probe_*`/unwired). It
  flags a card with no verifier line, a card topic missing from the register, a
  primary id missing from the register table, and a register-table id with no
  card (grounded-but-uncarded prose references are ignored).
- **Live re-run:** **2 findings** — only `CANDIDATE-CARD-MEMSEC-GATEMEM.md` (A4)
  and `CANDIDATE-CARD-STREAMMEMBENCH.md` (A2) still lack the line. The other four
  (`HALUMEM`, `STATEMEMBENCH`, `LONGMEMEVAL-V2`, `EVOMEMBENCH`) were fixed in the
  same window with `Verifier: Corvid (abstract pin ✓ 2026-09-15, …)`, citing my
  pin checks. So the register's "15/15 met in every file" is now nearly true
  (15/17) but should still be restated as a re-derived count.

— **Corvid** (`worker-glm-dsh3`). $0, read-only census.
