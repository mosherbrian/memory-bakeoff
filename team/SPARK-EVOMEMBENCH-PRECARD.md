# muse-drafter: EvoMemBench pre-card recon (spark pulse 2026-09-14)

Tees up the EvoMemBench/EvoArena candidate card (last of the goal-5 frontier harvest).

- Identity: **EvoMemBench**, arXiv:2605.18421 (v1 2026-05-18, v2 2026-06-15), Wang et al. Code: `github.com/DSAIL-Memory/EvoMemBench`. Unified benchmark of agent memory from a self-evolving perspective: 2 axes (memory scope in-episode vs cross-episode; content knowledge-oriented vs execution-oriented) = 4 settings. 15 memory methods vs strong long-context baselines, standardized protocol.
- Headline findings (vendor claims, NOT imported): no general solution yet; long-context baselines highly competitive; memory helps most when current context insufficient or tasks hard; no single memory form wins everywhere; retrieval-based strong for knowledge settings, procedural/long-term for execution settings when stored experience matches task structure.
- **Name-collision flag (important for the card):** `Evo-Memory` (arXiv:2511.20857, streaming search-predict-evolve framework + ExpRAG/ReMem baselines) and `EvolveMem` (arXiv:2605.13941, self-evolving retrieval-config architecture) are DIFFERENT works. Card must pin 2605.18421 explicitly.
- License note: arXiv page shows "arXiv.org perpetual non-exclusive license" (not CC) for the paper; code/dataset terms still to verify at card time (P1 rule: verify before adapter work).
- Goal-grounding preview: cross-episode evolution settings are the closest published analogue yet to our G2 (update/supersede) dynamics at agent scale; knowledge-vs-execution split maps loosely to G1/G4. Card to confirm abstract-level.

$0, web reads only (arXiv abs + HTML v1/v2, search), no Muse batching. — muse-drafter (Spark)
