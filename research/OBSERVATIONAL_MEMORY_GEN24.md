# pi-observational-memory Gen24

## Status

`blocked_native_quiescence_after_calibration`. No longitudinal-v1 observation
was exposed to the product, so no v1 contestant result, retrieval score,
lifecycle score, context-exposure diagnostic, or reader lane is published.

## Identity and frozen boundary

- pi-observational-memory 3.0.4, source `ce9fc982b3a219a7839f07c9f4a3e054e81a2b21`
- Pi 0.81.0 from the pinned package dependency
- LAN OpenAI-v1 endpoint `http://strix-halo.local:8080/v1`
- worker/session model `qwen3.6-35b-vulkan-nothink`, advertised by `/v1/models`;
  thinking off; server/runtime details otherwise unknown
- frozen v1 fixture/scorer hashes verified unchanged:
  `a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd` /
  `1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34`

## Native semantics audit

`src/index.ts` registers Pi `turn_end` consolidation, `agent_settled`
auto-compaction, `session_before_compact` rendering, commands, and `recall`.
The V3 ledger types are observations, reflections, and drop tombstones
(`src/session-ledger/types.ts`); `foldLedger` keeps first valid records and
removes tombstoned observations only from `activeObservations`
(`src/session-ledger/fold.ts`). The compaction hook renders the native
projection without an LLM (`src/hooks/compaction-hook.ts`). `recall` accepts
only a known 12-hex memory ID and explicitly forbids semantic search
(`src/tools/recall-observation.ts:438-482`). It traverses source provenance;
dropped observations remain recallable.

Consequently OM offers a lifecycle/context product surface, not a native
query-time semantic retrieval surface. `activeObservations` is pool membership,
not factual current truth. A drop tombstone is not supersession, invalidation,
or destructive deletion. Ledger/recall provenance can establish historical
recoverability, but current factual disposition remains unknown without more
native semantics.

## Calibration and stop

A clean non-v1 garden-journal Pi session used frozen synthetic-scale settings:
observe 256 tokens, reflect 512, observer chunk 1024, pool max/target 1024/512,
worker turns 4, normal dropper policy, debug enabled. The product's native
debug trace recorded `observer.start` and `observer.records` with four records,
then `observer.error`: “This extension ctx is stale after session replacement
or reload.” This occurred after the observer write in the same run.

The trace demonstrates hook/worker activation but not deterministic completion
or trustworthy quiescence. Under Gen24's stop condition, continuing into v1
would race a possibly half-written ledger and require a product-source fix or
semantic workaround. Neither is authorized. Raw query retrieval is also
`not_applicable_native_surface`: exact-ID recall cannot consume a held-out
natural-language v1 query without leaking an ID.

## Future Pi MemoryProvider seam (design only)

Generic Pi plumbing appears to be lifecycle hooks, source addressing, compaction
injection, tool/context registration, and instrumentation. OM-specific policy
is observer/reflector/dropper plus V3 ledger/fold/projection. A minimal future
shell would expose append source, wait/quiesce, render compaction context,
exact provenance traversal, and native-state snapshot. It must preserve three
non-equivalent profiles: OM policy plus ledger; OM policy plus alternate store;
and generic Pi shell with a backend owning ingest/query/lifecycle. Hazards are
raw-session leakage, treating context order as retrieval rank, and mapping pool
membership to factual truth.
