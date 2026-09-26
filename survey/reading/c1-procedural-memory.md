# Reading sweep — procedural memory, with compaction and a preference comparison

**cairn (Reader — local Qwen3.8 Flash-Next on Halogen, free) · 26 September 2026 · cycle 1.**
Signed opinion, not an audit. ROLES.md: *“The one idea in this area that most deserves our
attention.”* Steered by [panel-priority-steering.md](../panel-priority-steering.md): Brian's
Q1 answer is **re-learning procedures first, repeating preferences second**, so this sweep is
about procedures and preferences are treated as a comparison, not the subject.

**Provenance key.** `[read]` = abstract read at the source today (arxiv.org, 2026-09-26).
`[card]` = taken from our own field refresh / intake cards, **not** re-read at source this
cycle. `[ours]` = our measurement. Inference is labelled.

---

## Per source

**1. Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents** —
arXiv:2606.27472, submitted 25 Jun 2026. `[read]`
Replacing an agent's full context with a *bounded, self-maintained memory* drops LongMemEval
knowledge-update accuracy 92% → 77% on a frontier model (paired McNemar p<0.005), and the gap
persists across model scale. Growing the conversation 24× makes it worse (68% → 28%); granting
proportionally more memory recovers nothing (28% → 28%, n=25). The authors' reading: the
bottleneck is **maintenance, not comprehension**, and it scales with conversation length, not
compression ratio. They release an RL environment that rewards answering from the current value
and penalises stale ones; GRPO on Qwen2.5-3B moves held-out supersession accuracy 9.0% → 16.7%,
one run.
**Verdict: solid for the measurement, oversold for the fix** (single run, 3B, +7.7 points).
**Confidence: high** that the measurement transfers to Brian, **low** on the training result.
Why it belongs in a *procedure* sweep: it is the same failure shape as our
`failed_procedure_adoption` — the record is retrievable and the agent still acts on the wrong
one. **Source gap:** our field refresh calls the metric *FAMA* and the project *Memora*; the
abstract names neither, and describes an RL environment. Treat those two labels as unverified.

**2. A-MEM: Agentic Memory for LLM Agents** — arXiv:2502.12110, v1 Feb 2025, v11 Oct 2025. `[read]`
Zettelkasten-style notes with structured attributes, dynamic link creation, and
**“memory evolution”: a new memory can trigger updates to the contextual representations and
attributes of *existing historical* memories.**
**Verdict: solid as a mechanism description; the specific mechanism is our failure class.**
Evolving history in place is `late_history_corruption` by construction, and it violates Brian's
corollary — *“Don't delete the past just because you stop putting it in every prompt.”* The
roadmap wants history lossless and projection derived; A-MEM merges them. **Confidence:
medium.** Practical note: A-MEM is already one of the six harnesses inside MemConflict
(intake row 2), so we would measure it without a new admission.

**3. GateMem: Benchmarking Memory Governance in Multi-Principal Shared-Memory Agents** —
arXiv:2606.18829, 17 Jun 2026. `[read]`
Multi-principal shared memory: utility on long-horizon requests with state updates, access
control across contextual authorization boundaries, and agent-facing active forgetting after
explicit deletion. Headline: **no method achieves utility, access control and reliable
forgetting at once**; long-context prompting often scores best on governance at high token
cost, and retrieval/external-memory methods still leak unauthorized or deleted content.
**Verdict: solid, and the second independent external instance of the long-context null** (the
first is EvoMemBench, `[card]`). It is also the only source here that touches *concurrent
scoped truth* as a measured property rather than a design claim. **Confidence: high** as
reported; we have not reproduced.

**4. Zep: A Temporal Knowledge Graph Architecture for Agent Memory** — arXiv:2501.13956,
20 Jan 2025. `[read]`
Graphiti, a temporally-aware KG engine, synthesises conversation and business data while
maintaining historical relationships; DMR 94.8% vs MemGPT's 93.4%; up to +18.5% on LongMemEval
with 90% lower latency than the baseline implementation.
**Verdict: oversold for our question.** The headline DMR margin is 1.4 points over a system it
also inspired the benchmark of, and the LongMemEval gain is reported against a *retrieval
baseline*, not against full context. Our own runs make it worse: Graphiti v0.29.3 blocked
before the lifecycle and point-in-time sentinels — Gen19 native extraction produced no fact
edge for a single-entity assertion, Gen20's structured-episode profile failed its second gate —
so the temporal-invalidation machinery that is the reason to care was never exercised here.
`[ours]` **Confidence: medium-high** that the paper is sound on its own tasks, **low** that it
transfers to our ingestion shape.

**5. Voyager (arXiv:2305.16291) and Reflexion (arXiv:2303.11366)** — the origin pair for
“procedures as memory”. `[card]` — **not re-read at source this cycle.**
Voyager stores procedures as *executable code in a skill library*, retrieved by embedding of
the task description; Reflexion stores verbal self-critique in an episodic buffer replayed in
the prompt. **Verdict: solid as the origin of the direction, irrelevant as evidence for Brian** —
Crafter and programming-puzzle domains, and neither reports a coding-admin workload. Note the
asymmetry that matters below: Voyager's skill is *artifact-grounded* (the program either runs or
it does not), Reflexion's lesson is a *remembered claim* with no check. **Confidence: low.**

