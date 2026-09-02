# Graphiti Generation 20 structured-episode gates

Status: **blocked at the required second structured-ingestion gate; no score**.

This is a separately labeled Graphiti configured-product profile.  It uses
Graphiti OSS v0.29.3, the frozen Gen19 general entity/relation schema,
`EpisodeType.json`, LAN `qwen3.6-35b-vulkan-nothink` through the local
OpenAI-compatible endpoint, local Ollama `nomic-embed-text` (768-D), and
embedded FalkorDB Lite.  It is not a default Graphiti result.

## M035 first gate: passed

The representation-preserving JSON envelope for canonical M035 contained only
its copied canonical ID, assertion text, reference time, scope, and a constant
source kind.  Graphiti's native JSON extraction produced `frontend preview
environment`, `Redis`, `M035`, and `repo:demo`, then created this native edge:

> The frontend preview environment uses Redis database number 2.

The edge has native episode provenance `e3cd4509-978d-4027-a7b3-383c6d039426`.
The exact serialized body, native episode, nodes, edge, episodic edges, and
recorded native extraction responses are in
`results/graphiti_gen20_json_m035_gate/trace.json`.

The earlier Gen18/19 diagnostic called a synthetic alpha-branch sentence
"M035".  Canonical M035 is the preview-Redis record above; this Gen20 evidence
does not relabel the old synthetic diagnostic as corpus evidence.

## Second gate: failed, with exact provenance

The fixed second gate sequentially ingested canonical M011/M012, M013/M014,
M035/M036, and M023/M024, all with the same envelope and schema.  Each body
kept its original `repo:demo` scope.  Graphiti restricts native group IDs to
alphanumerics, dashes, and underscores, so the profile uses the documented
reversible group ID `scope_cmVwbzpkZW1v`; it is not an inferred scope or a
harness filter.

Some supported behavior worked:

- M011 produced a coordinator fact and M012 invalidated that older fact at the
  new reference time.
- M013 produced the old deployment command fact and M014 invalidated it.
- M035 again produced the correct preview-Redis fact with native episode
  provenance.
- M023 produced three procedure-sequence facts.

But the complete gate fails its no-repair semantic/lifecycle condition:

- M036 (development Redis DB 3) produced a development-specific fact but also
  invalidated M035's distinct frontend-preview Redis fact at M036's timestamp.
  These are coexisting environment-specific assertions, not a correction.
- M024 (the failed direct-edit generated-code procedure) produced no native
  fact edge at all.
- The M012 current-coordinator episode produced `REPLACES` and `INVALIDATES`
  relations, but no stable direct current-coordinator fact for `strix07`; its
  `REPLACES` edge was itself emitted with `invalid_at` equal to the update
  time.  This is additional cautionary evidence, not a successful temporal
  result.

The full per-episode native nodes, edges, invalidation timestamps, episode
UUIDs, episodic links, and recorded LLM responses are in
`results/graphiti_gen20_json_gate2/trace.json`.  No facts were repaired,
filtered, or supplied as triples.

## Stop decision

Because the fixed second gate has a false cross-environment invalidation and a
missing failed-procedure edge, Generation 20 must not continue to lifecycle
sentinels, point-in-time queries, or any 50/500 retrieval/reader score.  A
future evaluation would need explicit authorization for a new profile; it must
not retune this frozen envelope/schema/model from these observations.
