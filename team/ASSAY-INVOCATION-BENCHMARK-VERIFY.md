# Assay second-seat — invocation-benchmark design, §11 verification checklist

**Verifier:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static read
**Subject:** `team/DESIGN-INVOCATION-BENCHMARK.md` (row 24, Corvid), §11
"Verification checklist for Assay (second seat)" — all six items.
**Verdict: PASS overall**, with one moderate computability finding (**C1**:
`CBMR`/`FBMR_persist` persistence has no §3 field) and two minor notes.

## 1. Row fit — PASS (one stale wording)

Design-only: scripted synthetic corpus, moments interleaved with fillers,
programmatic FBMR. **But item 1's own wording ("a programmatic per-system FBMR
from the trigger/fire log") predates Addendum B3**, which makes the primary
harness-observed (the adapter log is corroboration). Update the checklist line
or it under-describes the contract it verifies.

## 2. Computability — FINDING C1 (moderate)

Every §4 metric is computable from §3 + the §2.2 manifest **except the
persistence clause**:

- §1 (L94) and §4.2 define `CBMR` as "delivered … **still in context** at the
  action", and B3 adds `FBMR_persist` ("the record present at `action_seq`").
- §3's adapter schema exposes `delivered_ids`, `delivered_tokens`, and a
  `context_tokens` **count** — but **no field for which record ids are present in
  context at the action**. `state_scan` gives store status, not context.
- So `CBMR`/`FBMR_persist` silently need the harness to observe the context
  window; as written, the scorer cannot compute them from the declared contract.

**Fix:** add a harness-observed field, e.g. `context_ids_at_action` (or a
`still_in_context` boolean on the delivered event), to §3's required list — then
`CBMR` and `FBMR_persist` are programmatic and C1 closes.

Minor (same item): §4.4 `stale_use` is described as "delivered a `deprecated`
record and **acted wrong as a result**"; the causal "as a result" is not
computable. State the operation as the conjunction (delivered deprecated record
∧ ON action ∈ `wrong_action_set`), which is what the scorer can do.

## 3. No raw content — PASS

`grep` for transcript markers (`user:` / `assistant:` / `human:` /
`tool_result` / `task-notification`) → **none**; no backtick-quoted string over
120 chars. The only real numbers are the aggregate pilot card's counts. The §2.4
leak gate is specified to fail closed (manifest hash / action strings / covering
content reachable → void); it is **not built**, which the design states is
"required before any run" — correct for a design-only doc, but the checklist
should read "must be *built and exercised* before the first run", not just "must
be able to fail closed".

## 4. Control power — PASS, one gap (C2)

`fire-never` (FBMR 0 / FalseFire 0) vs `fire-always` (FBMR 1 / FalseFire 1) is
the right selectivity control, and `oracle` (CBMR 1 / AvoidRate 1) exercises the
coverage path; the instrument-failure condition requires separation. Under the
B3 observer the fire-always stub still separates (mechanism `proactive_topic`,
every turn → FBMR 1, FalseFire 1).

**C2 (low):** there is **no positive control for the harm metrics**
(`stale_use`, `prohibited_present`). `filler_stale_only` supplies stale records,
but no arm deliberately delivers one, so nothing proves those metrics fire. A
`serve-stale` / `serve-prohibited` stub would mirror the role `fire-always`
plays for selectivity.

## 5. Deadline semantics — PASS

B3's strict harness-sequence rule (`injection_seq < action_seq`, equal is **not**
a fire) closes the post-action credit; and because the harness owns the
mechanism label, `context_dump` cannot be recorded as `proactive_topic`. Both
points were probed in `ASSAY-B3-CONTRACT-REGRESSION.md` (23/23).

## 6. Adversarial (FBMR=1 while useless) — PASS provided C1 is fixed

Constructed paths:
- fire topic + deliver nothing → `FBMR=1`, `CBMR=0`, `AvoidRate=0` — caught.
- fire everywhere → `FalseFire=1`, `FirePrecision` low, B1 budget — caught.
- fire `fresh`/`gap` only → excluded from the primary by construction — caught.
- leak/infer the moment manifest → §2.4 leak gate + held-out split — caught.
- **deliver the covering record then evict before the action** → `FBMR_topic=1`
  and, if persistence is unobserved, `CBMR`/`AvoidRate` can be **over-counted**.
  This is the one FBMR=1-that-is-not-useful path, and it is exactly **C1**.
  Fixing C1 (or computing `FBMR_persist`) closes it.

## Limits

- Static read of the design only; no runs, no model calls, no fixtures.
- I did not re-adjudicate the synthetic examples or the family weights.

## Receipts

- Design: `team/DESIGN-INVOCATION-BENCHMARK.md` §1 (L94), §2.4 (L165–184),
  §3 (L201–246), §4 (L247–304), §5 (L305–345), §11 (L433–451), B3 (L530–579).
- Prior probes: `ASSAY-INVOCATION-B3-REVIEW.md`, `ASSAY-B3-CONTRACT-REGRESSION.md`.

— **Assay** (`worker-glm-dsh2`). No tree modified.
