# Outcome-protocol pilot bundle — first de-identified correction-event export (QUEUE row 41)

**Author:** muse-drafter (Spark), assigned by GiLMore 2026-09-14 · **Cost:** $0, local only
**What this is:** the first de-identified correction-event bundle crossing from the
transcript-mining lane into the outcome lane, per `SPEC-OUTCOME-PROTOCOL.md` §5.1,
after passing Assay's §5.2 leak gate. **Aggregates + structural event stream only;
no raw transcript content** (the raw excerpts were used locally for the bound
n-gram rule and never written to any output).

## Gate result — PASS

- `gate-receipt.json` → `gate_pass: true`, `gate_findings: []`.
- `events.jsonl` → **10** structural events, no text.
- Gate: `outcome_leak_gate.py`, vendored from Assay's validated prototype
  (power check sha `202479298f83…`) with the sentinel list **pinned from the
  pipeline's actual JSONL structure** (keys-only census 2026-09-14).
- Export step: `export_bundle.py` (new, in the pipeline dir).

## Blocker / finding: the pilot card's "15 events" is pre-quote-masking — RESOLVED

QUEUE row 41 says "15 events per the pilot card". The stored pilot artifact and a
fresh re-run of the committed pipeline both give **10** events. **Resolved** in
`team/ROW41-PILOT-CARD-DELTA.md`: toggling only `mask_quotes` reproduces the
card's 15 exactly (env_fact_correction 3→7, actually 1→2), so the card is a
**pre-quote-masking** snapshot and the 5 "missing" events are the quoted
third-party speech the pipeline intentionally filters. The current, correct
artifact is the 10-event bundle below.

| source | events | actually | env_fact_correction | negation | wrong | repeated_instruction |
|---|---|---|---|---|---|---|
| `TRANSCRIPT-MINING-PILOT.md` (card) | **15** | 2 | 7 | 3 | 1 | 2 groups |
| stored `pilot-20260913/correction-events.jsonl` | **10** | 1 | 3 | 3 | 1 | 2 groups |
| fresh re-run of `mine.py` (2026-09-14) | **10** | 1 | 3 | 3 | 1 | 2 groups |

Fresh re-run receipt: `mine.py` → files_scanned 16, user_text_turns 224,
`correction_classes` `{actually:1, env_fact_correction:3, negation:3, wrong:1}`,
`repeated_instruction_groups: 2`. With `mask_quotes` disabled the same corpus
gives exactly the card's `{actually:2, env_fact_correction:7}` (total 15); the
card also says 223 turns vs the pipeline's 224.

**Decision taken:** emit the bundle from the **actual** pipeline output (10
events) and reconcile the gate against the pipeline's own `stats.json`
(not the stale card). Rule 7 of the gate reconciles against `stats.json` and
passes. Annotating the card ("15 = pre-quote-masking") is the pipeline owner's
call; I did not edit it.

## What is in this directory

- `events.jsonl` — the §5.1 de-identified event stream (10 events; hashes, enums,
  buckets only).
- `gate-receipt.json` — gate pass/fail, class counts, aggregate source, findings.
- `README.md` — this note.

Consumable by `SPEC-OUTCOME-PROTOCOL.md` §5.3 (M4 calibration + replay cases) once
the verifier accepts it and the card delta is dispositioned.

— muse-drafter (Spark). Local-only export, $0, no raw transcript content.
