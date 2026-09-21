# Changes in revision 2 — mapped to defects

**Basis:** r1 v2 documents at commit `03b0ba2` (`contract.md fd573ad3…`,
`transitions.md 77b79574…`, `ownership.md c8126700…`, `walkthrough.md
c45c72a2…`) — immutable inputs, preserved. **Defects:** the two gaps in
`acceptance-withheld.md` (Tern, 2026-09-21), which withheld freeze after a
narrow post-repair PASS (`49a52df6…`).

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
