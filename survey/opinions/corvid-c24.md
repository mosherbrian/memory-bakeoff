# Contrarian, cycle 24 — ReMe supports affordable self-curation, but failure reuse is not isolated

**corvid · 2026-09-26 · cycle 24.** Signed opinion; ROLES.md “best rival idea.” Source: ReMe,
Cao et al., [arXiv:2512.10696v2](https://arxiv.org/abs/2512.10696) (ACL 2026 Findings), §3, §4.2–4.4,
limitations. `[read]`

**Strongest pro-small-model case.** ReMe sets **LLM_summ = LLM_execute** (Qwen3-8B by default) — no
frontier curator. It samples N=8 trajectories/task, has the same local model distill
success patterns, failure triggers and comparative insights, validates via **LLM-as-judge**,
dedups by embedding, indexes by **usage-scenario** (not raw task text), retrieves top-K=5 (+ optional
rerank + rewrite), then refines the pool. The gains are real: Qwen3-8B+ReMe(dynamic) 34.94 vs
27.65 Avg@4 no-memory (avg over BFCL-V3/AppWorld), and **8B+ReMe Pass@4 (55.03) edges 14B
memoryless (54.65)**. So self-curation is affordable and can substitute for some scale. `[read]`

**What the ablations actually isolate.** Selective addition (+3.50 Avg@4 over full addition),
failure-aware reflection (modest), and **utility-based deletion** (Pass@4 +3.34) each contribute;
keypoint-level beats trajectory-level; scenario indexing beats raw/keyword keys; K saturates around
5 and more hurts (noise). Cost is modest: AppWorld latency 21.42→23.96s/task. `[read]`

**Strongest limit — and where I must say “unknown.”** The paper does **not cleanly isolate**
failure-memory vs retrieval vs generation policy: the executor is fixed, but the experience content
is written by that same model, and there is no arm feeding a fixed experience pool to a different
policy. Full addition *underperformed* selective addition, and stored failure lessons help chiefly
via **reflection-then-success** (retry, keep only if it worked; max 3), not as reusable failure
text. So “remembering failures” is not established as the source of the gain — curation quality,
scenario indexing and deletion are. Separately, **summarizer capability still scales the gain**
(8B summ 44.50 → 32B summ 47.83 Avg@4), so small self-curation is affordable but quality-bound —
not a frontier-parity requirement, but not free either. `[read]`

**For Brian.** This supports the c19/c23 smallest-core line: a competent local executor can
curate its own validated experiences, and the transferable parts are **selective addition, a
scenario/applicability index, a judge/validator, and utility-based retirement** — not a service or
graph. But ReMe is tool-use benchmarks, not Brian's model ops, and it does not show that stored
failure text is what helps. **Medium confidence.**

— corvid. `[read]` 2512.10696v2 fetched 2026-09-26; no reproduction, no experiment.
