# Blind-verdict adjudication — the two INCONSISTENT Task-B verdicts are a criterion artifact

**Author:** Corvid (`worker-glm-dsh3`), package preparer
**Date:** 2026-09-14 · **Cost:** $0, local, read-only
**Context:** the blind verdicts (`team/BLIND-VERDICTS-conductor-claude.md`) are
recorded, so the blindness window is closed and the verdicts can be adjudicated.

## What the judge returned

- **Task A (trigger firing decisions):** every item `AGREE` — the observed fire
  decisions are independently confirmed against the trigger rule.
- **Task B (correction-event classifications):** `RC-57d592c0` and `RC-d0767deb`
  marked `INCONSISTENT`, basis "class env_fact_correction with env_fact_kind
  null"; the rest `CONSISTENT`.

## Adjudication — the basis is a defect in the criterion I supplied, not in the events

The criterion file I put in the package
(`team/blind-package-20260914/row41-class-definitions.md`) says `env_fact_kind`
is "populated where the class is `env_fact_correction` and `null` otherwise".
That is **stricter than the frozen schema**:

- `SPEC-OUTCOME-PROTOCOL.md` §5.1 defines `env_fact_kind` as **nullable**.
- The exporter computes it only for `env_fact_correction` but its helper returns
  `None` when no kind pattern matches
  (`export_bundle.py:53 _env_fact_kind(...) -> str | None`; line 109).
- The §5.2 leak gate accepts it: `outcome_leak_gate.py:36 ENV_KINDS = {None,
  "path", "env_var", "port", "url", "version", "pin", "other"}` — `None` is
  explicitly in the vocabulary, and the gate's rule 5 passes on the emitted
  bundle.

So an `env_fact_correction` with `env_fact_kind=null` is **valid by
construction**: it means no environment-fact kind pattern matched the span — a
**signal** (the correction was detected but its kind was unresolved), not a
structural inconsistency. On the actual schema, all items are consistent, and
the two flagged items are a criterion over-reach on my side.

Independent second anchor: `RC-57d592c0` additionally has `evidence_span_length=0`
and `quoted_speech=true`; both are the exporter's own structural outputs and are
in-vocabulary, so they are likewise signals (an unresolved span and quoted
speech), not schema violations.

## Corrections

1. **For any future reuse of the package**, the Task-B criterion should read:
   "`env_fact_kind` is drawn from the frozen vocabulary **including `null`**; a
   `null` on `env_fact_correction` means no kind matched (a signal)." I did **not**
   edit the shipped package or its hashes after judging — that would post-hoc
   change the criterion the judge used. A corrected criterion lives here.
2. **No change to the bundle, the classifications, or the gate**: all are within
   the frozen schema.
3. The judge's Task-A result stands as an independent confirmation of the fire
   decisions.

## Limits

This adjudicates the **criterion**, not the judge: the two `INCONSISTENT` verdicts
were the correct reading of the rule they were given. The package remains
verdict-clean (`probe_blind_package_scan.py` → 0 findings); this note is outside
the package by design.

— **Corvid** (`worker-glm-dsh3`). $0, read-only.
