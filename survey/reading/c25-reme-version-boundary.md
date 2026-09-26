# Reading note — ReMe v2 vs v1: what the cost boundary actually says

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 25.**
One source, version comparison (Tern): **ReMe 2512.10696 v2 §4.4 "Computational Overhead" +
appendix model setup vs v1.** My c24 read was **v1**, where I grep-verified that **no token,
latency, or price figure exists anywhere**. Questions: what changed in reported cost / model /
provider assumptions between versions; is there a latency baseline; are acquisition, retries and
refinement included in the overhead accounting; is there any total-token or price claim.
Constraint: both versions sample 8 acquisition trajectories — do not infer local end-to-end cost
from the Qwen executor alone. No new paper. Useful partial first, deepen after.

**Provisional frame.** A v2 adding a "Computational Overhead" section is likely a reviewer-
driven response to exactly the gap I recorded. The decisive details will be: (a) which phase's
cost is measured (reuse-time only vs the full pipeline including up-to-8 sampling trials,
summarizer×3, judge, dedup, rewriter); (b) against what baseline (No Memory? A-Mem?); (c) units
— tokens, wall-clock, or dollars; (d) which models/providers the setup assumes (API vs local),
because that decides whether the numbers transfer to Brian's local-only lane. Written skeleton
now; facts after the v2 read.

*(facts + verdict appended after read)*

## What v2 adds over v1 (2512.10696v2 §4.4 + Table 6, App. B.2/B.4; v1 = my c24 read) `[read]`

**Cost: from zero figures to exactly one row.** v1 had no token/latency/price number anywhere
(my c24 grep-verified finding). v2's "Computational Overheads" is **Table 6: AppWorld, Qwen3-8B
only — No Memory 21.42 s vs +ReMe 23.96 s (+2.54 s) average inference latency per task**, with
the claim the cost is *"acceptable, which will not limit its applicability in long-running or
resource-constrained settings"*. Boundary of that row: it is **reuse-phase marginal cost against
a No-Memory baseline** — the task loop (21.42 s) dominates; +2.54 s ≈ +12% is retrieval +
rewriting. **Not included:** acquisition (8 sampled trials/task + three summariser prompts +
LLM-judge + dedup — App. B.4 confirms **n=8 in both versions**; my c24 "up to 10" was wrong,
corrected here), embedding upkeep, and the table doesn't say whether dynamic refinement /
reflection retries are inside the average (variant unlabeled). **No total-token or price claim in
either version; no serving-stack disclosure** (no GPU/API/provider statement), so the baseline
is opaque — per Tern's caution, no local end-to-end inference from the Qwen executor row alone.

**Model/provider assumptions changed.** v1: Qwen3-8B/14B/32B only. v2 adds a generalisation
table with **GPT-4.1 (48.25 → 54.67 dynamic) and o4-mini (54.67 → 60.00)** — so the
"small-models-only" transfer limit from c24 is now partly lifted: gains persist on frontier
executors on the reported suite. Method sections otherwise match v1 (component ladder,
selective addition, reflection-gated writes, utility deletion).

**Verdict on the boundary.** v2 answers the c24 gap *partially and honestly-shaped*: the
marginal reuse cost is now measured and small (+12% per task on one benchmark, one model);
the **pipeline-total remains unpriced in both versions**, and the "will not limit
applicability" sentence generalises beyond the single row — it is supported for reuse-time,
not for the offline phase. Confidence: high (the table is one row; nothing to misread).

**Useful number for Brian:** the only transferable cost figure in the ReMe record is **+2.54 s
per task at reuse on a 21.42 s loop**. Everything else must be measured in-lane — and on
Brian's local-free executor the unpriced 8-trial acquisition is *compute time, not dollars*,
which is exactly the currency where his lane is rich.

— cairn. Source `[read]`: arXiv HTML 2512.10696v2 §4.4 Table 6, App. B.2/B.4, vs v1 (c24).