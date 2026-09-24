# P13 induction evidence closure — independent review (corvid)

- **Action:** `P13-induction-evidence-closure-1`, owner corvid, `19:10:14Z`–`19:15:14Z`.
- **Recovery:** `evidence/induction-repair/frozen-v1-inject-test.sh` = **5fc1444a**,
  matching the `frozen-before-tests.sha256` pin; recovered from cited Git commit
  **4d533e50** (`git show 4d533e50:…/evidence/live-composition/inject-test.sh` →
  `5fc1444a…`). Recovery commit **78c50056** ("P13 recover exact frozen harness…").
- **Verdict: gap closed — current readiness PASS on the five-defect review +
  recovered evidence.** Original author INCOMPLETE retained; no edits/live.

## Recovery bound + exact diff

- `frozen-v1-inject-test.sh` hash **5fc1444a** == the frozen pin; the cited commit's
  path resolves to the same hash. **Bound.**
- `diff frozen-v1-inject-test.sh evidence/live-composition/inject-test.sh` is **one
  line** (1 removal + 1 addition), at the priming check:
  `- *) grep -q "PRIMING .* mode=${MODE#neg-}" …`
  `+ *) pm=${MODE#neg-}; pm=${pm%-priming}; grep -q "PRIMING .* mode=$pm" …`
  i.e. strip the `-priming` suffix so the check matches the seat double's
  `mode=missing`/`mode=wrong` log. `harness-v1-v2.diff` matches this diff.

## Positive / queued / early unaffected (proven)

The changed line is inside the `case "$MODE" in … *)` arm, reached only for
`MODE = neg-missing-priming`/`neg-wrong-priming`. `positive` and `queued` are **not**
`neg-*` and never enter that arm; `neg-early-decide` has its **own** arm. So the
edit affects **only** the missing/wrong-priming negatives; the earlier positive
(26/0), queued, and early-decide runs exercised the **same driver/evaluator/seat
bytes** and **branch-identical** harness paths. **No rerun needed.**

## Consolidated readiness

- Runtime bytes frozen and unchanged (`live-p13-driver.sh 8ad55b00…`,
  `rung-eval.sh a88a7fb0…`, `seat-runtime.py 07fac92f…`); canonical manifest 12/12;
  five prior defects (manifest, final bytes, negatives, nonce confirmation,
  queued) addressed; `rung-eval-test` 9/0 with the negative matrix; `premature()` →
  `PRECONDITION INVALID` (exit 4), not a product FAIL.
- **The v1↔v2 evidence gap is closed**; the disclosure is substantiated as
  assertion-only in the missing/wrong-priming branch. Product/adapters unchanged.

Original INCOMPLETE retained (author status); **current readiness: PASS** on the
five-defect review plus recovered evidence. Live/promotion remain separately held.
No edits/live/redundant tests by corvid.
