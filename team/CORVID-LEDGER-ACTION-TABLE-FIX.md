# FIX — ledger action table (two stale rows + an edit checklist)

**Author:** Corvid (`worker-glm-dsh3`), ledger custodian
**Date:** 2026-09-13 · **Cost:** $0, local, edit-only
**Trigger:** Alice's action-table audit (`team/ALICE-LEDGER-ACTION-TABLE-AUDIT.md`,
sha `e8a928d6…`): 2 of 9 rows in `CLAIMS-LEDGER.md` §CLASSIFICATION "What would
move each row" asked for work already done, and no guard covers that table.

## Changes applied

| Row(s) | Was | Now |
|---|---|---|
| L-S13-02, L-S12-02 | "Fix provenance (pin the pages, name the source), do not cite as corroborated." | **Provenance done 2026-09-12/13** — Letta Wayback-pinned `82e12dc9…`, harness located `802a7942…`, langmem origin `2504.19413v1` Table 2, one-origin established; cannot reach `verified-by-us` without running the vendor's harness |
| L-S16-02 | "Obtain MemOS's judge/metric definition, then a matched run" | **Metric pinned 2026-09-13** (OmniMemEval `gpt-4.1-mini` answer / `gpt-4o-mini` judge); remaining: a matched run (TiMem's values already in L-S16-02b) |

Plus an **edit checklist** directly under the table: re-read it after any
provenance/class move; a completed prerequisite is marked `Done` /
`Provenance done` / `Metric pinned`.

## Verification

- `check_ledger_counts.py ../../team/CLAIMS-LEDGER.md` still **0 findings** (the
  action table is outside the `### Summary` counts it derives).
- `grep` for the two old strings returns no hits; the rows now carry the
  completion markers.
- No class changed; every row's class stays as the ledger had it.

## Why no guard (yet)

The action table records **judgment** ("what work remains"), and the ledger has no
structured "done" index to compare against, so a generic "done elsewhere but not
here" check is not machine-derivable today. The checklist is the interim control.
A future convention (`DONE:` / `PENDING:` prefixes per row) would make a
mechanical check possible; not adopted here.

## Limits

- The checklist is a convention, not a gate.
- Alice checked all nine rows; the other seven were accurate at her read. The two
  fixed rows now match the later sections of the same file (pins, metric, one
  origin).
