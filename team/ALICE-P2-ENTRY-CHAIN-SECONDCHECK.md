# Second-driver — Kiln's P2 entry chain, via Assay's check (independent reproduction)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 12:36 UTC · **Cost:** $0, local (/tmp only), one turn · **Trigger:**
standing second-check of `team/ASSAY-SECOND-DRIVER-P2-ENTRY-CHAIN.md` (QUEUE
row 27 build state) — independent of his run. Canonical tree untouched.

## Verdict

**PASS / AGREE on every substantive claim**, reproduced from scratch: the
focused suite passes, the TS↔Python port parity holds on a clean store with
**byte-identical** regenerated hits, the non-idempotence defect is real, and the
pin gate returns the expected receipt. **One moving number:** the focused suite
is now **32 passed (12/8/3/9)**, not Assay's 30 (12/8/3/7) — the
transcript-mining file grew by 2 tests in ~10 minutes, so both his "30" and the
row's "expect 28" are snapshots of a growing suite.

## Pin gate — reproduced

```
PYTHONPATH=src python3 -c "from memory_bakeoff.portfolio import assert_run_pins; ..."
→ dataset_sha256 8ef9ec85…  upstream_commit ec51d5d3…  contract memconflict-benchmark-v1
  provider_arms {pi_lcm_store_reader: controlled_core, pi_lcm_history_null: baseline}
  engine_arms {longcontext_null: longcontext-null-v1}
rc 0
```

The dataset sha matches the Gen38 anchor dataset sha
(`ASSAY-SECOND-DRIVER-GEN38-SCORES.md`), as claimed.

## Port parity — reproduced from a clean store (my own /tmp mirror)

```
rm receipts/differential.db receipts/{ts,py}-hits.json
bun ts_side.ts      -> rc 0, "ts-side done: 6 queries"
python3 py_side.py  -> rc 0, "py-side done: 6 queries"   (PYTHONPATH=implementer/repo/src)
diff ts-hits.json py-hits.json -> EMPTY
sha256(ts-hits.json) == sha256(py-hits.json) == 63593d13…
```

Both regenerated files are byte-identical to the committed receipts
(`63593d132642e0ec…`), so Assay's parity result reproduces exactly. His
Deviation A (the row's bare `receipts/...` path) is confirmed by the layout:
the files live only under
`scripts/experiment_20260912_pi_lcm_differential/receipts/`.

## Non-idempotence defect — reproduced twice

```
# second run in the clean-store mirror (store now populated)
bun ts_side.ts -> rc 1: SQLiteError: UNIQUE constraint failed: conversations.session_id

# fresh mirror seeded with the committed store (the "as-committed" invocation)
bun ts_side.ts -> rc 1: same UNIQUE constraint at pilot_store.ts:85 (seedConversation)
```

So `RUN-AS-COMMITTED.md`'s advertised recipe cannot regenerate the committed
receipt without `rm -f receipts/differential.db` first — a real reproducibility
defect, exactly as reported. The canonical tree is `git status` clean and its
receipts still hash `63593d13…`, so Assay's in-place attempt was restored.

## Test suite — passes, count has moved

Ran the same four files individually:

| file | Assay | my run |
|---|---:|---:|
| `test_pi_lcm_store_reader_contract.py` | 12 | **12** (matches the row's contract suite) |
| `test_portfolio_composition.py` | 8 | **8** |
| `test_portfolio_realdata_smoke.py` | 3 | **3** |
| `test_transcript_mining.py` | 7 | **9** |
| total | 30 | **32 passed** (1.27 s) |

No failures. The row's "expect 28" is stale, and any exact figure will keep
going stale while Kiln adds tests — the recipe should use a floor (`≥ 28`) or
name only the 12-test contract suite, which is the stable claim.

## Scope and limits

- All runs in `/tmp/alice-diff*`; the canonical repo was read-only except the
  git-status check. `bun` v1.3.13, sqlite 3.50.2 (FTS5 native), as Assay's host.
- I did not re-run any engine or product; this re-runs the committed harness and
  compares bytes.
- The count observation is not a defect in Assay's check — it is evidence the
  number is time-sensitive, which is the point.
