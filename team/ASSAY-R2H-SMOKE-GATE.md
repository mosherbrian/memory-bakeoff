# Assay — R2H day-0 `smoke` gate power check

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~23:2x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — instrument power checks (deploy-behavior)
**Target:** `r2h_deploy.py cmd_smoke` — the day-0 receipt the fleet verifies
before day 1 counts. Fake agent dir + stub `pi`; nothing real read.

## Method

Stub `pi` writes a synthetic session file and (in one case) mutates the fake
store, so the real assertion logic and receipt generation run unchanged.

## Result — the hard gate has power

| Case | `nudge_delivered` | `store_unmodified` | verdict |
|---|---|---|---|
| good install | true | true | **PASS** |
| no `recall-nudge` in the session | **false** | true | **FAIL** |
| nudge delivered, store appended | true | **false** | **FAIL** |

Both failure modes the smoke exists to catch — the nudge was not delivered, and
the store was modified — are rejected (`hard = pi_ran ∧ nudge_delivered ∧
recall_registered ∧ store_unmodified`). The receipt is written in every case.

`recall_invoked` and `store_named` are **warnings**, not hard failures (the
script says so); the stub does not reproduce a real multi-call registration, so
they warn in all three cases — expected, not a defect.

## Limit

- Stub `pi`, not the real pi/extension: this bounds the assertion logic and
  receipt, not the extension's actual behavior. It complements the `close` path
  finding (`ASSAY-R2H-CLOSE-TRACES-BUG.md`), which is a separate defect.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/r2h_smoke_sandbox_check.py`
  sha256 `5335d4383753710b75d19c15d27db49ce8c8fb99cf327e1188419a326dad0c2b`
- Result: `.../sealed-r2h-smoke-sandbox-20260912/result.json`
  sha256 `50f82c6f8be864e2f9fade6d63430004e36b66d026c7d87146a940b325c7f566`
- Re-run: `python3 scripts/verify-20260912-assay-row1/r2h_smoke_sandbox_check.py`

— **Assay** (worker-glm-dsh2).
