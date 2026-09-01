# Graphiti Generation 18 — LAN-model follow-up and decision request

Status: **diagnostic only; no benchmark score or reader run**.

This follows the initial local-Qwen blocker in `GRAPHITI_GEN18_PREFLIGHT.md`.
It uses Graphiti OSS v0.29.3 (`021d3a57d511f21b10adaf7fa923bd5c1fce5e9d`),
the supported embedded FalkorDB Lite backend (FalkorDB 4.18.3), and the same
native `add_episode`/`search` path. Embeddings remained local Ollama
`nomic-embed-text` (768 dimensions). Every run used native Graphiti episode
UUIDs as the canonical-record linkage; no harness-made edges or triples were
used.

## Runs attempted

| Diagnostic | LLM / reranker | Policy | Outcome |
|---|---|---|---|
| Initial local | Ollama `qwen2.5:3b` | default | One M014 edge; no usable lifecycle sentinel. Earlier ingestion also emitted a target-node mismatch warning. |
| LAN 27B | `qwen3.8-27b-vulkan` at `strix-halo.local:8080/v1` | default | M012: 1 edge; M014: 2; M011/M013/M035/M036: none. Exact M012/M014 episode provenance worked. |
| LAN 35B | `qwen3.6-35b-vulkan-nothink` at the same endpoint | default | M012: 2 edges; M014: 2; M011/M013/M035/M036: none. M012 created a current strix07 edge and an invalidated prior-coordinator edge. |
| LAN 35B configured | same 35B | `custom_extraction_instructions` requiring short coding identifiers, branches, paths, commands, versions, and assignments | Indistinguishable edge coverage from 35B default. |

The full non-score evidence is under `results/graphiti_gen18_sentinel*/`.
The 27B result directory includes exact native edge-to-episode UUIDs. The
35B default and configured directories record the complete composite identity
and the configured instruction text.

## Focused native trace

A one-episode trace of M035, "The alpha release branch is release/alpha.",
isolates the failure without inference:

1. Graphiti's native node extraction returned one entity: `release/alpha`.
2. Its native edge extraction returned an empty edge list.
3. Graphiti therefore stored the episode/entity but had no fact edge to
   retrieve. This is **not** an edge-to-node name mismatch.

See `results/graphiti_gen18_m035_trace/trace.json`. The trace also shows why
the prompt-only configured policy did not help: Graphiti received the custom
instruction, but the model still supplied no edge.

## Important caveat

The default 35B search for the current coordinator returned the explicitly
invalidated strix03 edge alongside the current strix07 edge. This is a useful
harmful-context observation, not a score: current `search()` does not by
itself establish the temporal filtering behavior required for the benchmark.

## Decision needed before a valid benchmark lane

The benchmark's natural-language coding records contain relations whose
subjects are abstract domain concepts (`alpha` release channel, deployment
procedure, repository), while Graphiti's default generic entity policy retains
only concrete standalone entities. A stronger model and prompt instruction did
not bridge that modeling boundary.

The proposed next lane is a separately labeled **configured Graphiti product
profile**, frozen before scoring, with an explicit small coding-memory ontology:

- entity types: `ReleaseChannel`, `Branch`, `Host`, `Repository`, `Command`,
  `FilePath`, `Credential` (with precise, general descriptions);
- typed relations such as `ReleaseChannel HAS_BRANCH Branch` and `Host
  COORDINATES_BUILD Repository`;
- the same schema for every core/stress record and no query/record-specific
  rules.

This would still exercise Graphiti's real extraction, resolution, temporal
invalidation, storage, and retrieval. It must not be presented as Graphiti's
default-policy result. Do **not** substitute hand-authored `fact_triple` input
or harness-generated triples: that would change the evaluated ingestion mode.
