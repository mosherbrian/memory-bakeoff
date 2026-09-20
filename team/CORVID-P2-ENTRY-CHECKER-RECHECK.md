# Corvid P2-entry evidence-integrity re-check (checker suite at new canonical HEAD)

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Date:** 2026-09-13 · **Cost:** $0, read-only over the three trees + one
ledger label fix
**Trigger:** Kiln's `c30e8fa` ("P2 PREREQUISITE CLEARED" — MemConflict
materialized, `KNOWN_FAILURES.json` pruned, totals re-measured) changed the
canonical reset tree after the suite's last full pass (Alice, 22:42;
Corvid 23:34). This re-runs the eight guards and reports what P2 entry inherits.

## 1. Script identity and self-tests (all unchanged)

All eight `repo-glm-dsh3/scripts/check_*.py` sha256 values **match** the suite
receipt (`team/CORVID-RD-CHECKER-SUITE.md`) prefixes exactly; all eight
self-tests **PASS**:

| Script | sha256 | Self-test |
|---|---|---|
| `check_invalidated_pointers.py` | `1898733e…` | PASS |
| `check_results_value_pointers.py` | `d0d00ff2…` | PASS |
| `check_frozen_id_provenance.py` | `0efe5a7c…` | PASS |
| `check_query_fork.py` | `0911ce59…` | PASS |
| `check_gen38_anchor.py` | `496ba6ae…` | PASS |
| `check_membukkit_parity.py` | `b2f647e7…` | PASS |
| `check_protected_findings.py` | `bc9b52ca…` | PASS |
| `check_longmemeval_qualifiers.py` | `81592607…` | PASS |

No checker code changed, so Alice's second-seat hash verification stands.

## 2. Per-tree results at current HEADs

| Checker | `repo-glm-dsh3` (`399337b`) | canonical `implementer/repo` (`c30e8fa`) | `repo-glm-dsh2` (`86709b3`) |
|---|---|---|---|
| invalidated pointers | **exit 0** (uncued 0, dangling 0) | **exit 1** — uncued 1: `RESULTS.md:85` → `results/hindsight_gen4_core_r1` | **exit 1** — same |
| results-value pointers | **exit 0** (0 unbacked) | **exit 1** — rows 81 (0.583/0.542) and 82 (0.875/0.750) | **exit 1** — same |
| frozen-ID provenance | exit 0 (105 dirs / 24451 ids, all canonical) | exit 0 (102 / 24169, all canonical) | exit 0 (102 / 24169) |
| query-fork | exit 0 (26 ids, 0 forked) | exit 0 | exit 0 |
| Gen38 anchor | exit 0 (0 findings) | **exit 0 (0 findings)** | exit 0 |
| MemBukkit parity | exit 0 (0 findings) | **exit 0 (0 findings)** | exit 0 |
| protected findings | exit 0 (0 drift) | **exit 0 (0 drift)** | exit 0 |

**Reading.** The large canonical change (183 MB dataset + baseline prune) did
**not** perturb any frozen-result index or protected number: Gen38 anchor,
MemBukkit parity, and all four protected-findings groups are 0-drift on
`c30e8fa`, and every frozen `retrieved_ids` entry remains canonical. The only
canonical red is the **pre-existing row-12 pointer defect** (rows 81/82 value,
row 85 invalidated) — unchanged by `c30e8fa`. `fix-results-pointer-defects.diff`
still applies cleanly (`git apply --check` rc 0), so it is a one-command closure
for the implementer-of-record. Canonical's two dirty files are Alice's
`MANIFEST.md` + `canonical-repo-checks.txt` (the flag Kiln raised), **not** a
RESULTS.md edit.

## 3. LongMemEval qualifier census — owner files were NOT clean

Running the qualifier checker against the **canonical `team/` corpus** (its
real target; the suite receipt's "2 genuine (Alice's)" number was measured on a
different root and is now stale) surfaced owner-file findings that the earlier
census believed fixed. Inspected each in context:

- **`CLAIMS-LEDGER.md` — 4 genuine, all from the overnight MemOS/Zep merges,
  now FIXED by me (ledger custodian):**
  - `:827` OmniMemEval self-report `LongMemEval 89.20` → **LongMemEval-S 89.20**
  - `:848` OmniMemEval reproduced rows `LongMemEval 56.00…` → **LongMemEval-S**
  - `:857` Zep `LongMemEval 90.2` → **`(split unspecified)`** (getzep source
    gives no split)
  - `:859` same Zep list → **`split unspecified`**
  - Re-run after the fix: **0 ledger findings.**
- **`ECOSYSTEM-MAP.md:632` — 1 genuine, owner Stratum:** Hindsight report
  abstract "**91.4%** LongMemEval" carries no split (it is the LongMemEval-S
  arm). Flagged for Stratum's next fold.
- **`ECOSYSTEM-MAP.md:475` — one false-positive class:** "LongMemEval-family
  numbers" trips the score regex on Zep's `+18.5%`. The census already named
  generic "LongMemEval-class" as an FP class but `QUAL_RE` does not implement
  `family|class`; proposed one-line addition, **not applied** here to avoid
  invalidating the verified checker hash mid-cycle.
- Residual `team/` count is now **58 lines**, almost all working-prose in
  analysis notes (`SCOREBOARD`, `RD-THREADS`, `ALICE-*`). These are internal
  narration, not citable claims; the citable owner files are the ledger (now
  clean) and the map (one line above). The checker's exit 1 on `team/` is
  therefore expected and is a limits statement, not a regression.

## 4. P2-entry disposition

| Item | State |
|---|---|
| Real frozen results / canonical IDs | **gate passes** (0 non-canonical, 0 forked) |
| Protected findings on healed canonical tree | **gate passes** (0 drift, all four) |
| Portfolio anchors (Gen38, MemBukkit parity) | **gate passes** (0 findings) |
| Evidence index in canonical `implementer/repo` | **1 blocking item** — apply `fix-results-pointer-defects.diff` (rows 81/82/85); applies clean |
| LongMemEval split qualifiers | ledger clean; 1 map line open (Stratum) |

No number, class, or result directory changed. The only edits this turn are four
label strings in `CLAIMS-LEDGER.md` (split qualifiers), which move no score.

— **Corvid** (`worker-glm-dsh3`).
