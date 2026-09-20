# Assay — R2H `check` / `install-check` sandbox check

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~23:3x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — instrument power checks (deploy-behavior)
**Scope:** fake agent dir, fake extensions, stub `pi` on PATH. Nothing real read.

## Result — 3/3

| Check | Result |
|---|---|
| `check` on a correct install | **ALL PASS** (pi binary, agent dir, settings parses, store dir, store for cwd, `PI_PROJECT_RECALL`, `PI_RECALL_NUDGE`) |
| `install-check` with both extensions carrying their markers | **PASS, rc 0** |
| `install-check` after removing the nudge marker | **FAIL, rc 1** — the gate has power |

## R2H command surface, now fully exercised independently

| Subcommand | Assay check | outcome |
|---|---|---|
| `flip` / arm-strip | `r2h_deploy_sandbox_check.py` | 8/8 pass; sequence matches derived |
| `smoke` | `r2h_smoke_sandbox_check.py` | hard gate rejects no-nudge and store-modified |
| `close` | `r2h_close_sandbox_check.py` | privacy path good; **traces bug** found |
| `check` / `install-check` | this file | correct install passes; broken marker fails |

`status` is a read-only print of the same state `flip` writes and needs no
separate power check.

## Limit

- Stub `pi` and fake extensions: bounds the deploy script's own logic and gates,
  not the real pi/extension behavior.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/r2h_check_installcheck_sandbox.py`
  sha256 `a47eb9d93256db9fe9c0259bb1a43e1165bb89072e59dfaf5f0f9e60c86e3da1`
- Result: `.../sealed-r2h-check-installcheck-20260912/result.json`
  sha256 `883c413f8f8df5e8be6c54238bc970026e64d0b885c18f02d128ac71617519a6`
- Re-run: `python3 scripts/verify-20260912-assay-row1/r2h_check_installcheck_sandbox.py`

— **Assay** (worker-glm-dsh2).
