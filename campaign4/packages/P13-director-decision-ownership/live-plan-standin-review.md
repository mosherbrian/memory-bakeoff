# P13-liveplan-standin-1 — independent plan review (corvid)

- **Action:** `P13-liveplan-standin-1`, verify step (10 m). Stand-in author kiln;
  reviewer corvid independent.
- **Inputs:** `standin-author-release.json`, `live-plan-receipt.json`, admitted P13
  package/amendment, `candidate-review-repair-1.md` (`15945202…`),
  `standin-plan-claim.json` (`51fef53e…`).
- **Verdict: PASS** — offline plan-only; every requirement met with a runnable
  offline plan + negative tests, private isolation, and pinned sources. No live
  launch, real Signal, service mutation or product edit.

## Pins / outputs verified

- Product `df5e6fc627b8` / binary `47f69dfd…`; adapters `df51a1f4…` /
  `fdf49d0b…`; installed baseline `97a57db1…` — all match.
- `plans/MANIFEST.sha256` **8/8 OK**; every claim `outputs` hash matches
  (`decision-evaluators.sh ab4ea57f…`, `live-inputs.template.env af6c2e61…`,
  `live20-plan.sh 1dae5bd7…`, `promotion-plan.sh d781b35c…`, tasks `71992199…`/
  `8e378ed0…`, `rehearse.sh dc12fb2b…`). P12 pins `cutover.sh 2be6d13f…`,
  `live-checks.sh 19085856…`, `live-driver.sh f6afd9e0…` match.
- `rehearsal-1/rehearsal.log` = **29 passed, 0 failed**; I re-ran
  `rehearse.sh` independently → **29 passed, 0 failed, rc 0**.

## Requirement checks

1. **Runnable offline plan with negatives + isolation:** `live20-plan.sh` pins a
   **private `HOME`/`ROOT`** for every child, stubs only, private escalation
   ledger/watcher/resolve + **stub ticket**; rehearsal asserts **shared
   ledger/wake/escalation untouched**, **no real notify path touched**, **no secret
   material**, **no leaked exec**, **no shared paths**.
2. **Fixture policy + production policy:** fixture generic ladder **0/20/40 + 60 s**
   window is explicitly declared, and `policy_eval` states **production 0/300/600 is
   NOT proven by fixture offsets**; `required` policy is validated offline
   (`offs offs==[0,300,600]`).
3. **Intentional stop + ladder while stopped:** plan dispatches decision packages,
   then the **stop marker (exit 64)**, then rungs while stopped (real calendar timer
   + outside checker), capability ack/expiry **same-key recurrence**, authorized
   `decide`, suppression, restart no duplicates.
4. **Actors/onsets/exit/assertion:** explicit actors/actions, host-UTC onset/deadline,
   `result` rows FAIL/INCOMPLETE on any incomplete case; no unconditional rc 0.
5. **Absolute-calendar cleanup before tasks:** `live20-plan.sh:126-129` arms
   `--on-calendar` `AccuracySec=1s` and **verifies `next_elapse == deadline` before
   fixture tasks**; exact-ID stop; wall cannot be reset by reload; **capability-secret
   cleanup only after the bounded archive** (`:76`).
6. **Promotion plan:** archives installed `97a57db1`/config/watcher, `guard_absent`
   refuses if adapters absent or the **required policy invalid**, installs candidate +
   private adapters + config, preserves ledger decisions/deadlines, validates a fresh
   pass + checker; **rollback restores exact captured bytes/ownership, no DB
   migration/resend**.
7. **Bindings + late-bound fields:** helpers/config/templates/task texts and
   source/build/adapters pinned; late-bound IDs/time/root enumerated for signature;
   rehearsed offline with negative assertions.
8. **No product/tests/shared-script changes:** offline plan-only.

## Residuals (honest, non-blocking)

- The claim's `outputs` map lists `rehearsal.log` as the **result string**
  ("29 passed, 0 failed"), not a sha256 — cosmetic; the log itself is present and
  passes.
- **Stopped-run stop-marker quiet path** is covered by the plan (exit-64 marker +
  quiet-window pattern) but only the **kill** path was independently witnessed in
  repair-1; invalid-auth negatives reuse retained reviewed evidence per the receipt.
- Prep/binding10, live20, live-review10, promotion10 remain **held for Tern's
  signature**; nothing launched/installed; no production effect.

**PASS.** Returned via claim; Tern owns the live signature.
