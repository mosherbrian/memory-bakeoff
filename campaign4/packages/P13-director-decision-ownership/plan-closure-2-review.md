# P13 plan-closure-2 — independent review (corvid)

- **Action:** `P13-planclosure-review-2`, owner corvid, `17:26:52Z`–`17:41:52Z`.
- **Bound claim:** `plan-closure-2-claim.json` (`63a8ccaf…`) — author status
  **INCOMPLETE**, offline **36 PASS / 5 FAIL**; hash mismatches none.
- **Verdict: INCOMPLETE / no retro-PASS.** The rewritten ladder/ack/decide/restart
  path did not execute offline; the live sequence still does not reach decision.
  No source/product/live effect.

## Held-awaiting-receipt — concrete mismatch

- Evidence: `runloop.log` `{"ob-9eacbadc0d2e7a4f": "held-awaiting-receipt"}`;
  `results.tsv` `wait:verifier claim INCOMPLETE`, `wait:decision step INCOMPLETE`,
  `DECISION FAIL package never reached decision`.
- Product rule (`internal/host/adapter.go:236-325`): an outbox intent settles only
  on **proof** — a transport receipt `state in {sent,queued,delivered}`, plus
  `receipt.action == pending.target`, `receipt.execution == execution`,
  `CurrentExecution(action) == execution`, a `turn-seen:<stream_key>:<item>:<exec>`
  KV (`:322-325`), and `receipt.seat == RouteFor(target)`.
- The fixture `plans/tasks/decision-turn.sh` appends `{"t":"end","item":ITEM}` to a
  plan-chosen `--stream FILE` and writes the claim; the product records
  `turn-seen` with `end.stream_key` (the **stream filename**) and `item`
  (`internal/loop/loop.go:911`). **Smallest mismatch to close:** the worker turn's
  stream file must be named with the **product's routed stream key** and carry the
  matching item/execution, so `executionProven` sees the worker's `turn-seen`.
  Compare directly with the P12 live driver's turn route
  (`packages/P12-…/plans/live-driver.sh`, `turnEnd(key)`/`BindTurn`). Do **not**
  weaken the real-runtime receipt criterion.

## Remaining live/readiness gaps (exact)

1. Worker dispatch **receipt proof** unproven → verifier/decision never reached.
2. The rewritten **ladder/ack/expiry-recurrence/decide-suppression/restart** steps
   have **not executed** (unproven).
3. `rollback PASS` and caps-redaction rows to re-check after a full run.
4. **Isolation:** write-attribution is by identity (0 attributed writes, planted
   negative detected) and PASSED, but the **shared files did change** (production
   active) — accepted only under the attribution rule; re-assert after a clean run.
5. **Manual correction disclosed:** the in-flight run's rollback dirs were created by
   hand, so that run is **not fully from frozen harness bytes** — a **new run after
   correction** is required for any future acceptance.
6. **Bound:** the offline inputs set `LIVE_DEADLINE 2030`, which supplies **no safety
   bound**; the earlier `80 s after PREP` stop was the **enclosing author process
   bound**, not the plan window. Verify the enclosing wall and lingering-children
   cleanup; each offline run needs ~10–12 min (do not run a full one inside 15 m).
7. **Ticket stub is offline proof only**, not the actual Claude notification the live
   contract requires; the live plan must exercise the real private-ledger notify
   path with a labelled Claude notification.
8. Leftover private tmp roots (exact paths, for Tern/Cairn):
   `/tmp/p13repoff-NsDPtM`, `/tmp/p13repoff-HZeg2h`.

## Classification

- **Not a PASS:** unexecuted ladder + unreached decision + disclosed manual
  correction. The 36 PASS / old-fail negatives are retained as evidence of the
  structural fixes (F1–F5), not as live qualification.
- **No product/adapters/live/install/service/Signal change**; production
  `97a57db1` unchanged.

Returned to Tern immediately. No fake verifier claim; no source/live effect.
