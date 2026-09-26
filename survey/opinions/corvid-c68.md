# Contrarian, cycle 68 — STALE says invalidation is its own step

**corvid · 2026-09-26 · cycle 68.** Signed opinion; ROLES.md “best rival idea.” Source read:
STALE, Chao et al., **arXiv:2605.06527v1** (7 May 2026). `[read]` Confidence **medium**.

**Strongest case it changes our advice.** My c61 default — resolve currency at read time — assumed
the revision is *recognised*. STALE isolates **implicit conflict**: a later observation invalidates
an earlier memory **without explicit negation**, and probes **State Resolution** (detecting the
prior belief is outdated), **Premise Resistance** (rejecting queries that presuppose stale state),
and **Implicit Policy Adaptation** (proactively applying the update). Best model **55.2%**, with a
reported gap between **retrieving updated evidence and acting on it**. So the recurrent failure is
**invalidation detection**, not retrieval — and read-time relevance alone won’t catch a conflict
that carries no cue. The action that changes: add an explicit **state-adjudication** step (keep /
archive-stale / replace / unresolved) for a scoped fact or direction, instead of assuming the
newest or most relevant item is current.

**What is supplied vs inferred.** STALE supplies scenarios/labels and a **prototype (CUPMem)** that
strengthens write-time revision via structured state consolidation and propagation-aware search —
a benchmark + prototype, **not a deployable facility**, and the 55.2% headline is not architecture
proof. It tests user-assistant dialogue, not tool execution; transfer to Brian’s CLI work is
unestablished.

**Reversal.** If the measured failures are mostly retrieval/reading rather than invalidation
detection, or Brian’s facts arrive with explicit corrections, the extra adjudication step is
unnecessary.

— corvid. No experiment.
