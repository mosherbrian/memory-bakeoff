# P8 candidate readiness — Go8dda2bb
Tern, 2026-09-23. Read-only intake; full pins and registry evidence in
GO-CANDIDATE-INTAKE-20260923.json. Candidate exists, not fleet-qualified/adopted.
No installed binary was run; no model calls, timers or live sends made.

## Decision
Do not dispatch live P8 or install/adopt this candidate. First close these four
concrete prerequisites inside the already sponsor-directed Go product work:

1. Declared-input validity: bind declared inputs at registration and revalidate
before dependent dispatch. Changed/missing inputs invalidate eligibility with
owned visible reason; no stale or silently updated registration authorizes send.
2. Explicit dependency/judgment gate: unresolved prerequisite decision blocks
registered dependent dispatch. Record authorized dependency identities, reject
unknown/cyclic dependencies, resume only on an actual eligible recorded resolution.
Independent packages remain supported; independence is not evidence that a
requested dependent gate works. No general workflow engine needed.
3. Apply HOST-PORT-RULING-20260923.md finding2. internal/host/handoff.go still
writes done+terminal-rest unconditionally on director-close retry, and closeVerify
commits verify then decide separately. internal/loop.finishVerify calls that
host path for --on-pass. No disposition means no closed/rest; use authoritative
atomic closure and restart reconciliation. Finding1 already returns the correct
owned fault. Preserve expected divergences, not a misleading blanket identical
parity claim or README requirement to copy reference faults.
4. Correct and validate role/session configuration. examples/campaign4.json
corvid is56513e0e-1790000758, which live registry identifies as CAIRN; actual
corvid is493c0317-1790000758. Current transport sends logical names while the
observer uses configured session keys: they must identify the same intended seat.
Do not merely correct a string and infer safety. Validate the chosen fixture
routes/stream identities and principal separation before dispatch. Examples must
not be used as live bindings. Fresh isolated fixture identities required for P8.

These are finite readiness requirements, not new P6 rounds or a fleet allocation.
Claude owns the sponsor-authorized Go work. Tern owns acceptance of the next pin.
P8 can preregister checks against these known failures when its contract is opened;
no live work or product PASS until the blockers are corrected and independently
checked. Do not spend an admission solely to rediscover known absent features.
P8 remains one bounded package, <=4h prospective cap, one repair then demonstrate
PASS/NOT READY at cap. P9 remains packaging, not a place to hide safety repairs.

## Required P8 evidence on the next pin
Bind source commit, reproducible build/toolchain/platform, exact binary hash,
project config and isolated resources. Core/host parity plus named reference
exceptions and new entrypoint tests are separate. Exercise production dispatch/run/
status/claim/decide/stop/timer-callback, not a Python substitute. Existing fixed
checks remain: restart uncertain delivery no resend, enforced hung-step stop+owner,
input invalidation, pending-dependent block, evidence recovery, and truthful rest.
Include both missing-bound and false-terminal-close regressions already ruled on.
SQLite WAL/atomic claim files are mechanisms, not proof of interrupted composition;
real systemd+stub wake smoke proves timer plumbing, not actual seat cancellation.
No broad new latency matrix, runtime source-time port, fixture runner port or
multi-project expansion. Reported mutation coverage is useful sensitivity evidence,
not proof that all authorization/composition paths are correct.

No new fleet allocation now. Connect/P7 terminal decisions remain unchanged. No
script retirement or parallel live controller. Current candidate and installation
remain reference for evaluation only until separately authorized qualification.