**6. AgentRunbook-C and LongMemEval-V2** — `[card]` (our intake and field refresh; **not** read
at source this cycle, and AgentRunbook-C was deferred without a source read).
Reported: AgentRunbook-C augments a coding-agent harness with workflow documents and query-time
artifacts, 72.5% accuracy and 32% faster than Codex. LongMemEval-V2 (451 questions, 1,870
trajectories) makes *workflow knowledge* and *environment gotchas* first-class abilities.
**Verdict: the most relevant items in this sweep, and the least verified by us.** They are the
only two that measure procedure reuse in a coding agent, which is Brian's stated top cost.
**Confidence: low-medium until read from source** — I would not quote the 72.5% in the memo
without a source read.

**7. Compaction, as the foil.** `[ours]` The compaction literature and our own Gen45 pilot say
the same thing from opposite ends. Gen45: arm B's per-request context was flat (2.6× growth over
337 requests vs arm A's 209× over six) and it still lost 7/12 to 12/12 while using *more* total
bytes — bounding the view did not bound the work. Across all twelve arm-B runs: **6 state
patches accepted, 0 transitions, 0 completions gated.** `[card]` SKILL.state-style designs
(~16× shrink by replacing history with a state object) are an unverified literature lead per
the steering note; their named failure mode, *delayed relevance*, is the same object.

---

## The one idea in this area that most deserves our attention

**A procedure is an artifact whose applicability has to be re-established at the moment of use —
not a fact the agent remembers having succeeded with.**

Brian's five-part principle already contains this: *artifacts establish what is true* and
*executive reasoning decides what it means*. The design consequence is narrower than “build a
skill library”: store a procedure as **(executable/checkable artifact + the verifier that passed
+ the environment identity at pass time)**, and make the agent's step at use time a cheap
**re-check of the precondition against the current artifact** — does this script still run, does
this verifier still exist, is the config still the one it passed under — rather than a recall of
“we did this before.” A past successful trace is evidence, not a presently applicable procedure.

Why this is the one, from our own evidence rather than the literature:

- It is the only candidate mechanism that addresses a failure we have **measured**.
  `failed_procedure_adoption` recurs at identical counts across three engines `[ours]`; R53
  showed relevant notes being read with **no outcome advantage** `[ours]`; Gen45's model ignored
  a control layer it was given `[ours]`. Three different setups, one shape: the material is
  present and application fails. Supersede's independent external version — maintenance, not
  comprehension — is the same claim on other data. `[read]`
- It separates the four things Brian refuses to merge. Memory holds the learned procedure;
  state holds the one selected now; history keeps every prior attempt **including the ones that
  failed, with their outcomes** (Brian's corollary — the failed alternatives are what stop the
  agent re-deriving a dead end); the artifact decides whether it is still true today.
- It is cheap and it is checkable on Brian's stack: a re-check is a command exit code, not a
  model judgement, and it costs nothing when it passes.
- It tells us which literature to actually read next: **AgentRunbook-C at source** (procedure
  reuse in a coding agent, artifact-grounded), and HaluMem's *updating* stage decomposition,
  which is the external version of “which stage failed”.

**What would change my mind:** if AgentRunbook-C's gain turns out to come from longer prompts
rather than from the runbook (the long-context null has now bitten us twice externally —
EvoMemBench, GateMem — and once internally, in Gen45's arm A winning on verbatim replay).

**Preferences, briefly, since they rank second.** The one supported statement I have is
Supersede's 92%→77%: a *self-maintained, rewritten* store loses currency even on a frontier
model. `[read]` Inference: for preferences the safe shape is append-with-source-and-date plus a
currency check at read, not a rewritten profile — the same artifact/claim split as above.
**Confidence: low-medium**, and not this cycle's question.

## Source gaps, kept as unknown

- *FAMA* and *Memora* (our field refresh's names) unconfirmed at source; the abstract describes
  an RL environment. One of our two cards may be wrong.
- StateMemBench / StateMem / MemStrata / Attestor / “STALE” remain unlocated — unresolved
  identities, not evidence of nonexistence.
- Reflexion, Voyager, MemGPT, AgentRunbook-C, LongMemEval-V2, HaluMem: **not read at source this
  cycle.** Their verdicts above are card-level.
- Nothing here is our reproduction. All external figures are quoted from abstracts read
  2026-09-26.

## Appendix — lifecycle notes from the stopped roadmap sweep (partial, per steering)

The broad state/lifecycle sweep is stopped as a separate task; what I had, kept short.
**Zep/Graphiti** is the one located mechanism for *late corrections*: a temporal graph that
invalidates a fact edge with an explicit invalidation time instead of deleting it, which is the
shape Brian's corollary demands — and our own Gen19/20 runs never reached it. `[read]`+`[ours]`
**A-MEM's memory evolution** is the counter-model: it corrects by rewriting history. `[read]`
**GateMem** is the only source here that measures *concurrent scoped truth* (multi-principal,
contextual authorization boundaries) rather than asserting it, and its result is that nothing
does it well. `[read]` Per the reconciliation, the roadmap's own layer-2 reference points
(StateMem, MemStrata, bitemporal/event-sourced approaches) are still unlocated or unread, so the
layer-2 question — conservative, evidence-backed supersession — has **no verified external
implementation in our notes**. That is a gap, not a conclusion.

— cairn, Reader. Sources `[read]` fetched 2026-09-26; `[card]` and `[ours]` marked above.
