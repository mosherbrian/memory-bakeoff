# GUARD — coverage-map guard-hash drift (guard 15)

**Author:** Corvid (`worker-glm-dsh3`), suite owner
**Date:** 2026-09-13 · **Cost:** $0, static, no model
**Prototype:** Assay (`worker-glm-dsh2`), `team/ASSAY-MAP-HASH-AUDIT.md`,
checker sha `439dd1e1…`, power check `ef1e8e4f…`.
**Artifact:** `implementer/repo-glm-dsh3/scripts/check_map_hashes.py`
sha256 `cda1ee4a1ef0cfdf624c4b5ad72bb18bc2cefe88557807da767c160d69726220`
(rev 3; rev 2 `137a39c4…`, rev 1 `ccc95053…`).

## Why

Alice's hash-drift audit (`ALICE-CHECKER-HASH-DRIFT-AUDIT.md`, sha `745e62e7…`)
found the coverage map duplicates every guard hash and therefore must be edited
on every guard change — duplication that had already caused one map/receipt
drift (Assay's 13:00 check). It also showed a naive "first hash after the guard
name" audit false-positives on transition prose (`c6e2f38b… → 3ae6cf05…`). The
fix is to check the map's **table cells only** and compare them to the live
guard files, so the duplication is safe.

## What it checks

- Parses the coverage map's Layer B table rows (numbered or `—` rows naming a
  `check_*.py` and an 8-char hash prefix).
- Compares each cell's prefix to the live `scripts/check_*.py` SHA-256 prefix.
- Reports `hash drift: <guard> map=… live=…`, a map naming a missing guard, and
  structured `missing`/`unreadable`/`no table rows` prerequisites.
- **Ignores prose**: a transition sentence is not a cell, so it cannot fool the
  check (self-test covers this).

## Second-driver verification (Corvid, before adoption)

Ran Assay's prototype `439dd1e1…` independently → **0 findings** on the live map,
matching his result. Adopted with two changes: host-independent default paths
(derived from `__file__`, not the absolute host paths) and an extended self-test
(missing map + empty map structured cases, on top of his cell/prose/drift cases).

## Verification

- `--self-test` **PASS** (cells checked; prose transition ignored; table-cell
  drift caught; missing/empty map structured).
- Live run: **0 findings** — all guard hashes current, including the map's new
  maintenance row for this checker itself.

## Integration

Added to `team/CORVID-RD-CHECKER-SUITE.md` as **guard 15** and to the coverage
map's Layer B as a maintenance row (`—`). It takes a map path + scripts dir
rather than a results root, so it is outside the exit-contract meta-guard's
fixture set; its own `--self-test` is the positive control. The map's hash column
is retained and is now **self-checked**.

## Limits

- Only the map's Layer B table cells are checked; a guard with no map row is not
  audited, and hash comparison uses the 8-char prefix recorded in the map.
- It checks hash *consistency*, not that the map's descriptions are accurate.

## Rev 2 (2026-09-13) — Alice's partial-format blind spot + a live self-catch

Alice's second-seat check (`ALICE-MAP-HASH-CHECKER-SECONDCHECK.md`, sha
`8b80a3a5…`) PASSed Assay's prototype and found `ROW_RE` required exactly
`` `<8hex>…` ``: a drifted row in another format (no ellipsis, or a full 64-hex
hash) was silently skipped. Folded:

- Hash cell now accepts `([0-9a-f]{8,64})(?:…)?`; comparison uses
  `live.startswith(prefix)`, so 8- and 64-char forms both work.
- A guard row that names a `check_*.py` but whose hash cell does not parse is a
  structured **`unparsed hash row`** finding (counted per guard, so a mixed map
  cannot lose a row). Self-test adds no-ellipsis, full-hash, and unparsed-row
  cases.

**Dogfooding:** after the edit, the guard immediately flagged its own map row as
stale (`map=ccc95053 live=137a39c4`) — the exact drift class it exists for. The
map and suite rows were updated to `137a39c4…` and the guard now runs **0
findings**. sha `ccc95053…` → **`137a39c4…`**.

## Rev 3 (2026-09-13) — completeness in both directions

Assay's second seat of rev 2 found the inverse gap: the checker never diffed the
**live guard set against the map**, so a new `check_*.py` with no map row yielded
0 findings and the coverage view could be silently incomplete. His patch
`map-hash-completeness.diff` (`b96ecc54…`, Alice second-seat PASS sha
`2d97e1f9…`) adds `missing guard row: <name>` for every `scripts.glob("check_*.py")`
not present as a named map row, plus a self-test case. Corvid applied it; the
guard now checks **both directions**: map→live hash drift and live→map coverage.

**Dogfooded again:** the rev-3 edit immediately flagged its own stale map row
(`map=137a39c4 live=cda1ee4a`); map + suite rows updated, live run **0
findings**. Intended strictness (per Alice): any future non-suite helper named
`check_*.py` needs a map row or a rename. sha `137a39c4…` → **`cda1ee4a…`**.
