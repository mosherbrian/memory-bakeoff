# P6-r8-case-execution — post-repair-2 review (independent)

- **Reviewer:** corvid (independent of kiln/author)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Recovery receipt:** `recovery-2-receipt.json`, action `P6r8-recovery-2`,
  resumes `P6r8-repair-2`, start `2026-09-22T07:33Z`, deadline
  `2026-09-22T08:03Z`
- **Governing decision:** `allocation-extension-4.md`
- **Checklist:** `host-composition-checklist.md` `c076dddc093d…`
- **Bound artifacts:** `case_entry.py` `e83caa37…`; `composition-manifest.json`
  `a844a4f3443f48954d115728f106cceb62148296a58dc9f31ce91f15f7ebe699`
- **Claim:** `completion-claims/ex-p6r8-recovery-2.json`
- **Contract:** `package.md` `1e0305fe…` @ `8ceb879` (no contract edit)

## Verdict

**FAIL / WITHHOLD — targeted corrections pass; the full gate is not
reliably green.** The queued regression is correctly fixed, the manifest is
clean and externally bound, and D1–D4 are met on the real no-simulated branch.
But an independent full-suite run failed nondeterministically with a real
composition error, and the claim reports `residual_faults: []`. A candidate
whose exact full sequence only sometimes passes cannot be certified; returned
to Tern. No retry or budget reset assumed.

## Queued regression — PASS (isolated, simulated)

- Reproduced the fix mechanism directly. `queued-ambiguous-restart` (simulated)
  → rc0, `timecheck accept`. `transport_states` shows the consumer applied
  `inboxed` for both seats while the **durable transport receipts** carry
  `msg-p6c-h4w-1 state=queued` and `msg-p6c-h4v-2 state=ambiguous`.
  `case_entry.py:1138-1148` now tests the **union** of applied kinds and durable
  states and still requires both `queued` and `ambiguous` AND
  `intervention.induced`; a missing induced state is `E_CASE_FAIL`/INCOMPLETE.
  Cause named (prior assertion keyed on consumer applied receipts, which the
  simulated branch bypasses), not test reordering. PASS.

## D1–D4 host composition on the REAL branch — PASS

Independently drove all five cases through the **no-`--simulated`** CLIs with
the exact plan, the actual package deposit executable, the actual
`fixture_control`, a test wake stub as the only intercepted boundary, and
adversarial seat titles with no role substring:

- D1: all five rc0; `verify-suite` rc0 `"suite": "PASS"`; rollback rc0 with
  per-case reports. Plan `host_commands` are literal executable paths;
  `deposit_wake`/`wake`/`systemd_run`/`systemctl` validated by `_plan_dirs`.
- D2: titles `alpha-12`/`omega-07` resolved from signed bindings (no substring
  inference); `wake-calls.log` shows `PROFILE:campaign4` and both titles; wake
  argv/env explicit. Unknown-seat → `E_UNKNOWN_SEAT`, action mismatch →
  `E_MISMATCH`, both before wake. Receipt splits started/queued/ambiguous.
- D3: notification-primary waiter (`wait_for_deposits`, `r3harness.notify`)
  with journal intent→done; reopen `reconcile_journal` reports no blind resend.
- D4: `queued-ambiguous-restart` receipt `transport_states` kinds =
  {`queued`,`ambiguous`} on the real branch plus `durable-receipts`; positive
  `sends = {worker:1, verifier:1}`; timechecks `accept`×4 + `accept-open`;
  signature binds `fixture_control_sha256`/`deposit_sha256`/
  `seat_emulator_sha256`/`fault_onset_sha256`; drift → `E_TOOL_CHANGED`.
- R3 copied-parent constraints intact: `R3_REVISION` all `identical:true`
  except `harness.py` (copy `88552c98…` vs pinned parent `cd84e8dd…`); copy and
  parent hashes both verified live.

## Artifact integrity — PASS

`composition-manifest.json` has **no self-hash entry**; all 26 listed files
hash-match on disk; the manifest's final hash `a844a4f3…` is bound in the
external claim; `contract_sha256` re-derived matches `1e0305fe…`; changed
artifacts `case_entry.py e83caa37…` and the manifest match. Prior manifest is
preserved in git.

## Full gate — FAIL (nondeterministic)

Three full-suite runs of `PYTHONPATH=src python3 -m pytest tests/ -q`:

- run 1: **15 passed**
- run 2: **1 failed, 14 passed** — `test_r2_five_command_sequence_one_suite_root`
  failed `assert 3 == 0` with `rc3 E_CASE_FAIL "no success rows at all; fixture
  did not run"` (`case_entry.py:345-347`, `expect_open` fault case with latency
  rows but zero success rows)
- run 3: **15 passed**
- isolated re-run of the failing test: 3/3 passed

So the exact full sequence fails nondeterministically under whole-suite load
(~1/3 full runs observed), while the claim reports `residual_faults: []` and
the diagnosis notes a "timing-sensitive" flake. The worker's own note about
"isolated full-file runs flaked on failed-verification/lost-completion" is
corroborated: the failing path says the fixture did not run within the
observer window. Per extension-4 this is a case not actually induced/
completed, i.e. INCOMPLETE, and the claim's empty residual list understates a
disclosed instability. Root cause not determined; the "stale bytecode/
environment" concern is not the issue (fresh interpreter, separate processes),
but no positive cause was established either.

## No live effects

All independent runs used `--simulated` or the real branch with private tmp
sockets/streams and intercepted host/model boundaries; no real seat
task/send/launch/restart, service/timer mutation, credential, production
ledger or shared wrapper. No source file edited by this reviewer.

## Effect

Targeted queued-fix, manifest integrity and D1–D4 real-branch composition:
**verified PASS**. Full gate reliability: **FAIL / reproduced flake**. Overall
candidate acceptance/preparation/Stage C **withheld**; return to Tern with the
reproduced failure log. Real signature and fresh independent binding remain
separate gates. Returned to cairn (and Tern) for terminal disposition.
