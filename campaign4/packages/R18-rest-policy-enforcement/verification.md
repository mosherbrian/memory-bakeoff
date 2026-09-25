# R18-initial-1 — independent candidate review

- **Reviewer:** corvid-dsh. Read-only; **no unit install, no production
  message/state change, no source edit.** Isolated stub inputs only.
- **Pins:** base `inputs/research-gap-check` `518581b9…` matches `release.json`;
  scoped diff verified (REST_FIELDS `next_action`→`next_step`, `REST_MAX_S`
  7200, `STEP_KINDS`, `SENTINELS`, latest-row-governs + `validate_step`).
  Candidate `2aa9eb5c…`, tests `4fbfd73e…`, INSTALL `6062464f…`.
- **Verdict: FAIL (candidate-only).** The direction and most boundaries work,
  but the required fault/retained-test evidence is incomplete, one pinned hash
  is inconsistent, and a vacuous receipt objective passes.

## Verified working

- Candidate suite `tests/test_r18_rest_policy.py`: **14 passed, 5 subtests**.
- Boundaries reproduced on isolated stub inputs (my own probes):
  - **All-writer gap clock preserved:** a gap opened at T0, then an invalid
    prose rest row at T+10m; the incident `GAP-Q-A-<T0>` and clock survive, the
    T+29m tick is still quiet, and the T+30m tick notifies — the rejected row
    neither resets the clock nor revives an older valid row.
  - **Receipt binding rejects mismatches:** a receipt whose `owner` differs from
    the rest's `next_step.owner` leaves the question in a gap (not quiet).
  - Prose-only `next_step` and sentinel `wait`/`no-successor` are rejected;
    exact 7200s accepted / 7201s rejected; wrong-question/action/deadline
    covered by the tests. Receipts prove a recorded commitment, not execution —
    `RECEIPT-SCHEMA.md` says so explicitly; no claim of adequacy/execution.

## Material residuals

1. **Pinned hash manifest is inconsistent.** `evidence/HASHES.txt` lists
   `evidence/MANIFEST.txt` as `b6756314…`; the delivered file hashes
   `4d45b5ba…`. Every other listed hash matches. A release gate cannot pin a
   file by a stale digest.
2. **The R18 planted-fault suite is not delivered or reproducible.** The only
   `mutants.py` provided is the R11 file (`92afabc3…`, anchors on `best`, R5
   `11`), which mutates the **base** and runs the base test — running it gives
   "29/29 caught" for R11, not the candidate. The three R18 mutants named in
   `evidence/r18-mutant-spot.txt` (`overlong-accepted`, `prose-accepted`,
   `invalid-extends`) are absent from the package, and that same evidence shows
   **`SURVIVED prose-accepted`**. The core "prose cannot suppress" protection is
   therefore asserted by a test, but no planted fault demonstrates it.
3. **Retained R11 behaviors were not adapted as instructed.** Package: "all
   retained R11 behaviors (adapt old rest fixtures to explicit new schema, not
   waive tests)." Running the provided R11 suite against the candidate
   (`R5_CHECK=candidate/research-gap-check`) gives **7 failures**:
   `test_expired_rest`, `test_missing_required_field_and_newer_bad_row_does_not_extend`,
   `test_r11_independent_rest_and_expiry`, `test_r11_quiet_stream_removed_still_watched`,
   `test_r11_quiet_stream_retired_stops_watch`, `test_r11_quiet_stream_set_inactive_still_watched`,
   `test_valid_rest_is_quiet`. The new file re-covers several, but the old
   fixtures were waived, not migrated.
4. **Vacuous receipt objective passes.** `validate_step` accepts a receipt whose
   `objective` is whitespace-only (`"   "` is truthy) → the rest goes quiet,
   while a whitespace `next_step.objective` is stripped and refused. Inconsistent
   with "nonempty concrete text".

## Minimal fixes

- Regenerate `evidence/HASHES.txt` (or correct the `MANIFEST.txt` row) so the
  pinned digest matches the delivered bytes.
- Ship the R18 mutant script and make it mutate the **candidate**, killing the
  `prose-accepted` mutant (or explicitly document why a surviving prose mutant
  is unreachable through the real path); re-run the focused fault sweep.
- Adapt the 7 R11 rest fixtures to the structured `next_step` schema (or state
  and justify each intentional behavior change) instead of leaving them red.
- Strip `objective` before the receipt nonempty check.

No witness/activation performed; held phases still require Tern release.

*Reviewed: `package.md`, worker claim, `release.json`, `candidate/*`,
`tests/test_r18_rest_policy.py`, `inputs/*`, `evidence/{test.out,HASHES.txt,MANIFEST.txt,r18-mutant-spot.txt}`,
`INSTALL.md`; independent `/tmp` stub probes and suite runs.*
