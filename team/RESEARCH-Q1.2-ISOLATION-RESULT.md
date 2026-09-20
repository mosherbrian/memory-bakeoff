# Q1.2 result — cross-run leakage probe (run-integrity)

**Author:** Corvid (worker-glm-dsh3), R&D staff
**Task:** QUEUE row 14, Muse ideation batch 1 item Q1.2. Executes the design frozen in
`team/RESEARCH-Q1.2-ISOLATION-PREREG.md` (filed before this run).
**Date:** 2026-09-12 · **Cost:** $0.00 · **LLM calls:** 0 · **Network calls:** 0 ·
**Service processes:** 0 (in-process only)
**Status:** run complete. Both executions `PASS`.

---

## Plain English (for Brian)

We re-ran the same small memory benchmark twice against each of the seven cheap
in-process engines, on purpose, to check whether the second run quietly scores higher
just because the first run "warmed up" a cache or left records behind.

It does not. Every engine scored **byte-for-byte the same** on run 1 and run 2, on
every metric, whether we explicitly wiped the store in between or used a brand-new
engine object each time. The wipe is real: after clearing, every engine's store is
observably empty and asking it anything returns nothing.

To prove this test could actually catch a leak if one existed, we built a deliberately
leaky fake engine that remembers the answer key from run 1; the test flagged it
immediately (+0.96 Hit@5 on the second run). So the clean result is meaningful, not a
blind spot.

**No decision needed.** Nothing is blocked. The only thing this does *not* cover is
engines that run as a separate service (Hindsight, the agentmemory daemon, the
MemBukkit pretrained product path); those stay flagged as untested for this failure
class until the separate product arm runs.

---

## What ran

- Providers, cheapest first: `bm25`, `tfidf_cosine`, `dense_lsa`, `hybrid_rrf`,
  `habitus`, `membukkit_core_lsa`, `agentmemory_core_lsa`.
- Corpus: `build_corpus(distractors=0)` — the frozen core5 corpus (50 records, 26
  cases, sha256 `062b8b8471d092af1082e469262f183b1969029b30fa4facec17c974933ff965`).
- Per provider: a-track (same instance, `reset()` between runs), b-track (same
  instance, no reset), h-track (two fresh instances through `runner.run_provider`,
  the real harness semantics). Metrics at k=5.
- Two independent executions: `results/isolation_q1.2_20260912/` (first) and
  `results/isolation_q1.2_20260912_r2/` (corrected `h_ids_identical` reporting field;
  measurements identical). `probe.json` + `SUMMARY.md` in each.
- Probe code: `scripts/experiment_20260912_q1_2_isolation/` (`q1_2_isolation_probe.py`,
  `probe.sh`, `FINDINGS.md`).

## Result

| Provider | reset store empty | a2−a1 hit@5 | b2−b1 hit@5 | h2−h1 hit@5 | verdict |
|---|---|---:|---:|---:|---|
| `bm25` | yes (`docs=0`) | 0.000 | 0.000 | 0.000 | pass |
| `tfidf_cosine` | yes (`docs=0, matrix=None`) | 0.000 | 0.000 | 0.000 | pass |
| `dense_lsa` | yes (`docs=0, matrix=None`) | 0.000 | 0.000 | 0.000 | pass |
| `hybrid_rrf` | yes (`bm.docs+dense.docs=0`) | 0.000 | 0.000 | 0.000 | pass |
| `habitus` | yes (`mind=None`) | 0.000 | 0.000 | 0.000 | pass |
| `membukkit_core_lsa` | yes (`mem=None`) | 0.000 | 0.000 | 0.000 | pass |
| `agentmemory_core_lsa` | yes (`proc=None, encoder=None`) | 0.000 | 0.000 | 0.000 | pass |

Deltas are exactly 0 for all five recorded metrics (hit@5, all-relevant@5, MRR,
prohibited@5, mean context chars), not merely within a noise band. Retrieval ids are
identical across run pairs for every provider.

Post-reset behavioural check: after `reset()`, every provider returns **zero** retrieved
ids across all 26 cases — BM25 returns empty; the rest refuse for a missing built store
(`AttributeError`/`AssertionError`), which is the expected "no store" state.

**Power check (pre-registered, mandatory):** the synthetic leaking control
`ctrl_leaky_answer_cache` — a fake engine whose `reset()` fails to clear a cached answer
key — was flagged at `a2−a1 hit@5 = +0.958` and `b2−b1 hit@5 = +0.958`. The method has
power, so the clean real-provider result is informative.

**Corpus identity check:** run-1 metrics reproduce the frozen `results/current_core5/`
and `results/current_full_core5/` rows exactly for all seven providers (e.g. bm25
0.917/0.792/0.844/0.125; dense_lsa 0.958/0.958/0.837/0.125; membukkit_core_lsa
0.958/0.958/0.525/0.125; agentmemory_core_lsa 0.958/0.958/0.868/0.125). The probe
measures the same corpus the portfolio table does.

## Disposition

- **H0 holds** for the seven in-process deterministic providers: run 2 does not inflate.
  Nothing is dropped by name; no row-5 caveat is added from this probe.
- **Reset is observably honest** for all seven: introspection and behaviour agree.
- **No cross-run cache file** appeared under the result directory, and no provider reads
  a prior run's scratch path.
- **One disk-hygiene note, not a score leak:** `habitus` creates a fresh `mkdtemp`
  sqlite store per ingest (six new scratch dirs across its six runs). `reset()` sets
  `mind=None` but does not delete the file. A later run always gets a new path, so it
  cannot inflate a score; it does leave scratch data behind. Flagged for a later cleanup
  pass, not a correctness fix.

## Deviations from the pre-registration (recorded, not silent)

1. **The literal b-track cannot be built.** Every in-scope provider's `ingest()` calls
   `self.reset()` first, so "no reset between runs" collapses to "ingest twice", which
   is idempotent. The b-track was still run and recorded; the pre-registered power check
   rests on the synthetic leaking control instead of on a real engine.
2. **Added an h-track** (two fresh instances through `runner.run_provider`) because that
   is the actual harness semantics; the pre-reg's a-track reuses one instance.
3. **Added a second execution** (`_r2`) after fixing a reporting-only field
   (`h_ids_identical` compared latency-bearing detail rows). Measurements are identical
   across both executions; both are kept per the "new result dir" rule.

## Limits

- In-process, deterministic, no-LLM providers only. This cannot catch a **service-side**
  cache (Hindsight API, agentmemory daemon, MemBukkit pretrained product). Those remain
  a separate, later product arm needing the service-health preflight.
- Passing removes one failure class from these providers' numbers; it does not certify
  any provider's scores.

## Artifacts

- Pre-reg: `team/RESEARCH-Q1.2-ISOLATION-PREREG.md`
- Receipt: this file
- Run: `results/isolation_q1.2_20260912_r2/probe.json` (+ `SUMMARY.md`); first execution
  `results/isolation_q1.2_20260912/`
- Code: `implementer/repo-glm-dsh3/scripts/experiment_20260912_q1_2_isolation/`

— **Corvid** (worker-glm-dsh3). The cheapest way to lose a benchmark is to run it twice
and let the first run warm the second. For these seven, the second run is the first run.
