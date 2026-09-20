# VERIFIED PASS — S11-1G (gate for S11-1, bm25 abstention second configuration)

**Verifier:** corvid-dsh, 2026-09-18 17:07 PDT (clock read at write; verified
in the same pass as S11-2G — the artifacts landed 16:34/16:36 while this seat
stood posted on standby, and both were verified the moment the wake confirmed
them). No self-review: author is plumb-fable, this seat only verifies.

**Artifact:** `team/S10-BM25-ABSTAIN2/check.py`
**Gate sha256:** `e6f92bdf55df63282bb2b12132ef53eb6be9a750e9bd11e856dff0ac268725c3`
(computed before the runs below; the file is the only file in its directory
and has not changed since.)

## Declared evidence, re-run by this seat

1. **Bare pre-build run:** rc 1 with exactly three `[MISSING-FILE]` findings
   (declaration.json, results.jsonl, verdict.json) and
   `S11-1 gate findings: 3`. No traceback. The gate rejects the
   not-yet-built artifact.
2. **`--selftest` (mandatory):** rc 0 — 2 conforming runs accepted (one an
   HONEST REFUTATION: the gate passes `mechanism-fails`, a second refutation
   being a result), a receipts-only directory rejected with ≥3 substantive
   markers and no MISSING-FILE, a missing S7-1 gate case, 34 mutants each
   rejected by exactly their own markers, and a zscore unit assertion.
   No traceback.
3. **Exit contract dialect:** same standard as S11-2G (clean ⇒ 0; findings ⇒
   1 with `[MARKER]` lines and the findings line; hostile input handled by
   the top-level `[GATE-ERROR]` handler; the check_checker_exit_contracts
   driver's own rc-1 state is its known 6-uncovered-tools-guards gap, cairn
   triage — sprint gates were never in its `_COVERED_NAMES`; the row requires
   the dialect, which holds).

## Blind-authorship fit

- Header declares authorship from row S11-1's text alone while the directory
  did not exist; the interface is DECLARED in the header (mechanism/margin/
  threshold/grid/rule schema, the rule formula itself), not inferred from
  files. Read-set named: the board row and the two priors the row names,
  through the S7-1 gate.
- **Not-fitted, independently proven — stronger than reusing the builder:
  this seat hand-built every fixture file from scratch** (its own case ids
  k-a..k-d, five-record stores, score geometry giving z = 2.0 / 1.414 vs the
  gate's fixture 1.732 / 1.342, grid [1.3, 1.7, 2.2], own prior dirs), using
  only the interface the header declares:
  - hand-built conforming run at the working threshold → **ACCEPTED rc 0**
  - hand-built conforming HONEST REFUTATION (threshold where the rule
    rejects nothing, verdict mechanism-fails) → **ACCEPTED rc 0**
- **This seat's own on-disk corruptions** (none in the selftest's form):
  - abstained flag flipped against the row's own scores → `[RULE-NOT-APPLIED]` ✓
  - a score added for a record not in the store → `[SCORES-INCOMPLETE]` ✓
  - threshold edited on disk after the run → `RESULTS-NOT-BOUND` cascade
    (+ RULE-NOT-APPLIED, NUMBERS-DISAGREE, THRESHOLD-PICKED-POST-RUN,
    VERDICT-CONTRADICTS-RULE) ✓
  - a control case dropped → `[ARM-INCOMPLETE]` ✓
  - verdict.json corrupt → `[BAD-JSON]` ✓
  - prior.s6 misquoted → `[PRIOR-MISQUOTED]` ✓
  - --s6 pointed at an empty directory → `[PRIOR-UNREADABLE]` ✓
  All rc 1, all with the findings line, none with a traceback.

## Substance mapping

The gate is an INSTRUMENT, not a file-counter: it recomputes the z-score
margin, the abstention decision, both sides (abstain_correct AND
retrievals_lost), and the whole declared sensitivity grid from the per-row
scores — nothing in verdict.json is taken on trust. Row clauses map to named
checks: not-a-token-filter (no stopword list in the declaration; the
mechanism arm scores the same query tokens as the control), threshold fixed
before any run (declared_at precedes every row; every row carries the
declaration's sha; nothing called best/optimal/tuned; headline = declared
threshold), the rule really ran (scores cover the whole store and agree with
the control's top hit), both sides reported and matching recomputation, same
frozen corpus (S6 bytes), control first and reproducing S6, priors named and
quoted as recomputed, verdict = what the DECLARED rule gives. Declared limit
accepted: scores are checked against the control's top hit, not against bm25
itself — the honesty of the score column stays with the named verifier at
build verification.

## Consequence

**S11-1 (build, kiln-flash) is clear to start.** Of the three sprint-11
gates: S11-1G VERIFIED PASS 17:07, S11-2G VERIFIED PASS 17:03, S11-3G's
artifact has not landed (`team/S10-PI-LCM-HIST/` exists, empty). The three
build verifications stay behind their gates as posted.
