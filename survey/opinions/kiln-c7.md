# kiln (Practitioner) — c7: price learning honestly

**kiln · 2026-09-26 · ~500w · no new runs, no invented savings. Sources: Gen45 live pilot input (read this session), pi-lcm compaction engine source (read c2-cont). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack".**

## What Gen45 actually measured (carried, not estimated)

One local model (Qwen3.6-35B UD-Q4_K_XL, Vulkan 8060S, Pi 0.73.0, ctx 131k), four invented tasks × three stochastic samples, 24 runs. The cost ledger, separated:

- **Cumulative request bytes:** median 52,638 (A, stock) vs 64,757 (B, composed); mean 65,450 vs 321,832 — the mean gap is three T3 loops (~1.1MB each, all timeouts).
- **Requests / tool calls (median):** 7.0/8.0 vs 9.0/11.0; T3 arm B hit 337 requests + 591 tool calls in 900s.
- **Outcomes:** 12/12 vs 7/12 verifiers; 0 vs 3 timeouts.
- **Per-request growth:** A 209x over six requests (transcript replay), B 2.6x over 337 (bounded view works as designed — H2 supported while H1 falsified).
- **Control-layer use:** 6 patches accepted / 3 rejected / 0 transitions across twelve runs — the "state and control" arm was really a bounded window plus ignored tools. H5 untested, not supported.
- **Setup labor (real, rarely logged):** compatibility smoke passed on the third attempt (two harness bugs fixed pre-freeze); isolated agent dir to avoid contaminating the baseline.

## What remains unknown (not carried)

Wall-clock latency per task (digest explicitly excludes wall clock); pi-lcm compaction cost (never triggered — runs too short); summarization-call cost of eager compaction on Brian's box (the engine bounds cascade at 10 passes and chunks by token budget, but tokens-per-compaction and call latency are unmeasured); user-correction cost in real use (the 6 volunteered patches are not corrections); amortization of the setup labor over N tasks. The BRIAN-PRINCIPLES 16x figure is an unverified literature lead — not repeated here as evidence.

## Minimum cost accounting that would change a choice

Per task: **outcome (pass/fail/timeout) + cumulative request bytes + request count**, reported as the full pair table, never averaged across divergent outcomes. That triple is what falsified H1 while H2 held — per-request size alone would have declared victory while the runs looped and failed. Add amortized setup labor only when comparing *adopting* something (one-time smoke + config) versus *running* it. Everything else — latency percentiles, compaction-call budgets, correction counts — joins the ledger when a decision actually turns on it, not before.

**Practical read for Brian:** on current evidence the composed procedure costs more cumulative work for fewer passes on these four tasks (7/12, higher median bytes, 3 timeouts) — carried, not inferred. What would reverse it: the same triple on Brian's real recurring tasks, where transcript replay (209x growth) may hurt more than it did on 6-request toy runs. That is a measurement to run, not a saving to assume.

## Gap deepened: bounding the unmeasured compaction cost (same sources)

The card left eager-compaction cost unmeasured. Read-only config check bounds it structurally: defaults are 4k-token leaf chunks, condensation threshold 6, max depth 5, 8k summary cap, 10-pass cascade ceiling, tunable via env/file (`LCM_LEAF_CHUNK_TOKENS` etc.). So worst-case summarization work per compaction event is a known function of transcript length — but tokens-per-event and call latency on Brian's actual model/host remain unmeasured, and Gen45 never triggered the path at all. The bound tells us the cost is linear-ish in transcript size with a small constant; it does not tell us the constant. First real number worth capturing: tokens in/out of one compaction event on a real long session. Until then, compaction stays in the ledger as "bounded-unknown," not zero.

**Medium confidence** in the accounting recommendation; **low** in any cross-task generalization — four invented tasks, one model, stochastic samples, says the pilot itself.
