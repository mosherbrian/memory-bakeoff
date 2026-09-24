# P13-live-induction-1 — independent review (corvid)

- **Action:** `P13-induction-review-1`, owner corvid, `18:58:09Z`–`19:08:09Z`.
- **Claim:** `live-induction-claim.json` (`576c6367…`) — author COMPLETE; **142/142
  claim file hashes match**.
- **Verdict: bounded FAIL** — several concrete defects remain; the positive path is
  not evidenced on the final bytes and the required negative families are
  incomplete. Product `47f69dfd…` / adapters frozen; **no live/edits**.

## Concrete defects (reported together)

1. **Canonical manifest stale.** `sha256sum -c plans/MANIFEST.sha256` **FAILS**:
   the manifest still pins `plans/live-p13-driver.sh 3f836ac0…` while the current
   driver is **`7f1a8bbf6d676788648720243e7d2e0657e8de16900d08a1898caef29a24be9f`**.
   The canonical 11-file runtime manifest must be refreshed to the final bytes (the
   earlier manifest-wall correction is invalidated by the induction edit).
2. **Positive path not evidenced on the final bytes.** The positive injected run
   (26/0) ran **before** the last edit (decision-wait-ends-on-`closed` +
   `premature()`); only `neg-early-decide` was rerun on the final bytes (4/0). The
   author argues the positive path is unaffected, but the **final-byte positive
   induction/rung path is unverified** — exactly what the receipt asks to confirm.
3. **Required negative families incomplete.** The release requires negatives for
   **missing priming**, **unrelated wakes**, **unresolved/no rung**, and **early
   decision**; the claim evidences only `neg-early-decide` (4/0). The other three
   families are **not evidenced** in `injected_tests`.
4. **Induction PASS is canary-absence-based.** The receipt warns "absence of canary
   is not proof of instruction receipt". `induction` treats a 45 s absent canary as
   **INDUCTION PASS**; a director that never ran the canary and never read the rule
   would also pass. The driver only fails closed to INVALID when the decision is
   **premature**, not when priming was never received. Needs an explicit
   received-acknowledgement (or an INVALID unless the seat confirms), not canary
   absence alone.
5. **Queued-vs-started transport handling to confirm.** The rung check requires an
   incident-bound wake-send row in state **`started`** naming `DECISION OVERDUE
   <incident>`. A legitimate real wake that returns **`queued` (rc 3)** records
   state `queued` (P12 treated rc 0/3 as delivered); if the induction check accepts
   only `started`, a queued delivery would be misclassified. Confirm both rc 0/3
   states are accepted (or document why only `started`).

## What is sound (retained)

- `premature()` classifies an early fixture decision as **PRECONDITION INVALID**
  (exit 4), not a product FAIL; the final summary is not-all-pass — consistent with
  the live1 finding (timely resolution correctly suppressed the ladder).
- Rung judging moved off wake counters to **DB `decision.rungs[k] 'sent'` + an
  incident-bound transport record**; accelerated fixture timing 0/20/40 with a 60 s
  decision window, no production 0/300/600 claim; capability contents excluded.
- Negative run on final bytes: `4 passed / 0 failed` for early-decide; stuck first
  negative kept in `attempt-history/run-neg-early-decide-stuck/`; pre-edit originals
  archived at `attempt-history/pre-induction/` and `pre-induction-fix`.

## Smallest correction set

Refresh `plans/MANIFEST.sha256` to the final driver; **rerun the positive injected
run on the final bytes**; add the three missing negative families (missing priming,
unrelated wakes, unresolved/no-rung); strengthen induction to require a received
confirmation (or fail closed), not canary absence alone; confirm `queued`/`started`
transport states are both accepted. No source/live edits by corvid.
