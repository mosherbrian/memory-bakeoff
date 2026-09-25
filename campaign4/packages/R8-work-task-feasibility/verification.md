# R8-task-1 — independent review

- **Reviewer:** corvid-dsh. Read-only; no trial, live effect or author edit.
  R7 terminal (`RETIRED` S13 gate-repair pilot) treated as input.
- **Worker claim:** `ex-R8-task-1-w1.json`; hashes verified equal —
  `task-feasibility.md` `7eeac137…`, `manifest.json` `d08951a9…`.
- **Verdict: INCOMPLETE (outcome failed).** The selected task and its
  broken/fixed contrast are real and reproduce, but two output requirements are
  unmet: the required test inputs are not hash-pinned, and the recorded tallies
  are environment-dependent in a way the report does not disclose.

## Reproduced on the pinned pair (conductor-chat)

- Request/commit `cbc9d52` exists (real recorded fix); HEAD `a457a71`; working
  tree `workers/` clean — originals untouched.
- Hashes match: broken `cbc9d52^:workers/fleet-poller.sh` `a987e2e9…`, fixed
  `cbc9d52:…` `6607dc1a…`.
- Same existing check `workers/test-fleet-poller.sh` (unmodified) against
  isolated copies: **broken rc=1, fixed rc=0** — the exact defect contrast
  (a declared piped check is reported FAILED with the pipe named; the fixed
  revision passes). Relevance confirmed: the commit's own narrative shows the
  first too-broad fix was caught by this same existing assertion.

## D1 — required test inputs not pinned

The package requires pinning "required existing test inputs." `manifest.json`
pins the request commit and the before/fixed revs, but gives no sha256 for the
**check script** (`workers/test-fleet-poller.sh`, only a path) nor for the
external tool the check invokes, `~/.config/agent-deck/rowcheck`
(`ROWCHECK_BIN`). The test script is only indirectly referenced via the
informational `repo_state.conductor-chat_HEAD`; neither byte-set is bound.
Hash both (or, for `rowcheck`, record its hash and absence fallback).

## D2 — environment-dependent tally not disclosed

My clean reproduction gives **115 passed, 1 failed** (broken) and **116 passed,
0 failed** (fixed); the report records **116/1** and **117/0**. The single
difference is one assertion, `conductor lane enables the promise check
(acp-pi-worker)`, which prints `SKIP  cannot resolve the conductor's wrapper
(agent-deck unavailable)` here and PASSED in the author's live environment. The
rc and failure counts are unaffected, so the contrast is sound — but the report
records the tallies as fixed numbers and its `environment` block omits this
dependency. Per the task, a missing-dependency skip is a **setup error, not a
task defect**: record it as such so the counts are reproducible.

## What passes

- Real recorded request and immutable historical broken/fixed pair; existing
  regression used unmodified — no custom replacement oracle.
- Ordinary code repair (not an audit/eval framework, live seat/systemd effect,
  new infrastructure, or recall question).
- The second candidate (agent-loop `6a44c76`) is correctly excluded as a
  **missing-dependency** failure (no Go toolchain), not called a task defect.
- Equal ordinary files/tools across future arms; a real post-restart constraint
  named (the check's standing rule "nothing goes into fleet-poller.sh until
  this is green"); boundary prerequisite stated (single local shell run;
  later pilot would use existing agent-deck seat sessions); seen-solution
  contamination disclosed; no efficacy claim; evidence hashes verified from the
  repo root.

*Reviewed: `package.md`, `task-feasibility.md` (`7eeac137…`), `manifest.json`
(`d08951a9…`), `evidence/check-{broken,fixed}.log`, conductor-chat `cbc9d52`
and `workers/test-fleet-poller.sh` (HEAD `a457a71`),
`~/.config/agent-deck/rowcheck`; independent `/tmp/r8-sandbox` runs.*
