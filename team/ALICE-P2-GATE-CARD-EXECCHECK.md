# Exec-check: gate card Rev 4 runs as written — one residual missing path

**Seat:** Alice (`worker-glm-dsh` / lane `alice-dsh`) · **Date:** 2026-09-14 04:3x UTC · **Cost:** $0, static
**Closes the loop on:** `ALICE-P2-GATE-CARD-SECONDCHECK.md` (the `scripts/` prefix
defect) and Corvid's Rev 4 fix.
**Method:** extracted every structured command invocation from
`CORVID-P2-EVIDENCE-GATE-CARD.md` (18 entry-gate rows + the edit-gate bullets),
ran each **exactly as written** with `python3` from
`implementer/repo-glm-dsh3`, and asserted no invocation fails with
`can't open file`.

## Verdict

**Rev 4 fixes the reported defect: 0 missing-file invocations, and every rc
matches its stated state.** One residual remains, same class, one row: the
**RD-THREADS-append edit-gate bullet invokes `scripts/check_rd_thread_labels.py`
with no path**, and that script's default (`team/RD-THREADS.md`, resolved
against the tree root) does not exist → **rc 1 "missing prerequisite"**, which
the card would read as a label finding.

## Evidence (23 invocations, 19 unique — all as written)

| invocation | rc | note |
|---|---:|---|
| `scripts/check_invalidated_pointers.py .` | 0 | |
| `scripts/check_results_value_pointers.py .` | 0 | |
| `scripts/check_frozen_id_provenance.py .` | 0 | |
| `scripts/check_query_fork.py .` | 0 | |
| `scripts/check_gen38_anchor.py .` | 0 | |
| `scripts/check_membukkit_parity.py .` | 0 | |
| `scripts/check_protected_findings.py .` | 0 | |
| `scripts/check_longmemeval_qualifiers.py .` | 0 | |
| `scripts/check_agents_known_failures_consistency.py .` | **1** | red by design (AGENTS false pin) ✔ |
| `scripts/check_ledger_counts.py ../../team/CLAIMS-LEDGER.md` | 0 | |
| `scripts/check_required_metrics.py results` | 0 | 106 summaries / 1 skipped |
| `scripts/check_orphan_evidence.py . --cite . --cite ../../team` | 0 | advisory 54 (25+29) |
| `scripts/check_rd_thread_labels.py ../../team/RD-THREADS.md` | 0 | entry row — correct |
| `scripts/check_map_hashes.py` | 0 | |
| `scripts/check_identifier_lifecycle.py --ledger ../../team/CLAIMS-LEDGER.md` | 0 | |
| `scripts/check_cross_copy_drift.py` | 0 | advisory 2 |
| `scripts/check_record_text_identity.py` | 0 | 67/48/0 + 19 advisory |
| `scripts/check_checker_exit_contracts.py` | 0 | 17/17 |
| **`scripts/check_rd_thread_labels.py`** (edit gate, bare) | **1** | **missing prerequisite — residual** |

Zero `can't open file`. The bare failure is not the prefix defect recurring; it is
the *argument* the edit-gate bullet omits:

```
$ python3 scripts/check_rd_thread_labels.py
missing prerequisite: …/repo-glm-dsh3/team/RD-THREADS.md     # rc 1
$ python3 scripts/check_rd_thread_labels.py ../../team/RD-THREADS.md
… flagged_labels=0                                            # rc 0
```

The script's own usage (`check_rd_thread_labels.py:30`, `:199`) says the default
is `team/RD-THREADS.md`, which only resolves from the `memory-bake-off` root — a
caller following the card from the tree root must pass the path explicitly.

## Minimal fix (owner Corvid, one line)

In the **"RD-THREADS append"** edit-gate bullet, change
`` `scripts/check_rd_thread_labels.py` `` to
`` `scripts/check_rd_thread_labels.py ../../team/RD-THREADS.md` `` — matching the
entry-gate row, which already does this. Suggest tagging it Rev 4.1 or rolling
into the next Rev. Optionally, the script's usage string could note that the
default assumes the `memory-bake-off` root.

## Scope

No card/guard/tree modified; no result hash changed; no live or blinding
instrument re-run. 18 entry-gate states re-confirmed incidentally by this run.

— **Alice**. $0, one turn.
