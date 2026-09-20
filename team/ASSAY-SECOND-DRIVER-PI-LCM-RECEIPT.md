# Assay second-driver re-derivation — pi-lcm store-reader P1 receipt

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~18:2x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations (portfolio adapter receipts)
**Claim re-derived:** `docs/PORTFOLIO-P1-ADAPTER-RECEIPTS.md` §pi-lcm store reader
(receipt commit `bb0b4b0`, run at `2bed095`) — contract suite
`tests/test_pi_lcm_store_reader_contract.py -q` = **12 passed**; no-regression
neighbors = **28 passed**.
**Verdict: AGREE, exactly, and the measured files are unchanged.**

## Method

1. **Pin the measured bytes.** In the canonical implementer repo, the test and
   adapter blobs are identical at the receipt's run commit `2bed095` and at
   current HEAD `bb0b4b0`:
   - test blob `141833420d69…` at both; working-tree content sha256
     `427707e419b716644bb6d806f4454bc0bf2ccc6f707932f5413f02cbbad87e87`;
   - adapter blob `511ec077d320…` at both
     (`src/memory_bakeoff/providers/pi_lcm_store_reader.py`).
   `git diff 2bed095..HEAD` over both paths is empty.
2. **Re-ran the receipt's two commands** on HEAD with
   `PYTHONPATH=src:/home/bmosher/.local/lib/python3.14/site-packages`.

## Result

| Command (receipt) | Claimed | Re-derived |
|---|---|---|
| `pytest -q tests/test_pi_lcm_store_reader_contract.py` | 12 passed | **12 passed in 1.33s** |
| `pytest -q test_longcontext_null_contract + test_stale_use_penalty + test_agentmemory_core + test_agentmemory_localization` | 28 passed | **28 passed in 2.08s** |

The contract file contains exactly **12** test functions, matching the count.
Host matches the receipt's note: Python 3.14.6, sqlite **3.50.2**, FTS5 native.
The receipt commit itself is current HEAD (`bb0b4b0`,
"PORTFOLIO rows 1-2 receipt: pi-lcm store reader RECEIPTED").

## One provenance note for future verifiers (not a defect)

The receipt is **canonical-repo-scoped**. The worker fork
`implementer/repo-glm-dsh2` at its HEAD `86709b3` does **not** carry
`tests/test_pi_lcm_store_reader_contract.py` or the adapter, so a second driver
who runs from the fork gets a false "file not found." Run this receipt's checks
in `implementer/repo/`. Stated so the next verifier does not misfile it as a
missing artifact.

## Limits

- Re-run is at HEAD, not literally at `2bed095`; the blob-identity check makes
  that equivalent for the two measured files (and only those are checked here).
- This verifies the test/receipt claim, not the adapter's retrieval quality.

## Receipts

- Canonical repo: `implementer/repo/` @ `bb0b4b0`.
- Re-run commands (exact):
  `PYTHONPATH="src:/home/bmosher/.local/lib/python3.14/site-packages" python3 -m pytest -q tests/test_pi_lcm_store_reader_contract.py`
  and the four-file neighbor command above.

— **Assay** (worker-glm-dsh2).
