# Graphiti Generation 19 configured-schema preflight

Status: **blocked before lifecycle/point-in-time sentinels; no score**.

The frozen general configured-product schema in
`memory_bakeoff.graphiti_gen19_schema` was exercised through Graphiti v0.29.3's
supported `entity_types`, `edge_types`, `edge_type_map`, and
`custom_extraction_instructions` parameters. The real extraction stack was the
Gen18 LAN composite: `qwen3.6-35b-vulkan-nothink` through the local
OpenAI-compatible endpoint, Ollama `nomic-embed-text` (768-D), and embedded
FalkorDB Lite 4.18.3.

The publication-safe focused assertion was:

> The alpha release branch is release/alpha.

Despite the schema offering both `Configuration` and `ArtifactResource`, native
node extraction returned only `release/alpha` (`ArtifactResource`), and native
edge extraction returned `[]`. The model did not identify the `alpha` release
channel as a second entity. The complete native responses are preserved in
`results/graphiti_gen19_schema_trace/trace.json`.

This proves that merely supplying broad supported types and relations does not
make Graphiti extract an implicit/abstract subject from this sentence. It is
not a harness provenance problem, edge-name validation failure, or
post-processing omission.

Generation 19 therefore stops before the required lifecycle and point-in-time
sentinels. Running them would violate the explicit precondition that schema
extraction work without repair. The next decision is whether a genuinely
general, non-benchmark-shaped Graphiti ingestion representation exists for
single-entity assertions (for example a supported structured episode profile),
and whether evaluating that representation is in scope. Hand-authored
triples/edges and harness conversion remain prohibited.
