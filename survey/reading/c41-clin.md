# Reading note — CLIN: causal abstractions as memory — what exactly adapts, and what is the feedback privilege?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 41.**
One source (Tern): **CLIN, arXiv 2310.10134v1** — "CLIN: A Continually Learning Language Agent"
(identity as commissioned). Method shape as commissioned: the agent keeps a memory of **causal
abstractions** — self-generated inferences about environment dynamics — retrieved into the
prompt at decision time, and **revises** them when experience contradicts them. Questions to
answer at source: **methods and controls**; the **precise units of adaptation and
generalization** (per-task? per-environment? per-rule?); **trial budgets**; the **memory-vs-extra
feedback comparison** (is the win memory, or just more feedback passes?); **feedback privilege**
(what does the agent get that an ordinary lane wouldn't — ground-truth rewards, oracle
signals?); what **"causal abstraction" operationally means**; **source retention and costs**.
The two commissioned sharp questions: **are changed environment RULES tested, or new instances
under shared rules?** And: **which result most directly bears on stale procedure reuse?**

C40 qualifications carried: **Brian is the sponsor, agents execute** — the earlier "Brian the
executor" framing is retired; **GPT-3.5 is not a measured local executor**, and "cheap one-off
acquisition, local upkeep" is unproved for our lane; **manual-only attribution in AutoManual is
not clean**; **no universal never-load-all rule**; and my c40 "nobody measures" is narrowed —
selection-adjacent components HAVE been ablated; the defensible claim is narrower (no direct
selection-accuracy metric with ground truth in the reads so far).

**Frame held before the read (minimal):** a revision-on-contradiction mechanism, if actually
tested with rule changes, is the closest thing in the literature to Brian's stale-procedure
problem; the cycle's job is to find out whether the contradiction signal is supplied or
discovered. Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## What adapts, what generalizes, and what the simulator supplies (2310.10134v1, §3.1–3.3,
§4.1–4.3) `[read]`

**Mechanism:** memory = NL **causal abstractions** in a constrained syntax — *"X is NECESSARY
to Y"* / *"X DOES NOT CONTRIBUTE to Y"* — with **linguistic uncertainty** ("may" = moderate–
high, "should" = low). A **memory generator rewrites the whole memory list at every trial end**
from the current trial + the memories of the last three; saliency pruning is emergent (output is
smaller than the trial). Controller (frozen LLM) selects memory items per state; executor
validates actions against the simulator's valid-action list (embedding fallback, ≤5 refinements).
**Meta-memory**: best-trial-per-episode memories (level-replay archive, size 10) re-abstracted
with a target prompt ("same task, new environment" / "different task"), final rewards attached as
evidence.

**Exact units:** **Adapt** = same task, same configuration, ≤5 trials, empty-memory start, stop
at score 100. **Gen-Env** = 10 train configurations (objects/starting positions vary) →
meta-memory → unseen configuration, **same task**. **Gen-Task** = coupled related pairs
(boil→freeze), same environment. ScienceWorld, 18 tasks / 9 classes, 164 task-env combos,
simulator reward.

**Commissioned question — changed RULES or new instances under shared rules?** **New instances
under shared rules.** Configurations vary affordances (broken stove, lighter available), not task
mechanics; no test where the environment's rules change under the memory.

**Memory-vs-extra-feedback controls:** Adapt compares against Reflexion **under the same trial
scaffolding** — CLIN's relative gain larger, attributed to memory CONTENT (persistent refined
list vs current-trial reflections; learns both useful AND harmful actions vs mistakes-only).
Content ablations: **free-form advice instead of structured abstractions: −6 points**; removing
the controller: −18 ≈ ReAct-equivalent (base-config wins are hierarchy, not memory). Meta-memory
start: 52.7 vs 48.6, G+A +16 over Adapt, +23 over the reflective SOTA in Gen-Env.

**Feedback privilege — large:** simulator subgoal rewards converted to NL by 7 rules, NL
environment feedback, valid-action lists per state; no gold trajectories (that part is clean).
An ordinary lane has none of the reward plumbing.

**Source retention:** abstractions are rewritten each trial; **raw trials are not retained as
addressable sources**; the archive keeps derived memories only. Uncertainty escalation
("may"→"should" with use) is **stated as expectation, not measured longitudinally**. No cost
reported.

**Most directly bearing on stale-procedure reuse:** the broken-stove trace — a narrow item
("stove necessary to heat") fails in a stove-broken configuration, is revised, and the
meta-memory keeps the **broader disjunctive form** ("a heat source (stove, lighter) is
necessary…"), which then succeeds zero-shot in a third configuration. The only sweep read where
a stale-but-narrow procedure is demonstrably replaced by a broader one through ordinary failure
— but the revision signal is simulator reward and the change scope is configuration.

**Verdict: the most complete lifecycle design read (syntax-constrained content, trial-end
rewrite, uncertainty marks, meta-abstraction) — evaluated under privileged feedback.**
Confidence: high on mechanism, medium on generalization magnitudes, high on privilege and on
rules-untested.

— cairn. Source `[read]`: arXiv HTML 2310.10134v1, opened 2026-09-26; c40 qualifications
carried (Brian=sponsor not executor; GPT-3.5 not a measured local executor; no never-load-all
rule; "nobody measures" narrowed to: no direct selection-accuracy metric with ground truth in
reads so far).