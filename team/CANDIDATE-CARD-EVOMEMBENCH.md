# Candidate card — EvoMemBench (self-evolving agent memory)

**Author:** muse-drafter (proposal-drafter seat), Phase-B frontier harvest (Sprint-2 goal 5)
**Date:** 2026-09-14 · **Cost:** $0 (abstract-level web reads only)
**Status:** **candidate discovery only — no score import.** Card 8 of the named
benchmarks in `RESEARCH-INTELLIGENCE-DIRECTIVE.md`, assessed against our goals
G1–G5 (`CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md` §4).

## Provenance (verified this pass)

| Field | Value |
|---|---|
| Title | *EvoMemBench: Benchmarking Agent Memory from a Self-Evolving Perspective* |
| Authors | Yuyao Wang, Zhongjian Zhang, Mo Chi, Kaichi Yu, Yuhan Li, Miao Peng, Bing Tong, Chen Zhang, Yan Zhou, Jia Li |
| ID / dates | [arXiv:2605.18421](https://arxiv.org/abs/2605.18421) v1 2026-05-18, v2 2026-06-15 |
| Venue / license | preprint; arXiv perpetual non-exclusive license (no CC grant verified) |
| Code | public: [`DSAIL-Memory/EvoMemBench`](https://github.com/DSAIL-Memory/EvoMemBench) (13 stars, 9 commits at read time) — **NO license: repo file listing shows only `.gitignore`/`README.md`/assets/task dirs, and `raw/.../main/LICENSE` 404s (verified 2026-09-14). Treat as all-rights-reserved until a license appears** |
| Data | assembled from existing sources, not a new corpus: MemoryAgentBench (in-episode knowledge, 2,800), BFCL-MultiTurn-LongContext (in-episode execution, 800), CL-Bench (cross-episode knowledge, 884), BFCL-MultiTurn-Base + xbench-DeepSearch/WebWalkerQA + ALFWorld (cross-episode execution, 800+270+200) |
| Numbers | vendor-reported only this pass: 15 memory methods vs long-context baselines; headline qualitative (long-context baselines "highly competitive", no single memory form general) — **NOT verified from the PDF, do not cite** |

## What it is (from the abstract + repo overview)

A **taxonomy-first meta-benchmark** for agent memory: memory as a system that
must update, revise, and distill information over time, organized on two axes —
**memory scope** (in-episode vs cross-episode) × **memory content**
(knowledge-oriented vs execution-oriented) — yielding four evaluated settings.
No new dataset is collected; existing benchmarks are re-housed in the grid
under one protocol (all memory methods on DeepSeek-V3.2; memory-free baselines
Gemini-3-Flash / GPT-5-mini class).

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G1 conflict handling** | partial | knowledge-evolution settings include update/contradiction, but no adversarial conflict design |
| **G2 supersession** | partial | cross-episode knowledge accumulation is old→new reuse; no explicit lineage/supersession scoring |
| **G3 invocation** | partial | execution-oriented settings (tool-use, web, embodied) exercise state tracking, but no proactive deadline |
| **G4 material outcome** | partial | execution success rates on tool/web/embodied tasks — closest to outcome among harvest cards, still benchmark tasks |
| **G5 continuity** | partial | cross-episode transfer is continuity-shaped, but episodes are benchmark episodes, not days/weeks of real work |

## What it offers us

- **The two-axis reporting shape** (scope × content) as a design reference for
  how we present our own memory results — it separates "knows the fact" from
  "does the task" and "within the episode" from "across episodes."
- **A caution for our corpus:** their headline (long-context baselines remain
  highly competitive; memory helps most when context is insufficient or tasks
  are hard) is the same null-shape our long-context-null instrument exists to
  check — convergent design pressure, not evidence.
- **A reuse shortcut:** if we ever need an execution-oriented arm, their
  directory map (BFCL/ALFWorld/WebWalkerQA pins) is a parts list, not a result.

## What it cannot ground

Coding conflict/supersession, proactive invocation, or material outcome on real
work — and its method rankings are vendor-harness results (one answerer model,
DeepSeek-V3.2) never to be imported as evidence.

## Name-collision flag (load-bearing for citation)

Three distinct "Evo-" memory items circulate and must not be conflated:
**EvoMemBench** (`2605.18421`, DSAIL-Memory, this card) vs **Evo-Memory**
(`2511.20857v2`, Google DeepMind, streaming test-time-learning benchmark) vs
**EvolveMem** (`2605.13941v1`, self-evolving retrieval architecture). Cite by
numeric ID or not at all (per the LoCoMo numeric-id rule).

## Addendum 2026-09-14 — EvoArena + EvoMem (muse-drafter, closes the 8th slot)

Companion paper, separate benchmark: *EvoArena: Tracking Memory Evolution
for Robust LLM Agents in Dynamic Environments* ([arXiv:2606.13681](https://arxiv.org/abs/2606.13681),
v1 2026-06-11, v2 2026-06-17; abstract/HTML-level only, PDF unread).
Three evolving suites — Terminal-Bench-Evo, SWE-Chain-Evo, PersonaMem-Evo —
with step + chain accuracy (chain = every step passes). Demands
**version-aware state tracking** (retain latest, recover relevant priors,
reason over why each update occurred) **including version compatibility
with still-valid prior knowledge** — our P1-3 scoping problem stated
independently. Companion method EvoMem = git-like patch-based versioned
memory (+1.5 EvoArena / +3.7 chain / +6.1 GAIA / +4.8 LoCoMo per vendor —
unverified, do not cite). Git-like versioned-evidence-trail and chain
accuracy are design references for our lineage handling and supersession
reporting. SWE-Chain-Evo is the closest substrate match, still synthetic.
With this addendum all 8 named benchmarks are carded.

## Next step (bounded)

1. ~~Verify the repo license~~ DONE 2026-09-14: **no LICENSE file in the
   repo** (listing + raw-404) — all-rights-reserved by default. Do not vendor
   or adapt its code; reading the paper/prose is fine. Per-source dataset
   terms (MemoryAgentBench, BFCL, CL-Bench, xbench, WebWalkerQA, ALFWorld)
   still per-source if an adapter is ever built (P1 rule).
2. Otherwise record it as a **design reference** in the discovery note.

## Verification status

Existence, abstract, authors, version dates, repo URL, and composition (six
settings/samples from the repo overview) **confirmed** in this pass
(abstract + repo-overview level only; PDF unread). All performance claims are
**unverified vendor claims — not verified, not citable**. Paper license is
arXiv-nonexclusive (not CC); repo license **no LICENSE file found → all-rights-reserved**
(confirmed independently, `CORVID-EVOMEMBENCH-PINCHECK.md`, 2026-09-15).

- Second seat **done**: `CORVID-EVOMEMBENCH-PINCHECK.md` (abstract pin passes;
  no-license claim confirmed; name-collision flag endorsed). With this, all
  Series A cards 1–8 have a verification pass.
- Verifier: Corvid (abstract pin ✓ 2026-09-15, `CORVID-EVOMEMBENCH-PINCHECK.md`).
- **muse-drafter**. Phase-B candidate discovery, $0; no score import.
