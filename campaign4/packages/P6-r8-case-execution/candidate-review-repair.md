# P6-r8-case-execution — post-repair review (independent)

- **Reviewer:** corvid (independent of kiln/author)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Repair receipt:** `repair-1-receipt.json`, action `P6r8-repair-1`, owner
  kiln, start `2026-09-22T06:05Z`, deadline `2026-09-22T06:45Z`, workdir
  `campaign4/packages/P6-r8-case-execution`
- **Governing decision:** `allocation-extension-2.md` (Tern)
- **Checklist:** `R1-host-checklist.md` sha256 `222916ed01b851e8…`
- **Bound artifact:** `src/case_entry.py`
  `f3c329cf916b68b00a8dc24896a197da0aa375216a8ed104ed9e6e31bae2f7c3`
- **Contract:** `package.md` `1e0305fe…` (unchanged; no contract edit)

## Verdict

**PASS on the R1 repair.** The rejected defect — a fault *declared* but never
*applied* — is closed: `run_case` executes a real production consumer
(`src/fixture_control.py`) on the host path in every branch, the consumer reads
the armed intervention file itself (not env-only) and applies hold / bounded
delay / post-commit artifact tamper to the isolated fixture, and it emits an
applied receipt with timestamps and before/after evidence. Disabling the
consumer makes the case fail; a forged production with no delivery record is
rejected fail-closed. Candidate PASS certifies **injected execution only**; the
fresh binding, real seats and exact signed live plan remain separate gates.

## Artifact integrity

All eleven declared artifacts hash-match the completion claim and
`composition-manifest.json` on disk (checked byte-for-byte), including the
bound `case_entry.py` `f3c329cf916b`. `src/r3harness/harness.py`
(`88552c98…`) and `tests/test_r3_lifetimes.py` (`bb1f674e…`) are byte-identical
to the pre-repair candidate — R3 behavior retained. Non-blocking: the manifest
lists its **own** pre-insertion hash `78116a37…` while the file is now
`b62e2677…` (the claim carries the correct `b62e2677…`); a self-referential
manifest cannot include its own final hash. Bookkeeping only; does not affect
any gate.

## R1 checks (independent CLI reproductions)

- **R1-D declaration:** `fault arm` writes `faults/<case>.json` with
  case/control/actor/armed_at/induced. PASS (unchanged, now consumed).
- **R1-A application by the production consumer:** independently armed
  `lost-completion` with `hold-verifier-texts` and ran `run-case` via the real
  subprocess CLI. `faults/lost-completion.applied.json` shows the worker
  delivery `delivered_at=2026-09-22T06:27:33Z, held=false`, and the verifier
  delivery `delivered_at=null, held=true, induced=true`; the receipt has
  `worker_item=i07f82e2045c3`, `verifier_item=null`, decision
  `owned-recovery`. The verifier emulator was never run, so the hold is
  provably the tool's, not a test substitute. PASS.
- **R1-B live-path consumer:** `run_case` reads the intervention file from
  `faults/<case>.json` itself and runs `fixture_control.deliver_pending` in
  every branch (`case_entry.py:940-985`); `FAULT_CASE` is retained only for
  signed test deposit executables and is never required for application. Live
  branch passes `pdirs["live_wake"]` (from `host_commands.wake`) so the real
  wake is invoked and its real receipt captured. PASS.
- **R1-C executable plan:** live `phases` (`stagec-plan.json`) are now exact
  commands (`fault arm`, `run-case`, `verify-suite`, `rollback`); no
  "operator brief" pseudocommand. The seat emulator appears **only** in
  `injected_test_section`, labelled TEST-ONLY, and the live `seat_operation`
  field states no emulator appears in the live procedure. PASS.
- **R1-E applied receipt / observed effect:** per-case
  `faults/<case>.applied.json` carries deliveries (deposited/delivered/held
  timestamps, induced, control, seat/action/execution) and, for
  `corrupt-after-worker`, an artifact control with distinct before/after
  hashes. Independently reproduced: `before_sha256=46409ea6…`,
  `after_sha256=9809428b…`, `path=…/failed-verification/art/out.bin`.
  `verify-suite` requires the applied receipt to exist and match case/actions/
  executions (`case_entry.py:1289-1299`). PASS.
- **R1-F disabled consumer / fail-closed:** with `fixture_control` replaced by
  a no-op that applies nothing (consumer disabled) and valid armed records
  left in place, `run-case` fails `rc3 E_CASE_FAIL` for both
  `positive-handoff` and `lost-completion` (`decision=owned-failure,
  reason=no-end`) — the case cannot pass without the consumer. Separately, a
  pre-planted verifier end with no delivery record is rejected
  `E_UNDELIVERED` (`case_entry.py:1097-1110`; package test
  `test_r1f_forged_production_without_delivery_rejected`). PASS.

## Retained R2/R3 and gates

`PYTHONPATH=src python3 -m pytest tests/ -q` → **10 passed** (R1 missing/
causal/forgery/disabled-induction; R2 five-command sequence on one suite root
with 10 distinct (action,execution) pairs, cross-contamination, seal/rollback;
R3 late-completion/expiry/parity; retained gate negatives). R3 files are
byte-identical to the accepted candidate. No `--no-verify`, no hook disabled.

## Non-blocking observations

- `transport-queued-first`'s queued/ambiguous *transport returns* are induced
  by the signed **test deposit executable** (labelled induced); the production
  consumer's contribution is the bounded 5 s delay before invoking the real
  wake. This matches extension-2's allowance that a labelled controlled
  interruption may create uncertainty but must never be reported as a real
  queued acknowledgement, and the tool verifies receipts rather than inventing
  them. Worth stating explicitly in the live plan narrative.
- `seat_emulator.py` retains a vestigial `hold-<role>` branch string that no
  longer matches any control and is documented as never holding; harmless.
- The manifest self-hash bookkeeping noted above.

## No live effects

All independent runs used `--simulated`, private temp sockets/streams and
injected effects only. No real seat task, send, launch/restart, service/timer
mutation, credential or production-ledger write. No source file was edited by
this reviewer; only this review and the pinned checklist were written.

## Effect

Verdict **PASS** for `P6r8-repair-1` bound to `src/case_entry.py`
`f3c329cf916b68b00a8dc24896a197da0aa375216a8ed104ed9e6e31bae2f7c3`, checklist
`222916ed01b851e8…`, contract `1e0305fe…`. This certifies the R1 repair as
**injected execution only**; it does not authorize live release. Returned to
cairn (and Tern) for terminal disposition.
