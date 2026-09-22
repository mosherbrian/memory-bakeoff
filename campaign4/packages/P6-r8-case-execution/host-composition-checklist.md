# P6-r8 — host-composition checklist (pinned pre-worker on ac0882b4)

- **Author:** corvid (independent reviewer; tests only, no implementation design)
- **Date:** 2026-09-22
- **Preserved bytes under test:** `ac0882b464bc0f36d8d2a94db7682b800cf18f65`
- **Prior review preserved:** `candidate-review-repair.md`
  `84dde9cc57a55384c220f24fa5dc3b51c976b8bc7a7cb837d164533de5d4ceaa`
- **Governing decision:** `allocation-extension-3.md` (D1–D4)
- **Contract:** `package.md` `1e0305fe…` @ `8ceb879` — no contract edit.
- **Rule:** every check blocking. Any FAIL withholds candidate acceptance/
  preparation/Stage C. Injected-scope PASS (repair-1) stays injected-scope.
  A case not actually induced is INCOMPLETE, never PASS.

Each check names the failing preserved bytes and the required independent
observation; none prescribes an implementation.

## D1 — executable NO-simulated plan (BLOCKING)

- **HC1.1** Run the real branch (`run-case` **without** `--simulated`) against
  the exact proposed plan after fresh binding substitution. It must not raise
  `E_HOST_PATH` on its own declared commands.
  *ac0882b4:* **FAIL, deterministically.** `host_commands.deposit_wake` and
  `.wake` are metadata prose containing a path
  (`"package-owned fixture-wake-deposit (/home/...); candidate transport…"`,
  `"/home/.../wake (invoked ONLY by the deliver loop…)"`). `_plan_dirs`
  non-sim branch requires each of `deposit_wake`/`wake`/`systemd_run`/
  `systemctl` to be a literal executable file (`case_entry.py:1360-1369`) and
  raises `E_HOST_PATH` otherwise. Prose can never satisfy this.
- **HC1.2** Every path-valued `host_commands` field is a literal valid
  executable path; descriptive text lives in separate fields; the ACCEPTED
  binding token is not required as the signed live value.
  *ac0882b4:* **FAIL.** Fields are prose; `_plan_dirs` conflates metadata and
  path. `status` still reads "PROPOSED ONLY"; the plan is not executable.

## D2 — declared identity/role authority + real wake boundary (BLOCKING)

- **HC2.1 adversarial valid titles:** two real seats with titles that do **not**
  contain the substring `verifier` (e.g. `alpha-12`, `omega-07`) must route and
  validate correctly; role/action/execution come from signed bindings, not a
  title substring.
  *ac0882b4:* **FAIL.** `fixture_control.deliver_pending` sets
  `is_verifier = "verifier" in seat` (`fixture_control.py:75`) and drives both
  `hold-verifier-texts` and first-worker detection from it; a valid non-substring
  title is mis-roled.
- **HC2.2 unknown/wrong destination rejected before wake:** an unknown seat, or
  a deposited `(action, execution)` not matching the signed binding, must be
  rejected before any wake subprocess runs.
  *ac0882b4:* **FAIL.** `deliver_pending` reads `action`/`execution` from the
  text envelope and never validates them against a signed binding; unknown
  seats are delivered.
- **HC2.3 explicit profile argv/env:** the wake subprocess must receive the
  authorized `campaign4` profile env/argv explicitly, like the registry reader,
  not inherit the controller's cwd/env.
  *ac0882b4:* **FAIL.** `subprocess.run([live_wake, seat, text],
  capture_output=True, text=True, timeout=60)` (`fixture_control.py:93-95`)
  passes no `env`/`cwd`; the child inherits the controller's environment.
- **HC2.4 distinct transport receipts:** the applied receipt must capture real
  `started` vs `queued` vs `ambiguous` outcomes separately; queued must not be
  reported as proof of completion or acknowledged recovery.
  *ac0882b4:* **FAIL.** Only one `transport_ref` (last stdout line) is
  recorded; no started/queued/ambiguous distinction.

## D3 — notification-primary consumer, bounded and reconciled (BLOCKING)

- **HC3.1 no second bespoke polling loop:** the new consumer must use the
  existing notification primitive or a direct bounded event/callback path, and
  attach before the initial drain.
  *ac0882b4:* **FAIL.** `_deliver_loop` polls `stop_delivery.wait(0.5)` forever
  (`case_entry.py:982`); a bespoke 0.5 s scan added alongside the
  notification-primary contract, attached only when the thread starts.
- **HC3.2 reopen reconciliation:** after consumer interruption, durable
  deposit/delivery identity must prevent blind second sends; ambiguous delivery
  stays pending owned reconciliation and is never silently marked delivered or
  retried.
  *ac0882b4:* **FAIL / unproven.** No attach/reopen reconciliation path; the
  loop's only identity is a `_delivered` flag rewritten in place. An
  interrupted ambiguous delivery has no owned-reconciliation state.

## D4 — real NO-simulated five-case composition, hash-bound (BLOCKING)

- **HC4.1 real branch exercised:** the corrected **no-`--simulated`** path must
  be run with the actual package deposit executable and actual fixture
  controller; external host/model boundaries intercepted only. Test scripts may
  not supply missing production semantics.
  *ac0882b4:* **FAIL / not shown.** Every independent run to date used
  `--simulated`. D1 makes the real branch raise before any case runs.
- **HC4.2 real fault meaning:** the whole five-case sequence must actually
  induce each fault's declared meaning. A held verifier is not proof of a lost
  worker-completion signal; a 5 s delay alone is not proof of queued
  receipt/ambiguous-delivery recovery.
  *ac0882b4:* **FAIL.** `transport-queued-first` queued/ambiguous returns are
  produced by the test deposit executable, not the production consumer; the
  consumer contributes only a bounded delay. Not real-branch evidence.
- **HC4.3 transitive hash binding:** every invoked executable module/wrapper
  (including `fixture_control` and the deposit wrapper) must be bound by the
  future live signature; post-signing drift must reject before effect — checked
  as a new execution surface, not only the inherited entry/harness negatives.
  *ac0882b4:* **FAIL.** Signature binds entry + candidate harness + R3 harness
  only; `fixture_control.py` and `fixture-wake-deposit` are unbound.
- **HC4.4 full real-branch composition:** the exact five-command sequence on
  one suite root in the real branch, with the corrected plan, including join,
  one-send, provenance, isolation and rollback. "Parent tests passed
  elsewhere" is not sole proof the changed entry retains H1–H4.
  *ac0882b4:* **FAIL / not shown.** No real-branch sequence exists; parent
  suite is cited from the immutable parent.

## Artifact integrity (BLOCKING)

- **HC5.1** Remove the stale **self-hash** from `composition-manifest.json`'s
  artifact list; bind its final hash in the external completion claim; never
  report "all entries match" with the exception hidden as non-blocking; keep the
  previous manifest byte-exact in git; build a complete transitive execution
  inventory for signing with no self-hash cycle.
  *ac0882b4:* **FAIL.** The manifest lists its own stale hash `78116a37…`
  while its actual bytes hash `b62e2677…`; the prior repair review recorded this
  as "non-blocking", which extension-3 forbids.

## Verdict

**FAIL on `ac0882b4` for host composition.** D1–D4 and artifact integrity are
unmet as reproduced above. The repair-1 applied-control consumer is retained as
**injected-scope evidence only**; R1–R3, deadline bounds, one-send, provenance,
case isolation, stdlib boundary and rollback remain binding. No contract edit.
