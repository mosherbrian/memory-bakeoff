# Assay — P1 receipt re-derivation ledger (campaign-1)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~19:0x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations (portfolio adapter receipts)
**Purpose:** one page the fleet can read to know which P1 adapter-receipt claims
have been independently re-derived, which are only asserted, and where the gaps
are. Receipts claim; the run is the check.

## Re-derived this session (AGREE)

| Receipt claim (`docs/PORTFOLIO-P1-ADAPTER-RECEIPTS.md`) | Second-driver | Verdict |
|---|---|---|
| agentmemory `test_agentmemory_core.py + test_agentmemory_localization.py` → 13 passed | re-ran at HEAD `78cdd2d` → **13 passed in 0.97s** | agree |
| pi-lcm store reader contract `→ 12 passed` (run at `2bed095`) | blob-pinned at `2bed095` and HEAD; re-ran → **12 passed** | agree |
| pi-lcm no-regression neighbors → 28 passed | re-ran → **28 passed in 2.08s** | agree |
| long-context null + stale-use → 15 passed | re-ran → **15 passed in 0.02s** | agree |
| agentmemory license sha256 `76c8d49ab42216a2533f…` | recomputed full hash `76c8d49a…dcc012c` | agree |
| agentmemory vendor pin `e04ba888…` | matches `vendor/agentmemory/UPSTREAM.md` | agree |
| agentmemory false-supersession 418/450 = 92.9% | re-derived from raw `lifecycle.json` (r1–r3) | agree |

Detail: `ASSAY-SECOND-DRIVER-AGENTMEMORY-418.md`, `ASSAY-SECOND-DRIVER-PI-LCM-RECEIPT.md`.

## Re-derived, but note the pinning strength

- agentmemory 13 and long-context 15 reproduce at **current HEAD `78cdd2d`**;
  I did not byte-pin those test files to the receipt's original run time. Strong
  enough to catch a regression, weaker than the pi-lcm check (which is
  blob-identical at the receipt commit and HEAD).

## Still asserted, not independently re-derived (named gaps)

| Claim | Why it is a gap |
|---|---|
| perseus vault Hit@3 0.434 on the 27-persona dynamic slice (Gen38) | needs the held-out slice + anchored run; not in this pulse's scope |
| bm25 baseline "0.226 dynamic Hit@3" (BAR B floor) | historical number; source run not re-executed here |
| letta / langmem / a_mem / memobase / memos upstream harnesses | PENDING by design: blocked on materializing `external/MemConflict` (182 MB), not on code |
| native capture "INERT" | covered by earlier Assay row-0/row-2 reproductions, not re-run this pulse |

## Takeaway

Every **run-claim** in the P1 receipts that can be re-executed offline now has a
second driver and reproduces exactly. The remaining gaps are either frozen
historical scores (perseus 0.434, bm25 0.226) or explicitly dataset-blocked
harnesses — no receipt in the live build lane is resting on an unchecked test
count.

## Re-run commands

```bash
cd implementer/repo
PYTHONPATH="src:/home/bmosher/.local/lib/python3.14/site-packages" python3 -m pytest -q \
  tests/test_agentmemory_core.py tests/test_agentmemory_localization.py         # 13
PYTHONPATH="src:/home/bmosher/.local/lib/python3.14/site-packages" python3 -m pytest -q \
  tests/test_longcontext_null_contract.py tests/test_stale_use_penalty.py        # 15
```

— **Assay** (worker-glm-dsh2).
