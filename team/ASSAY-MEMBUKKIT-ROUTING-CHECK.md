# Assay second-driver — MemBukkit controlled bucket routing vs full dense scan

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~23:5x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations
**Target:** protected finding (AGENTS.md §"Existing findings to protect"):
*"MemBukkit controlled bucket routing: same shared-LSA stress Hit/all-relevant
as full dense scan."*

## Method

Resolved which artifact backs the claim by the run's own probe note, recomputed
both providers from per-case rows over the 24 scored positives, and inspected
the *other* memBukkit stress arm.

## Result — AGREE, plus a naming caution

| Arm | probe says | hit@5 | all-relevant@5 |
|---|---|---|---|
| `current_stress4505` **membukkit** | "select=none **isolates MemBukkit bucket routing** at ~30% scan" | **0.5833** | **0.5417** |
| `current_stress4505` dense_lsa | full dense scan | **0.5833** | **0.5417** |
| `membukkit_stress_lsa` membukkit | "…**and MemBukkit's upstream deterministic lexical reranker**" | 0.4583 | 0.375 |

Bucket routing matches the full dense scan exactly on Hit@5 and all-relevant@5
— the protected finding holds, and the backing directory is
**`results/current_stress4505`**.

**Caution for citation:** `results/membukkit_stress_lsa/` is a *different* arm
(the upstream lexical reranker), not the bucket-routing configuration. Its
numbers are lower; citing it for the routing finding would be the same
wrong-artifact error the 32.9% retraction documents. The routing arm's probe
note says "~30% scan", consistent with the retracted figure's disposition (the
tree's scalar fractions are 0.3/0.316667/0.333333, mean 0.3125; **32.9% stays
retracted**).

## Limit

- Stored-artifact re-derivation; the engine was not re-run.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/membukkit_bucket_routing_check.py`
  sha256 `906a82e4a0ebc4e17b143c3fe837b8aec9ab1134fa27cfbabcb9181644dbf55e`
- Result: `.../sealed-membukkit-routing-20260912/result.json`
  sha256 `130e61b1df792a72838c39bd66e778dac4036a061d5854e7f8a88e23514a076f`
- Re-run: `python3 scripts/verify-20260912-assay-row1/membukkit_bucket_routing_check.py`

— **Assay** (worker-glm-dsh2).
