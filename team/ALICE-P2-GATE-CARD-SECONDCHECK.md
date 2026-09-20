# Second seat: P2/P3 evidence-gate card — states reproduce, commands do not run as written

**Seat:** Alice (`worker-glm-dsh` / lane `alice-dsh`) · **Date:** 2026-09-14 04:0x UTC · **Cost:** $0, static
**Reviews:** `team/CORVID-P2-EVIDENCE-GATE-CARD.md` (Corvid, Rev 3 at ~03:49).
**Method:** re-ran every entry-gate command at the live tree state, then compared
to the card's `Expected` column. Read-only; no card or guard edited.

## Verdict

**Content: CONFIRMED — all 18 guards reproduce the card's expected states.**
**Executability: DEFECT — every command in the card omits the `scripts/`
prefix while the card says to run from `implementer/repo-glm-dsh3`.** A literal
copy-paste of any row gives `python3: can't open file '…/repo-glm-dsh3/check_…py':
[Errno 2]`, i.e. **rc 2**, a state the `Expected` column does not list. The 18
files live in `scripts/` (18 `scripts/check_*.py`; zero at the tree root).

```
$ cd implementer/repo-glm-dsh3
$ python3 check_invalidated_pointers.py .
python3: can't open file '…/repo-glm-dsh3/check_invalidated_pointers.py': [Errno 2] No such file or directory
# rc 2.  With the prefix: scripts/check_invalidated_pointers.py . -> rc 0
```

This matters at a gate: stop rule 2 already says a non-zero-because-it-cannot-see-input
run is an instrument failure to report, not rerun — but here the failure is the
*card's path*, and an operator following it gets 18 rc-2s that look like a broken
suite. Affected: all 18 entry-gate rows plus the publication-gate and edit-gate
command mentions (~24 invocations).

**Minimal fix (one edit, owner Corvid):** prefix `scripts/` on every command
(examples: `scripts/check_invalidated_pointers.py .`,
`scripts/check_map_hashes.py`, `scripts/check_ledger_counts.py
../../team/CLAIMS-LEDGER.md`). Alternative — change line 10 to "run from
`implementer/repo-glm-dsh3/scripts`" — requires rewriting the `../../team/...`
arguments to `../../../team/...`, so prefixing is the smaller, safer edit.

## Entry-gate re-run with the correct path (18/18 match)

| # | guard | card Expected | observed | ✔ |
|---|---|---|---|---|
| 1 | invalidated_pointers | rc 0, uncued 0 / dangling 0 | rc 0, uncued 0, dangling 0 (refs 10) | ✔ |
| 2 | results_value_pointers | rc 0, 0 findings | rc 0, 0 | ✔ |
| 3 | frozen_id_provenance | rc 0 | rc 0 | ✔ |
| 4 | query_fork | rc 0 | rc 0 | ✔ |
| 5 | gen38_anchor | rc 0 | rc 0, 0 | ✔ |
| 6 | membukkit_parity | rc 0 | rc 0, 0 | ✔ |
| 7 | protected_findings | rc 0, 0 drift | rc 0, 0 | ✔ |
| 8 | longmemeval_qualifiers | rc 0, 0 findings | rc 0 | ✔ |
| 9 | agents_known_failures | **rc 1**, known false pin only | rc 1, 1 finding = the AGENTS false pin | ✔ |
| 10 | ledger_counts | rc 0, 0 findings | rc 0, 0 | ✔ |
| 11 | required_metrics | rc 0; dsh3 106/1 skipped | rc 0; 106 summaries, 1 skipped, 0 | ✔ |
| 12 | orphan_evidence | advisory 54 (25 replica + 29 distinct) | rc 0; 106 scanned, 54 uncited (25/29) | ✔ |
| 13 | rd_thread_labels | rc 0, 0 flagged + advisory UNCHECKED-TIME | rc 0, flagged 0, unchecked 166 | ✔ |
| 14 | map_hashes | rc 0, 0 findings | rc 0, 0 | ✔ |
| 15 | identifier_lifecycle | rc 0, 0 uncued / 0 ledger gaps | rc 0, tracked 1, citations 33, uncued 0 | ✔ |
| 16 | cross_copy_drift | advisory, 2 known drifts | rc 0, 2 (KNOWN_FAILURES.json + dsh2 RESULTS.md) | ✔ |
| 17 | record_text_identity | rc 0; 67 ids / 48 checked / 0 forks / 19 advisory | rc 0; 67/48/0 forks/19 advisory | ✔ |
| 18 | checker_exit_contracts | rc 0, 17/17 hold | rc 0, 17/17 hold | ✔ |

So the "one red by design, two advisory" framing holds, and the gate card's
substance is trustworthy.

## Apparent 18-vs-17/17 discrepancy is NOT a defect (closed)

The card titles 18 guards but expects the meta-guard at **17/17**. I checked the
covered set: live `scripts/check_*.py` = 18, of which one is the driver
(`check_checker_exit_contracts.py`); its declared `_COVERED_NAMES` is exactly the
other **17**, and `uncovered()` is empty. 17 covered + the driver = 18. No guard
is outside the meta. Recording this because stop rule 4 makes an uncovered live
guard a real finding — it is not one here.

## Minor, non-blocking (historical prose, no state claim)

- The Rev 2 paragraph says "lifecycle **28 citations**"; the live run is **33**.
  Rev paragraphs are history, but a reader comparing them to the entry row will
  see a drift; consider a "(at Rev 2)" tag.
- Guard 1 now reports `refs=10` (earlier notes said 11). `uncued=0`/`dangling=0`
  are unchanged, which is what the card gates on.

## Sign-off

The gate card's **states and pass/fail semantics are second-seated** — I can
state, from independent re-runs, that a green entry gate currently looks exactly
as the card says. The card as a **runbook is not copy-pasteable** until the
`scripts/` prefix lands; the fix is mechanical and I recommend Corvid apply it in
the same edit that sets Rev 4.

**Not done:** no card/guard/tree modified, no result hash changed, no live or
blinding instrument re-run.

— **Alice**. $0, one turn.
