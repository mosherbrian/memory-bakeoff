# CSTM next-step 2: cross-session threat field proposal (design only, spark pulse 2026-09-14)

Executes `CANDIDATE-CARD-CSTM-BENCH.md` next-step 2. Grounding: `SPARK-CSTM-BODY-PASS-20260914.md` (26-taxonomy schema, `CSDA@action`/`CSR_prefix`) + `SPARK-MAGNET-GROUNDING-20260914.md` (capability accrual at correlator level).

## Proposed field (per retrieval-scored event, rolled up per correlator)

- `threat_taxonomy`: one of CSTM's 26 kill-chain × operation classes, or `none`. Our-domain subset first: T15/T16/T19/T20/T24/T25/T26.
- `correlator_id`: the session-grouping key (user-ID or task-thread). Scoring rolls up here, not per-session — Magnet's point.
- `rollback_flag`: whether the trace contains a retraction/cover-up of a prior alert (CSTM scores honouring in-band retraction as missed detection — our anti-retraction shape).
- `lineage_present`: whether the acting memory record carries supersession lineage (CSTM names missing lineage the enabler of semantic laundering — our provenance gate, stated adversarially).

## Scoring (design)

- Detection counted `CSDA@action`-style: flagged before action-on-objective, per correlator.
- Report alongside `CSR_prefix`-analogue only if a serving-stability question arises; not required for v1.

## Limits

- Design only, no run, no threshold. Needs security-arm owner + Alice validity seat before any probe build.
- All CSTM rates uncited; taxonomy borrowed as shape, not as claim.

$0, synthesis of existing receipts, no Muse batching. — muse-drafter (Spark)
