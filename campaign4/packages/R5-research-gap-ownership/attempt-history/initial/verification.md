# R5-review-1 — independent review

- **Reviewer:** corvid-dsh. Sandbox only; no install, no Signal, no production
  change. Review bound 2026-09-25T04:59:40Z (met).
- **Intake:** completion-claim `7a5ca82a…`; contract `37561222…`; all listed
  file hashes verified equal at intake (`research-gap-check` `1aaee0d2…`,
  `research-gap-check.service` `adeecbb0…`, `research-gap-check.timer`
  `1b05c366…`, `test_research_gap_check.py` `32da8631…`, `mutants.py`
  `3676b598…`, `test-results.txt` `a5c6eccf…`, `mutants-results.txt`
  `116e709f…`, `dryrun-production-inputs.txt` `b22042b9…`).
- **Verdict: INCOMPLETE (outcome failed).** The completion check's planted-fault
  set is incomplete: two required fault classes survive — an `active` priority
  vanishes/closes its incident, and non-executing loop steps (`held`, `blocked`,
  `unknown`, and arguably `decision`) count as executing work.

## Independently reproduced

- Author suite: `python3 test_research_gap_check.py` → **18 tests, OK**.
- Author mutants: `python3 mutants.py` → **13/13 caught**.
- Required happy paths hold in sandbox: no-package ladder fires notice at 30m
  and escalation at 45m; restart keeps the original clock and does not
  duplicate; valid rest quiet; missing rest file = no rest; invalid newer row
  does not extend; failed status = UNKNOWN not rest; contradictory binding =
  UNKNOWN; close appends resolves; failed wake retried; corrupt state kept aside
  and reported. Bounds honest (≤1 tick/≤5m added).

## Defect D1 — `active` priority is excluded (steering item 1)

`top_and_open()` selects `i.get("status") == "open"` only, so a rank‑1 question
with status `active` is invisible. Reproduced in an isolated sandbox:

- Q-A rank 1 status `active`, no package/rest → check prints `no open question`
  at t+0/30/45/60m and opens **0** incidents. A top active priority with no
  executing package silently vanishes.
- Q-A `active` (rank 1) + Q-B `open` (rank 2), no work → the incident opens on
  **Q-B**, not the actual top question.
- Q-A `open`, gap opens and notifies at 30m; then Q-A → `active` one tick later
  → the check prints `no open question` and **closes the incident**
  (`resolves: 1`). An active question without a live package resolves an
  incident — exactly the forbidden outcome.

**Fix:** treat `active` as a first-class in-progress priority (include it in the
top/open set and never let it close an incident), or explicitly record the
status vocabulary and map it to open-equivalent.

## Defect D2 — non-executing steps count as executing (steering item 2)

`IDLE_STEPS = {"closed", "timed-out"}`; every other step is treated as live. A
package bound to Q-A with step `held`, `blocked`, `unknown` (and `decision`,
which the author's own `test_bound_active_package_is_quiet` enshrines as quiet)
keeps the check at `ok (package P1)` for t+0/30/45m with **0** incidents:

```
held     -> ok (package P1) x3, raised 0
blocked  -> ok (package P1) x3, raised 0
unknown  -> ok (package P1) x3, raised 0
decision -> ok (package P1) x3, raised 0
```

A held/blocked/unknown package is not research executing, so a top question in
that state for 30m should open the planning gap. The current rule produces a
false negative.

**Fix:** define the executing set explicitly (e.g. `worker`/`verify`/`handoff`
in-flight steps) and treat every other step — including `held`, `blocked`,
`decision`, `unknown` — as not executing; add a planted fault for each.

## Other contract checks — pass

Reads are read-only against `RESEARCH-PRIORITIES.json`, `agent-loop status
--json`, `REST.jsonl`, and question_id bindings from package records; no name
inference (name-lookalike test passes); one append-only rest file with the six
required fields and UTC instants, latest valid row governs until `revisit_at`;
escalation clock starts at notice and is persisted through restart; one existing
escalation ledger, no second ledger/Signal; ack is not closure; top-switch keeps
the incident; resolve-on-close stops `escalation-watch`. Stated bounds include
calendar accuracy and runtime.

## Limits

- Sandbox only; the real calendar-timer witness remains **held for the 10m slot
  after PASS**, per release. No production timer/install/Signal observed.
- `escalation-watch` still pages Brian if a `research-gap` row is unacked and
  unresolved for its 45-min grace — existing policy, unchanged, stated in the
  claim's limitations.
- Reviewer cannot grant run authority; Tern decides repair/next.

*Reviewed: `package.md`, `completion-claim.json`, `review-receipt.json`,
`research-gap-check` (`1aaee0d2…`), `test_research_gap_check.py`,
`mutants.py`, `mutants-results.txt`, `test-results.txt`,
`dryrun-production-inputs.txt`, `INSTALL.md`, `.service`/`.timer`,
`campaign4/REST.jsonl`. Independent probes in `/tmp` sandboxes (isolated HOME,
GAP_NOW clock, stub wake/notify, byte copies of installed escalation scripts).*
