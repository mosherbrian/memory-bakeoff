# Reading note — SkillRL: skill bank vs trained policy, and the controls between them

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 15.**
One source (Tern): **SkillRL, arXiv:2602.08234, methods.** Questions: who creates skills, what
gets retrieved, when the bank changes, what policy is trained, and **whether evaluation
separates stored-skill benefit from training benefit**. Focus: repeated-procedure relevance and
acquisition/upkeep cost, not leaderboard. ROLES frame: *"one short paragraph per source and a
verdict per source"*; roadmap frame: layer-2 supersession should be *"conservative and
evidence-backed rather than 'nearest neighbor means replacement'"* — skill banks are where
Voyager's append-only library (my c2 read) meets RL.

**Provisional frame (before the read).** My inventory's prior on this shape: Voyager =
execution-verified skill library, append-only, no retirement, free runtime re-check; Memory-R1 =
learned policy over an editable store, correction outcome-gated. The interesting failure modes
to look for: skills admitted without verification, bank updates entangled with policy training
so the ablation cannot tell them apart, and retrieval of a stale skill that still *runs* but no
longer *fits* (applicability, my c2 question). Written skeleton first; verdict appended after
the methods read.

*(facts + verdict appended after read)*

## Protocol facts (SkillRL 2602.08234, §3.1–3.3, §4.3) `[read]`

**Who creates skills:** a **teacher LLM**, never a human. Base-agent rollouts are distilled —
successes into strategic patterns, failures into concise *failure lessons* (both retained, which
matches Brian's failed-alternatives value) — and during RL, after each validation epoch, the
teacher analyses stratified failures of under-performing task categories (trigger: per-category
success below threshold) and adds or **refines** skills. Bank grew 55→100 during training.
**Admission is teacher judgement, not execution verification** — the Voyager check my c2 read
praised is absent.
**What gets retrieved:** general skills always in context; task-specific via embedding
similarity (top-k, threshold) — nearest-neighbour retrieval, the roadmap's cautionary shape.
Skill schema = name + principle + **when_to_apply**: the first located store that *writes*
applicability into the record — but it is prose for the policy to read, never evaluated by the
runtime.
**When the bank changes:** cold-start build, then recursive evolution at validation checkpoints;
"refinements" revise existing skills **in place by LLM judgement — no lineage, no invalidation,
no tombstone** (A-MEM's history-rewriting pattern at the skill layer).
**What policy is trained:** GRPO on the skill-conditioned policy, after a **cold-start SFT**
stage that teaches the model to *use* skills — without it, −20 points. That is our
read-but-unused/uptake problem priced: utilisation must be trained, not assumed.
**Does evaluation separate stored-skill benefit from training benefit? Partially — and the gap
is named.** Ablations isolate *content format*: raw trajectories instead of skills −25,
no-hierarchy −13.1, no-evolution −5.5, no-cold-start −20. But **every arm is RL-trained**; there
is no trained-policy-without-library arm and no post-training skill-removal test — after
co-evolution, skill knowledge may partly live in the weights, so the library's marginal benefit
at deployment is unmeasured. The +15.3 headline is over baselines of different training, not a
skills-versus-weights separation.

**Verdict: solid method, one named control gap, weak lifecycle.** For Brian's repeated
procedures it is the closest located *automatic capture + automatic upkeep* implementation, and
its two strongest results transfer as design facts: abstraction beats raw replay by a wide
margin; skill *use* is a trained skill (cold-start), not a prompt. Upkeep cost is real but
unpriced (teacher calls every cycle); lifecycle discipline is the weakest part — append +
LLM-refine with no provenance, nearest-neighbour retrieval, unverified admission. Confidence:
medium (ALFWorld/WebShop scale, self-reported, no transfer evidence to coding-admin work).

— cairn. Source `[read]`: arXiv HTML 2602.08234 §3.1–3.3, §4.3, opened 2026-09-26.