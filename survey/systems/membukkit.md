# System card: Membukkit (bucket-routed memory with explicit supersession)

**kiln · 2026-09-26 · ~500w · advice only, no installs. Sources: read-only inspection of `implementer/repo/vendor/membukkit/src/membukkit/` (pipeline.py, retrieval/router.py, retrieval/buckets.py, supersession.py) + research/MEMBUKKIT_SCAN_FRACTION_AUDIT.md + Phase-2 roster. Identity caveat: AGENTS.md pins the vendor copy to upstream `f28a2e58`; the checkout I read sits inside the bake-off git tree and I did not independently verify blob SHAs — identity taken on the project's word, not re-proven.**

## What it adds over native files

Three mechanisms native files lack: (1) **bucket-gated retrieval** — facts assigned to KMeans topic buckets at index time, queries routed by centroid cosine, whole buckets opened to a budget fraction, then cross-encoder rerank + RRF fusion; (2) **query-type router** — rule-based classification (temporal / knowledge_update / aggregation / general) selecting temporal vs plain evidence organization, on the documented finding that fixed date-sorting is neutral-to-harmful outside temporal queries; (3) **explicit supersession links** — a newer highly-similar fact marks the older superseded with `valid_to`, and `fact_status()` resolves current-vs-historical **as-of** a query time. Turn-level provenance (`[Tn]` backpointers, degrading to session granularity) is built in. That third item is the distinct lifecycle mechanism this roster lead was chosen for — and notably, it stores the validity interval our native side and pi-lcm both lack.

## Concrete update/read path (from source)

- **Update:** `MemorySystem.from_pretrained(...)` → `ingest(sessions, dates)` → distiller emits atomic facts with turn refs → `supersession` links arrivals to highly-similar older facts (no silent DELETE; in-memory backend shares the Turbopuffer `supersede` contract). Mutable-state regex is a soft boost, not the decision rule.
- **Read:** `answer(question, question_date)` → router picks organization → bucket routing gathers candidates → cross-encoder rerank → fused top-k with provenance refs.

## What could fail (mechanism-specific)

- **Buckets are topical, not stateful:** a renamed-scope neighbor lands in the same KMeans cluster as the original — the S11-3 disease shape applies here too. Our controlled result (routing ≈ dense scan on stress) plus the **retracted** ~32.9% scan-fraction figure (audit) means the efficiency claim is currently unmeasured, and the scope-separation question (roster's reason for the revisit) is unanswered.
- **Router brittleness:** cue-phrase lists ("currently", "still", "no longer") decide organization; paraphrase outside the list misroutes silently.
- **Model dependence:** the whole path assumes the intended pretrained encoder/reranker/distiller (Gen40/41 provenance gaps); with substitute models it is a different system wearing the name — the repo's own `FallbackDetected` discipline exists for exactly this.
- **Supersession threshold risk:** "highly similar newer fact" is nearest-neighbor retirement by another name — agentmemory's 418/450 false-supersession lesson applies until a lifecycle gate says otherwise.

## Cost / fit

Install: model weights (encoder + reranker + distiller LLM, local or service), sklearn, optional Turbopuffer backend — heavier than files, lighter than a SaaS graph. Maintenance: model pins, bucket-count tuning, supersession-threshold calibration. Fit: retrieval-layer candidate for Pi/local shared history; irrelevant to Claude Code preference storage.

## Gap deepened: the distiller is an LLM call (same source)

The most consequential gap was *who* writes the atomic facts and provenance the card praises: `pipeline.py` shows `FactDistiller(llm_fn, prompts)` with default `llm="openai:gpt-4o-mini"` — every fact, turn-pointer, and supersession candidate originates in a vendor LLM extraction pass. So the "explicit lifecycle" is LLM-proposed structure, and the false-supersession risk is sharper than the card first framed: a mis-distilled fact poisons storage, buckets, and supersession links alike, with the `[Tn]` backpointer as the only audit trail. This confirms the model-dependence failure mode as the load-bearing one — any Phase-D admission must pin the distiller model identically to encoder/reranker, and a local-model fit question follows: who pays the distiller bill on Brian's box (local 35B vs API) is unanswered. Verdict unchanged (watch), confidence in the *mechanism description* high, in any *deployment* still low.

## Advice: **watch, medium-low confidence**

The as-of supersession + provenance design is the best lifecycle-shaped mechanism on the roster, but it must pass the idle Phase-D gate with intended models and answer the scope-separation question before any deployment talk. Next retest is named and narrow: near-neighbor scope families through bucket routing, false-supersession counted.
