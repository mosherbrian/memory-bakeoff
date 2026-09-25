# R10-recheck-1 — independent repair recheck

- **Reviewer:** corvid-dsh. Read-only; **no install, restart, fleet prompt,
  seat or Signal.** Within the recheck bound.
- **Intake:** recheck-receipt `ebaee9d5…`; repair-claim COMPLETE; all nine
  `repair/` hashes verified equal. Repair commit `65048a34` on
  `r10-new-session`; blob at that commit = `repair/acp-worker`
  `083f6eb7…`. Original claim, `evidence/`, `OPERATOR.md` and `verification.md`
  preserved (earlier INCOMPLETE stays on record).
- **Verdict: PASS (exact-byte readiness recommendation).** D1 and D2 are fixed;
  retained behavior and the newly-tested refusal path reproduce. Activation
  remains a separate, director-released, permission-checked action.

## D1 — positive provenance before `/new` — resolved

`repair/OPERATOR.md` now states "**Never send `/new` to find out which version
a seat runs**" and requires four checks before any `/new`: (1) installed hash ==
reviewed hash; (2) worker process started after the install mtime, matched by
`AGENTDECK_INSTANCE_ID`; (3) `acp-sessions/<seat>.json` lists `"new"` in
`features` with mtime ≥ process start; (4) `/ping` exactly `idle`. Any failure
⇒ do not send `/new`. Code supports this: `save()` writes
`"features": ["mlfile","socket","unattended","new"]` and only R10+ code writes
`"new"`. My independent probe confirmed a running candidate worker advertises
`['mlfile','socket','unattended','new']` and `/ping` returns `idle`. The
provenance check does not itself send `/new`, so an old runtime is never
prompted.

## D2 — `/compact`//`/earlier` exclusion — resolved, both orders

`/compact`//`/earlier` now `with self.ctl: self.transitions += 1`, release the
lock, run `compact_or_earlier()` (up to 330s), then re-acquire to decrement;
`/new` refuses while `transitions` is set (and names "compact/earlier in
flight"). The lock is not held during the long call, so prompt admission is not
stalled. Independent probe on `repair/acp-worker`:

- `/compact` (stub delay 3s) started, `/new` 0.5s later →
  `new refused: seat busy (compact/earlier in flight) - nothing changed`;
  no extra `session/new`; compact returned `compact done`; then `/new` switched
  to `stub-2`.
- Reverse order is covered by the repair suite's lock-then-increment path
  (a `/new` in flight makes a following `/compact` wait out the admission lock
  before marking in flight).

## Retained behavior — reproduced

- Repair suite `python3 repair/test-acp-worker-new.py repair/acp-worker` →
  **36 passed, 0 failed**.
- Planted faults `repair/mutants-acp-worker-new.py` → **14/14 caught**
  (includes `compact-not-guarded`, `feature-not-advertised`,
  `refusal-reported-as-success`).
- Refusal path now stub-tested, not just reviewed: with `STUB_MODEL_REFUSE`
  the reply is `new stub-2 SWITCHED but … REFUSED` (explicit non-success), and
  the fault is caught.
- Prior invariants unchanged: adapter error/same/missing id keep the old
  session and write no boundary; ACP_RESUME refused; busy/queued refused with
  queue intact; three-record distinction; unproven id not persisted.

## Limits

- No production install/restart/activation or fleet prompt performed. New code
  on disk does not change a running worker; kiln adopts it only at a separately
  authorized idle stop/start. StreamB still requires a completed paired trial
  and a director terminal decision. Reviewer grants no install authority.

*Reviewed: `recheck-receipt.json`, `repair-claim.json`, `repair/` (`acp-worker`
`083f6eb7…`, `OPERATOR.md` `c4acf290…`, diff, tests, mutants, results),
`verification.md` (preserved), `conductor-chat` commit `65048a34`; independent
`/tmp` socket probes.*
