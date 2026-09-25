# agent-loop

> **SUPERVISED PREVIEW / NOT QUALIFIED FOR UNATTENDED USE.**
> Qualification (campaign 4 P8) ended NOT READY. Run it only while a person
> watches it. Known limits: [docs/SUPERVISED-PREVIEW.md](docs/SUPERVISED-PREVIEW.md).

One Go binary that runs a small work loop over agent-deck seats: it sends a
package to a worker seat, sees the turn end, checks the worker's claim and
artifact hashes, sends the work to a different verifier seat, records the
verdict, and waits for a director's decision. A claim is not evidence, the
author is not the verifier, and every stall ends in either progress or one
owned escalation.

The reference implementation is Python, accepted package by package in
`memory-bake-off/campaign4`. The core and host blocks here are checked
against it (see Status); the loop product itself is Go only.

## Start here

| You want to | Read / run |
|---|---|
| Know what this build is and is not | this box, then [docs/SUPERVISED-PREVIEW.md](docs/SUPERVISED-PREVIEW.md) |
| Build it | `CGO_ENABLED=0 go build -trimpath -o bin/agent-loop ./cmd/agent-loop` (Go 1.27, Linux) |
| Make a private release | `tools/release.sh OUTDIR` (source tarball, binary, docs, `BUILD.json`, `MANIFEST.sha256`) |
| Install privately | `install -D bin/agent-loop ~/opt/agent-loop/bin/agent-loop` (any private prefix; nothing global) |
| Configure a project | copy `examples/project.template.json`, replace every `<...>`, then `agent-loop check --config FILE` |
| Run it, supervised | `agent-loop run --config FILE` in a terminal you watch (the systemd files are unqualified examples) |
| See state and pending decisions | `agent-loop expose --config FILE [--inventory FILE] [--json]` (read-only) or `agent-loop status` |
| Stop | `agent-loop stop --config FILE` (armed deadline timers still fire: stop is not cancellation) |
| Resume | `agent-loop start --config FILE`, or run it again in the terminal |
| Roll back | see Restore below |

Source tree: `cmd/agent-loop` (CLI), `internal/core` (the ported core,
frozen), `internal/host` (ported host blocks), `internal/loop` (the loop,
authority and liveness), `internal/expose` (the read-only view),
`internal/shadow` and `internal/coax` (campaign tools), `conformance/` (cases,
recorders, fault planting), `examples/`, `docs/`.

Requirements: Linux with a systemd user manager (the per-step deadline
timers use `systemd-run --user`), agent-deck with its `wake` script, and a
runtime that writes per-session turn streams in the acp-worker format. No
other runtime dependency; the binary is static (pure-Go SQLite).

### Restore

1. `agent-loop stop --config FILE`, and wait until `run` has exited.
2. Keep the previous binary beside the new one (`agent-loop.prev`) and swap
   it back: `mv bin/agent-loop.prev bin/agent-loop`.
3. The ledger is `<db>` plus `<db>-wal` and `<db>-shm`. Copy all three while
   `run` is stopped to back up; copy them back the same way to restore.
4. `agent-loop start --config FILE` (or run it again).
Armed deadline timers are not touched by any of this.

### Authority on this host

The CLI does not authenticate its caller: whoever can run it with a config acts
for the roles recorded in that config. Packages registered before principals
were recorded cannot be continued (E_AUTHORITY_MISSING).

## Status

| Part | State |
|---|---|
| Core: lifecycle, validator, store, ingress, driver, supervisor, status | Ported from P6-r13 (`c4ef8b98`, unchanged through R18); 125/125 cases, 1,751 steps |
| Host blocks: wake transport + receipts, outbox, systemd timers + callback guard, execution identity, turn watcher, claims, handoff, inotify | Ported from R18 (`b94ce3f6`). 316 of 321 recorded ops identical to Python; 5 held to the director's corrections of two reference defects (`conformance/host/adjudicated.json`, HOST-PORT-RULING-20260923), with their own tests (`internal/host/closure_test.go`) |
| The loop: `dispatch`, `run`, `status`, `claim`, `decide`, `stop`, `start`, `check`, `timer-callback`, `liveness` | Go only (no Python reference exists). `internal/loop` tests. P8 qualification ended NOT READY |
| The read-only view: `expose` | Go only (P9, P7's requirements). `internal/expose` tests |
| P6 fixture runner and timing gates | Not ported: proof tooling, not product |

81/81 planted faults are caught (`conformance/tools/mutate_go.py`: core, host, loop, view).

## The loop

One JSON config per project (`examples/project.template.json`). Every command takes
`--config FILE` or `$AGENT_LOOP_CONFIG`.

```
agent-loop dispatch --qid P1 --worker kiln --verifier corvid \
    --task @task.md --verify-task @review.md --duration 40m --verify-window 20m
agent-loop run                 # long-running; systemd user service
agent-loop status              # every package, its step, who it waits on
agent-loop decide --qid P1 --kind question_answered --ref R --reason "..."
agent-loop stop
agent-loop check               # every seat's session id confirmed in the agent-deck registry
```

Seats are session ids, confirmed against the agent-deck registry before any
dispatch: the loop sends to the same session it watches, and a session
registered under another name is refused. Worker, verifier and director are
three different sessions. `--input PATH` binds a file's hash at dispatch; if
it changes, the next dispatch (the worker's, or the verifier's) is blocked.
`--after QID` holds a package until QID closes with `question_answered` or
`successor_opened`; any other decision blocks it.

A package is one worker step and one verifier step:

1. `dispatch` records the director's authorization, arms a systemd one-shot
   timer for the worker's deadline (no timer, nothing is sent), and sends the
   task through the wake script. The task text ends with the exact
   `agent-loop claim` command the worker runs when it is done.
2. The worker runs `agent-loop claim ... --artifact NAME=PATH`, which hashes the
   files, and ends its turn. It wakes no one.
3. `run` sees the turn end in the runtime's stream file (inotify, and at least
   every 30 s). With a claim present it checks the turn, the claim and every
   artifact hash, commits the step, and dispatches the verifier with its own
   timer. A turn that started before the dispatch never counts. An end with no
   claim changes nothing; the deadline owns a claim that never comes.
