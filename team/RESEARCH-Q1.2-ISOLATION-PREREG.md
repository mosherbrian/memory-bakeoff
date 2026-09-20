# Pre-registration — Q1.2 run-integrity / cross-run leakage probe

**Author:** Corvid (worker-glm-dsh3), R&D staff
**Origin:** Muse ideation batch 1, item Q1.2 (`team/MUSE-IDEATION-01.md`), approved as the priority next probe by GiLMore 2026-09-12.
**Status:** pre-registered, design only. Not run. No spend.

---

## Question

When the portfolio harness runs one engine twice, does state from the first run leak into the second — cached embeddings, a pre-populated store, or precomputed answers — so that run 2 scores higher without the engine being better?

This is a run-integrity question, not a retrieval-quality question. If it fails for any candidate, that candidate's numbers are invalid until fixed, whatever the engine.

## Why now

The existing preflights are provider-specific and were not all green: `results/agentmemory_raw_product_gen13_isolation_preflight/preflight.json` records `status: failed` (service never healthy). The abstract `MemoryProvider.reset()` contract exists (`providers/base.py:36`) but nothing asserts, engine-agnostically, that a reset actually empties the store or that a second run is not inflated. Muse surfaced this; the Gen4 Hindsight invalidation (`results/hindsight_gen4_core_r1/INVALIDATED.md`, a stale service serving requests) shows the class is real in this tree.

## Hypotheses

- **H0 (integrity holds):** for every provider, run 2 == run 1 on the frozen core corpus after `reset()`; deterministic providers differ by exactly 0.
- **H1 (leakage):** at least one provider's run 2 has higher Hit@5 / all-relevant@5 / MRR than run 1 beyond its noise band.
- **Power check:** a deliberately un-reset pair ("contaminated" control) must inflate. If it does not, the test lacks power and the null is uninformative.

## Method (engine-agnostic, deterministic first, $0)

1. Pick the frozen core corpus already in the tree (`results/current_full_core5/` inputs); no MemConflict, no absent dataset, no LLM, no service where avoidable.
2. Providers, cheapest first: `bm25`, `tfidf_cosine`, `dense_lsa`, `hybrid_rrf`, then the vendored controlled cores (`habitus`, `membukkit_core_lsa`, `agentmemory_core_lsa`). Product/service providers (Hindsight, real agentmemory daemon) are a separate, later arm — they need the service-health preflight first.
3. Each provider, four runs in one process, into a **new result directory** (never overwrite an existing one):
   - `a1`, `a2`: `reset()` between runs (the honest path);
   - `b1`, `b2`: **no** reset between runs (the contaminated control).
4. Assert after `reset()`: the provider's store is empty (provider-specific introspection) and no cross-run cache file appeared under the run directory.
5. Metrics: Hit@5, all-relevant@5, MRR, prohibited@5 — same as the core5 table.

## Pre-registered criteria

- **PASS (H0):** every provider's `a2 - a1` is 0 for deterministic providers and within the repeated-draw band for stochastic ones (no LLM here, so expect 0).
- **FAIL (H1):** any `a2 - a1 > 0` beyond band → that provider is **dropped by name** from unfiltered portfolio scoring until the leak is fixed; the drop is reported, not silently patched.
- **Power:** the control must show `b2 - b1 > 0` for at least one provider. If the control is flat, report the test as **lacking power** and redesign rather than claiming integrity.
- **Falsifier of the whole probe:** if `reset()` cannot be observed to empty any store (no introspection path), the probe reports "not measurable" and the provider stays flagged, not cleared.

## Ownership / handoff

- **Corvid (R&D):** this pre-registration, the run, and the analysis.
- **Kiln (harness):** only if the run needs a harness hook for store introspection or a `reset` assertion; the probe should reuse the existing runner, not fork it.
- **P1:** result lands as a receipt; a FAIL adds a drop-by-name candidate and a row-5 caveat.

## Limits

- In-process deterministic providers cannot catch a *service*-side cache (a daemon holding embeddings across restarts). That is the separate product arm and is explicitly out of this first probe's scope.
- Passing this probe does not certify a provider's numbers; it only removes one failure class from them.

— Corvid. The cheapest way to lose a benchmark is to run it twice and let the first run warm the second.
