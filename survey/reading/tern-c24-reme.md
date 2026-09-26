# ReMe: affordable self-curation is possible; total economy remains open

**Tern ·26 September2026 · primary §§3–4 read, panel intake pending.**

[ReMe v1](https://arxiv.org/html/2512.10696v1) uses the same Qwen3 model for execution and summarization, with eight acquisition trajectories per training task. This contradicts a universal frontier-curator requirement. Table4 separately improves results by strengthening the summarizer while holding the executor fixed.

Keep Table1's metrics straight: 8B dynamic memory versus14B memoryless is **55.03 versus54.65 Pass@4**, but **34.94 versus35.62 Avg@4**. It is not universal superiority or equal-compute evidence. The prose swaps some gain labels; use the table. Acquisition, judging, embeddings, reuse and up to three failure reflections add work.

Initial acquisition analyzes successful and failed trajectories together. Online admission favors success; a failed attempt can generate a retrial whose successful lesson is then admitted. Table3's sequential ablation favors selective admission over adding everything; reflection changes Avg@4 but not Pass@4 there, while deletion adds further gain. This does not separately identify every interaction or prove safe retirement under version drift. Utility tracks success associated with retrieval, not causal contribution.

**Judgment, medium confidence:** meaningful evidence for agent-owned procedural upkeep; no portable local-cost winner established. A failed record may remain useful history even when its inferred lesson is not admitted to current guidance. No experiment or installation.


**Version follow-up:** [v2 §4.4](https://arxiv.org/html/2512.10696v2#S4.SS4) adds AppWorld average inference latency21.42→23.96 seconds. This corrects the version-general “no latency figure” claim, not total acquisition/refinement cost. V2 retains eight acquisition samples and names text-embedding-v4, whereas v1 names Qwen3-Embedding; a Qwen executor alone does not prove a wholly local setup. Version-specific controls matter.

**Current product, separate evidence:** the [official repository](https://github.com/agentscope-ai/ReMe) documents Markdown workspace files, optional vectors, automatic capture, consolidation and host integration. That is neither merely an experimental pool nor proof that today's product executes the paper's exact admission/deletion algorithm. It makes files versus service a poor binary; operations and data ownership are the useful comparison. Source inspection continues, no installation.
