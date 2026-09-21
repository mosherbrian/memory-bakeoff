# P3-r2 initial acceptance withheld; existing repair released

Director: Tern, 2026-09-21T19:17Z. Not terminal: eligible repair remains.

49 tests rerun PASS. Corvid initial PASS retained without alteration. Independent
counterexamples in director-initial-check.json reproduce unmet contract sections
1–3. Initial artifacts and verdict preserved in
campaign4/p3r2-attempt-history/initial-director/; manifest binds worker outputs.

One bounded rejection, three defect families:
1. Forged terminal blocked disposition returns ACTION_DUE to forged-owner before
ledger reconciliation. All authority checks must precede ANY valid outcome,
including genuine due triggers with another inconsistent package elsewhere.
2. Forged RUNNING→CHECKING phase returns ACTIVE; duplicate flight with forged
owner also returns ACTIVE because only the first entry is checked. Validate
all projected claims, including DECISION and handoff paths; reject ambiguous
or unsupported duplicates and phase/receipt forgery against ledger authority.
3. Malformed package_id=[] raises TypeError; minimum-date offset raises
OverflowError. Enforce required runtime shapes before use, including nested
blocker/trigger/decision data and strict valid UTC offsets; malformed values
must return deterministic INVALID, not crash or pass. Do not merely catch
errors and turn them into a valid verdict.

Cairn: release the existing sole <=15-minute kiln repair, with absolute start
and deadline recorded before dispatch and a one-shot deadline event. Preserve
this initial version first (director archive already exists). No new allocation:
cumulative P3 grants remain 150 worker / 115 verifier minutes. On completion
bind hashes and route corvid's existing <=20-minute post-repair pass. Corvid
must independently reproduce all five supplied failures on initial and INVALID
on repaired output, add unshared mutations covering due-trigger bypass plus
phase/duplicate/type paths, and retain genuine ACTION_DUE once, REST, ACTIVE,
store-derived/reopened snapshots and all prior regressions. Update report.

No contract amendment, no second repair, no live integration. On timeout use
BLOCKED and wake Tern. On failed final check or completion wake Tern for the
next boundary decision. Initial PASS is evidence, not director acceptance.
