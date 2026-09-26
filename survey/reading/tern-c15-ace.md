# ACE: incremental learning has a concrete mechanism and a feedback dependency

**Tern · 26 September 2026 · primary methods, no experiment.**

[ACE v1, §§3–4](https://arxiv.org/html/2510.04618v1) separates generation, reflection and curation, merging itemized updates with non-LLM logic. Bullets carry identifiers and helpful/harmful counters. The evaluated roles use the same non-thinking DeepSeek-V3.1, so the result is not inherently stronger-model tutoring of a weaker executor.

The main AppWorld online result includes offline warmup; the ablation reports a weaker but still positive result without it. Offline multi-epoch learning, warmed online adaptation and cold online adaptation are different comparisons. Its finance results also expose a limit: without reliable feedback, adaptation can hurt. Incremental editing limits wholesale rewrite collapse; it does not establish that every retained lesson is correct.

The cost comparison measures adaptation against specified alternatives, not Brian's whole workflow or human attention. The paper supports an existing alternative to repeatedly rewriting a summary and to assuming learned procedures require weight training. It does not demonstrate indefinite lossless retention, reliable applicability under arbitrary configuration change, or a universally optimal prompt length. **Medium confidence in practical relevance; comparative benefit here unknown.**
