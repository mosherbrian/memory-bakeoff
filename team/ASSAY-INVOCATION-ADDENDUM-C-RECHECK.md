# Assay re-check — Addendum C (B3-computable schema + harm controls)

**Verifier:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static read
**Subject:** `team/DESIGN-INVOCATION-BENCHMARK.md` Addendum C (design sha
`547741c1…` → **`42376c0c…`**), closing my §11 second-seat findings.
**Verdict: C1, C2, and both minor notes are properly closed — PASS.** One
residual (**R1**): the primary formula and the §4.2 deadlines still order by
wall-clock `at`, contradicting B3/Addendum C's own "`at` … never orders".

## Confirmations (fixes landed)

- **C1 — persistence is now computable.** §3's event row carries the B3 tuple
  `{channel, mechanism, reasons, record_ids, seq}` **plus**
  `context_ids_at_action` (L214–220); adapter contract item 4 adds
  `context_ids_at_action(turn)` (L242); §4.2 `CBMR` reads "present in
  `context_ids_at_action`" (L276–277). `FBMR_persist` is now derivable. The
  adapter's item 2 states the injection boundary is harness-owned and the
  `pi-change-trigger` log is **corroboration only** (L235–239).
- **C2 — harm controls added.** §5 adds `serve-stale` (`stale_use=1`) and
  `serve-prohibited` (`prohibited_present>0`) (L327–328), and the
  instrument-failure condition now fires if they register no harm (L334–337).
- **Minor 1:** §11 item 1 now reads "programmatic per-system FBMR from the
  **harness-observed injection events** (the trigger/fire log is corroboration,
  per B3)" (L451–454); the plain-English block matches (L29).
- **Minor 2:** §4.4 `stale_use` is stated as the programmatic conjunction
  (deprecated delivered **and** wrong action), explicitly not causal (L299–301).

## R1 (residual) — §4.1/§4.2 still order by `at`

Addendum C states "`at` is logs-only and never orders", but the written primary
is unchanged:

```
L263: FBMR_topic = |{ m in L : a proactive_topic event with at <= deadline(m) }| / |L|
L275: FBMR_any  = any fired event at/before deadline / |L|
L276: CBMR      = relevant record delivered at/before deadline
L279: ExplicitBefore = an explicit_call at/before deadline / |L|
```

B3's frozen predicate is `… ∧ e.seq < action_seq(M)` (strict, equal is not a
fire), and the 23/23 contract regression encodes that. As written, an
implementer coding §4.1 from the formula would use wall-clock ordering and
re-introduce exactly the tie/clock ambiguity B3 closed. The fix is one line each:
rewrite the primary as the B3 predicate (or at minimum `e.seq < action_seq(M)`)
and the §4.2 deadlines as `seq < action_seq`. Addendum C's "No §4.1 formula
changed" is the source — it should have changed, or the formula should
explicitly defer to B3.

## Limits

- Static read; no runs. I did not re-adjudicate the harm controls' values, only
  that they are specified and tied to the failure condition.
- The `context_ids_at_action` field is harness-observed, so it is not gameable by
  the system under test; absence fails closed via the required-fields list.

## Receipts

- Design: `team/DESIGN-INVOCATION-BENCHMARK.md` §3 (L208–246), §4.1 (L263),
  §4.2 (L275–279), §4.4 (L299–301), §5 (L327–337), §11 (L451–454), Addendum C
  (L641–664).
- Prior: `ASSAY-INVOCATION-BENCHMARK-VERIFY.md`, `ASSAY-B3-CONTRACT-REGRESSION.md`.

— **Assay** (`worker-glm-dsh2`). No tree modified.
