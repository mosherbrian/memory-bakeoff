# P6-r11 — amendment-2 admission (independent verifier-rejection contract)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r11-amendment2-admission-1` (separate reader ≤10 m)
- **Brief:** `amendment-2-verifier-rejection.md` sha256
  `8647b2c798849698bcfafdb9fd19a3f1091ab6ae8c57c0c63b92436f3507a001`
- **Scope:** independent admission + pinned acceptance cases. No authorship, no
  candidate edit, no live effect.

## Verdict

**ACCEPTED (bounded).** The causal decision is correct and matches the
independent FAIL evidence, the authorized surface is narrow and sufficient, and
the required semantics are implementable without a generic
`E_ARTIFACT_MISMATCH` blessing. Two bounded obligations are pinned: (a) the
committed-worker-reference source must be resolvable from the verify context
using only `turn_handoff.py`; if it is not, kiln returns the exact blocker
rather than widening the module set; (b) the negative acceptance cases must be
genuinely executable, not prose. Conditional kiln release follows only after
this admission and the pinned cases are confirmed.

## Pin resolution (all resolve)

- Prior FAIL/reproducer commit `70da7500c2a12d8068c89157db3650126f851c5b`;
  source baseline `05eba448`; entry `candidate/src/case_entry.py`
  `2504e07e38de…`; review `candidate-review-completion-1.md` `4c6990cd4251…`;
  `concrete-cases.md` `db840dd7…`; r9 frozen parent `f1d7c86`; governing
  `4be99bf`/`84f094e`/`883107e`/`650830c`/`b2384d7`/`7abab5f`/`58704e9`.
- Original r11 pins/constraints persist; no retroactive PASS, no scope change.

## Causal correctness

Independently reproduced (review `4c6990cd…`, evidence bundle): worker claim
`ex-61c76706a734.json` completed with `out.bin 46409ea6…`; `handoff-done`
committed; `corrupt-after-worker` then replaced the bytes (`9809428b…`) **after**
commit and **before** verifier recompute; the verifier was dispatched, produced
an end, and wrote `exv-61c76706a734.json` `outcome:"failed"`,
`check_detail:"hash mismatch: out.bin"` referencing the pre-tamper hash. The
mismatch is therefore a genuine rejection. `turn_handoff.run_handoff` invokes
`recompute_artifacts` **before** reading `outcome`, so
`E_ARTIFACT_MISMATCH` routes to `_recover` (owned-recovery/escalation) — the
defect the amendment targets. The amendment's premise (neither worker replay nor
a reason to disable recomputation) is confirmed.

## Authorized surface

- Modify **only** `candidate/src/r3harness/turn_handoff.py` **in addition to**
  the already-allowed `candidate/src/case_entry.py`; tests/plan/manifests/
  reports allowed. `harness.py`, `host_adapter.py`, lifecycle/store/ingress/
  validator/driver and frozen parents unchanged.
- If a rejection cannot be propagated without editing another module, kiln must
  return the exact blocker before changing it. No duplicated mini-verifier in
  `case_entry.py`.
- **Feasibility note (accept):** verified rejection is definable as
  `outcome=="failed"` on a bound verify-run where the claim's declared expected
  hash equals the **committed worker hash** recorded in the worker handoff
  intent (`handoff-intent:<worker_action>:<worker_execution>` carries `hashes`),
  while the independently recomputed on-disk bytes differ. The verify context can
  locate that intent by matching `verify_action`/`verify_execution`; if that
  lookup is not reachable inside `turn_handoff.py`, obligation (a) applies.

## Pinned acceptance cases (extend `concrete-cases.md`; no tailoring)

Baseline old-fail assertions are preserved verbatim and must not be re-labelled
new-pass. Corvid independently mutates at least one reference/failed claim not
supplied by kiln.

**Positive (new-pass on repaired bytes):**
1. FV-W (worker 18 s): authenticated durable rejection; post-commit before-check
   tamper with distinct expected/observed hashes persisted; `accept-open`; never
   `COMPLETE`; exactly one worker + one verifier send; no worker rerun.
2. FV-WV (worker 18 s, verifier 18 s): same, through verifier observation.
3. QR-W / QR-WV (worker >8 s, verifier >8 s): quiet/reopen correctness retained —
   setup genuinely commits, observation/reopen yields `duplicate-end-ignored`,
   no new dispatch, no repeated alarm.

**Negative (must never become verified rejection):** forged/missing route;
wrong action/execution/role/incarnation; invented expected hash; completed claim
with mismatch; failed worker; cancelled/malformed claim; and a `failed` verdict
**without** demonstrated mismatch. A `failed` verdict alone cannot satisfy the
deliberately-corrupted-artifact case.

**Durability / bounds:**
4. Replay and reopen preserve exact rejection identity/evidence with no duplicate
   dispatch, no second verdict effect, no repeated escalation; rejection logic
   idempotent under persisted state.
5. Expiry / stricter outer stop remains bounded owned disposition (existing
   mechanisms, original grants), no renewed interval or fresh dispatch.

**Gate / packaging:**
6. Whole retained 34-test gate **plus new executable tests** on final bytes, run
   deliberately with real time (prior 34 ≈14 m; a 120 s probe cannot justify
   exhaustion); record actual command, stdout, return code, times, residuals; no
   retry-until-green, skipped failure, fabricated onset, simulator shortcut or
   live fixture.
7. No manifest self-entry and no circular self-hash; bind the manifest externally
   from claim/receipt with mechanical hashes; all paths local and correct;
   supply an actual `candidate/stagec-plan.json` and exact proposed commands, not
   prose; preserve baseline old-fail tests and add genuine new-pass assertions.

## Bounds

ONE corvid admission/checklist ≤10 m (this); conditional ONE kiln ≤40 m (new
execution `P6r11-rejection-1`); ONE independent corvid ≤30 m on its own clock.
Ceilings `955worker/670verifier` → `995worker/700verifier`. Prior attempt grants
remain spent history; an early return is not full elapsed use; no automatic
further repair or clock reset. Candidate-only: zero live/preparation/witness
grant. The two missing control mechanisms (lost-completion, queued/ambiguous)
remain outside scope and unresolved.

## Effect

Admission **ACCEPTED (bounded)** with the pinned cases and obligations (a)/(b).
No implementation or release is conferred by this review. Returned to cairn/Tern.
