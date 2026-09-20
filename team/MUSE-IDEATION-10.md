# Muse ideation batch 10 — review throughput, pre-authorization, queue triage, decision backlog

**Tag:** `batch10` · **Prompt sha256:** `28c02b14aa7dba6edac0c1c2466fc092faf52a15ef9dbdbedeecca4e2b1736b8` (`PROMPT10.txt`, recorded before send) · **Date:** 2026-09-14
**Authorization:** standing Muse cadence (Corvid thread, `RD-THREADS.md`; original Brian/GiLMore approval 2026-09-12, `scripts/experiment_20260912_muse_ideation/PROTOCOL.md`).
**Fitted cause:** today produced many validated diffs/findings faster than the
owner could act (`CORVID-PENDING-DIFF-APPLICABILITY.md`, the decision register,
the declaration loop). This batch is about that bottleneck, not about memory
engines.
**Content policy:** public methodology only; no project detail, paths, results, or
strategy.

## Prompt (verbatim, preregistered)

See `PROMPT10.txt`: four public questions — (1) review throughput when workers
outpace a single reviewer; (2) safely pre-authorizing small reversible
already-validated changes; (3) telling "awaiting a decision" from "unowned or
forgotten"; (4) keeping a decision-backlog register decision-ready instead of a
graveyard.

## Receipt

One tagged call, `ready=true`, `end_seen=true`, latency 29.28 s, 3,800 assistant
chars, no block signals. Meter `spent $0.0274` before and after; `openrouter
$0.00 today` — cost ≈ $0.00. Receipts:
`scripts/experiment_20260912_muse_ideation/receipts/batch10-*`.

## Dispositions (Muse proposes, Corvid disposes)

1. **WIP limit + aging SLA; oldest-first cadence** — **ACCEPT** `[I]`, merged
   with 3. The register/queue should carry an **arrival date** and a
   **next-review date**, and the owner reviews oldest-ready-first. Bounded probe:
   add those two fields to the decision register and publish the count of items
   over SLA (mine to build).
2. **Pre-authorization memo with 4 binary gates + auto-log** — **ACCEPT** `[I]`,
   strongest for the live bottleneck. A change may skip serial review iff it
   (1) touches only listed paths/types, (2) reverts in one tested command,
   (3) passes named automated checks on the artifact, (4) is logged before merge.
   Bounded probe built: `team/PREAUTH-REVERSIBLE-CHANGES-DRAFT.md`, with the two
   currently-pending diffs as worked exemplars.
3. **Every open item: Owner + Decision-needed + Next-date; weekly blank/overdue
   scan** — **ACCEPT** `[I]`, merged with 1 (the two controls are the same
   register hygiene).
4. **Decision-ready definition + inflow/outflow rule; expire untouched entries
   to Rejected-stale** — **ACCEPT** `[I]`, merged with 1/3. The register gains a
   "decision-ready" predicate (owner + decision + options + recommendation +
   date) and a retire-at-least-as-many-as-arrive rule; publish
   ready/unready + arrivals/retirements.

**Net:** 3 ACCEPT / 0 DUPLICATE (1+3+4 merge into one register-hygiene probe; 2
is its own memo). No ACCEPT is a finding until its probe runs; the pre-auth memo
exists and the register-hygiene fields are the remaining build. Second seat open
(Alice/Assay).
