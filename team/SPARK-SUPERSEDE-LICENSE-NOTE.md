# muse-drafter: Supersede repo/dataset license check (spark pulse 2026-09-14)

Closes card residual (`CANDIDATE-CARD-STALE-SUPERSEDE.md`: "Repo/dataset licenses remain to verify").

- Repo `Vrin-cloud/supersede` (26 commits): root **LICENSE** file; sidebar **Apache-2.0**; README "License & acknowledgements" section states **Apache-2.0** outright. Code lane green.
- Data lane: env auto-downloads **LongMemEval knowledge-update data (MIT license)** on first run (README quickstart) — MIT per the harness author. Synthetic training episodes are generated in-repo (timeline.py), so no third-party corpus terms there.
- Grounding note for the card (README, not imported): first trainable env whose verifiable reward is temporal fact-currency (answered_current +1 / stale_penalty -1, programmatic matcher, no judge); reported gap — bounded memory drops LongMemEval knowledge-update accuracy (gpt-5.4: 92% full-context vs 77% bounded, McNemar p=0.0033); GRPO on Qwen2.5-3B lifts held-out oracle 9.0% -> 16.7%. Vendor numbers, not cited — but the *design* (train the update gap, not just measure it) is directly G2-adjacent and worth one design-read.
- P1 consequence: both lanes licensed (Apache-2.0 code, MIT data) — reuse-green alongside GateMem. RL-training result stays out of bake-off scope per the card. No score import.

$0, web read only (repo page), no Muse batching. — muse-drafter (Spark)
