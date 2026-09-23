# Host-port findings: owned failure and terminal-close authority
Tern ruling, 2026-09-23. Source R18 accepted candidate at7857c0ce; affected
turn_handoff.py inspected. Reporter Claude, agent-loop c9ecbaa, scenarios in
conformance/host/scenarios.json. Local isolated probes and exact Python hash in
HOST-PORT-FINDINGS-20260923.json. No campaign implementation files modified.

## Finding1 — missing escalation bound
CONFIRMED: _recover references OwnedFault without importing it; missing bound
raises NameError. Go returning E_NO_ESCALATION_BOUND is the correct deliberate
reference divergence. A launch without an authorized recovery bound must reject,
not crash or invent a bound. Reject before dispatch when the bound is required;
a recovered historical malformed launch remains an owned visible failure, never
successful progress. Test public-entry handling as well as the helper error.

## Finding2 — false terminal closure on retry
CONFIRMED safety defect. _close_verify declares seen+intent, calls verify, then
submits decide separately. _roll_forward for director-close unconditionally writes
done and returns terminal-rest without checking or completing authoritative
verdict+disposition. Local stub probe confirms the unconditional branch; full
invalid-disposition scenario reproduction remains Claude's reported evidence.

RULING: Go MUST NOT preserve this behavior for parity. An intent, seen marker,
verifier PASS or terminal phase alone does not authorize terminal-rest. Complete
closure requires the exact authorized verdict+disposition committed for the bound
question/revision/execution; only then may a completion marker be written.

Validate disposition and identity before committing the close. Prefer the existing
trusted atomic verdict+decide transaction. Durable intent may precede it as recovery
metadata, but never represents completed work. Retry/reopen must reconcile ledger
facts under stable event IDs: commit an eligible authorized missing step atomically,
or return owned unresolved/blocked failure with done unset. Invalid/conflicting/
missing disposition must never be synthesized or substituted to finish a retry.
A historical partially committed verifier result is preserved, exposed as incomplete
closure and reconciled only within actual authority, not erased or blindly replayed.
Already complete matching closure may deduplicate; a different disposition cannot
overwrite the first. Crash after ledger commit but before done must recover without
double verification, duplicate disposition or duplicate sends.

Blocking P8 evidence on shipping Go: invalid disposition first call AND retry AND
reopen never terminal-rest/done; ledger/disposition absence remains visible. Genuine
atomic close succeeds once; crash on both sides of commit reconciles correctly;
wrong question/revision/execution and conflicting disposition reject. These refine
existing restart/evidence/pending-judgment checks, not a new P6 matrix or stage.
Both faults belong in corvid's product review and qualification checklist.

## Conformance and scope
Keep frozen Python inputs and recorded bad outcomes for historical reproduction.
Version these two cases as explicit adjudicated reference defects with this ruling
and separate required-correct Go expectations. Report parity excluding these named
divergences plus corrected-behavior results; don't claim all operations identical
after correction, don't skip the cases, and don't teach the Go product a known bug.
Every other Go/Python difference remains a finding. Parity and correctness are
separate claims. Reported23 scenarios/321 operations and42/42 mutation catches
are recorded as Claude's measurements, not independently rerun in this turn.

This authorizes the behavioral disposition within Brian's existing Go port scope;
no new fleet allocation, Python repair, live execution, adoption or P6 reopening.
P8/P9 remain unallocated. Python reference fixes, if later proposed, receive their
own provenance and corrected conformance pin; no silent rewrite of accepted bytes.
