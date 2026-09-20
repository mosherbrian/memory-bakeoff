# CORVID-S4-11-VERIFY.md — corvid-dsh verification of QUEUE row S4-11

**Verdict: PASS** — 2026-09-16 14:45 PDT. kiln-flash authored; corvid-dsh
verifies (independence holds).

## Declared check

Both dirty fixtures rejected through the real path, rc 0 as declared:
`rowguard-claimlock --queue fixtures/claimlock-dirty.md` exits 1;
`rowguard-prereg --prereg fixtures/prereg-a.md --checklist fixtures/prereg-b.md`
exits 1 (the S3-1 two-producer class and the FirePrecision 54/150-vs-30/150
drift class respectively). Both `--self-test` runs: rc 0.

## Synthetic clean/dirty matrix (beyond the fixtures)

| Case | rc | Correct |
|---|---|---|
| claimlock: clean queue (single claimed per row) | 0 | ✓ holds |
| claimlock: double `claimed:` on one row | 1 | ✓ rejected |
| prereg: checklist identical to prereg | 0 | ✓ holds |
| prereg: checklist diverges on an `N/M` metric (S3-1 class, synthetic) | 1 | ✓ rejected |

No second dialect: both guards reuse the rowcheck exit contract (named
findings, rc 1 iff findings) — consistent with rowcheck's self-test classes
verified in CORVID-S4-8-VERIFY.md.

## Scope note (non-blocking)

`rowguard-prereg` diffs metric-shaped tokens (`Name N/M`). A prereg containing
no parseable metric at all passes vacuously — nothing is frozen, so there is
nothing to diff; coverage findings still fire when the prereg HAS metrics the
checklist lacks (self-test case 3). Defensible boundary; worth a line in the
next guard revision if preregs ever become free-form.

Row S4-11 moves done → **VERIFIED (PASS)**. corvid-dsh, 2026-09-16 14:45 PDT.
