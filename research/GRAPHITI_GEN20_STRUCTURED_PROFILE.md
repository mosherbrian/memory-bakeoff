# Graphiti Gen20 structured-episode profile

Status: frozen and exercised in Generation 20; the required second gate failed,
so this remains a separately labeled configured-product ingestion profile, not
a default Graphiti result or a score.

## Purpose

Graphiti v0.29.3 supports `EpisodeType.json` and selects its native JSON entity
extraction prompt for that source.  This profile tests whether that supported,
structured representation preserves enough of a short coding assertion for
Graphiti itself to extract, resolve, and link a native fact edge to its native
episode provenance.  It does not provide Graphiti with a fact triple.

## Frozen envelope rule

For every canonical `MemoryRecord`,
`memory_bakeoff.graphiti_gen20_envelope.build_episode_envelope` copies exactly:

- `canonical_record_id` from `record.id`
- `assertion_text` from `record.text`
- `reference_time` from `record.timestamp.isoformat()` 
- `scope` from `record.scope`
- `source_kind`, the profile-wide constant `benchmark_memory_record`

It serializes those fields as compact, sorted-key JSON and passes the result to
Graphiti as `EpisodeType.json`.  The profile uses the frozen Gen19 general
entity/relation schema unchanged.

For multi-record diagnostics, Graphiti's native `group_id` is mechanically
`scope_` plus unpadded URL-safe base64 of `record.scope`.  Graphiti only accepts
ASCII alphanumerics, dashes, and underscores in this identifier, whereas the
canonical `repo:demo` scope contains a colon.  The original scope remains
verbatim in the envelope.  This is an ingestion partition, not an envelope
field or a harness retrieval filter; it puts corrections and competing facts
from the same canonical scope in the same Graphiti graph without inventing a
project label from their text.

The envelope contains no inferred subject or object labels, entity types,
relations, fact triples, truth status, correction/supersession links, expected
query terms, or any answer-specific information.  Graphiti remains responsible
for native extraction, entity resolution, edge construction, provenance,
invalidation, and retrieval.

`envelope_config()` publishes the exact field list, mechanical rule, forbidden
field list, and SHA-256 configuration fingerprint into the native trace.

## Gate input correction

The previous diagnostic script called its synthetic alpha-branch sentence
"M035", but the canonical corpus's M035 is instead:

> The frontend preview environment uses Redis database number 2.

The Generation 20 gate uses the canonical M035 record above.  This correction
does not reinterpret or overwrite Gen18/19 evidence; it prevents a synthetic
sentence from being reported as a canonical corpus gate.

## Stop condition

This first gate has one fixed input, JSON shape, model stack, and frozen Gen19
schema.  If Graphiti does not produce a semantically correct native fact edge
that is traceable to the native episode for M035, Generation 20 stops without
trying alternate shapes, prompts, schemas, models, hand-authored triples, or a
benchmark score.
