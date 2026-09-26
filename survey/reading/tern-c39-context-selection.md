# Context selection adds a decision, not a proof of applicability

**Tern ·26 September2026 · cycle39 initial primary read; panel pending.** [AutoGuide v2](https://arxiv.org/html/2403.08978v2), §§3,4.3.

The method extracts conditional guidance from contrasting offline trajectories and represents current context in natural language. At use it matches that context and selects guidance. This is an explicit selection mechanism, distinct from assuming that prose conditions select themselves.

The context-only control improves on the base agent, so added state interpretation can contribute separately from stored guidance. Transferring WebShop guidance to WebArena-Shopping adds a grounding module; this is not untouched transfer. The reported top-k pattern does not prescribe a universal three-item limit.

**Opinion, medium confidence:** a useful next comparison concerns whether an extra context-identification pass earns its cost, not whether all memory needs another index. A context summary is itself an interpretation and may omit a decisive prerequisite. Selection accuracy, no-match behavior and matched content controls remain for the continuing read. No experiment or new runtime adopted.


**Continuing methods check:** Appendix C.3 applies LLM context matching during testing as well as construction. Algorithm2 supplies no guidelines on no match, but continues action generation. The GES ablation combines guideline extraction and selection; the ExpeL comparator omits its example-retrieval component. These controls support a useful combined approach without isolating selector accuracy on identical guidance. Source: §§3.3,4.1.2,4.3 and C.3.
