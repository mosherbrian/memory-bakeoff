# Contrarian, cycle 12 — make (B) the default, keep (A) as the source of truth

**corvid · 2026-09-26 · cycle 12.** Signed opinion, not an audit. ROLES.md: *“argue the
strongest case AGAINST the current position memo, and for the best rival idea.”* Sources already
read: Letta blocks/MemFS, sleep-time compute (2504.13171), R68, GateMem (2606.18829), Ground
Truth First (2607.21962), ReasoningBank (2509.25140), SEAL (2506.10943). `[read]`

**Strongest rival to Tern’s (A)-shaped start: (B) automatic integrated memory + executive
reasoning**, with (A) retained underneath as canonical source. (C) is not the practical rival:
learned policy needs a strong curator, finetuning infra and one model, has no provenance, and
forgets across edits (SEAL §5) — a compiler for stable procedures, not a default. `[read]`

**Why (B) wins on Brian’s two costs.** The memo’s bets still make Brian the author/curator of the
canonical record (“one authoritative source with host-specific views”) and reserve agent upkeep
for revision. But the scarce, *uncounted* resource in every piece we read is **Brian’s
attention**, not storage or tokens. (B) moves capture and upkeep agent-side: Letta commits every
memory-block edit to git (provenance for free), shared blocks update once and propagate across
agents, and sleep-time consolidation runs offline — reported same accuracy with **~5× less
test-time compute** and up to **+13–18%** accuracy, with **query predictability** as the
moderator. Repeated, predictable work is exactly where Brian pays re-learning and re-stating
costs, so that is where (B) wins. R68 already showed cheap automatic index delivery produced
correct runs 2/2. `[read]`

**What is evidence vs my assumption.**
- *Evidence:* versioned agent-side blocks and async consolidation exist and are cheap relative to
  full context; sleep-time gains are measured on synthetic tasks; R68 index delivery worked.
- *My assumption:* Brian’s maintenance time is the binding cost and is large enough to justify
  agent-side capture; his work is mostly repeated/predictable and few-principal; the integrated
  runtime preserves lossless history rather than curating into a budgeted map.
- *Explicitly not claimed:* that (B) supplies authority, governance, or a preference policy.

**What would reverse my choice.**
1. **Governance becomes binding** — GateMem: if memory is genuinely multi-principal, access and
   forgetting are orthogonal to provenance and vanish in integrated stores. `[read]`
2. **Tenure + budgeted curation** — Ground Truth First: the curated-map leader lost evicted
   content by 9 weeks (96%→72%) while a provenance-typed graph rose to 90%. If (B) evicts,
   (B) loses. `[read]`
3. **Curator cost/quality** — if consolidation must call a frontier model (ReasoningBank’s
   curator; SEAL’s 30–45 s/self-edit), the attention saved stops being cheap.
4. **Precision drop** — sleep-time’s own SWE case study edited more files at slightly lower
   precision; a measured rise in stale-procedure adoption would demote (B).

**Verdict.** Adopt **(B) as the default capture/upkeep mechanism, with (A) as the editable
canonical source and correction path**, and (C) only as a compiled cache for a dedicated local
model. The memo’s arrangement is not wrong; it under-assigns capture to the agent and over-assigns
it to Brian. **Medium confidence**, conditional on the four reversals above.

— corvid. `[read]` sources fetched 2026-09-26; assumptions and reversals stated. No experiment.
