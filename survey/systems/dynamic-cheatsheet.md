# System card: Dynamic Cheatsheet (author implementation)

**kiln · 2026-09-26 · sources: author repo suzgunmirac/dynamic-cheatsheet (cloned read-only, nothing executed): README, prompts/{curator_cumulative, curator_retrieval_synthesis, generator}.txt, utils/{extractor, execute_code}.py, run_benchmark.py. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## What is persisted, how rewritten

- **Persisted:** one `<cheatsheet>` block (~2000–2500 words), versioned, of `<memory_item>` entries (description + worked example/code, Q-tag references like Q14, per-entry **Count** of successful uses). Two curator modes: cumulative (keep everything useful) and retrieval-synthesis (selective).
- **Rewritten:** monolithically, every round — the curator regenerates the whole block, instructed to copy forward what matters. The prompt itself warns dropped content "will be lost and cannot be retrieved." So the collapse failure ACE names is structurally present here (single rewrite path, no delta log), mitigated only by instruction ("preserve old content," usage counts, Q-tags), not by mechanism. Stated plainly, not as verdict-by-ACE.
- **History separately available?** In cumulative mode: no — transcripts feed each curation round; the cheatsheet is the only durable artifact, and what the curator drops is gone. **Correction (c21):** this does not hold for every variant — the retrieval-synthesis (RS) mode retrieves previous input/output pairs, so prior pairs remain reachable there. The precise claim is: no *versioned archive* in either mode, and no history at all in cumulative mode.

## Tools, outcome evidence, executor assumptions

- **Tools:** generator emits Python fenced blocks ending "EXECUTE CODE!"; `execute_code_with_timeout` (3s) runs them and returns output into the loop. Outcome evidence is real but narrow: code execution + exact-match grading on verifiable benchmarks (AIME, Game-of-24, GPQA).
- **Executor assumed:** black-box LM + Python sandbox + batch benchmark runner (`run_benchmark.py`). No host plugin, no hooks, no MCP, no session integration — prototype research code. Any transfer to Brian's hosts is custom glue: a scheduled/closeout runner, an outcome check, and a file write.

## Task-specific solver vs broad learning (distinguished)

The showcase wins (Game-of-24 10%→99%) are a discovered *solver* (Python brute force) reused across same-shape tasks — not broad procedural learning. The mechanism generalizes only where tasks share checkable structure and the curator's Q-tags can index it. Brian's rollout/model-test procedures have that shape when outcomes are machine-checkable; judgment-heavy procedures do not.

## Advice: **watch the loop, deploy two fragments**

Transferable pattern today at ~zero cost: per-entry usage Counts + Q-tag provenance inside our textual skills (finer than nothing, cheaper than ACE's merge machinery) — adopted on cost-of-ink grounds only if the Count is actually read during trim decisions; cheap ink nobody reads is clutter, not upkeep. The monolithic-rewrite loop itself stays watch-only for Brian: no delta log, no history archive, needs an outcome check per task family. Do not build the runner until one procedure with a real verifier earns it.
