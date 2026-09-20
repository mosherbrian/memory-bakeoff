# Assay — R2H deploy script sandbox check (flip + arm-strip)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~21:5x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations (closes the limit
left by `ASSAY-SECOND-DRIVER-R2H-FREEZE.md`, which verified the frozen bytes and
the schedule derivation but did not exercise the executable).
**Scope:** temp `R2H_STATE` only; no pi, no network, no fleet contact.

## Checks — 8/8 pass

| Check | Result |
|---|---|
| `flip` × 10 arm sequence == `derive_schedule()` | `ONONOFFONONOFFONOFFOFFOFF` |
| `state.days_flipped == 10` | yes |
| flip log has 10 entries | yes |
| 11th `flip` emits no arm (schedule-complete path) | yes |
| `_strip_arm` drops exactly the `recall-nudge` lines | dropped **2** |
| stripped file keeps the 3 non-nudge lines | yes |
| no `recall-nudge` token remains | yes |
| a line with the bare word "nudge" is **kept** | yes |

The two mechanisms that carry the experiment are therefore exercised
independently of Stratum's receipt: the daily arm helper follows the frozen
schedule, and the blinding strip removes nudge lines without over-stripping
ordinary prose.

## Limit

- Does not run `check` / `install-check` / `smoke` / `close`; those need a real
  pi + agent dir and remain Stratum's day-0 receipt. This covers the schedule
  and the arm-strip, not the bundle assembly.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/r2h_deploy_sandbox_check.py`
  sha256 `cc0777b0299a826fdd7bf7a33861d9a3aa8af62bd64e921e3c7eee6984609606`
- Result: `.../sealed-r2h-deploy-sandbox-20260912/result.json`
  sha256 `935c211d39e7eaf0b2e8de84fb066613f997e1b99cdf1c567780607cade3ea13`
- Re-run: `python3 scripts/verify-20260912-assay-row1/r2h_deploy_sandbox_check.py`

— **Assay** (worker-glm-dsh2).
