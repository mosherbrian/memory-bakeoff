# Second-seat — Muse batch 6 (declared-list hygiene): are the ACCEPTs already covered?

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 18:1x UTC · **Cost:** $0, synthetic probes, one turn.
**Trigger:** `MUSE-IDEATION-06.md` handoff — "Assay/Alice: second-seat this note
(is any ACCEPT already covered? is the DUPLICATE correct?)".
Driver: `row-muse6-secondcheck/alice_muse6_check.py` (`eda98043…`), result
`result.json` (`32fc9540…`). Read-only over repo/team.

## Verdict

**All four ACCEPTs are genuinely uncovered; the item-4 DUPLICATE is correct;
the item-5c canary DUPLICATE is right for logic, not for live-arming.**
Reproduced each gap with the live guards (`check_identifier_lifecycle.py`
`f58a61c6…`, `check_cross_copy_drift.py` `f683903b…`):

| class | probe | result |
|---|---|---|
| **U6** vacuous pass | root with one stale `L-HS-02` doc, index `skip: DOC.md` | **rc 0, `citations=0 uncued=0`** — pass on an empty non-exempt denominator; without the skip rc 1 |
| **U7** inert entry | index `skip: DOES-NOT-EXIST.md` + `log: ALSO-MISSING.md` | rc 1 for the real doc; the missing entries are **never mentioned** — invisible |
| **U8** undeclared copy | two trees, `X.md` identical, `Y.md` diverged; declaration `shared: X.md` only | **rc 0, findings 0** (Y uncompared); declaring `Y.md` → rc 1, `cross-copy drift: Y.md` |
| **U9** index misses a supersession | ledger `supersed*` census | **6 marker lines, only 1 is an id move** (L793); the rest are label/prose/process |

Two constraints I would bind before the probes are built:

1. **U6 is a per-guard pattern with a precedent, not a new concept.**
   `check_map_hashes.py` already fails on `no coverage-map table rows` (empty
   map) and `check_frozen_id_provenance` counts `empty` rows, so U6 extends an
   existing idiom to the lifecycle guard — low cost, no new machinery.
2. **U9's derivation is the hard part.** The ledger's `supersed` surface is 1
   id move (`~~contradicted~~ **SUPERSEDED — see "L-HS split": L-HS-02a …` at
   L793) plus 5 non-id hits (the `third-party` **label** at L794/L860, a prose
   back-reference L821, the "Superseding table" header L853, and a process note
   L945). A word-based probe would report 5 false "missing supersessions"; the
   probe must parse only the id-mapping marker. As written it would also be
   green today (L-HS-02 is in the index), which is the intended canary shape.

**Item 4 DUPLICATE — correct.** The applied meta-guard (`6cd289e7…`) compares
live `check_*.py` against `_COVERED_NAMES` both ways (`uncovered` /
`orphan_controls`) and additionally refuses `_build_checks`-vs-declared drift; I
verified all directions in `team/ALICE-META-COVERAGE-APPLIED-CHECK.md`. Muse's
"required control implemented by zero checkers" = `orphan_controls`; "checker
advertising an unlisted control" = `uncovered`. The residual sub-case (a fixture
that no longer exercises its guard) is indeed the meta-guard's dirty-marker
contract, not statically checkable from the list.

**Item 5c canary DUPLICATE — mostly correct, one wording caveat.** The lifecycle
`--self-test` does plant `L-HS-02` canaries through the real `scan()` path, so
the detection logic is canaried. It is not a **per-run canary on the live
corpus** (Muse's literal proposal); the live 0-uncued census plus the self-test
is a reasonable substitute, but "DUPLICATE" is doing a little more work than the
code does. Not worth a probe (planting canaries in the live tree is intrusive);
worth one clause in the disposition.

## Scope and limits

- Synthetic fixtures in temp dirs plus one read-only ledger census; counts only;
  no tree modified.
- I did not build any of U6–U9; this only answers coverage, as asked. The probes
  and their self-tests remain Corvid's, per the note.
