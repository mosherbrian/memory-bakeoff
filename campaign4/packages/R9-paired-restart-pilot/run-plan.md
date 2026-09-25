# R9 run plan: one seen-task paired restart pilot (summary delivery)

Preparation only. Nothing below has run. Operator: Claude. Worker: kiln (idle, sequential). Reviewer: Corvid.

## Task and inputs (from R8 director closure, hashes in input-manifest.json)
- `fleet-poller.sh` = broken.sh (cbc9d52^), the exit-127 declared-check misclassification.
- `test-fleet-poller.sh` (a457a71), unchanged in both arms. Pinned with `ROWCHECK_BIN` and `ACP_WORKER` to the arm's own `rowcheck` and `acp-worker` snapshots.
- Reproduced in preparation on fresh copies with these pins: broken rc=1 "116 passed, 1 failed"; fixed rc=0 "117 passed, 0 failed". The optional live-registry lookup is not reached with these pins; if a SKIP line appears, it is recorded as SKIP, identical in both arms, and never counts as a task failure.
- fixed.sh is NOT copied into any arm and is not in any prompt.

## Arms and treatment
- Two arms, T (treatment) and C (control), each in its own copy: `/var/home/bmosher/r9-arms/<arm>/` holding fleet-poller.sh, test-fleet-poller.sh, rowcheck, acp-worker and an empty notes/. Arm directories sit outside the campaign4 tree, so the R8 closure (with fixed.sh) is not beside them.
- Same model and seat config (kiln, `opencode-go/muse-spark-1.3-contributor`, same wrapper), same prompts, same minutes.
- Phase 1 (10 min): templates/phase1-task.txt. Inspection and notes only. In T only, the operator then sends templates/summary-request.txt in the same conversation; that time is inside T's phase-1 10 minutes.
- Fresh conversation boundary (see below).
- Phase 2 (10 min): templates/phase2-resume.txt. T gets templates/summary-block.txt with the verbatim summary in {SUMMARY_BLOCK}. C gets an empty {SUMMARY_BLOCK}. Nothing else differs. Both keep all their files and notes.
- Order: before the first worker prompt, the operator records `python -c "import secrets; print(secrets.randbits(1))"` in execution-log.json; 0 = T first, 1 = C first.

## Fresh conversation: the existing mechanism, and the obstacle
acp-worker (kiln's runtime) has no operator command for a new conversation. `/cancel`, `/compact`, `/ping`, `/mlfile` exist; none starts a new session. A plain restart (`agent-deck session restart`) does NOT qualify: on start, acp-worker reads `acp-sessions/a79067ca-1790000758.json` and calls `session/load` with the stored sessionId, which resumes the old conversation.

The only existing code path that opens a new conversation for this seat is `fresh_session()` (ACP `session/new`). It runs when the state file holds no sessionId (on start), or after a stall. Proposed operation, for each boundary (before T-phase1, C-phase1, T-phase2 and C-phase2):
1. Confirm kiln is idle and its outbox has nothing for it.
2. Copy the state file aside once (`kiln-state-before-R9.json`, hash recorded).
3. Write the same state file with `"sessionId": null`, all other fields unchanged.
4. `AGENTDECK_PROFILE=campaign4 agent-deck session restart a79067ca-1790000758`. agent-deck skips a restart of a session started in the last 60 s; the operator confirms a new worker PID, and uses `--force` only if the restart was skipped.
5. Evidence of a fresh identity: acp-worker saves a new sessionId only once the session is proven, so it is read after the first reply. The new sessionId in the state file differs from every earlier one; the pane banner has no "(resumed)"; `opencode session list` (the engine's own store, independent of acp-worker) shows the new session id; the first worker reply is checked for no mention of earlier-phase content not in its files.
After the trial: restore the saved state file byte for byte and restart once, so kiln returns to its normal conversation. Its history file is append-only and is not touched.

This touches kiln's runtime state file and restarts the seat. That is a runtime operation this preparation is not allowed to perform, and the contract does not already grant it. **Tern must authorize it explicitly, or name a different mechanism.** If not authorized, the obstacle stands: no fresh conversation is available on kiln without it, and no harness is invented here.

## Scoring (fixed now; not retuned after outcomes)
Per arm, phase 2: SUCCESS when the unchanged test exits 0 with "117 passed, 0 failed" (a documented identical SKIP allowed) and the diff touches only fleet-poller.sh. Also recorded: test output and rc before and after, wall-clock minutes to first passing run, worker actions (from acp-history), whether T's summary was delivered and whether the worker referred to it, whether any arm read files outside its arm dir or any git history of conductor-chat (a contamination flag, reported, not hidden). A timeout, partial fix or edited test is reported as such.

## Interpretation limits (stated before the run)
n=1 per arm, seen task (kiln may know the historical fix), same model both arms. This can show that the procedure works and give one paired observation. It cannot show that memory helps in general.
