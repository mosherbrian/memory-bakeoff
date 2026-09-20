# Second-seat check — map-hash completeness fix (guard 15 residual) verified

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 14:39 UTC · **Cost:** $0, local, one turn · **Trigger:** standing
second-check of `team/ASSAY-MAP-HASH-COMPLETENESS-FIX.md` (unapplied diff).
Read-only.

**Subjects:** diff `b96ecc54…`, guarded `cda1ee4a…`, power check `988a0e47…`,
result `2dd9f6fe…`, target `137a39c4…`.

## Verdict

**PASS / AGREE — the residual is real, the fix closes it, and the two directions
coexist.** Canonical rev 2 silently ignores a live guard with no map row; the
guarded version flags it, while still flagging a map row that names a missing
guard. Live map: 0 findings (all 15 guards covered). Diff applies cleanly.

## Verified

| claim | check | result |
|---|---|---|
| diff `b96ecc54…`, guarded `cda1ee4a…`, power `988a0e47…`, result `2dd9f6fe…` | re-hashed | ✓ all match |
| diff applies in `repo-glm-dsh3` | `git apply --check` | ✓ rc 0 |
| power check 5/5 | re-ran | ✓ rc 0 |
| **residual reproduced** | synthetic scripts with `check_b.py` unlisted in the map | ✓ canonical `[]` (silent) |
| **fix** | same map, guarded | ✓ `missing guard row: check_b.py` |
| map→live direction still fires | map row names `check_d.py`, absent from scripts | ✓ `map names a missing guard: check_d.py` **and** the missing-row finding |
| live map clean | guarded, live map + live scripts | ✓ 0 findings, rc 0 |

So `check_map_hashes.py` now covers both directions of the duplication invariant
(every map row ↔ a live guard), which is what the coverage map's "inverse view"
role needs.

## Note (intended strictness, not a defect)

The reverse check is `scripts.glob("check_*.py")`, so **any** file named
`check_*.py` in the scripts dir is demanded in the map — including a future
non-suite helper. That is the right default for this directory (only suite
guards live there), but if a shared helper is ever added under that prefix it
will need a map row or a rename. Worth one line in the guard's docstring.

## Limits

- Synthetic maps under `/tmp` + one live run of the guarded copy with explicit
  `--map`/`--scripts` (as Assay's limits note); no tree modified.
- It checks listing/hash coverage, not that a guard is semantically the right one
  for its defect class (the map's stated limit, unchanged).
