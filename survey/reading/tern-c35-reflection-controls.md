# Reflection can help without becoming authority

Tern ·26 September2026 · cycle35 initial methods reading; panel synthesis pending.

[Generative Agents, Park et al., UIST2023, v2](https://arxiv.org/html/2304.03442v2), §§4.2–4.3,6.1–6.5: reflections cite supporting memory IDs and can build on earlier reflections. Plans also enter the memory stream. These are generated interpretations and intentions, not additional independent observations.

The interview ablations restrict access to memory types after a shared full-system simulation; they do not independently rerun each architecture's life. Human evaluators rank believability. The full architecture ranks highest; the paper separately describes retrieval misses and embellished memories. Its claim that shared histories make differences conservative is an interpretation, not a guaranteed bias direction.

**Judgment:** source-linked reflection is a credible way to make experience useful for synthesis. It does not establish factual faithfulness merely by attaching citations, nor measure Brian's correction burden. The ablation identifies an interview-time contribution under its shared-history setup; the whole simulated trajectory requires a different comparison. High confidence in these controls, medium in the reusable mechanism, fleet benefit unknown.

**Design inference:** keep a reflection's supporting events accessible and its status distinct from observation, completed action and authorized direction. This can be done in an existing record; it does not select a new service.
