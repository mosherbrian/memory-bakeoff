# muse-drafter proposal: a class-graduation rule for the §5.1 event vocabulary (2026-09-15)

**Proposal only — no spec edit.** Resolves the *recurring* `i_said` question at
the policy level: the current choice (exclude vs. add `i_said`) has no criterion,
so it will recur with the next newly-detected class. $0, synthesis.

## Problem

`SPEC-OUTCOME-PROTOCOL.md` §5.1 freezes the event-class enum
(`negation|actually|env_fact_correction|wrong|repeated_instruction`), but the M4
detector emits classes on its own schedule (`i_said` at scale). The gate
correctly fails closed on an unlisted class; the exporter now offers
`--exclude-class`. What is missing is **when an excluded class is allowed into
the schema** — currently an ad-hoc owner call.

## Proposed rule (add to §5.1 as a "class graduation" clause)

A detector class may be **added to the §5.1 enum** only when both hold:

1. **Volume** — the class has ≥ *K* **adjudicated** events in a scale-corpus run
   (candidates alone do not count). Suggest *K* = 20, or state a different K.
2. **Measured precision beats its floor** — a per-class precision estimate exists
   from adjudication, and its **lower confidence bound** exceeds the stated
   "excluded" base rate (the reason it was excluded — for `i_said`, the pilot
   found 0 genuine firings). If not, the class **stays excluded** and the export
   reports the exclusion count (the existing fail-closed reconciliation already
   prevents the exclusion from masking a mismatch).

Corollary: the pipeline's stats schema must **pin its class list** so the spec
and pipeline cannot drift again (the scale run dropped `repeated_instruction`
from `correction_classes`; the pilot included it).

## Applying it to `i_said` today

- Scale run (`full-20260913`) produced **10 `i_said` events** and **no
  adjudication** is available in the workspace → rule says **keep excluded**
  (option 2), report the exclusion; revisit when adjudicated.
- The rule makes the owner's include/exclude choice mechanical instead of a
  judgment each time.

## Handoff

- **Spec owner (Assay / QUEUE row 25):** accept the graduation clause + pick *K*
  and the precision floor, if adopting.
- **Pipeline owner (Kiln):** pin the stats class list.
- **Row-41 verifier (Cairn):** the rule is testable — a fixture class below the
  volume/precision bar must remain excluded; one above it must fail the gate if
  omitted.

$0, read-only synthesis; no score import. — muse-drafter (Spark)
