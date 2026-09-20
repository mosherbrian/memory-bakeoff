# Checker-suite second-seat verification — 7/7 green, but the canonical tree is not

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** `team/CORVID-RD-CHECKER-SUITE.md` names this
seat as the standing second check · **Cost:** $0, static, one turn.

**Receipts:** `team/row-checker-suite-verify/` (`MANIFEST.md` with sha256):
script hashes, self-test log, `repo-glm-dsh3` main-check log, canonical-tree log.

## Verdict

- **7/7 script hashes match** the suite's stated prefixes.
- **7/7 self-tests PASS** (each rejects its synthetic bad input).
- **`repo-glm-dsh3` is green** on all six main checks.
- **The canonical reset tree `implementer/repo` is NOT green** — it still carries
  the three pointer defects, and the fix diff still applies cleanly. The suite
  note's "both checkers are green in both" is **stale for the canonical tree**.
- **One genuine defect in my own artifact** (flagged by the qualifier checker)
  is **fixed**.

## 1. Hashes and self-tests (all pass)

| Script | sha256 prefix | Matches suite | Self-test |
|---|---|---|---|
| `check_invalidated_pointers.py` | `1898733e…` | ✓ | PASS |
| `check_results_value_pointers.py` | `d0d00ff2…` | ✓ | PASS |
| `check_frozen_id_provenance.py` | `0efe5a7c…` | ✓ | PASS |
| `check_query_fork.py` | `0911ce59…` | ✓ | PASS |
| `check_gen38_anchor.py` | `496ba6ae…` | ✓ | PASS |
| `check_membukkit_parity.py` | `b2f647e7…` | ✓ | PASS |
| `check_longmemeval_qualifiers.py` | `81592607…` | ✓ | PASS |

## 2. `repo-glm-dsh3` main checks (green)

| Check | Result |
|---|---|
| invalidated pointers | rc 0 — uncued 0, dangling 0 |
| results value pointers | rc 0 — 0 unbacked rows |
| frozen id provenance | rc 0 — **dirs 105, ids 24,451, all canonical** (suite said 102 / 24,169; drift from new runs, expected, still 0 flagged) |
| query fork | rc 0 — 26 ids, 0 forked |
| gen38 anchor | rc 0 — 0 findings (1142/2631, 1103/2631, 594/2631) |
| membukkit parity | rc 0 — 0 findings |

## 3. Canonical `implementer/repo` is not green (contradicts the suite note)

Tree: branch `reset/practical-pi-20260907`, HEAD `a44b321`.

```
check_results_value_pointers.py .   rc=1  unbacked RESULTS.md rows: 2
  RESULTS.md:81 stated=[0.542, 0.583, 32.9] links membukkit_stress_lsa=(0.458,0.375), membukkit_core=(0.333,0.25)
  RESULTS.md:82 stated=[0.75, 0.875]        links membukkit_hybrid_1.0=(0.5,0.417), membukkit_stress=(0.083,0.083)
check_invalidated_pointers.py .     rc=1  uncued=1
  [UNCUED] RESULTS.md:85 -> results/hindsight_gen4_core_r1
git apply --check fix-results-pointer-defects.diff   rc=0  -> fix NOT applied
```

The suite note (21:43) says the diff is "applied … in the canonical reset tree
`implementer/repo` … both checkers green in both." That was overtaken: Corvid's
later entry (~22:1x) records **reverting** his uncommitted canonical `RESULTS.md`
edit to restore the one-writer-per-tree rule. The suite note was not updated, so
its canonical-green claim is now false. **The implementer-of-record still needs
to apply `fix-results-pointer-defects.diff` to `implementer/repo`**; until then
the checker is a failing closure gate there, which is the correct behavior.

## 4. My own defect, found and fixed

The qualifier checker flagged **2 genuine lines in my** `ALICE-REDERIVE-ZEP-HEADLINE.md`
(rows 3 and 4: `LongMemEval "15.2%"` / `"18.5%"` with no split or version).
I edited them to **`LongMemEval-S`**; the re-run no longer lists my artifact. (The
root scan went 46 → 44 unqualified lines; the remaining are mostly append-only
RD-THREADS prose, including my own log line, which I left as historical text.)
Its known false positive (`reviews/accounting-2026-09-07/ACCOUNTING_glm-5.3.md:90`,
"an unrelated number near the word") reproduced.

## Recommendation

1. **Update `CORVID-RD-CHECKER-SUITE.md`**: canonical `implementer/repo` is
   **not green**; the fix diff is pending there. (repo-glm-dsh3 is green.)
2. **Implementer-of-record:** apply `fix-results-pointer-defects.diff` to
   `implementer/repo`, then re-run the two checkers (expect rc 0).
3. Keep the suite as the second-seat pass — this run took one turn and found a
   stale cross-document claim, which is exactly its job.

## Method and limits

- Ran every script in read-only mode; my only write was the two-word fix to my
  own `team/` artifact. No tree outside `team/` was modified.
- Static checks only: green means pointer/label hygiene, not measurement
  correctness. I did not re-derive the underlying results.
