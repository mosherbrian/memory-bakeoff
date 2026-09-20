# muse-drafter: StateMemBench release watch (spark pulse 2026-09-14)

- Paper arXiv:2608.19652 v1 (2026-08-20). HTML says "We release StateMemBench" but carries no repo/HF URL in the fetched sections; only outbound code link in refs is Microsoft's STATE-Bench (distinct item, already flagged in the card's name-collision note).
- Web search "StateMemBench github code dataset": no author repo or HF dataset hit; only arXiv mirrors, alphaXiv, and a third-party blog. opentrain.ai reports "no trustworthy direct or curated Hugging Face artifacts found yet".
- Verdict: **still unreleased publicly as of 2026-09-14** — release watch stays open; card status unchanged (design reference only, no score import, no license to check).

## Re-check 2026-09-15
- Targeted search ("StateMemBench" github OR huggingface): still no author repo or dataset. opentrain.ai now explicit: "no verified maintained implementation", "no trustworthy HF artifacts"; only adjacent (ruvnet/ruflo, not paper-verified) + third-party explainers (Neodrop, Compendia, Beckmann) + memorypapers.org entry. Bonus grounding detail from explainers (not imported): anti-update conditions (unauthorized newer statement must NOT replace the rule) — a permission-aware supersession shape our P1 cases don't test.
- Verdict unchanged: watch stays open.

$0, web reads only (arXiv HTML + search), no Muse batching. — muse-drafter (Spark)
