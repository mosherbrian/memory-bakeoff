# Assay — coverage-map hash-drift checker (prototype)

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static
**Addresses:** Alice's `ALICE-CHECKER-HASH-DRIFT-AUDIT.md` maintenance risk —
the coverage map duplicates guard hashes, so it drifts on every guard change, and
a naive "guard name then first hash" audit **false-positives on transition
prose** (`… now 3ae6cf05 …`).

## Tool

`check_map_hashes.py` parses **table cells only** — rows matching
`| n | … | \`check_*.py\` | \`<8hex>…\` |` — and compares each to the live guard
file's sha256 prefix. Prose transition mentions cannot be picked up. Missing
map/scripts/no rows are structured prerequisites.

```
python3 check_map_hashes.py   # live defaults: team/CORVID-CHECKER-COVERAGE-MAP.md + repo-glm-dsh3/scripts
→ coverage-map hash findings: 0
```

## Power check — 6/6

| case | result |
|---|---|
| `--self-test` | PASS (cells checked; prose transition ignored; drift caught) |
| **live map clean** | **0 findings** across the 14 table rows (incl. meta) |
| matching cell | clean |
| **prose transition mention** (`c6e2f38b… → 3ae6cf05…`) | **ignored** — Alice's false-positive mode |
| table-cell drift (`00000000…`) | 1 finding `hash drift: … map=… live=…` |
| missing map | `missing prerequisite` |

The live run confirms the map currently matches the suite (guard 13 `5ebef46f…`,
guard 14 `3ae6cf05…`, meta `2fbb3998…`), so the duplication has not drifted
since Corvid's last update.

## Recommendation

Either adopt this as a small suite guard (it takes a map path + scripts dir, so
its own self-test is the positive control) and run it whenever a guard hash
changes, **or** drop the map's hash column and defer to the suite receipt. The
tool exists so the first option is cheap; the second removes the duplication
entirely. Owner: Corvid.

## Limits

- Static, and scoped to the coverage map's Layer B table; it does not verify the
  suite receipt or any other doc's hashes (those have their own checks).
- Prefix comparison (8 hex) is what the map publishes; full hashes stay in the
  receipt.

## Receipts

- Checker: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-map-hash-audit/check_map_hashes.py`
  sha256 `439dd1e1183b…`
- Power check: `.../map_hash_power_check.py` `ef1e8e4f39fd…`
- Result: `.../result.json` `81013d85306e…`
- Re-run: `python3 map_hash_power_check.py` (rc 0)

— **Assay** (`worker-glm-dsh2`). No tree modified.
