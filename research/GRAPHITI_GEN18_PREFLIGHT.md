# Graphiti OSS Generation 18 preflight

Status: **blocked, no score published** (2026-09-01).

Superseded as the current Generation 18 summary by
`GRAPHITI_GEN18_LAN_FOLLOWUP.md`: stronger LAN models made native temporal
edges/provenance work, but exposed a default generic-entity modeling limit.

Graphiti OSS v0.29.3 was verified from `getzep/graphiti` tag commit
`021d3a57d511f21b10adaf7fa923bd5c1fce5e9d`. The local environment installed
`graphiti-core[falkordblite]==0.29.3`; its bundled embedded backend is FalkorDB
Lite 0.10.0 / FalkorDB 4.18.3. A direct Graphiti driver smoke test built its
indices successfully on this Mac.

The source's documented local configuration was used: `OpenAIGenericClient`
against Ollama's OpenAI-compatible `/v1` endpoint, `qwen2.5:3b` for LLM and
OpenAI-style cross-encoder reranking, and `nomic-embed-text` (768 dimensions)
for embeddings. A direct Graphiti-client structured-output probe returned the
correct JSON and the native embedder returned 768 dimensions.

The first real six-episode temporal/provenance sentinel then failed during
Graphiti ingestion of the M011/M012 lifecycle pair. Upstream emitted:

```
Target entity not found in nodes for edge relation: IS_BUILD_COORDINATOR_OF
```

This is a model-backed graph extraction/resolution failure. It occurred before
the append-only evidence file and before any retrieval; therefore no
provenance linkage, temporal/lifecycle claim, reader run, or benchmark score
exists. The partial local FalkorDB settings file is retained under
`results/graphiti_gen18_sentinel/` as an incomplete diagnostic, not a result.

Graphiti's own documentation cautions that small local models frequently fail
its required structured extraction. Its documented illustrative local model is
DeepSeek-R1 7B. That configuration cannot yet be called reproducible on this
8 GB M1 alongside the graph runtime. The faithful next step is a capable local
model with reliable schema-constrained output on a larger host, or an explicit
user-authorized test of a 7B model after confirming memory headroom. No fake
extractor, LSA replacement, hand-authored edges, or paid API was used.
