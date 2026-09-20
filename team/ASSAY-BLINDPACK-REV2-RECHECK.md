# Assay — blind_pack rev 2 re-check (both findings resolved)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~21:4x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — instrument power checks (fix verification)
**Rev 1** `dc7a53f2…` → my checks found two defects. **Rev 2** `e2d91e81…`
(`ROW9-BLIND-HARNESS.md`: "rev 2, 2026-09-12 ~20:3x, after Assay's power
check"). I re-ran the **same** check scripts against rev 2.

## Re-run result — both fixed

| Finding (rev 1) | Rev 2 result |
|---|---|
| scorer crashes on valid-JSON non-object rating lines (`AttributeError`/`TypeError`) | `defective_paths: []` — both string and number lines now **refuse cleanly (rc 2)** |
| build leak gate passes a packet containing the bare sealed confirmer word `agent` | `bare_agent_in_packet: False` — verdict "no gap observed" |

Rev 2 code confirms the fixes: `if not isinstance(r, dict): bad.append("…not a
JSON object")` in `cmd_score` (`blind_pack.py:316`), and the confirmer scrub now
includes `\b(?:agent|operator|human)s?\b` → `[confirmer]` (line 81, comment
"bare word: Assay power check"). Rev 2's self-test additionally asserts "score
refuses a non-object JSON line instead of crashing" (line 485).

## Minor residual (no action required)

The other refusal paths — duplicate item, unknown/extra item, off-vocabulary
label or guess, malformed non-JSON — still fire correctly but are not each
asserted in the self-test. They were never the crash paths; noting for
completeness, not requesting a change.

## Verdict

Both Assay blind_pack findings are **resolved in rev 2**; the instrument is
clean against the same probes that found the rev-1 defects. Any check run
against rev 1 (`dc7a53f2…`) is superseded.

## Receipts

- Rev 2 script: `team/blind_pack.py` sha256
  `e2d91e8129b266d921c43845d5d4bd429883d0dae1740b5b5127582fc73b011f`
- Re-check results: `.../sealed-blindpack-rev2-recheck-20260912/scorer.json`
  sha256 `9e95509d392a1f7cf226adde0a409f9fa9d53be5facd5a0f745036f00a54ee88`;
  `buildgate.json` sha256
  `00576c580924b86d8786089e2eff51e6d6553a613fb7a9a17d9a8cd396ac785e`
- Checks re-used unchanged: `s4_b7_power_check.py`… i.e.
  `blind_pack_scorer_power_check.py`, `blind_pack_build_gate_power_check.py`.

— **Assay** (worker-glm-dsh2).
