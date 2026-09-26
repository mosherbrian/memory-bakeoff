# Reading note — MINJA: how a forged statement becomes durable guidance, and what transfers to one principal

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 28.**
One new source (Tern): **MINJA — "Memory Injection Attacks on LLM Agents via Query-Only
Interaction", arXiv:2505.03704 → 2503.03704; NeurIPS 2025 preferred.** Question for the cycle
(*whose statement becomes durable guidance?*): read the **threat model and methods/controls** —
what must the attacker access, what must victim memory share, which **evaluator/admission path**
admits the forged record, and **what transfers to a single-principal assistant reading external
material** (Brian's lane). Distinguish demonstrated access from speculation. No payload
construction or reproduction.

C27 corrections carried: **the richer-signal transplant claim is downgraded to an open
question** (utility can itself be binary; my inference is unestablished); the **reversal finding
is retained**; I do not claim all hard-task evaluators are worst, and I impose no per-line
counters.

**Provisional frame (before the read).** MINJA as known from the trail: attacker interacts only
through ordinary queries (no backend write access), injects plausible "helpful" records into the
agent's long-term memory via the normal self-writing path, later retrieved and followed by the
SAME agent or other users sharing memory. If so, the lifecycle point for our panel is sharp and
on-topic: **the admission path that needs no checker is exactly the attack surface** — the
self-curation channels I have read (DC label-blind curator, ReMe success-counter with an
LLM-judge at write, A-MEM evolution) all admit records without author verification. For a
single-principal assistant the multi-victim amplification drops away, but the core question
remains: whose statement entered memory — Brian, the agent's inference, or external material
that merely passed through? Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## Threat model and controls (MINJA 2503.03704, NeurIPS 2025, §3, §4, §5.2, §5.4) `[read]`

**Attacker access [explicit, the paper's headline constraint]:** *query-only* — behaves as a
regular user; no memory-bank manipulation, no trigger injection, cannot touch victim queries.
Prior poisoning work assumed backend write access; MINJA's contribution is showing the
**normal self-writing path is sufficient**.

**What memory must share [explicit assumption]:** a **shared memory bank** across users —
stated as an assumption, with real deployments cited. Cross-user attack needs it; the paper
does not test single-user settings `[missing]`.

**The admission path that lets records in [explicit]:** records are *agent-generated* and
stored after *user feedback* — "the user will provide feedback as the basis for the agent to
decide whether or not the record will be stored". There is **no author-identity check anywhere**:
the attacker wins by *inducing the agent to author and store* the malicious record itself
(indication prompts + progressive shortening; bridging steps like "data of A saved under B"
— mechanics referenced, not reproduced, per commission).

**Demonstrated magnitude:** injection success **ISR uniformly >95% mean**; attack success ASR
~60–90%+ (pair-dependent, higher variance); benign utility drop **<2%** on three datasets —
stealthy by measurement, not assertion. Retrieval is plain query-similarity: the attack designs
for it (benign-looking, form-matching queries).

**Defenses (§5.4) — where detection fails is instructive:** targeted flag prompts catch the EHR
agents (131/135, 130/135) but **0/135 on RAP**; general flags weaker with false positives (34/50
on one set). When the malicious content rides inside the agent's *own reasoning style*, flagging
it as foreign fails — the carrier is indistinguishable from normal work.

## What transfers to a single-principal assistant (Brian's lane)

**Drops away:** the shared-bank, attacker-vs-victim-user framing.
**Transfers structurally [inference, labelled]:** the three enabling conditions — self-writing
memory, similarity retrieval, **no provenance check at write** — all hold in a single-principal
assistant. There, the "attacker" is any **external material the assistant reads and stores**
(email, web page, doc): prompt-injection-by-another-route. MINJA is the measured price of an
admission path with no author check: >95% injection, <2% utility cost.

**Verdict: solid demonstration under its stated assumption (shared bank); the single-principal
transfer is structural, not demonstrated** — I claim the mechanism conditions transfer, not the
numbers. Confidence: high on threat model/results (explicit), medium on transfer, and the
"identity disguise is easier" line is the authors' assertion, not an experiment.

**The one idea for *whose statement becomes durable guidance*:** provenance **at write time**
is the only control this attack class respects — tag every record *user-uttered / agent-inferred
/ external-observed*, and grant directive authority only to user-uttered. MINJA forges the
middle category (agent-authored, feedback-blessed); detection flags cannot catch it when the
record looks like the agent's own reasoning (RAP 0/135). The tag cannot be applied after the
fact — which is exactly what this sweep's self-curation channels (DC label-blind, ReMe
judge-at-write, A-MEM evolution) never write.

— cairn. Source `[read]`: arXiv HTML 2503.03704v3 §3, §4, §5.2, §5.4, opened 2026-09-26; c27
corrections carried (transplant claim downgraded to open question; reversal retained).