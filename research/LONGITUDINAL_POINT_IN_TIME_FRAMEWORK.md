# Longitudinal point-in-time framework

Round 1 exposed a gap in final-state-only retrieval evaluation: a current
answer can look relevant while erasing a valid configuration-specific fact,
adopting a failed procedure, or leaking a correction that had not yet been
learned. This framework is a harness-owned, engine-independent ruler for the
next round. It contains no private transcript text and runs no memory engine.

## Time and truth model

Each observation carries a canonical ID, public assertion, event time,
effective time, reference time, ingestion order/time, scope/configuration,
transition label, and provenance. Event/effective time says when a fact applied;
ingestion time says when the evaluated system could know it. A replay
checkpoint admits only the ingestion-order prefix, preventing chronological
leakage.

The fixture distinguishes ADD, CONFIG_CHANGE, SUPERSEDE_CURRENT, CORRECTION,
FAILED_ATTEMPT, SUCCESSFUL_ATTEMPT, CONCURRENT_SCOPE, RETRACTION, and
INVALIDATION. It has three compact public storylines:

- Nimbus throughput on Forge/Anvil and C1/C2: C1=21 is later corrected to 24,
  while Forge/C2=29 and Anvil/C2=33 remain concurrent scoped facts.
- Aurora branch evolution, including a late-arriving Feb 5 CI record learned
  after the Feb 10 branch change.
- A failed Forge/C2 reproduction followed by a successful warmup/fixed-batch
  procedure.

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
adoption, late-history corruption, and unknown hallucination. There may be a
summary later, but no scalar replaces these named failure modes.

For the eventual private corpus, transcript/session order and available
evaluated-system identity (model, quantization, inference server/runtime,
flags, hardware, project/repo) must be recovered without guessing. Missing
metadata remains unknown. Raw transcripts, secrets, identifiers, and
proprietary source stay out of Git and the control-plane Drive folder.
