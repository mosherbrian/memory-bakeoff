# R10-review-1 — independent review

- **Reviewer:** corvid-dsh. Read-only: **no production install, restart, model
  prompt, seat or Signal.** Within the review bound.
- **Intake:** review-receipt `2f4f…`; claim `2f4f3816…`; all 10 listed artifact
  hashes match. Source commit `ab82f157` on `r10-new-session`; blob at that
  commit = `evidence/acp-worker` `5543a23f…`; installed
  `~/.config/agent-deck/acp-worker` = `6871ceb1…` = the stated base, **unchanged**.
- **Verdict: INCOMPLETE (outcome failed).** The code is sound on the tested
  paths (I reproduced 30/30 and 11/11), but the contract's idle-only rule and
  the activation-safety requirement are both violated as delivered.

## Reproduced independently

- `python3 evidence/test-acp-worker-new.py evidence/acp-worker` → **30 passed,
  0 failed** (real process, real unix socket, stub engine).
- `mutants-acp-worker-new.py` → **11/11 caught**.
- Installed runtime bytes unchanged; unrelated dirty files untouched; the drift
  hook was bypassed with `--no-verify` because the branch is deliberately ahead
  of the host (correctly documented).

## D1 — activation probe is unsafe (blocking)

`OPERATOR.md` says to learn whether a seat runs the new code by sending
`/new` and seeing whether it replies `new ...` "rather than being sent to the
model as a prompt." I proved against the **old** runtime (`a457a71`, the
installed bytes) that `/new` is **not** a control command there: it returns
`{"ok":true,"status":"started"}` and the stub engine receives a
`session/prompt` whose text is literally `/new`. So probing with `/new`
**starts a model turn** on any pre-R10 seat — the exact side effect this
package forbids.

The steering is explicit: require **positive process/version provenance
BEFORE** sending `/new`; `/new` itself must not be the first version probe.
**Correction:** determine active version from file hash + worker process start
time vs install time (as OPERATOR.md's "Mirror" paragraph already gestures at),
and only then send `/new` on a verified-idle seat. Never probe by `/new` on an
unverified runtime.

## D2 — `/new` does not serialize with other control transitions

The idle predicate covers running/queued/permission-pending and is correctly
locked against prompt admission (`self.ctl`, running set under the lock —
verified). But `/compact` and `/earlier` take **no** `self.ctl` and never set
`self.running` (`workers/acp-worker` ~1266–1283: `self.call(method, …, timeout=330)`
directly). The contract requires `/new` to reject while "another control
transition in flight."

I demonstrated the race: on the candidate worker with a stub whose
`session/compact` sleeps 4s, I sent `/compact` on one connection and `/new` on
another 0.5s later. `/compact` returned `compact done` and `/new` returned
`new stub-2 …` — i.e. `/new` **switched sessions while `/compact` was still in
flight** against the old session. (On the `-32601` fallback `/compact` calls
`self.prompt()`, which would set `running`; the direct-method path does not.)

**Correction:** have `/new` and the other control transitions share an
in-flight guard (e.g. track a control-in-progress flag under `self.ctl`, or
admit `/compact`//`/earlier` through the same lock), and add a planted fault /
concurrency test for `/new` vs an in-flight `/compact`.

## Adequate / accepted as scoped

- Truthfulness on adapter error / no id / same id: old session kept, no
  boundary written, never success — tested, reproduced.
- Three-record distinction (reply id vs history boundary vs persisted-proven
  state) is correct; unproven new id not persisted.
- ACP_RESUME refusal prevents silently resuming the named conversation.
- `SWITCHED but … REFUSED` model/mode path is code-reviewed only, and
  permission-pending is defensive-only — both disclosed; not blockers, but the
  refusal path should get an independent stub probe before activation.

## Limits

- No activation/install/restart/model prompt performed; StreamB still requires
  a completed paired trial. New code on disk does not change a running worker;
  R9's freshness mechanism remains unauthorized. Reviewer grants no install
  authority.

*Reviewed: `package.md`, `completion-claim.json`, `OPERATOR.md` (`3991112f…`),
`evidence/acp-worker` (`5543a23f…`), `acp-worker.diff`, `test-acp-worker-new.py`,
`mutants-acp-worker-new.py`, `test-results.txt`, `mutants-results.txt`;
`conductor-chat` commit `ab82f157`, installed `acp-worker` (`6871ceb1…`),
old runtime `a457a71:workers/acp-worker`; independent `/tmp` socket probes.*
