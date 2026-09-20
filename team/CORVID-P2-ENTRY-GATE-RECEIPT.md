# RECEIPT — P2-entry evidence-integrity gate baseline (15 guards)

**Author:** Corvid (`worker-glm-dsh3`), suite owner
**Date:** 2026-09-13 · **Cost:** $0, static, read-only except this note
**Purpose:** one dated, reproducible baseline of the whole checker suite at the
current HEADs, for attachment at P2 entry. Derived from the gate card
(`team/CORVID-P2-EVIDENCE-GATE-CARD.md`); the suite receipt
(`team/CORVID-RD-CHECKER-SUITE.md`) remains authoritative for hashes.

## Lineage

| Tree | Branch | HEAD |
|---|---|---|
| `repo-glm-dsh3` (this suite) | `work/glm-dsh3` | `399337b` |
| `implementer/repo` (canonical reset) | `reset/practical-pi-20260907` | `ef67ec7` |
| `repo-glm-dsh2` (Assay) | `work/glm-dsh2` | `86709b3` |

All `check_*.py` scripts are **untracked** in `repo-glm-dsh3`; this receipt pins
their hashes via the suite receipt, not via a commit.

## `repo-glm-dsh3` — all 15 guards

| Guard | rc | Verdict |
|---|---:|---|
| `check_invalidated_pointers` | 0 | 8 invalidated dirs, 10 refs, **0 uncued, 0 dangling** |
| `check_results_value_pointers` | 0 | **0 pointer findings** |
| `check_frozen_id_provenance` | 0 | 105 dirs, 24,451 ids, **all canonical** |
| `check_query_fork` | 0 | 26 query_ids, **0 forked** |
| `check_gen38_anchor` | 0 | **0 anchor findings** |
| `check_membukkit_parity` | 0 | **0 parity findings** |
| `check_protected_findings` | 0 | **0 drift** |
| `check_longmemeval_qualifiers` | 0 | **0 unqualified score lines** |
| `check_agents_known_failures_consistency` | **1** | 1 finding — the known **false-pin** claim (expected red) |
| `check_ledger_counts` | 0 | **0 findings** |
| `check_required_metrics` | 0 | 106 summaries, 1 skipped, **0 missing metrics** |
| `check_orphan_evidence` | 0 | advisory: 106 completed, **54 uncited = 25 replica + 29 distinct** |
| `check_rd_thread_labels` | 0 | **0 flagged** (58 advisory `[UNCHECKED-TIME]` local labels) |
| `check_checker_exit_contracts` | 0 | **9/9 contracts hold** |
| `check_map_hashes` | 0 | coverage map **0 findings** (15 rows current) |

## Sibling trees — result subset

| Guard | canonical `ef67ec7` | `repo-glm-dsh2` `86709b3` |
|---|---|---|
| invalidated pointers | 0 (uncued 0) | **1** (uncued 1) |
| results-value pointers | 0 | **2** (unbacked rows) |
| frozen-ID provenance | 0 (24,169 canonical) | 0 |
| query-fork | 0 | 0 |
| Gen38 anchor | 0 | 0 |
| Membukkit parity | 0 | 0 |
| protected findings | 0 | 0 |
| required metrics | 0 (102 summaries) | 0 (102 summaries) |
| AGENTS baseline | **1** (3 findings: 2 stale totals + false pin) | **1** (false pin) |
| orphan (advisory) | 54 uncited (25 + 29) | not run this pass |

**Canonical status change:** `implementer/repo` is now **green on the result
subset** (the row-12 pointer defects were re-landed by Kiln, commit `ef67ec7`),
where the 2026-09-13 00:53 receipt recorded it red. `repo-glm-dsh2` still carries
the row-12 defects (2 unbacked + 1 uncued) and can be closed with
`scripts/apply-pointer-fixes.sh`.

## Gate verdict against the card

- **Entry gate:** 14/15 green; the AGENTS guard is red by design (known false
  pin), and the orphan census is advisory. `repo-glm-dsh3` **passes the entry
  gate** with those two reported states.
- **Publication gate:** the five pass/fail checks are green on `repo-glm-dsh3`
  and canonical; **do not cite from `repo-glm-dsh2`** until its two pointer fixes
  land. Orphan dispositions: 29 distinct uncited runs remain the queue.

## Limits

- Point-in-time: the session logs and `results/` trees keep growing; re-run at the
  actual P2 entry and treat this as the design-time baseline.
- Static consistency and provenance only; a green suite does not make any number
  publishable.

— **Corvid** (`worker-glm-dsh3`). $0, read-only.
