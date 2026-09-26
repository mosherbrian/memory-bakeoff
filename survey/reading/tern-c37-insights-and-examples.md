# Later-task learning needs both a transfer boundary and a cost boundary

Tern ·26 September2026 · cycle37 primary reading; panel synthesis complete.

[ExpeL v3](https://arxiv.org/html/2308.10144v3), §§4–5: training-task trials populate an experience pool; success/failure comparisons and groups of successes revise an insight list. LLM-selected ADD/EDIT/UPVOTE/DOWNVOTE operations adjust counts and remove zero-count insights. Those counts are not measured per-item causal utility.

Evaluation uses unseen tasks, retrieved successful trajectories and the full insight list. All acting models use GPT-3.5 in the reported setup; default insight extraction uses GPT-4. Retrieval-only and insights-only controls show differing relative strengths across environments. Four-fold evaluation and single-attempt testing distinguish this from retrying the same test problem. Transfer from HotpotQA to FEVER includes adapting insights with GPT-4 and target demonstrations, not untouched zero-cost migration.

**Judgment:** this is direct evidence for cross-task external learning, with both abstract guidance and examples contributing. It does not establish that either representation alone is universally best, or that no parameter updates means no acquisition expense. Medium confidence in transfer relevance; changed-environment procedure reuse and total upkeep remain separate questions. Appendices C–E checked: resource/setup details do not supply a complete acquisition bill. See the panel response for marginal-comparison qualifications.
