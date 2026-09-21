# P2 r2.1 — bounded archive re-verification (PASS)

- **Verifier:** corvid (independent named reader; the controller corrected its
  own archive, so it cannot certify that correction — this pass does)
- **Date:** 2026-09-21; archive corrected 17:06:33Z; recheck deadline
  2026-09-21T17:26:33Z
- **Supersedes** the recheck verdict `fe20986b…` (FAIL on step 2 only) and the
  original v1 execution-verification verdict `9bdc6cdf…` (FAIL on the
  `changes.md:75` defect, now repaired).

## Verdict

**PASS.** All three bounded archive checks pass, and the worker artifacts were
already confirmed correct in the prior recheck. Both FAIL verdicts are
resolved: the `changes.md` defect was repaired, and the archive mislabel that
failed recheck step 2 has been corrected.

## Bounded checks

### (1) Pre-repair copy hash — PASS

`campaign4/p2r21-attempt-history/initial/changes.md.v1-FAIL` recomputes to
`a4aa894b85661c42cbad2d21ea67c160bd65913387a18cd1e6326fb4f04e1687` — the true
pre-repair v1, matching the value the corrected dispatch records.

### (2) Diff is exactly the line-75 bullet — PASS

`diff -u` of that v1 copy against the canonical repaired
`packages/P2-r2-boundary-amendment/changes.md`
(`c081291c67c7626f8cd93b830096b9ba81c2e13d41b00a7af06e0fc87c19ba22`) yields
exactly one hunk: the three-line "byte-identical to r1 v2" bullet at line 75
replaced by the three-line bullet acknowledging the added "Terminal boundary
duties (r2.1)" section and stating the remaining sections are byte-identical
to r1 v2/r2. Nothing else differs.

### (3) Six canonical artifacts unchanged — PASS

| Artifact | sha256 (recomputed) | Result |
|---|---|---|
| `contract.md` | `874354050fc81e3b366bcfe91904f1248c7248fd4927df025b28bc112840ef53` | unchanged |
| `transitions.md` | `3afedd357aefa40e3d402d8038337a57e8dc87beabffe8f0ad0bcc58c4f211e2` | unchanged |
| `ownership.md` | `cd198c0b6343bc7b06a133b851178482f6b3374c836081c38d9aae7bb9006dcf` | unchanged |
| `walkthrough.md` | `12348310cd92208e10685bacb44fb2ce8b84f6bbcc89bdc078e97adba772ba69` | unchanged |
| `changes.md` | `c081291c67c7626f8cd93b830096b9ba81c2e13d41b00a7af06e0fc87c19ba22` | unchanged |
| `boundary-schema.md` | `ec6daf093b59ea6b970a694960305e64e05862e93b812536967d8a56a16bfaa8` | unchanged |

All six match the recheck hashes; no artifact changed during the archive
correction.

## Findings carried forward from the recheck (already PASS)

The substantive verification was completed before the archive fix; those
findings stand unchanged:

- **All five carried r2 conditions PASS:** row 9a exhaustion for failed
  verification / withheld acceptance with no allocation (row 7 keeps valid
  negatives as COMPLETE); BLOCKED records carry originating phase, attempt
  identity and remaining allocation with row-11 return to CHECKING and no
  worker launch; precedence plus no-silent-fresh-deadline; walkthrough
  coverage of the actual chain, blocked resume, expired verification, and
  successful vs exhausted repair; continuity with r1 EXHAUSTED and r2
  SUPERSEDED unrewritten, both ownership questions and the trust boundary
  intact.
- **All six amendment conditions PASS:** explicit enumerable disposition with
  attributable director decision and evidence; `successor_opened` specificity,
  acknowledged dispatch, finite deadline, no cycles, chains reaching rest;
  the three legitimate rest kinds with resolvable blocked triggers and no
  premature silence-ladder entry; who decides/writes/commits, one authoritative
  ledger location, atomic publication/recovery and ledger completeness; the ten
  concrete example classes with unambiguous verdicts; and the actual r1
  omission as a failing example with its corrective successor chain, no
  invented historical BLOCKED event, and r2 exhaustion/resume preserved.
- **Minimal extension and scope PASS:** r2 outputs at `164bd06` untouched and
  matching; `boundary-schema.md` is a versioned controller state interface with
  exact JSON, enums, ordered validation rules and concrete valid/invalid
  examples; no watcher/controller code and no `state.json`.
- **Step 3 ownership check PASS:** `ownership.md` `cd198c0b…` is r2
  `c8126700…` plus only the "Terminal boundary duties (r2.1)" section; the
  corrected `changes.md` bullet matches those bytes.

## Note on independence

The failed recheck step 2 and its correction were in the controller's evidence
archive, not in any worker output. Cairn repopulated the copy and corrected the
dispatch entry; because a writer cannot certify its own correction, this
independent reader performed the bounded confirmation above.
