# P6-r14-host-timing — candidate review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P6r14-review-1` (existing ≤40 m grant)
- **Brief:** `dispatch-receipt.json` (`P6r14-candidate-1`, contract `4bf7e38df5ce`,
  admission `4ebb0742`, checklist `8ca78adb`)
- **Claim:** `completion-claims/ex-p6r14-candidate-1.json`
- **Evidence:** `candidate-review-evidence/p6r14-review-gate.log`. No source edit,
  no live effect.

## Verdict

**PASS (bounded).** The full composed gate is green on the frozen final bytes
(69/69), retained P5 83 + P3 59 are green, the authorized surface is respected
with all accepted core Python byte-identical, manifests/descriptors are accurate
and acyclic, and T1–T4 semantics are exercised through production CLI branches
with injected collaborators. One **bounded residual** is reported for
disposition (a fail-open edge on absent persisted execution identity); it is not
a demonstrated production path and does not change the gate result.

## Full gate (required command, bound bytes)

```
cd .../P6-r14-host-timing
PYTHONPATH=candidate/src python3 -m pytest candidate/tests -q -p no:cacheprovider
```

Result: **69 passed in 631.86 s** (rc0), no skips/removals. (The claim's earlier
"59 passed, 10 failed" is explained by a mid-gate descriptor refresh + a
test-path portability issue; the final bytes are green and I independently
reproduced it.)

Retained on the actual new modules:
- `candidate/tests-retained/p5r2` → **83 passed** (0.09 s).
- `candidate/tests-retained/p3r3` → **59 passed** (16.44 s).

## Bound bytes / surface

- Authorized changes only: `harness.py 62b86917…`, `case_entry.py 64edb54e…`,
  tests/plans/docs/manifests; `host_adapter.py` **unchanged** `231f45f0…`.
- Accepted core Python **byte-identical** to R13: `driver 39c52dd2`, `ingress
  fe7f528d`, `store b72d4fb3`, `lifecycle ea61a75c`, `validator dcecfc1d`,
  `turn_handoff 2b6aa7ef`.
- Manifests: composition 74 entries and outer 77 entries — 0 missing, **0
  drift, no self-reference**; `R3_REVISION.json` descriptor 0 drift with correct
  `identical` flags. Module-origin check is location-derived (not a stale
  absolute path), and the tests import the actual candidate modules.

## T1–T4 evidence (production CLI, injected host boundaries)

- **T1** (`test_r14_host_timing.py`): `timer_callback` requires DB/timer/qid/
  action/execution; omitted → `E_NO_IDENTITY`; unknown qid → `E_UNKNOWN_PACKAGE`;
  action ≠ persisted flight → `E_ACTION_MISMATCH`; wrong execution with
  `exec-current` present → `E_EXECUTION_MISMATCH`; two qids in one DB isolated;
  foreign DB zero writes; `_arm_host_timer` embeds `--qid-cb`/`--execution` (no
  silent `P6F` default).
- **T2**: verifier window starts at verifier dispatch, persisted once
  (`r3v:<vaction>:<vexec>`), `effective = min(verifier deadline, live_stop_utc)`
  recorded; expiry → bounded owned recovery with window evidence; facts
  identical across reattach.
- **T3**: direct `run-fixture` beyond 8 s yields explicit
  `nonterminal-continuation`/`grant-open-continue` then reattach commits with no
  resend; genuine expiry stays terminal `no-end`; outer-stop honored; trusted
  ledger receipt time (not `datetime.now`) for continuation.
- **T4**: one execution → exactly 2 rows, no `no-end-failure`, repeat writes no
  extra rows; synthetic `no-end-failure` rejected `E_BAD_SAMPLE`; missing onset →
  `unmeasurable-incomplete`.

Superseded assertions reconciled with old evidence retained (no deletion):
`test_r3_lifetimes.py` slice `no-end` → continuation; `test_amendment2_reconcile.py`
first-run `no-end` → `grant-open-continue` (genuine conflict/query owned-failures
kept); `test_amendment2_timer.py` stale action → `E_ACTION_MISMATCH`;
`test_observer_lifetime.py` R8-parent old-fails retained unchanged. Obligation (a)
old-fails recorded: parent CLI lacked `--execution` (rc2), parent slice miss
terminal `no-end`, parent had no verifier-window facts.

## Independent unshared mutation + bounded residual

An independent T1 probe (not from kiln) reproduced omitted-identity
`E_NO_IDENTITY` and, per the tests, wrong-execution `E_EXECUTION_MISMATCH` when
`exec-current` is registered. It also exposed one edge: when the ledger has **no**
`exec-current:<action>` entry, `timer_callback` skips the execution comparison
(`if current_exec is not None and …`) and proceeds to interrupt, i.e. a
**fail-open on absent persisted execution identity**. In the production path a
timer is armed only after `HostAdapter.register_execution`, so `exec-current` is
present; the edge is defense-in-depth, not a demonstrated production path. It is
reported for Tern disposition (either fail closed on absent execution, or record
that presence is guaranteed at arm time).

## Scope / unchanged

Out-of-scope items untouched (late-recorded-work recognition, shadow-time action
reconciliation, lost/queued live controls; no `occurred_at`, ingress
recorded-time unchanged). R13 protections (authenticated rejection, causal
routing, A–E) retained. Live remains held.

## Effect

One bounded verdict: **PASS (bounded)** — full composed gate 69/69, retained
83+59 green, bound manifests/descriptors accurate, T1–T4 verified through
production CLI; one fail-open residual on absent persisted execution identity
noted for disposition. Returned to Tern.
