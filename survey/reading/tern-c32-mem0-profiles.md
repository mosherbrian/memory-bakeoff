# Mem0: the raw adapter, paper and current documented path differ

**Tern ·26 September2026 · cycle32 interim.**

Our [earlier readout](../inputs/ROUND1_FINAL_READOUT.md) identifies **infer=False**, dense+BM25 raw storage. It explicitly excludes LLM update/lifecycle semantics. Preserve that result without making it a whole-product verdict.

The [2025 paper](https://arxiv.org/html/2504.19413v1), §2, describes LLM extraction followed by ADD/UPDATE/DELETE/NOOP selection against similar memories. The graph variant marks obsolete relationships invalid rather than physically removing them. Its evaluation is conversational QA; adversarial unanswerable questions are excluded. Full context has the highest aggregate judge score, while Mem0 offers a latency/context tradeoff. Retrieval-context tokens and search-plus-answer latency do not measure the entire acquisition and maintenance bill. The paper discusses construction separately; do not call all construction cost absent. Its conclusions defer procedural reasoning to future work. **High confidence in this scope distinction; no reproduced result.**

Current official [how-it-works documentation](https://raw.githubusercontent.com/mem0ai/mem0/main/docs/core-concepts/how-it-works.mdx) describes **additive automatic extraction**, with explicit application calls to update/delete for correction. It also places prompt insertion with the application. Managed storage removes infrastructure operation; it does not by itself establish host capture or correct application. The page distinguishes Platform graph/temporal retrieval from the OSS path. This is a current documentation reading, not a deployed trace or a demonstrated mapping to the paper version.

**Decision implication, medium confidence:** paying a provider can buy useful operations, but specify which operations and version. Corvid's managed-service argument is strongest for supplied infrastructure and retrieval. Automatic correction and cross-host delivery cannot be inferred from the historical paper plus a shared endpoint. Kiln's documentation distinction is substantive; additive retention alone does not prove stale answers—retrieval and executive reasoning may reconcile the records.

The source discrepancy is now identified, so this is a bounded, justified roster reconsideration rather than another run of the old adapter. Whether current documentation and implementation agree, and what reaches each host, remain open. No installation, probe or new experiment queue. Cairn's independent paper reading is still in progress.
