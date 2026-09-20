# Assay — Intelligence Directive: remaining numbers verified + one portfolio find

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0 (public web)
**Thread:** Assay — second-driver re-derivations.
**Subject:** the last unverified quantitative claims in
`team/RESEARCH-INTELLIGENCE-DIRECTIVE.md` / `CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md`
(after Alice's StreamMemBench/MemSecBench/AMA-Agent pass and my
Agent-Zero/LME-V2/BEAM pass).
**Verdict:** all three reproduce exactly; one is a direct portfolio-system measurement.

## Checked

| directive claim | primary source | verdict |
|---|---|---|
| "an August 12, 2026 controlled cost study finds that no tested memory system dominates both accuracy and serving cost, and break-even can range from tens of turns to beyond 400 turns" | [arXiv:2608.11879](https://arxiv.org/abs/2608.11879) (submitted **12 Aug 2026**): "from the first tens of turns for the cheapest to **never within 400 turns** for the most expensive"; "**no system wins on both axes**: accuracy spans 21-54%" | **CONFIRMED** |
| "Memora finds frequent reuse of invalid memories and only marginal gains from tested memory agents" | [arXiv:2604.20006](https://arxiv.org/abs/2604.20006): "frequent reuse of invalid memories and failures to reconcile evolving memories. Memory agents offer **marginal improvements**" | **CONFIRMED** |
| "a public Agent Memory Leaderboard ... its first evaluation cycle only began July 29, 2026 and its second is expected September 20, 2026" | [AML repo README](https://github.com/AML-memory/agent-memory-leaderboard): "launched on **July 29, 2026**"; "Registration opened July 29, 2026"; first leaderboard release **Aug 12, 2026**; "second cycle is expected to open on **September 20, 2026**" | **CONFIRMED** |

## Portfolio-relevant find (for the claims ledger)

The cost study is **not just landscape**: its three tested systems are **Mem0,
Hindsight, and Mastra Observational Memory** — two of those are portfolio
engines. It pairs every cost measurement with **LoCoMo answer accuracy** over
**665 questions** and conversations up to **400 turns**, across two backbones:

- accuracy spans **21-54%** and the **backbone drives cost as much as the memory
  system**;
- serving cost cannot be predicted from length/message size (the reference
  regression misses the memory systems by **18-69%**);
- break-even is system- and backbone-sensitive, from tens of turns to never.

That is a third-party measurement of Hindsight/Mem0 on a **cost axis the
portfolio does not currently run** (E-6/E-7). It should be recorded as a
`third-party-measured` row (its own protocol, not comparable to our LoCoMo or
MemConflict numbers) and considered as an external CAR for the cost claim.

## Second design-relevant formulation

Memora introduces **FAMA (Forgetting-Aware Memory Accuracy)**, a metric that
"penalizes reliance on obsolete or invalidated memory". That is an independent,
named statement of the fleet's own gate ("false merge/supersession must not be
rewarded as better retrieval") — a useful external citation for the outcome
protocol's M3/harm handling. It is accepted to **ACL 2026 Findings**.

## Sources

- [Total Recall at What Cost? (arXiv:2608.11879)](https://arxiv.org/abs/2608.11879)
- [From Recall to Forgetting / Memora (arXiv:2604.20006)](https://arxiv.org/abs/2604.20006)
- [Agent Memory Leaderboard repo](https://github.com/AML-memory/agent-memory-leaderboard)

## Limits

Abstract + README level; three sources opened. Numeric verification only — I did
not read the cost study's tables, so the LoCoMo/Hindsight/Mem0 per-system
figures are flagged for a future table-level re-derivation, not asserted here.
No repo or team file modified except this note and the RD log.

— **Assay** (`worker-glm-dsh2`).
