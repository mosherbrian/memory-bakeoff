# Reading note — OS-Copilot/FRIDAY: self-improving tool acquisition — does any control isolate the stored tools?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 58.**
One source, identity per commission: **Wu et al., "OS-Copilot: Towards Generalist Computer
Agents with Self-Improvement," arXiv 2402.07456v2 (15 Feb 2024)**; FRIDAY is the agent. No later
projects/versions mixed. Focus: **acquisition, stored tools, critic/admission, component
controls**; Excel/PowerPoint endpoints separated from GAIA.

C57 corrections carried: dynamic state is change but distinguish it from rules/UI versions;
Cradle has regeneration, not proven robust correction; **one paper's missing library control
does not negate stored-content evidence elsewhere**; no five-layer validation inference.

**Frame held before the read (minimal):** FRIDAY's pitch is self-directed learning — the agent
writes its own Python tools from documentation and practice, keeps them in a library, and is
supervised by a **select/critic mechanism**. The panel's question is the same one Cradle could
not answer: is there a condition that separates **previously acquired tools** from retries,
critic loops, and framework scaffolding — on held-out tasks, at measured cost? Written skeleton
first; facts after the read.

*(facts + verdict appended after read)*

## Two w/o-learning controls — one modest, one confounded (2402.07456v2, §2.2–2.3, §3.2, §4.1–4.2) `[read]`

**Architecture:** planner (DAG) + configurator (declarative profile/knowledge; **procedural
memory = tool repository**; working memory) + actor (executor + **critic**). Seeded with **4
manual tools**; tools are Python files or API services; the critic — an LLM reading pre/post
system state, **no ground truth** — judges subtask completion, proposes error fixes, and drives
tool-code updates. **Admission is the critic's success verdict on the task that spawned the
tool**; no independent verification gate (LATM's red flag, restated).

**Control 1 — GAIA, held-out properly:** FRIDAY explores the **GAIA dev set**, accumulating **9
more tools**, then submits to the official test-set server. **FRIDAY vs FRIDAY w/o learning**
(same framework, same GPT-4-turbo, seed tools only): **36.56→40.86 / 17.61→20.13 / 6.12→6.12**
(levels 1/2/3). A real same-agent with-vs-without comparison — the control Cradle never ran —
and the accumulated-library effect is **modest**: +4.3, +2.5, 0.0.

**Control 2 — Excel, dramatic but confounded:** on SheetCopilot-20, FRIDAY w/o learning scores
**0%** (grasps pandas/matplotlib, wrong interface), then self-generates **10 practice tasks**,
acquires **8 tools**, and reaches **60%** — beating the manually-crafted SheetCopilot agent.
The largest stored-content gain in this corpus, but the 0% is largely an **interface-discovery
failure**: the 8 tools encode "use the right package correctly" as much as many procedures;
practice and test are the **same app domain** (no cross-app holdout); PowerPoint evidence is
qualitative only.

**Costs:** unpriced — "limited budget" chose the model; no token or dollar ledger; practice-run
cost of the 10-task curriculum unreported.

**Verdict: FRIDAY supplies what Cradle lacked — same-agent controls isolating the acquired
library — and the two answers differ in kind: on genuinely held-out general tasks the acquired
tools add a few points; on an unfamiliar application the right eight tools are the difference
between useless and state-of-the-art.** Read together: **stored procedures pay where the
interface is unknown and fail to pay much where the executor already improvises.** The weak
seam is admission — critic-judged, no ground truth, self-generated tools unverified. For Brian:
the Excel shape (one unfamiliar app, ~10 practice runs, ~8 small tools, big jump) is the
best-evidenced case for his procedure store; the GAIA shape warns not to expect much on tasks
the local model already muddles through. Confidence: high on both controls' structure
(explicit), medium on the Excel gain generalizing beyond same-app transfer, high on costs
unpriced (searched).

— cairn. Source `[read]`: arXiv HTML 2402.07456v2, opened 2026-09-26; c57 corrections carried
(dynamic-state vs rules-change; Cradle regeneration ≠ proven correction; one paper's missing
control ≠ negation of stored-content evidence elsewhere; no five-layer validation inference).

— cairn. Source: arXiv 2402.07456v2, opened today.