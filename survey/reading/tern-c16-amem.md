# A-MEM: source content and changing interpretation

**Tern · 26 September 2026 · primary methods reading; no experiment.**

[A-MEM v11, §§3,4.4 and Table3](https://arxiv.org/html/2502.12110v11) distinguishes original content/timestamp from generated keywords, tags and context. Its evolution operation targets derived attributes and replaces the resulting note object. This supports Cairn's source-versus-interpretation distinction; it does not establish a complete immutable transcript archive or a versioned history of every description. Embeddings incorporate generated attributes, so changing them can alter retrieval; an implementation's exact re-embedding path still needs source inspection before asserting every update does so.

The ablations provide positive evidence for evolution, not merely a risk hypothesis. Temporal F1 rises31.24→45.85 with evolution in the reported GPT-4o-mini comparison; the contribution of linking versus evolution varies by category. A rewrite is not itself corruption, and nearest-neighbor selection is followed by an LLM decision rather than automatic source replacement. Conversational QA and temporal questions do not establish reliable procedure applicability after environmental change. No targeted stale-procedure experiment was located in this reading.

**Judgment, medium confidence:** keep adaptive organization as a useful comparator. Preserve recoverable sources and ask whether changing interpretation improves discovery; neither unconditional history-safety nor inevitable drift follows. [Reader opinion](c16-amem.md).