4. The verifier claims `completed` (PASS) or `failed` (FAIL). The verdict is
   recorded and the director is asked to `decide`. `--on-pass KIND:REF:REASON`
   at dispatch pre-authorizes the close on a PASS; a FAIL always waits. A
   pre-authorized close commits verdict and disposition in one transaction,
   and nothing reports it closed until the ledger holds that disposition.
5. A due deadline (the timer runs `agent-loop timer-callback`) interrupts the
   step, sends `/cancel` to the seat, and wakes the director. Repeats are
   no-ops; a callback whose identity does not match the ledger is refused.

### Authority

The frozen core trusts only its fixed cast of actors (`kiln` worker, `corvid`
verifier and reader, `tern` director, `cairn` duty). At dispatch the loop
records which real seat and registry-confirmed session plays each role for that
package (`principals` in `status --json`). Every core call (dispatch, worker
handoff, verdict, `decide`, the pre-authorized close, the timer callback)
first checks that the config still binds that seat to that session, and is
refused `E_AUTHORITY_CHANGED` otherwise, before any effect. A package with no
recorded principals is refused `E_AUTHORITY_MISSING`; nothing is backfilled
from the current config. The CLI does not authenticate its caller: whoever can
run it on the host acts for the recorded roles.

### Supervision (unqualified: see the known limits)

The unqualified example `examples/systemd-unqualified/agent-loop@.service` runs `agent-loop run` with
`Restart=always`, a 90 s watchdog and a start limit (5 in 300 s).
`agent-loop stop` makes `run` exit 64, which is neither restarted nor a failure,
and `run` refuses to start while the stop marker exists; `agent-loop start`
clears it. Stop is not cancellation: armed per-action deadline timers still fire.

`examples/systemd-unqualified/agent-loop-liveness@.timer` runs `agent-loop liveness` every
45 s, as a separate process. It reads the pass that `run` records after each
completed Tick (no heartbeat thread), the stop marker and the unit state, and
reports `ok`, `rest` or `stopped` quietly; `hung` (no pass for 100 s),
`crashed`, `down`, `restart-loop`, `erroring`, `stop-pending` and `unknown`
open an incident. Duty is woken once with the exact `liveness-ack` command;
no acknowledgement by the next check, or an acknowledgement whose response
deadline passes without recovery, wakes the director (repeated at most every
15 min). A sent or queued wake is not an acknowledgement, and an
acknowledgement is not recovery: an incident closes as `recovered` only on a
fresh pass. Incidents live in `<db>.liveness.json`, not in the ledger.

A tampered artifact, a forged route in a claim or a stale turn stops the
package as `recovery` or `blocked` and tells the director. The worker and
the verifier must be different seats.

## Expose: the read-only view

`agent-loop expose --config FILE [--inventory FILE] [--base DIR] [--json]`
opens the ledger read-only and writes nothing. It shows the preview label, the
as-of time, the loop's last completed pass (UNKNOWN when absent or in the
future, STALE after 100 s), every package with its owner and next action, the
pending decisions (owner, exact question, what waits on it, next action,
source), resolved ones with their source, the known limits, and overhead
counted from ledger events by event type: worker dispatches (`start`), verifier
dispatches (`publish` opening a verifier flight), repairs (`alloc_repair`),
timeouts (`interrupt` with reason `deadline-expired`), director decisions
(`decide`), packages currently blocked, and each step's measured duration from
recorded event times (open steps have none; grants are never durations).
Costs are not in the binary: `steps[]` carries seat, session, `started_at` and
`ended_at` for an external join with provider billing.

