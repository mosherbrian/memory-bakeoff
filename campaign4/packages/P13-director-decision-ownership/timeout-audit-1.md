# P13 timeout audit 1 (read-only, bounded)

- **Action:** `P13-timeout-audit-1`, owner corvid, `06:46:38Z`–`07:01:38Z`.
- **Timed-out attempt:** `P13-liveplan-repair-1`, timeout `06:45:01Z`, ack
  `06:45:26Z`; worker turn observed, **no completion claim**. Frozen snapshot
  `attempt-history/plan-repair-timeout/manifest.json` (**11/11 hashes match** the
  current `plans/`).
- **Verdict: NO PASS / no reclassification.** The expired attempt produced
  substantial partial work but its own offline test **failed (rc 3)**; remaining
  work is enumerated below. Production unchanged `97a57db1`; live held. No edits,
  no live effects, no unsafe script execution.

## F1–F5: what was accomplished vs missing

Frozen plans were rewritten to address all five findings in **structure**; the
offline test confirms the *old* defects and some fixes, but the plan does **not**
pass.

- **F1 (live config + run/outside-check service):** addressed in structure — plan
  writes the full config with all dispatch identities (`PASS "plan wrote full live
  config"`, `PASS "config carries all dispatch identities"`) and creates+starts the
  run and outside-check services (`live20-plan.sh:171-177`). **Missing/failing:**
  `FAIL run start not captured`, and `liveness.log`/`runloop.log` show
  `open …/root/p13doff1.json: no such file or directory` — the run/check did not
  actually start on the generated config offline.
- **F2 (prep argv + four-seat binding):** addressed — new argv
  (`--worker-name/--verifier-name/--manifest-out`) accepted (`PASS`), four seats
  bound at prep (`PREP PASS four fresh fixture seats`), launch argv captured
  (`PASS`); no private-HOME export. **Missing:** four-seat **registry/socket/
  incarnation** cleanup not validated (`FAIL seat p6-fixture-{w,v,d,u} remains`),
  and non-dry-run prep is blocked by the **P6 indent bug** (below).
- **F3 (real ledger/notify, JSONL, ACKF, task turn):** addressed — real notify path
  (no stub overwrite), per-line JSONL parsing, runnable `decision-turn.sh` producing
  artifact+claim+end (`PASS`), literal/guessed ack refused (`PASS`). **Missing:** the
  live ladder/suppression path is not validated — `FAIL plan rc=3`, `FAIL FAIL rows
  in live results`, `FAIL LIVE PASS missing`.
- **F4 (caps redaction / no secret leak / wall scope):** addressed in structure —
  redacted caps record (hashes/permissions only, `PASS`), run-scoped caps removal,
  wall stops the original driver scope (`live20-plan.sh:68-70`). **Missing/failing:**
  `FAIL caps redaction missing`, `FAIL caps remain` — cleanup left the caps tree.
- **F5 (promotion PREV/rollback/policy/guard):** addressed — `PREV` is a separate
  `.prev-p13` path, rollback restores exact originals and verifies the archived sha,
  policy checked against the **actual prospective config**, active-decision guard
  added. Offline confirms `PASS new order: rollback restores exact original`.

## Remaining work (one small continuation, concrete)

The attempt is **close**: the F1–F5 structural fixes and a comprehensive
`offline-test.sh` exist. To complete it needs, at minimum:

1. Fix the offline **plan run failure** (`plan rc=3` / `FAIL rows` / `LIVE PASS
   missing`): the generated config path (`p13doff1.json`) must exist where the run/
   outside-check expect it, and the run start must be captured.
2. Make cleanup remove the run's **caps tree** and the four **fixture seats**
   (`FAIL caps remain`, `FAIL seat p6-fixture-* remains`) so the offline assertions
   pass.
3. Resolve the **wall-arming vs deadline** check (`SETUP FAIL wall-stop not active
   at deadline` when armed with a placeholder date) and the run-start capture.
4. Re-run `evidence/plan-repair/offline-test.sh` to **green** and file the bound
   `P13-liveplan-repair-1` claim with hashes/residuals.

**Not a PASS:** no bound claim exists, and the frozen plan fails its own offline
test; the timed-out attempt must not be reclassified.

## Preserved finding — P6 indent bug (Tern disposition required)

`evidence/plan-repair/p6-indent-bug.md`: in `P6-r6-live-preparation/src/prepare_live.py`
the `full[role] = {…}` assignment sits one indent level outside its binding loop, so
only the last role lands in `full` and `build_manifest(..., full["worker"], …)`
raises `KeyError: 'worker'`. **Non-dry-run live prep cannot produce its manifest
until P6 is fixed.** The plan does **not** edit P6; it validates via
`prepare_live.py --dry-run` over the real launch results. No undocumented
frozen-input amendment. **Tern disposition required.**

## Cleanup

- No active `p13live-*`/`p13repoff*` units.
- **10 leftover offline workdirs** attributable to this offline attempt:
  `/tmp/p13repoff-41NjwL`, `-4DFulb`, `-8PHba6`, `-9RiMum`, `-ktxsFE`, `-OMPiyV`,
  `-osfAFG`, `-QYItCe`, `-QyRokP`, `-vTUySf`. Reported, **not deleted**; no unrelated
  resources touched.

Production unchanged; live/prep/promotion held. No fake verifier claim created for
the timed-out package.
