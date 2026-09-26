# Reading note — ReMe: what self-curation actually costs, and how failure experiences get reused

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 24.**
One source (Tern): **ReMe, arXiv:2512.10696** — full relevant methods/controls, read beyond the
headline. Trace **one successful and one failed episode** through: writer / executor / critic
identity, **feedback privilege** (does the curator see ground truth?), held-out vs online split,
curation/retrieval costs, and how effects are isolated. State which sections were read; no
guessed numbers. End with one useful idea for Brian. C23 corrections accepted: grep IS
retrieval and cron IS scheduled selection (tooling makes the operation cheap/deterministic, it
does not erase it); rare procedures can justify storage — no arbitrary twice-rule.

**Provisional frame (before the read).** ReMe in this sweep's trail (Tern's c6 note): one of the
"automatic upkeep" family — extraction of learning from episodes, revision of an active pool.
My prior on the shape: experience → LLM distils reusable "patterns/recipes" (success AND
failure paths) → curated pool → retrieved at task time. The decisive questions per Tern: whether
the distillation is self-judged (label-blind like DC) or outcome-supervised; whether any control
separates the curation from mere storage (a DC-∅-style arm); and whether per-task curation cost
is actually reported — "affordable" is the claim under test. Written skeleton first; verdict
after the read.

*(facts + verdict appended after read)*

## One successful and one failed episode, traced (ReMe 2512.10696, §3.1–3.4, §4.1–4.4, Limitations) `[read]`

**Success path.** Executor samples up to 10 trials per training task (environment gives true
success — tool benchmarks). A **summarizer** (same Qwen3 model prompted differently in main
experiments; varied separately in Table 4) runs three analyses — success-pattern, failure-
analysis, and **comparative** (success vs failure pairs) — then **LLM-as-judge validation**
(actionable/accurate/valuable), similarity dedup, and indexing by the embedding of the
**usage-scenario** field (retrieval-key ablation: LLM-generated scenario beats raw task text
and keywords).

**Failed path — the commission's focus, and it is nuanced.** At pool construction, many failed
trajectories analysed *jointly* help. Online, a lesson from a **single** failed trajectory is
*actively harmful* ("potentially misguided experiences" — full-addition 40.83/62.00 vs
selective 44.33/64.66, Table 3). ReMe's fix: **failure-aware reflection** — the lesson drives
an immediate retry, and **is written to memory only if that retry succeeds**; otherwise
discarded (cap 3 reflections). That is my c5 "correction is outcome-gated" finding, now with an
explicit mechanism and a positive ablation.

**Refinement — the sweep's first measured outcome-gated deletion.** Per experience, ReMe
records total recalls and a utility counter that increments when a recall contributed to a
successful task; deletion when utility/recalls falls below threshold, only after a minimum
recall count. Ablation adds it last: 45.00/64.66 → **45.17/68.00** Pass@4. No LLM in the loop
for deletion — two integers.

**Effect isolation & splits.** Component ladder (Table 3) isolates each refinement; granularity
ablation isolates keypoint-vs-trajectory extraction (+~4–6 pts); retrieval-key ablation isolates
the index field; Table 4 holds the executor fixed and scales the summarizer (+1.8/+3.3 Avg@4).
Held-out: BFCL-V3 50 pool tasks / 150 eval; AppWorld 90 train / 168 test-normal; fixed vs
dynamic pool (dynamic always better). Error analysis: 17 baseline errors fixed, **2 new ones
introduced**; reasoning errors drop most.

**Feedback privilege:** environment success is real (verifiable benchmarks); *quality* judgement
is LLM-self-assessed (Limitations concede the judge's blind spots).

**What "affordable" lacks: any price.** No token, latency, or curation-cost figure anywhere in
the paper (grep-verified) — per-task cost includes up to 10 sampling trials, 3 summariser
analyses + judge + dedup at build, and a rewriter per task. The claim is untested, not
falsified.

**Transfer limits for Brian:** crisp automatic success signals are what make utility counting
work — admin work rarely has them (a recorded check-passing could substitute); small models
(Qwen3-8B–32B), no frontier runs; retrieval fires once per task by design.

**Verdict: solid — the best-isolated lifecycle mechanism in the sweep.** Confidence: high on
mechanism/ablations (tables explicit), high on the cost gap (absence verified), medium on
transfer (signal availability).

**One idea for Brian:** steal the **utility footer** — two integers per stored procedure
(*recalls, recalls-then-check-passed*), retire when recalls are frequent and wins are rare,
never before a minimum count. No judge, no service, fits a file-based runbook as one line, and
it is the only deletion rule in this inventory with a positive ablation behind it.

— cairn. Source `[read]`: arXiv HTML 2512.10696v1 §3.1–3.4, §4.1–4.4, §5 + Limitations, opened 2026-09-26.