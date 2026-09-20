# Post-landing guard sweep (landing steward, 2026-09-15)

**Author:** Corvid (`worker-glm-dsh3`) · **Cost:** $0, read-only
**Why:** after the landing-steward sweep applied
`ALICE-INSTRUMENT-FIXES.diff` and `CORVID-PRODUCT-INGEST-FIX-COMBINED.diff` to
`repo-glm-dsh3`, ran the **full 20-guard suite** to confirm the src changes broke
nothing.

## Result — no regression

| guard | rc / verdict |
|---|---|
| invalidated pointers · results-value pointers · frozen-id provenance | 0 / 0 / 0 (105 dirs, 24,451 ids all canonical) |
| query-fork · gen38 anchor · membukkit parity · protected findings | 0 / 0 / 0 / 0 |
| LongMemEval qualifiers · ledger counts · required metrics | 0 / 0 / 0 (106 summaries, 1 skipped) |
| `check_agents_known_failures_consistency` | **rc 1 — the known false-pin only** (pre-existing) |
| orphan evidence (advisory) · rd-thread labels (advisory) | 0 / 0 (170 unchecked-time labels) |
| map-hash · cross-copy drift · record-text identity | 0 / 0 / 0 (cross-copy now **4** findings) |
| reachability · experiment-class · card-register | 0 / 0 / 0 |
| meta-guard (exit contracts) | **20/20 hold** |

## Reading

The landing changed instrument semantics and provider capability flags; the only
non-zero is the long-standing documented `AGENTS.md` false pin, so the applied
changes are guard-clean. Cross-copy drift is now **4 findings** (2 owned
`known-drift` + 2 fork-only `(NEW)` from the P2 chain), down from 6 before the
landing. **Commit remains the owner's** per AGENTS; this sweep verifies the
working tree, not a commit.

— **Corvid** (`worker-glm-dsh3`). $0, read-only.
