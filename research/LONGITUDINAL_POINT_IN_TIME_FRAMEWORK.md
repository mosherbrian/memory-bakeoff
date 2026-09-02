# Longitudinal point-in-time framework — frozen v1

Round 1 exposed a gap in final-state-only retrieval evaluation: a current
answer can look relevant while erasing a valid configuration-specific fact,
adopting a failed procedure, or leaking a correction that had not yet been
learned. This framework is a harness-owned, engine-independent ruler for the
next round. It contains no private transcript text and runs no memory engine.
Generation 23 freezes this ruler as `longitudinal-v1`; its canonical fixture
and scorer/contract fingerprints are published in
`research/LONGITUDINAL_V1_FIXTURE.json` and
`research/LONGITUDINAL_V1_MANIFEST.json`.

## Time and truth model

Each observation carries a canonical ID, public assertion, source/event time,
effective (world-valid) time, ingestion order/time, scope/configuration, and
provenance. Event/effective time says when a fact applied; ingestion time says
when the evaluated system could know it. There is no decorative reference-time
field in v1. A replay
checkpoint admits only the ingestion-order prefix, preventing chronological
leakage.

The fixture distinguishes ADD, CONFIG_SELECTION, SUPERSEDE_CURRENT, CORRECTION,
FAILED_ATTEMPT, SUCCESSFUL_ATTEMPT, CONCURRENT_SCOPE, RETRACTION, and
INVALIDATION. It has three compact public storylines:

- Nimbus throughput on Forge/Anvil and C1/C2: C1=21 is later corrected to 24;
  Forge selecting C2 is a separate active-configuration transition, while
  Forge/C2=29 and Anvil/C2=33 remain concurrent scoped measurements.
- Aurora branch evolution, including a late-arriving Feb 5 CI record learned
  after the Feb 10 branch change.
- A failed Forge/C2 reproduction followed by a successful warmup/fixed-batch
  procedure, plus Aurora generated-client invalidation and retraction facts.

`AS_OF` asks world truth at the supplied effective/event coordinate using only
evidence ingested by its checkpoint. Thus Forge/C1 on Jan 10 returns 21 at
CP04 and 24 at CP05: same world coordinate, different transaction-time
knowledge. `HISTORICAL_BELIEF` instead asks what was recorded then (21 even
when evaluated after CP05), while `CORRECTED_HISTORY` asks what later verified
evidence establishes (24). They are deliberately not aliases.

At every checkpoint the oracle supports current/configuration truth, as-of
event truth, historical belief, corrected historical truth, recommended
procedure, negative/unknown, and late-history queries. Historical belief means
what was reasonably recorded then; corrected historical truth means what later
evidence now establishes about that earlier event. They must not be collapsed.

## Scoring

The reference oracle in `memory_bakeoff.longitudinal` is fixture/test
infrastructure only, never a contestant. Its unit tests validate chronology
and targets. Adapter results should be scored separately for future leakage,
stale persistence, false persistence, history erasure, scope collapse, false
supersession, correction failure, belief/truth confusion, failed-procedure
adoption, missing procedure recommendation, late-history corruption, unmapped
provenance, and unsupported retrieval evidence. `unknown_hallucination` is
reader-only: non-empty raw retrieval for a negative query is not a hallucinated
answer.

Lifecycle state is a separate adapter surface. It records only native evidence
an adapter can establish: active/current, historically recoverable, a
retired/superseded/corrected/retracted/invalidated/deleted/unknown disposition,
and evidence strength. Active-state absence never implies destructive deletion.
A concurrent Forge/C2 and Anvil/C2 state sentinel makes false supersession
detectable without relying on retrieval output.

The future result contract includes fixture and scorer hashes, system identity,
repetition, checkpoint and ingested-prefix hash, case ID, requested cutoff,
native rank/order, exact provenance mapping, native scope/temporal operations,
optional reader answer, lifecycle evidence, and named failures. The harness
never post-filters wrong-scope or stale returns before scoring. Adapters receive
only public observations and chronological/scope metadata; expected IDs,
prohibited IDs, truth keys, transition/lineage labels, and answer targets stay
harness-private.

Once a product is evaluated against v1, the fixture, query set, truth labels,
and scorer semantics cannot change. Any repair requires v2; prior v1 results
remain historical evidence.

For the eventual private corpus, transcript/session order and available
evaluated-system identity (model, quantization, inference server/runtime,
flags, hardware, project/repo) must be recovered without guessing. Missing
metadata remains unknown. Raw transcripts, secrets, identifiers, and
proprietary source stay out of Git and the control-plane Drive folder.
