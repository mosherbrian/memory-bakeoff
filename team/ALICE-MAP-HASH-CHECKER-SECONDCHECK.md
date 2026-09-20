# Second-seat check — coverage-map hash checker (Assay) + a partial-format blind spot

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 14:28 UTC · **Cost:** $0, local, one turn · **Trigger:** standing
second-check of `ASSAY-MAP-HASH-AUDIT.md`, the tool built from my hash-drift
finding. Read-only.

**Subjects:** `check_map_hashes.py` (`439dd1e1…`), `map_hash_power_check.py`
(`ef1e8e4f…`), result `81013d85…`.

## Verdict

**PASS / AGREE** — hashes match, self-test PASS, live map 0 findings, power
check rc 0, and the parser correctly ignores my prose-transition false-positive
mode. **One new finding:** a table row written in a slightly different format
(no `…`, or a full 64-hex hash) is **silently skipped**, so a drifted row in that
format reports **0 findings**. The live map is uniformly `…`-formatted, so there
is no current miss; the gap is latent.

## Verified

| claim | check | result |
|---|---|---|
| checker `439dd1e1…`, power `ef1e8e4f…`, result `81013d85…` | re-hashed | ✓ all match |
| `--self-test` PASS (cells checked; transition ignored; drift caught) | re-ran | ✓ rc 0 |
| live map 0 findings | re-ran | ✓ `coverage-map hash findings: 0`, rc 0 |
| power check 6/6 | re-ran | ✓ rc 0 |
| prose transition cannot fool it | synthetic `deadbeef… → current` | ✓ ignored (table cell wins) |
| well-formed cell drift caught | synthetic `00000000…` | ✓ `hash drift: …` |

## Finding — a non-matching format is skipped, not failed

`ROW_RE` requires the hash cell to be exactly `` `<8hex>…` ``. Probes on a
synthetic map with two good rows plus one drifted row:

| drifted row format | findings |
|---|---|
| `` `00000000…` `` (canonical) | **1** — caught |
| `` `00000000` `` (no ellipsis) | **0** — **silently skipped** |
| `` `<64-hex>` `` (full hash) | **0** — **silently skipped** |

`if not pairs: return missing prerequisite` catches only the all-or-nothing case;
a mixed map loses the unparsed rows silently. The map today publishes 8-hex + `…`
for every row, so this does not bite — but the whole point of the tool is to run
after a guard change, which is exactly when a hand edit might drop the ellipsis
or paste a full hash.

**Fix:** relax the cell regex to `([0-9a-f]{8,64})(?:…)?` and compare on the
8-prefix, and/or add a coverage assertion — the number of parsed rows must equal
the number of map rows naming a `check_*.py`, otherwise a structured
`unparsed hash row` finding. A one-line self-test case (the no-ellipsis row
above) locks it.

## Limits

- Synthetic maps under `/tmp` + one read-only live run; no tree modified.
- The tool is scoped to the coverage map's Layer B table by design; the suite
  receipt has its own hash authority (I audited it separately, 14/14).
- The finding is latent (0 live misses today); it is about the checker's
  detection of a malformed citation, not about any wrong hash.
