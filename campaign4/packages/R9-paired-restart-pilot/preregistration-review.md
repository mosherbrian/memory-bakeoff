# R9-prereg-review-1 — preregistration review (read-only)

- **Reviewer:** corvid-dsh. Read-only; **no reset, restart, model task,
  runtime-state write, seat or Signal** — runtime operation remains HELD.
- **Intake:** `prereg-review-receipt.json` `aa121b77…`; preparation claim
  `COMPLETE_WITH_OBSTACLE`, all listed hashes verified at intake.
- **Verdict: PASS (preparation/preregistration only) with mandatory
  pre-execution corrections.** The obstacle is real; the minimum corrections
  below must be recorded and Tern must authorize the runtime op before any
  execution release.

## Frozen scoring / equal files — pass

`run-plan.md` (755 ≤1000 words) fixes scoring before outcomes: unchanged
`test-fleet-poller.sh` in both arms; success = test rc 0, 0 failed, diff limited
to `fleet-poller.sh`; SKIP recorded identically and never a task failure; no
retuning; timeouts/partials reported. Treatment is a ≤300-word summary returned
as **reply text** (not a file) so control's ordinary files stay identical;
inputs (broken.sh, test, rowcheck, acp-worker) are hash-pinned in
`input-manifest.json`; `fixed.sh` is excluded from every arm. Contamination is
disclosed (seen task; worker may know the fix).

## Fresh-session mechanism and CLI — verified against source

- acp-worker has **no** operator command for a new conversation: the handlers
  are `/compact`, `/earlier`, `/ping`, `/cancel`, `/mlfile`
  (`workers/acp-worker` lines ~1266–1346). The run-plan's claim is correct.
- `fresh_session()` (`session/new`) runs at start when the state file has no
  sessionId (`resume()` returns false → `fresh_session()`, lines 790/818); the
  state file stores `sessionId: self.session if self.proven else None`
  (line 947). So the null-sessionId mechanism is the existing path.
- **`--force` is a real documented flag** on `agent-deck session restart`
  (verified `--help`: "Restart even if the session is already healthy and
  fresh"); `-force` exists, `--all`, `-env` too. Not an invented command.
- Engine-identity proof is adequate: pane banner appends " (resumed)" only when
  loaded (code confirms), `opencode session list` exists on PATH as an
  independent store, and a new state-file sessionId is required.

## Old-process overwrite race — must be addressed before release

`save()` is called only at process start on resume (line 795), in
`fresh_session()` (831), and once when the session becomes **proven** (1080).
There is **no shutdown, signal, or periodic save** (no `atexit`/`SIGTERM`
handler). So a genuinely idle, already-proven old process is unlikely to rewrite
the state file between the null write and the restart; and a stall/interrupt
during that window (`fresh_session()` at 1025) would write a *new* id, which
still yields a fresh conversation. The race is therefore low-probability — but
the plan's order (write null → restart) is the unsafe order and this analysis is
not recorded.

**Minimum correction:** either (a) reorder to confirm idle/outbox, **stop** the
old worker and verify its PID is gone, *then* write `sessionId: null`, then
start/restart; or (b) keep the current order and record the `save()`-call-site
analysis above as the safety argument. Either way, name the exact read-only
idle/outbox commands (currently unspecified), and apply the same stop-before-edit
(or recorded justification) to the **restore** step.

## Limits

- Feasibility only, n=1/arm, seen task; no general efficacy claim. Runtime op
  unauthorized here; StreamB start still requires a completed paired trial and
  director terminal decision. Preparation reproduction (116/1, 117/0) matches
  R8 with pinned snapshots; the optional lookup assertion stays a documented
  identical SKIP. No approval of execution beyond a readiness recommendation.

*Reviewed: `prereg-review-receipt.json`, `package.md`, `preparation-claim.json`,
`run-plan.md` (`f2eeaa8d…`), `preregistration.json` (`3f3b93be…`),
`input-manifest.json` (`e00f19ae…`), `templates/*`,
`conductor-chat/workers/{acp-worker,test-fleet-poller.sh}`, `agent-deck session
restart --help`.*
