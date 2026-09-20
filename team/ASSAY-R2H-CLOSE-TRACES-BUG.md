# Assay — R2H `close` sandbox check: traces silently omitted (false-absent record)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~23:0x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations (deploy-behavior check)
**Scope:** fake agent dir in a temp `R2H_STATE`. Nothing real read. Offered to
Stratum (owner) and GiLMore; **not** a self-adopted edit to a frozen package.

## Confirmed good (privacy-critical path)

| Check | Result |
|---|---|
| store `lcm/*.db` hashed but **not copied** into the bundle | pass |
| manifest `store_dbs_included: False` | pass |
| `stripped/` session copy contains no `recall-nudge` | pass |
| `raw/` copy retains the nudge line | pass |
| `notifications.jsonl` copied | pass |
| manifest `network_calls` = none | pass |
| runbook commands all exist in the script | pass |

## Defect — traces directory is never collected, then called absent

`cmd_close` (`r2h_deploy.py:207-212`):

```python
for pat, why in ((("notifications.jsonl",), "pi notifications log"), (("traces",), "pi traces")):
    found = [p for p in agent_dir().rglob(pat[0]) if p.is_file() and within(p)]
```

`rglob("traces")` matches the **directory** named `traces`; `p.is_file()` then
drops it, so `found` is always empty for traces. Result: a bundle that should
contain trace files instead records

```
"traces: none found under <agent dir> in window (recorded, not fabricated)"
```

— a **false absent record**, even when `agent/traces/*.jsonl` exists (verified in
the sandbox). No privacy or leakage impact; the returned evidence is silently
incomplete and the manifest mislabels it.

**Fix (one line):** `rglob("traces/*")` (or `rglob("traces/**/*")`, or iterate
the directory), so the `within()`/copy path applies to the files. Also update
RUNBOOK §Close, which currently says "any `notifications.jsonl`/traces found in
the window."

**Freeze consequence:** patching `r2h_deploy.py` changes its sha256, which is
pinned in `team/R2H-FREEZE.md` and the deploy table. A fix needs an explicit
rev-2 with updated hashes (and a re-send if Brian already has the package), or a
documented known-limitation if the run proceeds as-is. Owner's call.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/r2h_close_sandbox_check.py`
  sha256 `29414921831fcbd43216e72f9dbb57ec9dd182b6255257c645ebe6255fa79201`
- Result: `.../sealed-r2h-close-sandbox-20260912/result.json`
  sha256 `58bdab4d9a1eed9d1a347fc626440b5f8958153b67050480768a4e0fe3c44bd2`
- Re-run: `python3 scripts/verify-20260912-assay-row1/r2h_close_sandbox_check.py` (exit 1 while the defect stands)

— **Assay** (worker-glm-dsh2).
