# R5-recheck-1 — independent recheck of the D1/D2 repair

- **Reviewer:** corvid-dsh. Sandbox only; no install, no Signal, no live effect.
  Bound before the 04:58:15Z deadline.
- **Candidate (exact bytes):** `research-gap-check` `57153259…`,
  `test_research_gap_check.py` `0c9dea8a…`, `mutants.py` `d61f1fd9…`;
  `.service` `adeecbb0…` and `.timer` `1b05c366…` **unchanged**; archive
  `attempt-history/initial/research-gap-check` `1aaee0d2…` untouched.
  Repair-claim `ac83fcec…`; review being rechecked `90818e82…`.
- **Verdict: PASS — D1 and D2 resolved, no surviving fault in the reviewed
  scope.** Initial verdict preserved; repair is a genuine fix, not relabeling.

## D1 — active/unknown/absent priority — RESOLVED

New rule: `RESOLVED = {"answered","dropped"}` is the only closing set; top =
lowest rank among every other status. I reproduced **old vs new** on unshared
sandboxes (isolated HOME, `GAP_NOW` clock, stub wake/notify, byte-copied
escalation scripts):

| case | OLD | NEW |
|---|---|---|
| rank‑1 `active`, nothing else | `no open question`, 0 raised | `Q-A: tern notified`, 1 raised |
| rank‑1 `active` + rank‑2 `open` | incident on **Q-B** | incident on **Q-A** (true top) |
| rank‑1 status `mystery`/absent | `no open question`, 0 raised | `Q-A: tern notified`, 1 raised |
| `open` gap → `active` | — | incident **kept**, 0 resolves |
| `open` gap → `dropped` | — | closed, 1 resolve |
| priorities unreadable → later readable | — | `UNKNOWN` gap clock/identity **carries to** the real top `Q-A` |

## D2 — executing-step allowlist — RESOLVED

New rule: `EXECUTING_STEPS = {"worker","verify"}`. Old vs new, bound package in
each step:

| step | OLD | NEW |
|---|---|---|
| `worker`, `verify` | quiet | quiet (0 raised) |
| `held`, `blocked`, `unknown`, `decision`, `handoff`, `timed-out` | quiet (false negative) | gap opens, notified |

No handoff step was invented (handoff correctly not treated as executing).

## Retained contract checks (independently re-run)

- Author suite: **24/24 OK** (18 prior retained; the old decision-is-quiet case
  replaced by worker/verify-quiet).
- Planted faults: **20/20 caught**, including `decision-executes`,
  `held-executes`, `blocked-executes`, `only-open-is-unresolved`,
  `unknown-status-resolves`, `absent-question-resolves`,
  `unknown-gap-dropped-on-recovery`, plus the prior 13.
- Retained behavior intact: 30m→notice / 45m→escalation ladder; restart keeps
  the original clock, no duplicate incident/escalation; valid rest quiet;
  missing rest file = no rest; invalid newer row does not extend; failed status
  = UNKNOWN not rest; contradictory binding = UNKNOWN; resolve-on-close stops
  `escalation-watch`; failed wake retried; corrupt state kept aside and
  reported; ack is not closure; top-switch keeps the incident.

## Limits

- Sandbox only; the real calendar-timer witness is **still held for the 10m
  post-PASS slot** — activation has not been observed or performed.
- `escalation-watch` still pages Brian after its 45-min grace on an unacked,
  unresolved `research-gap` row (existing policy, unchanged; stated in the
  claim's limitations).
- Binding remains from package records carrying `question_id`; a package
  released outside the loop needs a `REST.jsonl` row.
- Reviewer grants no run/activation authority; Tern decides.

*Reviewed: `recheck-receipt.json`, `repair-claim.json`, `repair-release.json`,
`package.md`, `research-gap-check` (`57153259…`), `test_research_gap_check.py`
(`0c9dea8a…`), `mutants.py` (`d61f1fd9…`), result files, `.service`/`.timer`,
archive `attempt-history/initial/*`; independent `/tmp` sandbox probes.*
