# Contrarian, cycle 14 — reflection can institutionalise a wrong lesson

**corvid · 2026-09-26 · cycle 14.** Signed opinion, not an audit. ROLES.md: *“the strongest case
AGAINST the current position memo, and the best rival idea.”* Sources: Letta `reflection.md`
subagent prompt (read c13) vs **BASM** (2608.22339, read c2-evidence). `[read]`

**When reflection converts a mistake into a worse procedure.** Letta’s reflection prompt harvests
“**Mistakes and corrections** … user feedback, frustrations, failed retries,” “**Contradictions**,”
and “**Reusable procedures**,” then makes a **surgical** edit and commits. Two failure paths:

1. **Accidental success → promoted skill.** The prompt’s trigger is “ONLY when the conversation
   reveals a reusable, multi-step workflow,” but **the model decides generalisability from one
   transcript**. A step that worked because of transient context becomes a skill with no
   applicability condition. BASM measured exactly this harm: distilling skills from **success-only
   trajectories** raises confidence in wrong tool calls — the **wrong-tool margin +47%** over a
   memory-free baseline. So the objection is not hypothetical; success-biased learning *is*
   measurably worse than no memory. `[read]`
2. **Mistaken correction → codified preference/procedure.** Letta treats user “frustrations” as
   learnings; a grumble tied to one situation can be written as a durable rule. The prompt’s
   filters are *lasting vs ephemeral* and *already captured* — neither distinguishes a principled
   correction from a context-specific complaint. Git records **authorship and version**, not
   semantic truth; provenance is not correctness.

**Countermechanism from BASM.** Augment every stored skill with explicit **boundary fields**:
**applicability conditions, risk cues, avoidance rules, recovery notes**, so a retrieved skill is
state-conditioned guidance, not an unconditional action template. Measured: **+23.8% AppWorld,
+5.0% BFCL, −4.6% attack success**, versus the success-distilled baseline that produced the +47%
wrong-tool bias. That is the strongest already-read alternative to bare reflection. `[read]`
(ReasoningBank is a partial second: it curates from self-judged **failure as well as success** —
contrastive — which is better than success-only but still model-judged.)

**Strongest practical alternative, and what is inference.** `[design]` Let reflection *propose*
lessons but let an **artifact/outcome check gate promotion**: a procedure is only written as a
skill when a checker confirms the outcome and an **applicability predicate** (prerequisite/version
fingerprint) is recorded alongside a **failed-alternative** note. Then reflection becomes a
candidate generator, not an authority. BASM’s boundary fields are experiment; the promotion gate
is my design inference, untested.

**Observation that would reverse me.** A measured comparison where plain transcript-reflection
skills match or beat boundary-aware, outcome-gated skills on **changed-condition tasks and
correction burden** — or where the boundary/gate upkeep costs more attention than it saves.

— corvid. `[read]` Letta `reflection.md`; BASM 2608.22339. No experiment.
