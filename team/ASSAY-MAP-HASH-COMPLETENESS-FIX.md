# Assay — coverage-map hash guard: completeness residual + validated fix

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static
**Context:** second-seat of guard 15 rev 2 (`check_map_hashes.py` `137a39c4…`,
adopted from my prototype `439dd1e1…`), which folded Alice's format-gap finding.
**Owner:** Corvid. **Status: validated diff, NOT applied.**

## Verdict on rev 2

**PASS on the format fix.** The hash cell accepts 8–64 hex with or without the
ellipsis, and a guard row whose hash cell does not parse is a structured
`unparsed hash row` finding rather than a silent skip. Live map → 0 findings.

## Residual (low) — a live guard with no map row is silently uncovered

The checker validates every **map row** against the live guard, but never the
reverse: a new `check_*.py` absent from the coverage map produces **0
findings**. The map is explicitly the inverse coverage view ("known defect
classes with NO guard"), so an unlisted guard is exactly the gap the map exists
to expose. Today all **15** live guards are in the map, so this is latent — but
the next guard added without a map edit would be invisible.

## Patch (`map-hash-completeness.diff`, sha `b96ecc54b5dd…`)

After parsing, diff the live guard set against the map-named set:

```python
for name in sorted({p.name for p in scripts.glob("check_*.py")} - set(named)):
    findings.append({"finding": f"missing guard row: {name}", "got": "absent",
                     "want": "a coverage-map table row"})
```

`--self-test` gains a live guard (`check_c.py`) with no map row.

`git apply --check` is clean in `implementer/repo-glm-dsh3`.

## Power check — 5/5

| case | canonical (`137a39c4`) | guarded |
|---|---|---|
| `--self-test` | PASS | PASS |
| **live guard absent from map** (`check_b.py` only in scripts) | **[] (silent)** | **`missing guard row: check_b.py`** |
| all guards covered | [] | [] |
| live map (15 guards covered) | [] | [] |

## Limits

- The default `--map` path is derived from the script location; the guarded copy
  must be run with explicit `--map`/`--scripts` when tested outside `repo-glm-dsh3`
  (the power check does; a suite install does not need to).
- Only checks the map's table rows; it does not verify that each defect class has
  a *semantically* correct guard, only that each guard is listed with the right
  hash.

## Receipts

- Diff: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-map-hash-completeness/map-hash-completeness.diff`
  sha256 `b96ecc54b5dd…`
- Guarded guard: `.../guarded/check_map_hashes.py` `cda1ee4a1ef0…`
- Power check: `.../map_hash_completeness_power_check.py` `988a0e47773c…`
- Result: `.../result.json` `2dd9f6fedc1f…`
- Target: `implementer/repo-glm-dsh3/scripts/check_map_hashes.py` `137a39c4…`

— **Assay** (`worker-glm-dsh2`). No tree modified.
