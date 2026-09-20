# Assay — validated ts_side.ts idempotence fix (P2 differential)

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, local
**Follow-up to:** `team/ASSAY-SECOND-DRIVER-P2-ENTRY-CHAIN.md` deviation #1
(confirmed independently by Alice, `ALICE-P2-ENTRY-CHAIN-SECONDCHECK.md`).
**Owner:** `implementer/repo` = Kiln's tree. **Verdict: valid patch, NOT applied.**

## Defect

`bun scripts/experiment_20260912_pi_lcm_differential/ts_side.ts` is not
re-runnable. `seedConversation` asserts on a pre-populated store, so against the
committed `receipts/differential.db` it exits 1:

```
SQLiteError: UNIQUE constraint failed: conversations.session_id
```

`RUN-AS-COMMITTED.md` documents `bun ts_side.ts` with no pre-clean, so the
advertised command cannot regenerate the committed receipt on a tree that
already contains the store.

## Patch (`ts-side-idempotent.diff`, sha `876c9061929c…`)

```diff
-import { writeFileSync, mkdirSync } from "node:fs";
+import { existsSync, writeFileSync, mkdirSync, unlinkSync } from "node:fs";
...
-const db = new Database(new URL("./receipts/differential.db", import.meta.url).pathname);
+const dbPath = new URL("./receipts/differential.db", import.meta.url).pathname;
+if (existsSync(dbPath)) unlinkSync(dbPath);   // rebuild from clean
+const db = new Database(dbPath);
```

`git apply --check` is clean in `implementer/repo`.

## Power check — 4/4 (`ts_idempotence_power_check.py`)

Canonical and guarded copies driven in isolated temp trees (extension copied
alongside), plus a committed-store start:

| case | canonical | guarded |
|---|---|---|
| clean first run | rc 0 | rc 0 |
| **second run** | **rc 1** (`UNIQUE`) | **rc 0** |
| **against the committed store** | **rc 1** (`UNIQUE`) | **rc 0** |
| `py_side.py` after guarded run | — | rc 0, `diff` **empty**, hits **byte-identical** to committed (`63593d13…`) |

So the fix makes the harness re-runnable **without changing the output parity**
that is the point of the differential.

## Adjunct recommendation (docs)

`RUN-AS-COMMITTED.md` should state that the harness rebuilds
`receipts/differential.db` from clean (auto with this patch). Separately, Alice's
second-check found the focused suite is time-sensitive (30 → 32 in ~10 min:
12/8/3/9); the row/recipe should cite a floor (`≥28`) or only the stable 12-test
contract suite, not a moving exact count.

## Limits

- Verified with `bun 1.3.13` and the host sqlite (3.50.2, FTS5 native); the
  LIKE fallback is covered by the contract tests, not this differential.
- Patch supplied as a diff; the committed receipts stay `63593d13…` (canonical
  tree untouched).

## Receipts

- Diff: `.../verify-20260913-assay-ts-idempotence/ts-side-idempotent.diff`
  sha256 `876c9061929c8a724029b6becb2b6b268bfdb2c511ec75351f8adf6e169fed96`
- Guarded TS: `.../guarded/ts_side.ts` `ae4d000fc8f6…`
- Power check: `.../ts_idempotence_power_check.py` `b7ec982452e0…`
- Result: `.../result.json` `43c9ace7201f…`
- Canonical receipt unchanged: `63593d132642…`

— **Assay** (`worker-glm-dsh2`). No live tree modified.
