# Sponsor decision: agent-loop Go release target
Recorded by Tern at 2026-09-23T04:25:40.656824+00:00, relayed by Claude from Brian.

## Binding target and scope
The deliverable is a single Go binary, agent-loop, repository
https://github.com/mosherbrian/agent-loop. Brian's explicit sponsor decision
supersedes IMPLEMENTATION-LANGUAGE-DECISION-20260922.md for the DELIVERABLE ONLY.
That historical decision and accepted Python contracts/source/verdicts stay intact.
Python remains the behavioral reference and source of the conformance suite.
Every Go/Python difference is a finding for Tern, not automatically a Go defect or
permission to bless a known Python defect. Adjudicate and version corrections.

Clarification from Brian, 2026-09-23: no standalone loop product exists in Python
either. Python harness.py is the P6 fixture runner, not a production entrypoint.
Claude ports reusable host BUILDING BLOCKS: transport and receipts, outbox,
systemd timers and callback guard, execution identity, turn watcher, route-free
claims, handoff and inotify, with Python/Go parity tests. Claude builds the NEW
product entrypoint agent-loop run/status/stop in Go on top of those components.
The fixture runner and P6 timing gates are NOT ported. Other Python fixture/proof
tools remain development evidence, not shipped runtime requirements.

Python is the reference where equivalent core/component behavior exists. There is
NO Python reference for the new product entrypoint and no claim of whole-product
parity. P7 is an unaccepted view prototype, not an accepted status implementation.
No new fleet package, allocation, kiln implementation task or operations in the
target repository is requested or released by this record.

Brian/Claude report current Go core parity on125 R13 recorded cases (core
unchanged throughR18) and25/25 planted faults. Preserve as reported evidence;
this turn did not independently rerun or certify those results. Core parity does
not certify newly ported host operations, P7 functionality or live adoption.

## P8 and P9 adjustments
P8 MUST qualify the exact shipping Go program, or both implementations with Go
explicitly included. Bind agent-loop commit, built binary SHA256, build/toolchain,
platform and runtime configuration to results. Python-only success cannot pass a
Go release. Retain the fixed five open adoption checks and existing package cap;
no new Connect chain. Python proof tooling may drive the binary but must exercise
its real production paths; no substituted Python controller behind a Go command.
For run/status/stop and component composition, P8's predeclared acceptance checks
and corvid's independent review are the proof, not conformance to a nonexistent
Python program. Test those public commands against the same persisted state and
effects: launch/handoff, restart/uncertain delivery, enforced stop, input and
judgment gates, truthful status and evidence recovery. Retain the eight overall
architecture checks; prior Python results do not exempt new Go orchestration.
Component parity and product acceptance are separate evidence in the verdict.
This clarification changes the qualification target, not the fixed scope/cap.

P9 packages that Go binary, with docs/config/install/run/status/stop/restore and
known limits. Normal source and tests live in agent-loop; preserve provenance to
accepted Python pins without copying/re-writing campaign history. State supported
OS/architecture and actual host dependencies (agent-deck/runtime/service manager)
plainly. A single Go binary does not eliminate external agent runtimes or make
host-specific adapters universal. Python proof tooling remains optional development/
qualification tooling, not an undisclosed runtime requirement.

P7 ended EXHAUSTED, not accepted. Its view may be reused/ported but its false
cache-free claim and current-stage/link limitations are not an accepted spec.
P8's visibility/enforcement evidence and P9's shipped status/docs must be checked
on the actual Go output; the port cannot inherit a PASS by translation.

## Director disposition
No safety objection to the target change. The essential safeguard is exactly
Brian's requirement: qualify what ships. Known reference defects remain findings;
no historical Python witness is transferred to Go. No release/adoption/cutover,
script retirement, new live fixture, fleet allocation or budget expansion follows
from this target decision. P8/P9 remain unallocated pending concrete contracts.
