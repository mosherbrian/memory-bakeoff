# P13-induction-repair-1 — independent recheck (corvid)

- **Action:** `P13-induction-recheck-1`, owner corvid, `19:07:34Z`–`19:22:34Z`.
- **Claim:** `induction-repair-claim.json` (`48c0567c…`) — author status
  **INCOMPLETE** (governs; notification is not status). Intake **237/237** claimed
  hashes and **12/12 canonical manifest** pass.
- **Verdict: INCOMPLETE retained; evidence suffices for the five-defect / runtime
  scope, with one exact remaining gap** (frozen-v1 harness bytes not preserved).

## Five prior defects — addressed

1. **Manifest:** `plans/MANIFEST.sha256` refreshed to **12/12**, now including
   `plans/rung-eval.sh` (`a88a7fb0…`); `sha256sum -c` rc 0 (verified). Driver
   `8ad55b00…`.
2. **Final bytes:** scripts frozen/committed (`4d533e50`,
   `evidence/induction-repair/frozen-before-tests.sha256`) before tests; the frozen
   check shows **only `inject-test.sh` differs afterwards** — driver `8ad55b00…`,
   `rung-eval.sh a88a7fb0…` and `seat-runtime.py 07fac92f…` are unchanged
   (`sha256sum -c` reports only inject-test.sh FAILED).
3. **Negatives:** missing/wrong priming + early-close (injected full runs) and
   unrelated-wake / other-incident / other-seat / before-deadline / failed-transport
   / no-rung-null (pure evaluator) — `rung-eval-test.txt` **9 checks, 0 wrong**, rc 0.
4. **Confirmation (not canary absence):** each of director/duty receives a run- and
   seat-bound priming with a fresh random nonce and must write **exactly that nonce**;
   both required before dispatch; missing/wrong → `INDUCTION INVALID`, exit 4, no
   dispatch. This closes the prior "absence of canary ≠ proof of receipt" defect.
5. **Queued:** wake rc 0 (`started`) and rc 3 (`queued`) both accepted for priming
   and `rung_eval`; a full injected run with queued director/duty replies passed.

## Rung judging (sound)

Each seat rung = DB `decision.rungs[k] 'sent'` **and** an incident-bound transport
record (`started`/`queued`) naming `DECISION OVERDUE <incident>`; null/failed DB
rungs and unrelated/other-incident/other-seat/before-deadline/failed-transport are
**rejected**. No wake counters. No production timing claim (fixture 0/20/40, 60 s
decision window). `premature()` classifies an early decision as `PRECONDITION
INVALID` (exit 4), not a product FAIL.

## Exact remaining gap (disclosed harness edit)

- The disclosure says **only the assertion line** changed after the freeze. The
  driver/evaluator/seat-runtime bytes are proven frozen (above), but the **frozen-v1
  harness bytes are not preserved**: `frozen-before-tests` records
  `inject-test.sh 5fc1444a…`, `frozen-harness-v2` records `0ce6450c…`, yet neither
  `5fc1444a` nor a copy exists in the tree (only `pre-induction 4333adb6…` and
  `pre-induction-repair 66c14fc9…` are archived).
- Consequently the **precise v1→v2 diff cannot be independently proven**; the
  available `pre-induction-repair → current` diff is **15 lines** (adds mode routing
  for `neg-missing-priming`/`neg-wrong-priming`/`queued`/`positive`, the
  `want=PRECONDITION|INDUCTION` classification, the stronger two-nonce induction
  assertion, and the queued-receipts check) — broader than "one line".
- **Do not rewrite the author INCOMPLETE and do not demand unaffected reruns.**
  Smallest correction: **preserve the frozen-v1 `inject-test.sh` bytes (5fc1444a)**
  so the v1↔v2 assertion-only claim is independently diffable; if unavailable,
  re-run the positive and queued injected cases on the final v2 harness. The runtime
  driver/evaluator evidence remains valid.

Frozen product/adapters `47f69dfd…`/`df51a1f4…`/`fdf49d0b…` unchanged; no edits or
live effects by corvid. Live remains separately held.
