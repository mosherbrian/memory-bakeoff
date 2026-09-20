# Assay second-driver — R2H freeze verified before day 1

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~21:2x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations
**Target:** `team/R2H-FREEZE.md` + `deploy/r2-habit-20260912/` — the R2
explicit-prompt habit arm that ships to Brian's work machine and runs
unmonitored. The freeze claims "every hash above is checkable; nothing here
requires trusting anyone's memory."

## Result — AGREE, every check

| Check | Result |
|---|---|
| 6 sha256 recomputed (`r2h_deploy.py`, `RUNBOOK.md`, `SCHEDULE.txt`, `SEED.txt`, proposal v2, adjudication rule) | **6/6 match** |
| schedule independently re-derived from seed | `ONONOFFONONOFFONOFFOFFOFF`, **== `SCHEDULE.txt`** |
| derived order | `[1,5,2,7,4 | 10,3,9,6,8]` (first five ON, last five OFF) |
| deploy script's embedded `SCHEDULE` vs derived | **equal** |
| deploy script's own guard `assert derive_schedule() == SCHEDULE` | present |
| network paths in the shipped script | **none** |

The seed-hash commit half holds: `sha256(SEED.txt) = 7c9f7d5e…` and the schedule
provably follows from the committed seed, so the arm sequence predates the data.
The freeze's own correction stands — blinding is by arm-stripping + rater
procedure, not seed secrecy.

## Limit

- This verifies the **frozen bytes and the schedule derivation**. It does not
  re-run Stratum's end-to-end sandbox test of `r2h_deploy.py` (flip/smoke/close/
  arm-strip), which is a separate receipt in the freeze.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/r2h_freeze_rederive.py`
  sha256 `4d6f08ec0cc22421922492b8ce0251da4966d15bfeee7885804e9f3ad09c5c38`
- Result: `.../sealed-r2h-freeze-rederive-20260912/result.json`
  sha256 `ecf9ffe46a4097ef65fc735fba7ad26e810ffb3f8adc2d0ba79e5e5fec8b2ea3`
- Re-run: `python3 scripts/verify-20260912-assay-row1/r2h_freeze_rederive.py`

— **Assay** (worker-glm-dsh2).
