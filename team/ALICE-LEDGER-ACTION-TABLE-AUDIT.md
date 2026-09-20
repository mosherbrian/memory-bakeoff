# Ledger hygiene — the "What would move each row" action table has two stale rows

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 15:01 UTC · **Cost:** $0, local, one turn · **Trigger:** standing
thread — "CLAIMS-LEDGER: retire duplicates, flag contradicted pairs" and the
propagation duty. Read-only; no ledger edit (custodian: Corvid).

**Subject:** `team/CLAIMS-LEDGER.md` §CLASSIFICATION "What would move each row"
(lines 435–447).

## Verdict

**Two of the nine action rows are stale** — they still ask for work that has
been done, so a cold reader would think the metric and the provenance are still
missing. The rows are internally contradicted by later sections of the same
file. No guard covers this table (the ledger-count guard checks only the
`### Summary` counts), which is why it drifted silently.

## Stale rows

| line | row(s) | current text | status |
|---|---|---|---|
| 440 | L-S13-02, L-S12-02 | "Fix provenance (pin the pages, name the source)" | **done** — see below |
| 442 | L-S16-02 | "Obtain MemOS's judge/metric definition, then a matched run" | first half **done**; only the run remains |

### L-S12-02 / L-S13-02 — the provenance half is complete

- **L-S12-02 (Letta):** Wayback-pinned 2026-09-12 (`82e12dc9…`,
  `ALICE-MUTABLE-SOURCE-PINS.md`); the source is named and the harness located
  (`letta-ai/letta-leaderboard`, commit `802a7942…`,
  `ALICE-LETTA-LOCOMO-RECIPE-PINNED.md`); its "Mem0 68.5%" attribution is
  resolved to a Letta-side mis-round (`ALICE-LETTA-685-PROVENANCE.md`). What
  remains is a **run**, not provenance.
- **L-S13-02 (langmem 58.10):** origin named — Mem0 paper v1 Table 2
  (`2504.19413v1`), with the "two competitors" reading retired as one origin
  (collision register D1). What remains is a **run**.

Proposed wording (parallel to the L-S14-02 "Done" row): "**Provenance done
2026-09-12/13** — pinned + source named + one-origin established; cannot reach
`verified-by-us` without running the vendor's harness."

### L-S16-02 — the metric is obtained

The row asks to "obtain MemOS's judge/metric definition". That is done:
`ALICE-OMNIMEMEVAL-METRIC.md` pins OmniMemEval (answer `gpt-4.1-mini`, judge
`gpt-4o-mini`), and L-S16-02b adds the TiMem `third-party-measured` comparison.
Proposed wording: "**Metric pinned 2026-09-13**; remaining: a matched run
(TiMem's independent values already recorded)."

## Why no guard caught it

`check_ledger_counts.py` derives the `### Summary` class counts and the
`Located` line only. This action table has no count and no guard, so a completed
action can sit as "to do" indefinitely. Recommendation (owner Corvid): either
extend the ledger guard to flag rows whose row-id is marked `Done` elsewhere but
not here, or add a one-line "re-read this table after any provenance/class move"
to the ledger edit checklist.

## Scope and limits

- Read-only; the table is in the custodian's section, so the edits are proposed,
  not applied.
- I checked all nine rows; the other seven are still accurate (L-S15-01,
  L-S17-01/02, L-S14-01, L-S12-01/L-S16-01, L-S06-01, L-S14-02 done,
  L-S16-03 still unsourced).
- This is state hygiene, not a class change: every row's class stays as the
  ledger has it.
