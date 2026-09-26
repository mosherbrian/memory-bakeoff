# Contrarian, cycle 7 — memory multiplies the executor; it does not replace it

**corvid · 2026-09-26 · cycle 7.** Signed opinion, not an audit. ROLES.md: *“the best rival
idea.”* Primary source read: ReasoningBank / MaTTS, Ouyang et al.
([arXiv:2509.25140](https://arxiv.org/abs/2509.25140), ICLR 2026). `[read]`

**Verdict on the compute-cost case.** The evidence does **not** justify a small local executor +
auto-learned memory over a stronger memoryless executor for Brian — *not at equal total compute*.
Memory is real and cheap-ish, but it is a **multiplier on the executor**, and its curator must be
strong. **Medium-high confidence.**

**Distinguish the four costs the headline hides.**
- **Execution-model size.** WebArena pass@1: Gemini-2.5-**flash** no-memory 34.2 → ReasoningBank
  **38.8**; Gemini-2.5-**pro** no-memory 54.0 → 57.4. So memory adds ~+4.6 to the small model and
  ~+3.4 to the large — and **flash+memory (38.8) is still far below pro no-memory (54.0)**. On
  this benchmark, learning does not buy back a model tier. `[read]`
- **Memory-generation / refinement compute.** ReasoningBank distils “generalizable reasoning
  strategies” from **self-judged** success *and* failure; that judgement is a model call. MaTTS
  explicitly spends *more* test-time compute to synthesize higher-quality memory. The curator is
  Gemini-2.5-class, not the small local executor. A local setup must therefore pay for a strong
  curator (usually remote) or accept weaker memory. `[read]`
- **Acquisition amortization.** No method here reports a **reuse-to-repay** curve — how many
  repeated tasks it takes for curation compute to be recovered. Without it, “automatic learning
  is cheaper” is an assumption, not a result.
- **First-attempt vs best-of-many.** MaTTS’s parallel setting uses **Best-of-N** as the final
  metric; scaling runs k=1→5 (49.7→55.1 parallel, 49.7→54.5 sequential) versus MaTTS-without-
  memory wobbling 39.0–42.2 / 37.4–40.6. Some of the gain is *more sampling*, not better memory,
  and is not comparable to a single-attempt memoryless baseline. `[read]`

**What would justify small-local + memory.** Equal-**total**-compute accounting (execution +
curation + retrieval) showing a small local executor with memory matching a stronger memoryless
executor on **first-attempt** success over *held-out* tasks, with a locally affordable curator.
ReasoningBank does show genuine transfer (Mind2Web cross-task/cross-website/cross-domain), which
is the strongest pro-memory fact here — but not those budget terms. Absent that, a stronger
memoryless executor plus **deliberate, artifact-grounded reuse** is the safer spend for Brian,
because deliberate reuse needs no curator model and its check is an exit code.

**Strongest rival I will still grant.** For a *fixed* local executor that cannot be upgraded,
self-curated memory is one of the few levers that grows with use, and it reduced steps (30.3→27.5
flash) as well as raised success. If Brian’s constraint is “run local, cannot call a stronger
model,” automatic learning is worth trying — with the curator problem solved or explicitly paid
for.

**Concrete result that would reverse my verdict.** A matched-budget study where a 7–30B local
executor + locally-curated memory reaches first-attempt parity with a frontier memoryless model
on Brian-like repeated admin/rollout tasks, and the reuse-to-repay curve is under a handful of
repeats. Until that exists, I would not let “automatic learning” drive a smaller-executor choice.

## Deepened gap
The load-bearing unknown is **curator quality versus executor size**: every strong result uses a
frontier model to judge and distill memory. Whether a local model can *self-judge* well enough to
curate non-harmful procedures is untested here — and BASM already showed success-distilled skills
can raise wrong-tool confidence (+47%). So the real question is not “small model + memory” but
“who writes the memory, and can that writer be the same weak model?” That is the gap that decides
the local architecture. Source gap, not a conclusion.

— corvid. `[read]` arXiv:2509.25140 (v2) methods/results fetched 2026-09-26; no reproduction,
no experiment.
