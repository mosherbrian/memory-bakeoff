# Assay — ROW9 blind-harness samples rebuilt under rev 2

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, local, sealed-counts only
**Trigger:** `team/ALICE-ROW9-BLIND-HARNESS-RECEIPT-CHECK.md` — the four sample
packets are **rev 1** (`dc7a53f2…`) under a rev-2 (`e2d91e81…`) receipt table,
and the s3 sample still carries the bare-confirmer leak rev 2 was written to
scrub. **Owner of `blind_pack.py`/samples: fsync.** This note rebuilds them.

## Rebuild (documented flow, same seed/close)

```
python3 team/blind_pack.py build --kind s3 \
  --sessions '/home/bmosher/acp-pi/.pi-agent/sessions/*/*.jsonl' \
  --window-open 2026-09-12T11:05:00-07:00 \
  --window-close 2026-09-12T21:30:37Z --seed sample-not-for-rating \
  --out /tmp/assay-row9-rev2-s3
# s2 identical + --min-overlap 2 → /tmp/assay-row9-rev2-s2
```

Both builds rc 0 (the rev-2 leak gate passed and wrote).

| | rev-1 sample | rev-2 rebuild |
|---|---|---|
| s3 `script_sha256` | `dc7a53f2…` | **`e2d91e81…`** |
| s3 items | 11 | **11** |
| s3 bare confirmer words | **4** | **0** |
| s2 `script_sha256` | `dc7a53f2…` | **`e2d91e81…`** |
| s2 items | 15 | **15** |
| s2 bare confirmer words | 0 | 0 |

So Alice's finding is reproduced and the fix is confirmed: rebuilding under rev 2
yields a clean s3 sample (**4 → 0 bare confirmer words**, `[confirmer]` markers
2 → 6) with the same item count.

## Answer integrity across the rebuild (s2 key detail)

The s2 **rated items are byte-identical** across rev 1/rev 2
(`items_sha256 587a8c64…` unchanged), so the extra scrub does not perturb s2
content. Its `key_sha256` changed (`75ba65fe…` → `938b161b…`) **only** in the
top-level `sessions` metadata: the non-`sessions` parts are equal, and
`sessions` 15 → 20 because the live tree grew. **No answer/label drift.**

s3's item/key hashes necessarily change (the scrub edits rated text, and item
ids are content-derived).

## Input-drift caveat (recommendation)

The live session tree now matches **20** files where the rev-1 sample used
**15**. The pinned `--window-close` keeps `n_items` stable (11 / 15), but the
rebuild is **not byte-reproducible from the live tree**. Recommended (owner
fsync), matching the S5 lesson: freeze the input manifest for the sample run, or
quote the per-sample `script_sha256` in the receipt table rather than the
revision header. Also close the stale line "second seat re-check of rev 2
requested from Assay" — that was completed 2026-09-12
(`ASSAY-BLINDPACK-REV2-RECHECK.md`).

## Limits

- Scratch builds in `/tmp`; no `team/` file and no live session content modified.
  Counts and hashes only — no rated text printed, sealed KEY not displayed.
- The samples remain **not for rating**; this is a receipt-revision fix, not an
  S2/S3 result.

## Receipts

- Rebuilt s3 manifest: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-row9-rev2-rebuild/s3-rev2-MANIFEST.json`
  sha256 `3a0701f07e65…`
- Rebuilt s2 manifest: `.../s2-rev2-MANIFEST.json` `d95241424ade…`
- Comparison: `.../comparison.json` `b2c9054f52d0…`
- Rev-1 scratch: `/tmp/fsync-row9-final-143037/` (unchanged); rebuilds in
  `/tmp/assay-row9-rev2-s3`, `/tmp/assay-row9-rev2-s2`.

— **Assay** (`worker-glm-dsh2`). No tree modified.
