# Reading note — Xiong et al.: does retained-vs-deleted quality support the success-counter proxy?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 27.**
One source (Tern): **Xiong et al., arXiv:2505.16067v2** — the prior work ReMe imports its
deletion thresholds (α=5, β=0.5) from. Sections: **§4.3, Appendix B.5, plus the §3.1 evaluator
definitions needed to read them.** Question: does the **intrinsic quality of retained vs deleted
memories** support using a *success-counter proxy* (recall→success association) as the pruning
signal, and **where does it reverse?** Tern has §4–5.1; Corvid owns the oracle/coarse-setup
argument — no repetition of their summary. Focus: quality comparisons, **task dependence**, and
what these comparisons **cannot establish about rare/hard procedures**. No new sweep.

C26 corrections carried: difficulty-related pruning is a **risk, not observed fact**; a simple
counter being computationally cheap **does not price the outcome supervision** the counter
consumes; Brian prioritized procedures but **did not quantify rare-use incidence**; the minimum
floor is a **candidate, not a five-use rule** for his files; ReMe v2's embedding model names
conflict internally (main text vs B.4.2) — noted, not mine to resolve.

**Provisional frame (before the read).** If Xiong shows that memories surviving a
success-counter rule score *higher on independent quality measures* than the deleted ones, that
is the strongest available evidence that the proxy tracks quality without an oracle per entry.
The reversal to look for: **task-dependence** — the proxy should degrade where success is rare
(hard tasks) or where quality and success decouple (exploratory/insight memories that pay off
later). Whether their design can even see that reversal depends on their evaluator definition
(§3.1) — if "quality" is itself judged by task success, the loop is circular. Written skeleton
first; facts after the read.

*(facts + verdict appended after read)*

## What the evaluator definitions do to the proxy (Xiong et al. 2505.16067v2, §3.1, §4.1, §4.3, App. B.5) `[read]`

**§3.1 [explicit] — the counter is not label-free.** Four agents: RegAgent (synthetic, error
measurable), EHRAgent, AgentDriver, CIC-IoT. Utility for deletion comes from an **evaluator E
applied per retrieval**: *strict* = human/oracle (simulated via ground truth); *coarse* = C1
GPT-4o-mini, C2 GPT-4.1-mini, C3 a 4.1-mini **fine-tuned on 300 judge labels**. History-based
deletion = the α-floor + mean-utility rule ReMe imports, with the floor's stated purpose
*"to reduce the estimation bias for the average utility"* [explicit — the floor's origin].
**Design-transplant finding [inference, flagged]:** ReMe cites this paper for α=5/β=0.5 but
replaces evaluator-scored utility with a **binary task-success counter** — the imported evidence
is for a richer signal than the one ReMe ships, and neither paper acknowledges the swap.

**§4.3 + B.5 — where the proxy is supported, where it reverses.** Support: RegAgent + C1 KDE —
retained records show **lower intrinsic error than deleted**; "consistent trends across other
agents" with various evaluators; Table 4 correctness-vs-ground-truth gaps: CIC-IoT large
(retained 78.9/72.2/86.6 vs deleted 56.7/55.1/61.0), **EhrAgent small** (44.1/49.1/54.8 vs
36.3/32.1/48.2 — ~6.6 pts at best evaluator). **Reversal [explicit, authors' own word
"Interestingly"]:** AgentDriver under the weakest evaluator (GPT-4o-mini) — *"the retained
memory ... exhibits lower average quality than the deleted records"*: the rule pruned the
**better** records. So the proxy's validity is **task- and evaluator-dependent**, not general.

**What these comparisons cannot establish about rare/hard procedures [missing]:**
(1) every deletion/quality analysis conditions on **retrieved ≥ 5** — sub-floor (rare) records
are never analyzed either way; (2) the authors themselves say true context/distribution
misalignment is *"case-specific and difficult to capture directly"* and substitute
evaluator-induced error *"for clearer illustration"* — the mechanism shown is a stand-in, by
their statement; (3) the reversal case is the warning for **hard** procedures: coarse evaluators
are least reliable exactly where judging success is hard, which is where a counter inherits the
worst noise [inference from (2) + the reversal].

**Verdict: solid diagnostic, conditional endorsement.** Intrinsic-quality comparisons support
the counter proxy **only when the evaluator is decent**, quantify task-dependence, and contain
one explicit reversal; they say nothing about rare records and their own mechanism demonstration
is a declared proxy. Confidence: high (tables explicit; reversal and stand-in admission are the
authors' own text).

**For Brian's no-checker question:** the honest reading is *counter-with-a-floor plus a named,
inspectable evaluator per line* — Xiong prices what a counter consumes (an evaluator per
retrieval; the strongest coarse one needed 300 labels), so "no reliable checker" shifts to
"which fallible checker, and does its reversal case look like my tasks?"

— cairn. Source `[read]`: arXiv HTML 2505.16067v2 §3.1, §4.1–4.3, App. B.5, opened 2026-09-26.