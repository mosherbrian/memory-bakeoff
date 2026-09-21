# Changes in revision r2.1 — mapped to defects

**Basis:** r2's five outputs at commit `164bd06` (same bytes as r1 v2 at
`03b0ba2`: `contract.md 74c2f79d…` after r2's own edits — see below;
`transitions.md 3920a528…`, `ownership.md c8126700…`, `walkthrough.md
40699f70…`, `changes.md 5d490190…`) — immutable, kept outside this directory.
r2 completed 16:31:06Z inside its bound and was SUPERSEDED by this admitted
amendment; its unused repair/verifier allocations were cancelled, not spent.
**New requirement:** Brian's boundary-disposition instruction (after r2
launch 16:25:05Z — hence an amendment, not a hidden change): a missed
director handoff must be distinguishable from legitimate rest. **r2 defects
closed:** the two `acceptance-withheld.md` gaps (row 9a, CHECKING return —
inherited unchanged from the r2 candidate).

## r2.1 additions (boundary declaration)

- `transitions.md`: rows **17–18** (verdict-held pending bounded
  director-decision task; overdue/missing disposition → INVALID fault waking
  Tern) + "Terminal boundary declaration" section (atomic commit rule, four
  enumerable kinds, missing-disposition fault, BLOCKED≠blocked, chain
  resolution, single writer + atomic publication + validation points).
- `contract.md`: one boundary-declaration bullet + rev note (compactness
  holds — no per-package gate authoring).
- `ownership.md`: "Terminal boundary duties" table (Tern decides, cairn
  solely records/publishes/validates, worker/verifier evidence only).
- `boundary-schema.md` (new): exact JSON, field matrix, ordered validation
  rules, valid/invalid examples for all twelve amendment-condition classes.
- `walkthrough.md`: new examples 0 (actual r1→r2→r2.1 chain) and 3 (actual
  r1 omission as FAILING schema example + corrective chain as recovery, no
  invented BLOCKED event); r2 exhaustion/resume/repair/amendment cases
  preserved; P2's own tail PROJECTED.

## Inherited r2 closures (unchanged, summarized — full mapping in r2's changes.md)

Row 9a (failed-verification exhaustion, 7-vs-9a boundary); BLOCKED records
carry phase/identity/allocation; row-11 return to CHECKING without worker
launch; CHECKING precedence; no silent fresh deadline. `ownership.md` other
sections byte-identical to r2.


## Defect 1 → fix: no exhaustion path for failed verification / withheld acceptance

- **Defect** (`acceptance-withheld.md` §1): rows 7/8/9/14 left the
  unsuccessful-repair-with-no-allocation disposition implicit — row 14
  exhausts only from BLOCKED, so an implementation had to invent CHECKING →
  EXHAUSTED or an exhaustion route through BLOCKED.
- **Fix:** new row **9a** — CHECKING → EXHAUSTED on verification FAIL or
  withheld acceptance with no eligible allocation, with owned recorded reason
  (`failed-verification-no-allocation` / `acceptance-withheld`); Tern decides
  the terminal disposition and successor. Row 7 clarified: a valid negative
  finding completes there and never routes to 9a. New note pins the 7-vs-9a
  boundary for implementers.
- **Touched:** `transitions.md` (row 9a, row-7 text, 7-vs-9a note);
  `contract.md` (one summary bullet); `walkthrough.md` (example 3 walks the
  actual r1 history through 9a; example 6b walks exhausted repair).

## Defect 2 → fix: blocked verification could not resume correctly

- **Defect** (`acceptance-withheld.md` §2): row 9 could enter BLOCKED from
  CHECKING but row 11 returned only to REGISTERED/RUNNING — resolving a
  missing artifact during verification forced a worker rerun; phase/attempt
  identity and remaining verifier allocation were unspecified.
- **Fix:** row 9 BLOCKED records now carry **originating phase, attempt
  identity, remaining allocation**; row 11 returns to **CHECKING under the
  same attempt identity with no worker launch**, resuming inside the original
  verifier allocation; expired verification (remaining allocation zero) exits
  only via termination/exhaustion or an explicit recorded allocation — never
  a silent fresh deadline. New precedence note orders simultaneous CHECKING
  events (deadline → integrity → invalid measurement → repair → exhaustion).
- **Touched:** `transitions.md` (rows 9/11 text, precedence + no-silent-deadline
  notes); `contract.md` (one summary bullet); `walkthrough.md` (examples 4, 5).

## Unchanged

- `ownership.md`: byte-identical to r1 v2 — both decided ownership questions,
  independence rules, and standing constraints are intact per completion
  condition 5.
- Amendment path, budget-continuity rules, liveness/supervision section, §7
  demonstration gate: unchanged except cross-reference consistency (row
  numbers cited in notes).
- `contract.md` compactness: two bullets + one header parenthetical added; no
  new schema, no per-package gate authoring — Tern's line holds.