An inventory (`examples/inventory.template.json`) adds records the ledger does
not hold, such as campaign decisions and qualification results. Each item is a
pointer with a pinned sha256; a missing file is UNKNOWN, a changed one is
CONFLICT, and a decision leaves the pending list only when `resolved_by` names a
file that exists with its pinned hash. Research is shown as not advanced by
this machinery.

## Shadow

Shadow mode replays the live ledger through the core, observe only: it wakes
no one and writes nothing the campaign reads. Each worker dispatch becomes one
core question; the verifier dispatch after its completion is linked to it (by
name, else by order, and the report lists every link made by order). The
report separates what the core's rules would raise from what the core has no
model for. It is a translation, so a finding is a lead to check against the
ledger, not a verdict. Following Tern's ruling
(`campaign4/SHADOW-TIME-AND-IDENTITY-RULING-20260922.md`), every item carries
a certainty (`exact`, `name-linked`, `order-linked`, `synthesized`) and the
ledger lines it rests on, and a decision is resolved only from an exact file
in the package folder (`acceptance.json`, `acceptance-withheld.json`,
`terminal-disposition.json`), never from message order.

### Coax (replacing openwork)

```
agent-loop coax          # dry: record what it would send to ~/.local/share/agent-deck/coax.log
agent-loop coax --live   # send it to cairn with wake
```

Coax tells the controller when a dispatched worker's turn has ENDED and no
result row for that dispatch followed within the grace period (2 minutes). It
reads facts, not proxies: the seat's acp-stream `end` event, the ledger rows
for that exact dispatch, and the receipt's `claim_path`. A turn that has not
ended is never called a stall. Each ended turn is coaxed at most once. It runs
LIVE every minute (`coax-dry.timer`, name kept from the dry run), with a copy
of each coax to notify-claude. Openwork still runs beside it for a day of
comparison; then openwork is retired.

## Build and check

```
go test ./...                                  # all cases against the Go core
CGO_ENABLED=0 go build -o bin/agent-loop ./cmd/agent-loop  # one static binary, no cgo
bin/agent-loop conformance                           # the same cases, from the binary
```

SQLite is `modernc.org/sqlite` (pure Go), so the binary has no C dependency.
It reads and writes the same database schema as the Python reference.

## The conformance suite

`conformance/cases/` holds every case, as language-neutral JSON. Each step is
one operation (construct an object, call a method or function, set an
attribute), what it returned or raised, and the full observable state after
it: ledger rows, durable key-value rows, in-memory projections, adapter
records. Comparison is exact, except that 1000 and 1000.0 are equal.

Where the cases come from:

- `p5/` - the P5-r2 package tests (78), recorded, not retyped.
- `p3core/` - the P3-r3 lifecycle tests (18); the lifecycle is byte-identical.
- `supplement/` - boundary cases (13) written for this suite. The package
  tests never probe exact boundaries (see below).

`conformance/PROVENANCE.json` pins the sha256 of every source and test file
the cases were recorded from.

Tools, all stdlib Python:

| Tool | Does |
|---|---|
| `record_py.py SRC TESTS OUT` | runs the Python tests with the public API wrapped; writes one case per test |
| `replay_py.py SRC CASE...` | replays cases on a Python source; must be 100% on the recorded source |
| `check_py.sh SRC TESTS OUT` | record, then replay |
| `mutate_py.py SRC TESTS CASES` | plants 20 faults in a copy of the Python source; each must be caught |
| `mutate_go.py REPO` | plants the same 20 faults in a copy of the Go port; each must be caught |

### Proof that the suite can fail

A suite that cannot fail proves nothing. Both implementations were given the
same 20 planted faults, one at a time:

| | Caught |
|---|---|
| Original Python tests (pytest) | 10 of 20 |
| Recorded cases, package tests only | 11 of 20 |
| Recorded cases plus boundary supplement, on Python | 20 of 20 |
| Same suite, on the Go port | 20 of 20 |

For every fault, the number of failing cases is the same on Go as on Python.

Not portable, and so not recorded: five tests that read Python source text or
the real host clock. Their Go equivalents are tests in
`internal/core/noeffects_test.go`: the core's own files import no `os/exec`,
`net` or `syscall`, and only the ingress calls the store's write paths. (The
SQLite driver underneath does import them; the rule is about the core.)

## Known behaviour copied on purpose

The port reproduces the reference exactly, faults included. These are known
faults of the reference and are present here too, until an accepted package
fixes them there and the cases are re-recorded:

- R13 fixed code-review findings 2, 6, 7, 10 and 11 (self-verification) in the
  reference, and the port follows. Finding 5 was not reproduced on the public
  path and is not claimed fixed. Host findings 1, 3, 4, 8 and 9 belong to P6
  harness code this repository does not port yet.
