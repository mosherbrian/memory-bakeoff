# R18-repair-1 — independent recheck

- **Reviewer:** corvid-dsh. Read-only; **no install, witness, production state
  or notification.** Isolated stub inputs and inert probes only.
- **Intake:** worker claim `ex-R18-repair-1-w1.json`; **all 9 claimed artifact
  hashes recomputed equal**; `HASHES.txt` entries **all match actual bytes** and
  it does **not** list itself (acyclic, no self-referential digest). Initial
  FAIL preserved at `attempt-history/initial/verification.md`.
- **Verdict: PASS — candidate-only.** Witness/activation remain HELD for
  separate Tern release.

## Repairs verified

1. **Whitespace objective refused.** `validate_step` now strips the receipt
   objective before the nonempty/sentinel checks. My probe: a rest whose receipt
   `objective` is `"   "` → the question stays in a gap (`Q-A: gap 0m`,
   incident `GAP-Q-A-<T0>`), not quiet. A nonempty objective still goes quiet.
2. **Candidate-targeting mutant proof.** `tests/mutants_r18.py` mutates
   `candidate/research-gap-check` (not the base) and runs the R18 suite with
   unique anchors; independently re-run → **5/5 caught**, including
   `prose-accepted` and `whitespace-objective-accepted`, plus `overlong-accepted`,
   `invalid-extends`, `receipt-unchecked`.
3. **Migrated retained behavior + labeled changed rule.**
   `tests/test_r11_retained_adapted.py` **7/7 OK**; it adapts exactly the seven
   R11 fixtures that failed before and labels the one intentional change:
   `test_latest_invalid_overrides_old_valid_changed` ("R18 latest-row-governs;
   R11 kept the older valid row"). My independent probe: with an older valid row
   (until T+40m) and a newer row expired at T+8m, the T+15m tick opens a gap —
   the older valid row does **not** revive. A bad `next_step.kind` is also
   refused.
4. **Final hash integrity.** All 9 loop-claimed artifacts match; `HASHES.txt`
   is internally consistent with the delivered bytes and avoids a self-hash.
   `evidence/test.out` (23 passed + 5 subtests) matches my separate runs
   (`test_r18_rest_policy.py` 16 OK; `test_r11_retained_adapted.py` 7 OK).
5. **Unchanged scope respected.** `inputs/*` unchanged (base pin `518581b9…`);
   no install/witness; the receipt still proves a recorded commitment, not
   execution (`RECEIPT-SCHEMA.md` unchanged).

## Residuals (disclosed, not blocking this candidate)

- The full R11-base mutant sweep was not rerun (base untouched; out of scope,
  and the base is pinned). No calendar witness/unit install yet.
- An arbitrary substantive objective can still pass (only nonempty/strip is
  checked) — by design; adequacy remains director/reviewer judgment, and the
  checker does not claim otherwise.

No production effect, no source edit, no live transport.

*Reviewed: `repair-release.json`, worker claim, `candidate/research-gap-check`
(`337521b0…`), `tests/{test_r18_rest_policy.py,test_r11_retained_adapted.py,mutants_r18.py}`,
`evidence/{test.out,r18-mutant-sweep.txt,HASHES.txt,MANIFEST.txt}`, `INSTALL.md`,
`inputs/*`; independent inert probes and suite runs.*
