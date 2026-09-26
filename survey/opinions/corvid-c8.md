# Contrarian, cycle 8 — memory governance is a separate mechanism, and a multiplicative one

**corvid · 2026-09-26 · cycle 8.** Signed opinion, not an audit. ROLES.md: *“the best rival
idea.”* Chosen operation-level benchmark: **GateMem** (Ren et al.,
[arXiv:2606.18829](https://arxiv.org/abs/2606.18829)), read at methods level (§3–4.3).
Complementary to Tern’s central HaluMem reading: HaluMem is single-user reliability; GateMem is
**multi-principal shared memory governance**. `[read]`

**Which attractive survey claim GateMem exposes as misleading.** Two:
1. **“Better memory / more recoverable history is the safe default.”** GateMem scores
   `MGS = U·(1−A)·(1−F)` — utility multiplied by access-control safety and forgetting safety.
   Full-history Long-Context has the **highest utility and usually the best MGS, yet still
   leaks 20%+** in access-control or post-deletion recovery on several backbone/domain blocks.
   More retained context is more *exposure*. That directly stresses Brian’s corollary: “don’t
   delete the past” is right for reconstructability and wrong as a retrieval policy in a shared
   setting. Retention must be paired with a boundary mechanism, not assumed safe.
2. **“Explicit memory systems supply governance.”** A-Mem, Mem0 and ReMem introduce structure
   but **do not consistently beat simpler baselines on MGS**; policy-aware RAG trades utility
   for safety and **over-refuses legitimate requests**. Governance does not emerge from memory
   organisation. `[read]`

**What it actually tests.** Incremental ingestion of natural-language turns; hidden
checkpoints at turn boundaries with requester identity + policy context; four normalized
actions (`answer`, `answer_redacted`, `refuse`, `no_memory`); requester roles/scopes/relations;
**interface-level** forgetting (non-recovery/confirmation/reconstruction after a deletion
request), explicitly *not* physical erasure. Access failures are driven by **soft overreach**
(indirect inference, delegated authority, label-existence probing), not blunt unauthorized
queries; forgetting failures come from **yes/no confirmation and split reconstruction**. This
is a governance test, not a recall test.

**What it misses for Brian’s two priorities.** *Procedures:* no checkpoint category for
applicability, prerequisites, or failed-alternative retention — GateMem cannot tell whether a
runbook helps or hurts, only whether facts are disclosed/withheld/deleted. *Preferences:*
single-user preference revision is out of scope (the positioning table puts PrefEval/
PersonaMem in private memory), and GateMem treats information as access-controlled facts, not
as **authorized directions with supersession**. It also hands the agent structured policy
context at evaluation, so it does not test inferring scope from prose or keeping authority
current. Deletion here is non-recovery, not provenance-aware supersession. `[read]`

**Strongest challenge to the current memo.** My c5–c6 push was “one integrated runtime +
minimal policy.” GateMem says the *policy that survives* is a distinct, separately-scored
mechanism, and its failure modes are behavioural (over-refusal, indirect recovery). If Brian’s
multi-agent setup shares memory across roles at all, the memo’s “recoverable history + agent
upkeep” needs an explicit **who-may-see-and-forget** layer, or the first leak makes the whole
store a liability. That is the strongest surviving case for keeping one lifecycle/authority
mechanism separate — not because versioning is absent, but because **access and forgetting are
orthogonal to provenance**.

**Confidence:** high that GateMem’s measurement is sound and the governance gap is real;
medium that it transfers to Brian’s smaller, mostly single-principal workloads; low that MGS’s
multiplicative form is the right score for him (one leak zeroes the product).

## Deepened gap
The unsolved question for Brian is **whether his memory is actually multi-principal**. GateMem’s
result only bites if features, agents, or roles share a pool. If Brian’s use is single-principal,
the governance layer is pure overhead; if it is multi-agent with shared blocks (as Letta-style
shared blocks imply), then “who may read/forget” is a hard requirement the survey has not priced.
Decision test: enumerate Brian’s sharing cases before adopting any retention-first design.
Source gap, not a conclusion.

— corvid. `[read]` GateMem arXiv:2606.18829 methods/results fetched 2026-09-26; no reproduction,
no experiment.
