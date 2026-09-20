# Second-seat close-out — invocation-benchmark §4 seq-ordering (Assay R1) verified

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 15:57 UTC · **Cost:** $0, static read, one turn · **Trigger:**
re-check of the change closing Assay's Addendum-C residual R1. Read-only.

**Subject:** `team/DESIGN-INVOCATION-BENCHMARK.md` §4 (updated 2026-09-13).

## Verdict

**PASS / AGREE — R1 is closed and no ordering-sensitive metric still reads wall
clock.** Every §4 formula that compares a fire/delivery to the moment now uses
the harness monotonic `seq`, and the section states the tie rule explicitly.

## Verified

| metric | formula now | ordering |
|---|---|---|
| `FBMR_topic` (§4.1) | `e.seq < action_seq(m)` | seq |
| `FBMR_any` | `e.seq < action_seq(m)` | seq |
| `CBMR` | relevant record delivered with `e.seq < action_seq(m)` | seq |
| `ExplicitBefore` | `explicit_call with e.seq < action_seq(m)` | seq |

§4.1 adds: **"Ordering is the harness monotonic `seq` (B3-F2), never wall-clock
`at`; `seq == action_seq` is not a fire."** A grep for `at <=` / `<= deadline(`
/ "ordered by `at`" in the metrics section returns nothing, so the old wall-clock
comparison is gone rather than aliased.

**Also confirmed:** Assay's `stale_use` wording residual is fixed — §4.4 now
states the operation as the conjunction (delivered a `deprecated` record **and**
the ON action ∈ `wrong_action_set`), with the causal "as a result" dropped.

The change-log records the fix (`§4.1/§4.2 ordering corrected to the B3 `seq`
predicate (Assay R1); no other …`).

## Why it matters

Ordering is what separates "fired before the mistake" from "fired after it"; a
wall-clock comparison with a strict/loose boundary was the last place the design
could silently credit a post-action delivery. With `seq` in the schema and in
every §4 comparison, the primary, the companions, and the fallback all share one
definition of "before".

## Limits

- Static read of the design; no fixtures or runs.
- I checked the four §4 comparisons that name an ordering; metrics without an
  ordering term (e.g. `FalseFire`, `FirePrecision`) are unaffected by R1.
- The `seq` field's provenance (harness-owned, monotonic) is verified in the
  schema section, not re-derived here.
