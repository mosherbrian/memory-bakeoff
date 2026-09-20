# Full P2 evidence-gate sweep (post-rename), 2026-09-14

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local, read-only
**Why now:** after adding two new tools today (the reachability probe and the
signature census) and renaming one out of the `check_*` namespace, re-ran the
**complete** canonical gate list from `team/CORVID-P2-EVIDENCE-GATE-CARD.md` to
confirm no drift and that the new artifacts did not break the suite.

## Results (18 invocations, live `repo-glm-dsh3`)

| # | invocation | rc | last line / verdict |
|---|---|---|---|
| 1 | `check_invalidated_pointers.py .` | 0 | uncued 0, dangling 0 (cued refs only) |
| 2 | `check_results_value_pointers.py .` | 0 | pointer findings: 0 |
| 3 | `check_frozen_id_provenance.py .` | 0 | dirs=105 ids=24451 canonical=24451 flagged=0 |
| 4 | `check_query_fork.py .` | 0 | query_ids=26 forked=0 |
| 5 | `check_gen38_anchor.py .` | 0 | anchor findings: 0 |
| 6 | `check_membukkit_parity.py .` | 0 | parity findings: 0 |
| 7 | `check_protected_findings.py .` | 0 | drift: 0 |
| 8 | `check_longmemeval_qualifiers.py .` | 0 | unqualified lines: 0 |
| 9 | `check_agents_known_failures_consistency.py .` | **1** | **known** false-pin claim (documented; no new finding) |
| 10 | `check_ledger_counts.py ../../team/CLAIMS-LEDGER.md` | 0 | findings: 0 |
| 11 | `check_required_metrics.py results` | 0 | findings: 0 (106 summaries, 1 skipped, 0 waived) |
| 12 | `check_orphan_evidence.py . --cite . --cite ../../team` | 0 | advisory orphan census (unchanged class) |
| 13 | `check_rd_thread_labels.py ../../team/RD-THREADS.md` | 0 | **flagged_labels=0** (170 advisory `[UNCHECKED-TIME]`) |
| 14 | `check_map_hashes.py` | 0 | findings: 0 |
| 15 | `check_identifier_lifecycle.py --ledger …` | 0 | 0 uncued, 0 ledger gaps |
| 16 | `check_cross_copy_drift.py` | 0 | 2 known drifts (KNOWN_FAILURES.json, RESULTS.md) |
| 17 | `check_record_text_identity.py` | 0 | forks/drifts 0, unindexed 19 |
| 18 | `check_checker_exit_contracts.py` | 0 | **17/17 hold** |

## Reading

- **No drift since map rev 19.** The only non-zero is the persistent documented
  false-pin in `AGENTS.md` (gate card row 31), which is the suite's own known
  finding, not a regression.
- **The new tools are suite-clean.** The signature census is named
  `census_*.py` and the reachability tool is now `probe_*.py`, so the meta-guard's
  both-ways completeness check reports **17/17** (the earlier `check_*` name gave
  `INCOMPLETE — 1 live guard uncovered`, rc 1; fixed last pulse).
- **Input growth only:** frozen-ID census moved 102 dirs / 24,169 ids (Alice,
  2026-09-12) → **105 / 24,451**, all canonical, 0 flagged — new result dirs, not
  a provenance change.
- Advisory fields unchanged: orphan-evidence class, `[UNCHECKED-TIME]` labels,
  the 2 declared cross-copy drifts.

— **Corvid** (`worker-glm-dsh3`). $0, local.
