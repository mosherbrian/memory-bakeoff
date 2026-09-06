# Gen112 — a contradiction could pass a control gate. Repaired before any run.

**Nothing was executed.** No reader, model, sidecar, engine, endpoint or GPU.
**The reader question is still OPEN.** Gen112 is not a result.

Frozen: `reader-interference-v3`, `contract_sha256` `c9b4196fcce35bbd…`, at
`results/gen112/attempt1/`. `reader-interference-v2` is recorded
**`SUPERSEDED_AS_RULER / NON_EVIDENCE`** with every Gen111 byte intact.

## The defect

Found by control-plane review of the frozen v2 truth table and grader — **before
v2 ever ran**. One line of my reasoning, written twice:

```python
said_current = case["current_opaque"] is not None and contains_value(...)
said_stale   = case["stale_opaque"]   is not None and contains_value(...)
```

That conflates **"this role's record was not presented"** with **"this value is
not in the answer."**

In `CLEAN_CURRENT` there is no stale record, so `said_stale` was forced false. A
reply of *"41 t/s, previously 27 t/s"* — which contradicts the single record it
was shown — graded `correct_current_answer`. In
`CLEAN_STALE_NEGATIVE_CONTROL` the mirror image graded
`correct_stale_control_answer`.

**Both are control conditions.** A self-contradicting answer could therefore pass
a control gate and silently certify a core as interpretable, which is the one
failure a control exists to prevent. Every downstream Q1–Q4 verdict for that core
would have rested on it.

Both witnesses were reproduced against v2 **before** any repair, and are recorded
in `gen111_grading_defect_audit.json` with their v2 outcomes, their required v3
outcomes, and the root-cause branch.

**No scientific result is lost.** v2 was frozen and never executed. Only the
ruler was wrong.

## The repair

The two questions are now completely separate:

1. **What did the answer say?** `classify_answer(answer, core)` — and note the
   signature. It takes the text and the core name, and **cannot** see
   `current_opaque`, `stale_opaque`, `records`, `context_order`, `condition` or
   `citations`. The defect is not merely unwritten; it is unrepresentable.
2. **Is that correct here?** Decided afterwards, condition-relative, with the
   citation relation computed only once the answer class is known — so citation
   validity can never erase the fact that an answer is `BOTH`.

`BOTH` resolves to `mixed_contradictory_answer` in every non-parser condition,
including both controls. It is never a control pass.

## Verification

| question | result |
|---|---|
| **D1** classification independent of presented records | signature takes `(answer, core)` only; `BOTH` detected in all five conditions |
| **D2** both witnesses repaired | both now `mixed_contradictory_answer` |
| **D3** matrix total and exclusive | **360 rows**, all 9 outcomes reachable, every condition covers all 5 answer classes |
| **D4** controls have one passing form each | `CLEAN_CURRENT` = `CURRENT_ONLY`+`MATCHES_CURRENT`; `CLEAN_STALE_NEGATIVE_CONTROL` = `STALE_ONLY`+`MATCHES_STALE`; `INSUFFICIENT_CONTROL` = `INSUFFICIENT`+`EMPTY` |
| **D5** prompts unchanged | all 20 **byte-identical** to v2, hashes recorded, blinding audit passes |
| **D6** history intact | Gen109, Gen110, Gen111 all verify unchanged |

And the specific proof requested: adding a contradictory canonical value to
either single-record control answer converts it to
`mixed_contradictory_answer`, which fails the gate.

## Unchanged from v2

Four cores, record texts, scopes, configurations, questions, five conditions,
opaque identifiers, prompt projection, parser contract, canonical values,
normalisation, response schema, repetition plan, control-gate policy, and the
prohibition on deriving anything from Gen110 output. v3 repairs grading only.

## The pattern worth naming

This is the fifth ruler defect across three contract versions, and the third
found by review rather than by me. The through-line in all three of mine is the
same: **I let a fact about the experimental setup leak into a judgement that
should have been about the data alone** — record prose standing in for an answer
value, a role-bearing id standing in for a blinded one, and now a missing record
pointer standing in for a missing value.

The v3 repair is shaped against that specifically. `classify_answer` cannot
reach the case, so the next version of this mistake cannot be written in the
first place.

## What this does not establish

Nothing about reader behaviour. No model has been asked anything under v2 or v3.
No prior reader response may be reused or rescored.
