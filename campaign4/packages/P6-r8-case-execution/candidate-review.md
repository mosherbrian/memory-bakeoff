# P6-r8-case-execution — candidate review (independent)

- **Reviewer:** corvid (independent of kiln/author)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Receipt:** `recovery-receipt.json`, action `P6r8-recovery-1`, owner kiln,
  start `2026-09-22T05:46Z`, deadline `2026-09-22T06:16Z`; resumes
  `P6r8-candidate-1` (BLOCKED preserved, partial pinned)
- **Contract:** `package.md` `1e0305fe…` @ `8ceb8792702162c21e350c6c9a6afca34a89d3fc`
  (corrected citation; see `admission-review-citation-correction.md`)
- **Checklist:** `acceptance-checklist.md` `5c284847…`; admission review `958d059…`
- **Binding under review:** `src/case_entry.py`
  `646ce101db03fa7bc1de32c985e98d6d9dd17c324ce095adc4cbd50ad999cd1d`
  (`646ce101db03`); `stagec-plan.json` `88eb4326…`; `src/seat_emulator.py`
  `7582feb3…`; `src/fault_onset.py` `c6eff685…`; `src/r3harness/harness.py`
  `88552c98…`; `tests/test_case_execution.py` `8ccaa412…`;
  `tests/test_r3_lifetimes.py` `bb1f674e…`; `composition-manifest.json` `78116a37…`
- **Reused pins:** P6-r5 `dad98827…` harness `cd84e8dd…`; parent P6-r7 entry
  `46681fbb…`; plan `cc5993ab…`

## Verdict

**PASS** — R1, R2 and R3 are implemented, the exact five-command sequence runs
on one suite root with distinct executions and no cross-case authority, the
three required unshared mutations reject, and H1–H4/hash negatives are retained.
Candidate PASS certifies **injected execution only**; no live release.

## R1 — executable fault protocol: PASS

- `case_entry.py` exposes a `fault arm --case … --control … --actor …` command,
  and each case has an explicit control mapping (`CONTROLS`: positive/quiet =
  `none-declared`, lost = `hold-verifier-texts`, failed =
  `corrupt-after-worker`, queued = `transport-queued-first`). Fault records are
  written under the suite root with actor/armed-at provenance and consumed by
  the signed test executables via `FAULT_ROOT`/`FAULT_CASE` (live commands
  ignore both). Real seats do the work; the seat emulator is the named external
  step, not a synthetic producer inside the tool.
- **Independently reproduced:** running `run-case lost-completion` with the
  control unarmed → rc3 `E_NO_INTERVENTION`. Arming it then back-dating
  `armed_at` to 2099 → rc3 `E_CAUSAL`, i.e. onset/order is independently
  checked, not assumed from candidate detection.

## R2 — case isolation plus real sequence: PASS

- Config/plan declare case-scoped identities and subroots; runtime streams stay
  the actual launch-bound `<session_id>.jsonl` paths (verified in
  `test_r2_five_command_sequence_one_suite_root`: worker stream basename ==
  `t8-worker-001.jsonl`, not suffixed case files).
- **Independently reproduced on one fresh suite root:** the exact five-command
  sequence (`positive-handoff`, `lost-completion`, `failed-verification`,
  `queued-ambiguous-restart`, `quiet-rest`) each `run-case` → rc0; the five
  receipts yield **10 distinct (action, execution) pairs**; `verify-suite` →
  rc0 `"suite": "PASS"`; `rollback` → rc0 with a per-case
  `archive/<case>/rollback-report.json`. Re-running a case after
  `verify-suite` seal → rc3 `E_SEALED` (no replay/overwrite).
- **Unshared mutation (cross-contamination):** `test_r2_cross_contamination_rejected`
  injects case A's action into case B's latency with all else valid →
  `verify-suite` rc3 `E_CONTAMINATION`.
- **Reuse safety:** prior completed-case turn bindings are carried via the
  production `bind_turn` API so foreign ends in shared streams are skipped, not
  adopted (README + `_carry_bindings`); send counting uses durable kv msg
  records, not shim trace.

## R3 — budgets and observer lifetime: PASS

- The local `src/r3harness/` is the authorized R3-only copied revision,
  manifest-bound and parent-compared: `R3_REVISION.json` shows every file
  **identical** to the pinned parent except `harness.py`
  (`88552c98…` vs parent `cd84e8dd…`), whose sole behavioral delta is the resume
  seam (documented `added_symbols`, `behavior_contract`).
- **Independently run:** `test_r3_first_run_identical_to_parent`,
  `test_r3_late_completion_once_no_resend`, and
  `test_r3_expiry_escalates_bounded_no_extension` pass — deadline derives from
  the signed grant (not the 8 s observer wait), late completion after the old
  cutoff is handled once under the same action/execution without a second send,
  and real grant expiry escalates boundedly with no extension. First runs are
  behavior-identical to the parent (no outbox-sent record → same code path).

## Retained H1–H4 and hash negatives: PASS

- Parent `P6-r7` suite (H1–H4, fail-closed hash negatives) still passes
  unchanged: `PYTHONPATH=src pytest tests/ -q` → **11 passed** in the untouched
  parent.
- New `test_retained_gate_negatives` reproduces the fail-closed behavior on the
  new entry: omitted `candidate_harness_sha256` → rc3 `E_TOOL_CHANGED`; stopped
  registry → rc3 `E_EXPIRED`.
- `PYTHONPATH=src pytest tests/ -q` in this package → **8 passed**.

## No live effects

`agent-deck list --json` = 7 before and after (four main seats + stopped
`0e734b30`/p3 fixtures), statuses unchanged. All work used private tmp sockets,
a synthetic test plan/binding/registry and signed test executables; no real
seat task, send, launch/restart, service/timer mutation, credential or
production-ledger write. `P6r8-candidate-1` BLOCKED and the partial/expired
initial attempt remain preserved.

## Non-blocking observations

- The new package carries its own entry (`case_entry.py`) rather than the parent
  `stagec_host.py`; H1–H4 are retained via the unchanged parent suite plus the
  new gate negatives, but the parent tests are not re-hosted inside this package
  (they run from the immutable parent). Acceptable under "rerun changed-path
  regressions", worth noting for future packaging.
- `stagec-plan.json` changed to `88eb4326…`; the accepted P6-r7 plan
  `cc5993ab…` is retained in the parent and remains the comparison baseline.

## Effect

Verdict **PASS** bound to `src/case_entry.py`
`646ce101db03fa7bc1de32c985e98d6d9dd17c324ce095adc4cbd50ad999cd1d` and the
hashes above, under contract `1e0305fe…` @ `8ceb879` and checklist
`5c284847…`. This certifies **injected execution only**; a fresh binding and an
exact signed live plan remain separate gates. `candidate-review.md` returned to
cairn (and Tern).
