# P12-cutover-plan-closure-1 — independent review (corvid)

- **Action:** `P12-cutoverplanreview-1`, start `03:49:01Z`, deadline `04:04:01Z`.
- **Claim:** `cutover-plan-closure-claim.json` on acceptance `1bedb9be`; product
  **frozen** `8ad12b86fa82` / `97a57db1`; no install/service/switch/live effect.
- **Verdict: PASS.** The cutover deployment mismatch is closed: the handler unit is
  installed, its wiring preflighted, and rollback drains it. Ready for Tern's held
  cutover decision.

## Pins / integrity

- **222/222** `files_sha256` match; `plans/cutover.sh` = `2be6d13f…`,
  `plans/live-checks.sh` = `19085856…`, handoff tasks and inputs template pinned;
  product binary `97a57db1…` unchanged; installed preview still `221bb3aa…`
  (**no install effect**).

## Requirements verified

- **Handler installed in `switch`:** `UNITS` now lists **all four** qualified units
  including `agent-loop-liveness-failed@.service` (`cutover.sh:33-34`), each copied
  from the release and asserted byte-equal; switch then checks systemd wires
  `OnFailure=agent-loop-liveness-failed@campaign4.service` (`:148`) and rolls back
  if not.
- **`cli_preflight` (read-only, fails the stage):** 4 units present, the exact
  `OnFailure=agent-loop-liveness-failed@%i.service` line, the exact
  `checker-failed` command, units run the installed binary path, and the required
  commands + version answer (`:74-85`).
- **Rollback handler drain:** rollback drains the check **then** its OnFailure
  handler (`drain "$NEW_LIVE.service" "$NEW_FAIL" …`, `:182`) and verifies none
  active, restores kept unit files / removes added ones, and restores the **exactly
  captured** state (campaign4-watch recreated only if it was active); refuses
  without `state.tsv`.
- **Seat identity:** every seat id must be registered in the `campaign4` profile
  under its role title before any effect (`:88-90`); all messages carry
  `AGENTDECK_PROFILE=campaign4`.
- **`must()`:** a failed required command fails the stage — never PASS.
- **Post-switch verification** uses the live-qualified predicates (`pass_eval` for a
  fresh loop-pass by the current InvocationID/MainPID, then `healthy_eval` for a
  completed outside check reading `rest`), replacing the text greps.
- **Open-dispatch terminal verbs** (`NOT-READY`, `BOUNDED-FAIL`, `CLOSED`) added so
  finished reviews are not read as open; `real-dry` shows 6 → 1 (this round).

## Independent evidence (my run)

- `rehearse.sh` (sandbox home, stub `systemctl`/`agent-deck`/`wake`, copy of the
  release) → **24 checks, 0 wrong**: capture PASS + exact state; DRY
  switch/handoff/rollback; negatives — missing handler (no mutating systemctl), no
  `OnFailure`, wrong handler command, failed required command (no switch PASS),
  wrong seat identity (no disable), rollback order (handler drained before old
  owners), only captured-active timers started, captured-enabled re-enabled, added
  unit files removed, campaign4-watch not recreated when inactive, rollback without
  state refuses.
- `real-dry/` on the real host (read-only, `DRY=1`): capture/switch/handoff/rollback
  **rc 0**, all PASS; `switch` "4 units installed (bytes = release, OnFailure
  wired)"; `rollback` "old owners active, agent-loop off, open items handed to
  cairn"; product frozen.

## Residuals (carried to the held cutover)

1. The post-switch verification (`pass_eval`/`healthy_eval`) and the rollback
   "not rest" path cannot be reached offline (stubs produce no real pass); those are
   the live-qualified predicates, tested with negatives in
   `evidence/live-measurement/checks-test.sh` (54/54). **The first real run of
   `switch` is the cutover itself.**
2. Transient `campaign4-watch` is recreated with the original 45 min settings only
   if it was active at capture; its exact next-elapse phase is not preserved.

No source/install/live effect by corvid. **PASS** returned to Tern and cairn
immediately; the held 45 m cutover + 10 m post-review remain Tern's signed decision.
