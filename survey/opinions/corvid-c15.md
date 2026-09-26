# Contrarian, cycle 15 — verification is the good part, but it eats an outcome signal Brian often lacks

**corvid · 2026-09-26 · cycle 15.** Signed opinion, not an audit. ROLES.md: *“the strongest case
AGAINST the current position memo, and the best rival idea.”* Primary source: SkillForge methods
(arXiv:2608.24747, read §3, ablations, transfer control). `[read]`

**What SkillForge actually does.** Skills carry intent, principle, **applicability conditions**
and a status flag; the agent invokes them with a `<skill_call>` tag, so **usage is a traceable
event**; per-skill **EMA success rate × usage count** yields an underperformance score
`(1−p̂)(1−0.5^{n/h})`; high scorers are prioritized for **LLM reflexion → keep or revise**;
induction adds skills from successes, failures and **contrastive** pairs; GRPO trains the policy
and the invocation decisions together. `[read]`

**Separate the three claims the headline merges.**
- **Skill verification** = outcome-tracked quality control. This is the genuinely good, portable
  idea, and it is a real rival to reflection-only curation: BASM/c14 said self-judged lessons
  institutionalise mistakes; SkillForge replaces self-judgment with **observed episode outcomes**.
- **Invocation learning** = policy training (GRPO; 8–16 H20 GPUs; Qwen3-Max teacher). Not
  portable to Brian’s files, and its gains are policy gains.
- **Held-out policy gains** = mostly the RL effect. The control that isolates the bank is the
  **transfer experiment (Table 3)**: applying a 4B bank to a 30B model *without further training*
  gives only **27.9 → 32.9 ALFWorld, 27.4 → 31.5 AppWorld**, over a no-skill 26.4/26.8. Modest.
  The headline 87.9/44.6 is a trained-policy number, not a skill-bank number. `[read]`

**Does it rival Tern’s selective agent-maintained procedures?** The *verification mechanism* does,
if an outcome signal exists. The *system* does not, for Brian: it presupposes a per-episode
**machine-checked reward** from environment interaction, and induction/reflexion need a strong
teacher. Brian’s admin/rollout work often has no clean reward, and his specific hazard is
**commands exiting zero when the prerequisite changed** — the case where the outcome signal is
false. Verified skills are only as good as the verifier.

**Strongest practical alternative** `[design, not from source]`: port the mechanism without the
RL — store each skill with explicit **applicability conditions**, log **invocation × outcome**,
and **retire/revise on measured underperformance**, where the outcome is supplied by an
artifact/checker (exit code, config hash, version probe) rather than a benchmark reward. This is
the c14 promotion gate with a concrete score. It is a genuine improvement on reflection-only
curation **where a checker exists**, and just another unverifiable note where none does.

**Conclusion-changing limit.** The transfer control is the paper’s only bank-only result and it is
single-digit; if a bank without RL and without a reliable outcome signal were shown to beat
reflection-only curation on changed-condition tasks, my “needs an outcome signal” objection would
fall. As read, environment verification is a mechanism to borrow, not a system to adopt.
**Medium confidence.**

— corvid. `[read]` 2608.24747 fetched 2026-09-26; no reproduction, no experiment.
