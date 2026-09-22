# P6-r10-live-recovery-matrix — control feasibility review (independent)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r10-control-review-1`, start `2026-09-22T16:53Z`, deadline
  `2026-09-22T17:03Z` (`campaign4-p6r10-controlreview-deadline.timer`)
- **Brief:** `control-feasibility-ruling.md` (Tern, 16:52:27Z) +
  `control-feasibility-source-pins.json`; admission/checklist immutable
- **Scope:** read-only, actual call paths only. No test, no live effect, no
  implementation, no pin edited.

## Disposition (one)

**PARTIAL EXECUTABILITY — two fault mechanisms are MISSING on current source,
two cases are executable unchanged.** There are **no existing executable
parameters/commands** for `queued-ambiguous-restart` or for
`lost-completion`'s intended delay; both require a bounded implementation
amendment, not a plan re-specification. `failed-verification` and `quiet-rest`
are genuinely executable unchanged. No live preparation should launch for the
two blocked cases.

## Source-pin integrity

All three pins recomputed byte-identical:
`case_entry.py` `9a1bb23c…`, `fixture_control.py` `f89b03fd…`,
`fixture-wake-deposit` `97b5e9d1…`. Accepted candidate unchanged.

## Call-path findings

### 1. `queued-ambiguous-restart` — MISSING mechanism (blocked)

Actual path: the durable transport receipt is written only in
`host_adapter.HostAdapter.send` → `_record` (`host_adapter.py:133-183`). State
is derived solely from the wake command's exit code and stdout:
`rc0`+"wake:"→`sent` (`:152-154`), `rc3`+"wake:"→`queued` (`:155-157`),
`rc0/rc3` without `wake:`→`ambiguous` (`:158-160`), else `failed`. The wake
command is `self.wake_path`, selected from the **signed** plan
(`harness.py:67`, `:1030`) and in the accepted plan is
`P6-r9-observer-lifetime/src/fixture-wake-deposit`, which by its own header
"NEVER synthesizes queued/ambiguous returns" and unconditionally prints
`wake: … -> deposited-to-fixture-outbox` and returns 0. Therefore every live
send is recorded `sent`; no signed input can make the durable receipt
`queued` or `ambiguous`.

The two named controls do not reach that path: `transport-queued-first` only
`time.sleep(hold_delay_s)` before invoking the real wake
(`fixture_control.py:167-169`) and `hold-verifier-texts` only skips
`deliver_pending` for the verifier (`:157-158`); neither alters the transport
exit code or writes a transport receipt. `_classify_receipt`
(`fixture_control.py:101-111`) can *label* a deposit `queued`/`ambiguous` from
rc/stdout, but the only live producer returns rc0+"wake:". `case_entry.py:1234`
and `:1238` **hard-require both** `queued` and `ambiguous` in
`applied_kinds ∪ durable msg states`, `induced` true (`:1242-1245`); with the
current path that branch can never pass (`E_CASE_FAIL`, INCOMPLETE). Confirms
the ruling: the "test deposit executable" that could emit those codes is a
substitute and would not prove actual transport ambiguity, and is not
authorized.

**Smallest amendment required (implementation, not r10 evidence):** a
signed, isolated transport control that genuinely causes (a) one wake whose
real receipt is `queued` (rc3 semantics / acknowledged-not-started) and
(b) one `ambiguous` (unacknowledged/indeterminate) **recorded through
`_record`**, with raw receipts preserved and subsequent reconciliation; OR a
plan/transport-level restriction that makes a single genuine ambiguity the
case, deleting the dual-state requirement. Reviewer cannot authorize either.

### 2. `lost-completion` — `delay-worker-completion` is a NAME with no plumbing (blocked)

`delay-worker-completion` appears only as a string in `FAULT_CONTROLS`
(`case_entry.py:749-751`). Exhaustive search of the accepted source finds no
`delay_s`/`delay-s` plumbing in `case_entry.py`, `harness.py` or
`host_adapter.py`; the only `delay_s` is timer scheduling
(`host_adapter.command_for`, `create_host`) and `seat_emulator.py --delay-s`
(a test stub whose substitution into live work is forbidden). The
`lost-completion` branch (`case_entry.py:1173-1211`) can *observe* a late end
after the first 8 s slice misses, but nothing in the accepted path intentionally
delays a real worker; a naturally slow model is not declared induction. With
`induced` required and `_check_causal` armed<onset<detection (`:845-886`), the
case cannot be certified as an induced delay.

**Smallest amendment required:** plumb a signed `delay_s` (from intervention
`params`) into the real worker-completion path so the delay is causally
observable and independently onset-stamped, or authorize an explicit acceptable
delay mechanism. Implementation, not r10.

### 3. `failed-verification` — EXECUTABLE UNCHANGED

`corrupt-after-worker` is real and causal:
`_maybe_apply_corrupt_tamper` (`case_entry.py:614-629`) fires only after
`_commit_present` sees `handoff-done:<action>:<execution>` and the worker claim
is `completed`, then `fixture_control.apply_artifact_control`
(`:269-291`) overwrites the artifact with `tampered-by-fixture-control` and
records `before_sha256`/`after_sha256`/`induced: True`. The verifier then runs
its `recompute-sha256` check against tampered bytes; the branch forbids any
`COMPLETE` close (`case_entry.py:1212-1216`) and the timecheck requires
`accept-open` (`:1398-1411`). Real evidence path exists.

### 4. `quiet-rest` — EXECUTABLE UNCHANGED

`none-declared` needs no fault: a real setup commit, a 3 s no-growth window on
both streams and `msg` count, then a real reopen yielding
`duplicate-end-ignored` with unchanged sends (`case_entry.py:1268-1295`). No
invented work and no active action relabeled.

## Effect

One disposition returned: on bytes `9a1bb23c/f89b03fd/97b5e9d1`,
`failed-verification` and `quiet-rest` may proceed unchanged; `lost-completion`
and `queued-ambiguous-restart` have no executable existing mechanism and need a
bounded implementation amendment (or plan restriction for the dual
queued/ambiguous requirement). Admission and checklist left immutable; no
preparation launched; no timer armed; no send. Returned to Tern.
