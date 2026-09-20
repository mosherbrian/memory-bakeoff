# Candidate card — StateMemBench (state tracking over superseded values)

**Author:** muse-drafter (proposal-drafter seat), Phase-B frontier harvest (Sprint-2 goal 5)
**Date:** 2026-09-14 · **Cost:** $0 (abstract/HTML-level web reads only)
**Status:** **candidate discovery only — no score import.** Card 6 of the named
benchmarks in `RESEARCH-INTELLIGENCE-DIRECTIVE.md`, assessed against our goals
G1–G5 (`CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md` §4).

## Provenance (abstract-level; PDF not read)

| Field | Value |
|---|---|
| Title | *Can Agent Memory Systems Track Evolving State?* (benchmark: StateMemBench; method: StateMem) |
| ID | [arXiv:2608.19652](https://arxiv.org/abs/2608.19652) v1 2026-08-20, UIUC (Fan/Liu/Yang/Ouyang/Han); NSF-funded (MMLI/I-GUIDE/ACCESS); paper license arXiv-nonexclusive |
| Scale | **234 multi-session scenarios, 322 graded probes**: Set A 190 single-probe × 18 sessions (median 165 turns, ~3k tokens); Set B 44 fused × ~38 sessions (median 599 turns, 7–15k tokens), 3 probes each |
| Design | scenarios generated as **symbolic event programs** (typed state ops over ground/derived/declared state); gold by deterministic replay; traps = exactly where lazy-reader policies (recency/frequency/stale-derivation/eager-invalidation) disagree with replay → **failure-mode signature fixed by construction**; five modes: status / salience / sequence / compound / anti-trap; probes **closed-pool** (gold + drift target + neutral distractors, 3–4 options) so drift vs off-pool is separable |
| Generation | D.5 pipeline: sampled program → grounded in public data surface only (Instacart 2017 / credit-card-txn dataset; surface never decides trap semantics) → sonnet-4.6 renders dialogue → programmatic verify (load-bearing facts present, banned-phrase check), re-render on fail |
| Validation | D.6 + App A: adversarial filter + cross-family judging bias exclusions *against* drift; judge agreement κ=0.67 (LME) / 91.6% raw (MA-shopping); humans assign *less* drift than judges (judge rates are ceilings); reasoning-trace A/B no-help (84→76%, n.s.) |
| Judges/models | answers graded by fixed **deepseek-v4-pro** judge; substrates Qwen-3.5-9B / DeepSeek-V4-Flash (thinking off); long-context baselines incl. GPT-5.4-Nano |
| Numbers | vendor-reported only (single run each, temp 0): StateMem overall **0.363** (DeepSeek) / **0.233** (Qwen) vs **0.205 strongest same-backbone baseline** (DeepSeek) and **0.149 strongest memory system** (Qwen) — per abstract; best long-context GPT-5.4-Nano **0.277** is a **body/HTML** figure, not abstract; wrapper **+32–67 pts** per backend with length/cost-matched control isolating **+15–32 structural**; StateMem LongMemEval 0.580/0.656, LoCoMo 0.566/0.592 — **NOT verified from raw rows, do not cite** |
| Code/data | **no code/dataset link found in the paper HTML** (only a Microsoft STATE-Bench URL in refs) — nothing to license-check yet; treat as unreleased until a repo appears |

## What it is (from the abstract/HTML)

A benchmark for **state tracking**: as facts, constraints, and decisions are
revised over a long interaction, answers must reflect the **current** state,
not a superseded one. Failure modes defined and computed (drift / retrieval /
composition / schema / reason), cross-benchmark failure-mode distribution
tabulated (Table 1, incl. LongMemEval-oracle slice). Companion method
StateMem is state-first (state + relational dependencies; ablations credit
supersession handling), also offered as a single-call wrapper over existing
systems.

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G1 conflict handling** | **good** | revised facts/constraints/decisions across sessions; failure-by-construction |
| **G2 supersession** | **good (design)** | superseded value as scored outcome is the closest published match to our P1-2/P1-3 cases |
| **G3 invocation** | weak | no proactive action deadline |
| **G4 material outcome** | weak | accuracy, not time/errors/corrections |
| **G5 continuity** | partial | multi-session, but synthetic scenarios not longitudinal real work |

## What it offers us

- **A scored-supersession template:** "failure fixed by construction, old
  value scored" is exactly the shape our P1 cases hand-build each time —
  worth one design-read of their scenario generator (§4 + Table 2 +
  Appendix C/D) before we author the next case batch.
- **A failure-mode distribution table** (drift/retrieval/composition/schema/
  reason) as a reporting shape for our own stale-action failures.
- **The wrapper result (+32–67, unverified)** as a hypothesis only: a
  deterministic state layer over recall may beat more recall — convergent
  with our EXPLICIT_LINEAGE direction, not evidence for it.

## What it cannot ground

Real coding conflict/supersession, invocation timing, or material outcome —
synthetic multi-session scenarios, vendor-run numbers, never importable as
evidence. **Name-collision flag (verified 2026-09-14, three distinct items):**
our **StateMemBench** (`2608.19652`, UIUC, state-drift probes — no repo
released) vs Microsoft's **STATE-Bench** (enterprise workflow tasks, MIT,
`microsoft/STATE-Bench`, 98 commits) vs **Parslee-ai/statebench**
("conformance test for stateful AI agents", MIT, unrelated v1/v2 scoring).
Cite by arXiv ID or repo URL, never by name alone.

## Next step (bounded)

1. ~~One PDF pass~~ DONE 2026-09-14 (HTML full-text read): generator +
   validation gates + Table 2 + wrapper/control split recorded above.
   Still open: code/dataset release watch (none linked in-paper).
2. If the generator shape transfers, adapt only the
   **fixed-by-construction supersession probe** to our case-authoring guide
   (design, not a run).
3. Otherwise record as **design reference**.

## Verification status

Existence, ID, scale, and design claims **confirmed full-text
(HTML) level**. All numbers **unverified vendor claims — not citable**
(single runs; vendor judge). Paper license arXiv-nonexclusive; **no code/
dataset link in-paper — release watch open**. Cross-refs confirmed: STALE
(`2605.06527`, LLM-adjudicator over schema vs StateMem deterministic pass —
convergent design pressure); STATE-Bench is Microsoft enterprise tasks
(App C confirms distinct). Any future
citation carries version/date/metric under our citation rule. **Second seat done:**
`CORVID-STATEMEMBENCH-PINCHECK.md` (abstract pin passes; baseline labels fixed;
Series A open-verifier set closed).
- Verifier: Corvid (abstract pin ✓ 2026-09-15, `CORVID-STATEMEMBENCH-PINCHECK.md`).

— **muse-drafter**. Phase-B candidate discovery, $0; no score import.
