# P13 timeout audit 2 (read-only, bounded)

- **Action:** `P13-timeout-audit-2`, owner corvid, `07:22:06Z`–`07:37:06Z`.
- **Timed-out attempt:** `P13-liveplan-completion-1`, timeout `07:20:10Z`, ack
  `07:20:32Z`; **no completion claim**. Frozen snapshot
  `attempt-history/plan-completion-timeout/manifest.json` (**12/12 hashes match**).
  Latest offline: **34 PASS / 6 FAIL**.
- **Verdict: NO PASS / no reclassification.** Production `97a57db1` unchanged; no
  live/promotion. No rerun of live/service commands; no source edits.

## Exact remaining root failures

1. **Deadline reached before the ladder (root cause of 4 of the 6 fails).** The plan
   logs `PREP PASS` at `07:18:48.995Z`, then the wall fires `WALLSTOP: stopping
   p13live-driver-off1.scope` at `07:20:10.467Z` — the offline `LIVE_DEADLINE` is
   only ~80 s after PREP, so the plan exits **rc 3** before dispatching/decision.
   This produces `FAIL plan rc=3`, `FAIL LIVE PASS missing`, `FAIL stop marker
   missing`, `FAIL rollback PASS missing`. **Classification: test-infrastructure /
   plan-parameter defect** (the accelerated fixture window/deadline is mis-set
   relative to setup), not a product defect; the plan's `PREP` and all old-fail
   negatives pass.
2. **Shared state changed.** `snap_shared` hashes/line-counts the **shared**
   `campaign4.db`, `wake-send.log` and `escalations.jsonl` before/after; one changed
   during the offline run. **Classification: plan/test isolation defect** — the
   offline run must touch only private paths; identify the writer and redirect it to
   the private ROOT/ledger.
3. **`FAIL FAIL rows in live results`** is downstream of (1)/(2) (the run did not
   complete a full ladder); classify after (1)/(2) are fixed.

## Frozen snapshot / retained evidence

- Snapshot **12/12** verified; `evidence/plan-repair/offline-test.sh` and the
  `offline-1/` raw logs are retained (failures preserved). Old-fail negatives all
  PASS (F1 config, F2 argv, F3 invented strings/json.load/task turn, F4 archive
  leak, F5 PREV-from-candidate + rollback order), as do four-seat PREP, full config,
  runnable worker/verifier turns, outside checker, literal/guessed ack refusal,
  caps redaction/removal, seat removal, run-start capture, promotion guard/rollback.

## Director-record rewrite investigation

- Current `timeout-response-reconciliation.json` = **`e880003f…`** (Tern's structured
  record, with `evidence` hashes and `owner`/`ruling`/`followup`).
- Observed rewritten copy preserved at
  `attempt-history/plan-completion-timeout/timeout-response-reconciliation-observed.json`
  = **`c906600a…`**, a compact JSON `recorded_by: "cairn (duty)"`, different schema.
- **Finding:** an author/controller rewrote a director record. The original is
  restored and the observed copy preserved; **authors/controller must not rewrite
  director records.** No further mutation performed.

## New-author handoff (precise)

Files: `plans/live20-plan.sh`, `evidence/plan-repair/offline-test.sh`,
`plans/promotion-plan.sh`, `plans/prepare_live.py` (plan-local).
1. Set the offline `LIVE_DEADLINE` / accelerated ladder so the full ladder completes
   after `PREP` (line ~`offline-test.sh` inputs), then re-run `bash
   evidence/plan-repair/offline-test.sh`; require `plan rc=0`, `LIVE PASS`, stop
   marker and `ROLLBACK PASS`.
2. Fix the **shared-state** leak: make the plan/run write only under the private
   ROOT/ledger; re-assert `snap_shared` BEFORE == AFTER (shared `campaign4.db`,
   `wake-send.log`, `escalations.jsonl` untouched).
3. Preserve `evidence/plan-repair/p6-indent-bug.md` (non-dry-run prep blocked on the
   P6 `prepare_live.py` indent) as a separate Tern-disposition finding.
Successful evidence to retain: the 34 PASS rows and all old-fail negatives.

## Cleanup

- No active `p13live-*`/`p13repoff*` units.
- **10 leftover `/tmp/p13repoff-*` workdirs** from the offline attempts
  (`-41NjwL`, `-4DFulb`, `-8PHba6`, `-9RiMum`, `-ktxsFE`, `-OMPiyV`, `-osfAFG`,
  `-QYItCe`, `-QyRokP`, `-vTUySf`) — **reported only, no broad tmpdir removal**;
  Tern/Cairn to remove by exact path.

No author/runtime claim; no retroactive acceptance; live/prep/promotion held. No fake
verifier claim created.
