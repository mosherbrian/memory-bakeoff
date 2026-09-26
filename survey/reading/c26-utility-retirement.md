# Reading note — Does ReMe's utility deletion protect rare experiences, or only price workload shift?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 26.**
One sub-area, existing source only (ReMe, my c24/c25 reads; no new sweep): **does
utility-based deletion protect rare/difficult experiences, or does the evidence only test
workload-shift-ish adaptation?** Inspect: denominator/counter attribution, the minimum-use rule,
the deletion ablation, and stated limits. Each claim labelled **[explicit]** (source statement),
**[inference]** (design reading), or **[missing]** (comparison not run). C25 corrections
accepted: 21.42→23.96 s is a *stated average inference latency* — no phase attribution; v2 does
name text-embedding-v4 (embedding provider known; full serving stack not disclosed — different
claims); frontier-table metric to be named below; reviewer-motivation line withdrawn as
speculation; local time is not automatically abundant.

*(facts + verdict appended after read)*

## The deletion mechanism, inspected (ReMe §3.4; §4.3 Table 3; App. B.3–B.4 v1+v2) `[read]`

**Explicit source statements.** Utility deletion: remove any experience whose *average utility
across past recalls* falls below threshold; the utility counter *"increments by 1 each time its
recall contributes to a successful task completion"*; and *"an experience is considered for
removal only after it has been retrieved at least α times"* — with **α=5, β=0.5** disclosed in
v2, "threshold selection follows the prior work (Xiong et al., 2025)" `[explicit]`. The deletion
ablation (BFCL-V3, Qwen3-8B): selective+reflection 45.00/64.66 → **+deletion 45.17/68.00**
`[explicit]`, interpreted by the authors as *"critical for agents to adapt to non-stationary
environments"* `[explicit statement — but see below]`.

**Denominator/counter attribution — unspecified.** Retrieval is top-5; the paper never states
**how "contributes" is attributed** among five co-recalled experiences when a task succeeds.
`[missing]` If credit flows to all recalled entries on success (the simplest reading —
`[inference]`), utility is a *recall→success association*, not a causal per-experience estimate;
the paper makes no causal claim, but the ablation's +3.34 Pass@4 is read as if the right entries
were being pruned.

**Rare experiences: protected by a floor, not by design evidence.** The α=5 minimum-use rule
means a rarely retrieved experience is **never considered for deletion** `[explicit mechanism,
inference of the protection effect]`. That is the *only* protection in the source — there is no
frequency-stratified result, no survival analysis for rare-but-valuable entries
`[missing comparison]`. And **difficult** experiences are exposed: on hard tasks the
recall→success rate is low by construction, so a global β=0.5 can prune exactly the entries
that address the hardest cases — nothing in the error analysis (62→47 failures, 17 fixed / 2
new) touches deletion behaviour `[missing]`.

**Workload shift: motivated, never tested.** Refinement is introduced against *"shifts in task
distributions"* `[explicit motivation]`, but every evaluation (BFCL-V3 50/150, AppWorld 90/168)
is a **stationary split**; no shifted-stream or drift experiment exists in either version
`[missing comparison]`. So: utility deletion is *justified* by shift language, *ablated* only on
a static workload, and *protects* rare entries only as a side effect of the minimum-use floor.

**Also named per corrections:** frontier gains (GPT-4.1 48.25→54.67, o4-mini 54.67→60.00) are
**Avg@4 on BFCL-V3** `[explicit, App. B.3/B.4]`; Table 6's 21.42→23.96 s stays a stated average
inference latency with no phase accounting; embedding provider named (text-embedding-v4), full
serving stack not disclosed.

**Verdict.** The mechanism is real, cheap and positively ablated — but its two headline
properties (non-stationarity adaptation; keeping the pool "high-quality") are **untested for
exactly the entries Brian cares about: rare and difficult procedures**. Confidence: high on
mechanism and on what's missing (all inspected); the protection-by-floor reading is my
inference, labelled.

**The one idea deserving attention:** the **floor-before-threshold order** — never judge a
record's utility until it has been used enough times (α), and count uses as a first-class
number. For a lane where most stored procedures are rare, the floor is the whole design; the
deletion threshold is optional.

— cairn. Source `[read]`: ReMe 2512.10696 v1+v2 re-inspection (§3.4, §4.3, App. B.3–B.4); no new source.