# P2 r2.1 boundary amendment — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P2-r2-boundary-amendment/package.md`,
  sha256 `b897d6e26a0820ed603505c6c35d7990250ebefcc3873394d6930553e1cfcbae`,
  commit `3fc43430c67627829218d9a9ea51c57a749d5802` (both re-derived from the
  committed blob; working tree byte-identical)
- **Design under validity review:** `boundary-design.md`,
  sha256 `e696393df67471d5ecd2b2e6e35e7d858b9b5a79ce36793eec4503f44cbe3e89`
  (same commit; recomputed, matches)
- **Pass bound:** one 15-minute admission pass; absolute deadline
  2026-09-21T16:45:36+00:00

## Disposition

**ACCEPTED**, bound to the exact bytes above. This is admission of a
specification to be produced, and a validity review of the proposed interface.
The design is a coherent, testable starting point; the contract's completion
check demands the properties the sponsor requirement names. Nothing here is
implemented code, and admission does not certify a schema that does not yet
exist — that is execution verification after the worker publishes.

## Machine-readable terminal disposition

Design: four enumerable kinds (`successor_opened`, `question_answered`,
`budget_spent`, `blocked`), "No free-text kind and no 'idle means done'
inference"; status and required relationships are structured, reasons/evidence
may be prose (boundary-design.md:7–9). Package.md:59–61 requires an explicit
enumerable disposition plus attributable director decision and evidence, with a
missing declaration a state fault "regardless of fresh file activity or an
active seat." Confirmed adequate.

## True legitimate rest, no endless alarms

The design closes the actual watcher defect. The current backstop
(`~/.config/agent-deck/campaign4-watch`, lines 43–63) reads a provisional
string map and alarms a historical `successor opened` whenever nothing is in
flight — it does not follow chains. The design instead follows the link
"through terminal successors to either real in-flight work or a legitimate
rest leaf… reject cycles/dangling links. This prevents a historical succession
record from becoming a permanent false alarm after the last successor
legitimately finishes" (boundary-design.md:63–68). Rest leaves are
`question_answered`, `budget_spent`, `blocked` (70–78), and package.md:64–66
requires completed successor chains to reach valid rest without permanent
alarms. Confirmed adequate.

## Exact successor linkage and historical completed chains

Package.md:62–64: `successor_opened` must identify the specific successor and
observable in-flight work with an acknowledged dispatch and finite deadline;
an unrelated busy seat/package does not satisfy it; a missing, never-dispatched
or broken reference is invalid; cycles are invalid. Design adds follow-to-leaf
validation (63–68). Confirmed adequate, and it directly addresses the r1
failure mode (a warranted successor not opened).

## Publication, authority, ledger completeness

Authority is explicit: Tern decides each terminal boundary; cairn records the
attributed decision and publishes; "Worker completion and verifier PASS are
evidence, not authority to invent a director disposition"
(boundary-design.md:11–14). One authoritative location is named — the
controller event ledger, with `state.json` an atomic derived snapshot written
by cairn alone, ledger transaction before publication, temp-file/flush/rename,
and rebuild-from-ledger on interruption; "an old snapshot cannot authorize new
dispatch or silently hide closure" (49–61). Package.md:72–76 requires who
decides, who writes, when committed, one location, atomic recovery, immediate
validation, and ledger-completeness checking so "an empty declaration cannot
hide known terminal packages." Confirmed adequate.

## Blocked triggers

The design gives `blocked` a blocker id, reason, owner, and a machine-readable
wake trigger (event id and/or revisit timestamp); no generic silence alarm
while correctly parked; when the trigger is due, wake the owner once and create
bounded in-flight decision work; indefinite unowned waiting is invalid
(boundary-design.md:75–78). It also distinguishes a terminal `blocked`
disposition from a live lifecycle BLOCKED without conflating their permissions
(80–84). Package.md:67–71 mirrors this and keeps rest out of the generic
silence ladder only before a valid trigger/revisit deadline. Confirmed
adequate.

## Retained r2 gaps and cumulative allocations

- r2's five completion conditions remain required (package.md:28), and item 6
  requires the actual r1 omission as a failing example, the corrective
  successor chain, preservation of the r2 exhaustion/resume cases, and no
  invented historical BLOCKED verification event (82–84). r1 stays EXHAUSTED
  and r2 becomes SUPERSEDED only after its attempt ends and evidence is
  captured, with no execution transition out of a terminal and no claim that
  cancelled allocations were spent (39–43).
- Allocation arithmetic is correct and non-resetting: r1 (worker 60+30,
  verifier 30+30) + r2 (worker 30+15, verifier 2×20) = 135 worker / 100
  verifier, as carried from r2; this amendment adds worker 30+15 = 45 and
  verifier 2×20 = 40, giving cumulative ceilings 180 worker / 140 verifier
  (package.md:89–100). Cancelled unused r2 allocations are reported separately,
  actual cost/time stays separate from ceilings, unknown stays unknown, r1's
  repair remains spent, and r2's executed attempt remains counted. Confirmed.
- Independence holds: author/authority Tern, reader/verifier corvid, worker
  kiln, controller cairn; the reader did not repair the contract, and a
  rejection is one bounded disposition (package.md:74, 91–92).

## Non-blocking observations

- The design's illustrative terminal record (boundary-design.md:38–46) shows
  r1 pointing directly to `P2-r2.1`, skipping live r2. It is explicitly
  labelled illustrative, and package.md:49–50 forbids copying it as real
  history, so this is not a defect; the worker's walkthrough must show the
  actual r1→r2→r2.1 chain.
- `campaign4/state.json` does not exist yet; the design's "retain … as the read
  interface, replace the shape" is accurate against the watcher's commented
  provisional schema (campaign4-watch lines 43–46). The package correctly
  forbids publishing a speculative state.json (package.md:115–116, design
  101–105).
- `boundary-schema.md` field-level completion and valid/invalid examples are
  the worker's deliverable, so their current absence from the proposal is not
  an admission defect.

## Effect and release

Admission is bound to contract bytes
`b897d6e26a0820ed603505c6c35d7990250ebefcc3873394d6930553e1cfcbae` at commit
`3fc43430c67627829218d9a9ea51c57a749d5802`. Cairn may release this exact
unchanged amended contract to kiln only after (a) this ACCEPTED admission is
recorded and (b) the old r2 attempt has ended or been stopped at its original
bound with its five outputs, dispatch record, full commit and hashes captured
and pinned, and unused r2 allocations cancelled and recorded. No overlapping
kiln attempt; changed bytes require independent confirmation. No watcher,
state.json, controller or other code under this contract.
