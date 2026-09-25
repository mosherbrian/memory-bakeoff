# R8 task feasibility: exit-127 gate-conflation repair in fleet-poller.sh

## Request (real, recorded)

Commit `cbc9d52` (Brian, 2026-09-17): "Exit 127 was hiding six broken gates;
a truncated check now FAILS instead of vanishing." Found by kiln: rowcheck
splits table cells on `|`, so a declared check containing a pipe truncates
and the remainder executes the literal word `check:` (exit 127); row_gate
mapped 127 to `none` ("no command declared"), silently downgrading "a
command was declared and could not run" into "never had a gate." Six live
rows declare piped checks, so six gates were not running and nothing said
so. This is ordinary recurring fleet-maintenance work with a verifiable
useful artifact (gates that cannot run are reported failed).

## Before / fixed revisions (immutable pair, originals untouched)

- Broken: `cbc9d52^:workers/fleet-poller.sh`, sha256
  `a987e2e98ed752ae36a2996612cbd63853d91ef6e5df51dc58124f6d40677e3e`.
- Fixed: `cbc9d52:workers/fleet-poller.sh`, sha256
  `6607dc1a993bfacb348aef2e14a30c2131675891d03ba8119389248b46e33ed8`
  (+29 lines: mis-split signature detection — a declared check beginning
  with `check:` counts failed with a log line naming the pipe; legitimate
  prose rows still read `none`).
- Check: `workers/test-fleet-poller.sh` (current committed version), run
  unmodified against isolated copies in `/tmp/r8-sandbox/`; bash 5.3.0,
  no network, no model calls.

## Results (exact, from evidence/)

- Broken copy: exit rc=1. Findings printed: "a DECLARED check that cannot
  run counts FAILED, not absent (expected: fail, actual: none)" and "127
  logging (expected: a log_once naming exit 127, actual: absent)". Tally
  line reads "116 passed, 1 failed" (the first finding prints from a
  subshell and is tallied separately; both findings are real — see
  `evidence/check-broken.log` lines 119–124).
- Fixed copy: exit rc=0, "117 passed, 0 failed"
  (`evidence/check-fixed.log`).
- The contrast is exactly the defect: piped checks that cannot run are
  reported failed with the pipe named, while prose rows keep `none`.

## Historical constraint relevant after restart

The check file's own standing rule: "nothing goes into fleet-poller.sh
until this is green," with exit contract 0 = clean / 1 = findings. Both
future arms receive this identical rule with the task; it constrains the
solution shape without revealing it.

## Boundary capability and memory contrast

This task needs no session boundary: single local shell execution against
files on disk. Stated prerequisite is python3/git/bash only (all present).
For a later paired pilot, runtime sessions are the existing agent-deck seat
sessions (registry IDs with socket identity); the boundary record would be
session ID plus sha256 file inventory at session end/start. Memory vs
control differ only in prior-session notes retrieved; all ordinary files
(task, gate, reviews, tools) are identical in both arms. No compaction
boundary observed or claimed.

## Contamination and limits

I have read the fix commit message (which describes the defect) and the
check expectations — seen-task feasibility scope only; completion must be
by independent execution, and any later unbiased estimate needs unseen
tasks. Second candidate considered and excluded: agent-loop `6a44c76`
(withdrawn-capability test) — a test-only addition with no production
behavior contrast, and no Go toolchain exists on this host to run it
(`which go` empty; missing-dependency failure must not be called a task
defect). No efficacy claim; choosing this task implements no memory system.
No experiment, code edit, install, or shared-file write was performed.
