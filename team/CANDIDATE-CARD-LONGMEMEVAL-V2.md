# Candidate card — LongMemEval-V2 (environment-experience memory for web agents)

**Author:** muse-drafter (proposal-drafter seat), Phase-B frontier harvest (Sprint-2 goal 5)
**Date:** 2026-09-14 · **Cost:** $0 (abstract-level web reads only)
**Status:** **candidate discovery only — no score import.** Card 7 of the named
benchmarks in `RESEARCH-INTELLIGENCE-DIRECTIVE.md`, assessed against our goals
G1–G5 (`CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md` §4).

## Provenance (abstract-level; PDF not read)

| Field | Value |
|---|---|
| Title | *LongMemEval-V2: Evaluating Long-Term Agent Memory Toward Experienced Colleagues* |
| Authors | Di Wu, Zixiang Ji, Asmi Kawatkar, Bryan Kwan, Jia-Chen Gu, Nanyun Peng, Kai-Wei Chang |
| ID / dates | [arXiv:2605.12493](https://arxiv.org/abs/2605.12493) v1 2026-05-12 ("Work in Progress"); presented ICML 2026 SCALE workshop |
| Paper license | **CC BY 4.0** (abstract) |
| Code | [`xiaowu0162/LongMemEval-V2`](https://github.com/xiaowu0162/LongMemEval-V2) — **Apache-2.0** (raw `LICENSE` + GitHub API; Corvid pin 2026-09-15) |
| Data | HF `xiaowu0162/longmemeval-v2` — **Apache-2.0** (API-verified; `SPARK-LMEV2-DATA-LICENSE-NOTE`) |
| Scale | **451 manually curated questions**, histories up to **500 trajectories / 115M tokens** (ICML page: 25M–115M; Small/Medium splits) |
| Numbers | vendor-reported only: AgentRunbook-C 72.5% avg (70.1% Medium / 74.9% Small per ICML), RAG baseline 48.5%, off-shelf coding agent 69.3%, frontier LLMs ≤14.1% without trajectory evidence — **NOT verified, do not cite** |

## What it is (from the abstract)

Not a v2 of the chat-assistant LongMemEval — a different benchmark for a
different job: can a memory system accumulate **environment-specific
experience** (interface affordances, state dynamics, workflows, recurring
failure modes, "gotchas") so a web agent becomes a knowledgeable colleague?
Five abilities: static state recall, dynamic state tracking, workflow
knowledge, environment gotchas, premise awareness. Formulation is
**context-gathering**: memory consumes history trajectories and returns
compact evidence for downstream QA. Two reference methods: AgentRunbook-R
(RAG over raw states/events/strategy notes) and AgentRunbook-C (trajectories
as files + coding agent gathering evidence in a sandbox).

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G1 conflict handling** | weak | no conflicting-record design |
| **G2 supersession** | partial | dynamic state tracking + premise awareness touch it; no lineage |
| **G3 invocation** | weak | no proactive deadline |
| **G4 material outcome** | partial | web-task experience, not coding task time/errors/corrections |
| **G5 continuity** | partial | 115M-token histories, but web trajectories not longitudinal work |

## Comparability warning (load-bearing)

**LME-V2 ≠ LongMemEval.** Assay already flagged this (Agent Zero's
"LongMemEval" number is not LME-V2). The v1 benchmark (chat assistants,
500 questions, ICLR 2025) and V2 (web-agent environment experience, 451
questions) share authors and a name prefix, nothing else. Any citation
must say which one with ID + date, or it is a misattribution.

## What it offers us

- **The context-gathering formulation** (memory returns compact evidence
  for a downstream decider) as a design reference for our delivered-level
  rule — it separates formation quality from use quality by construction.
- **"Gotchas + premise awareness" as question types** — the closest
  published analogue to our stale-instruction concern in an agentic
  setting (environment gotchas ≈ decommissioned deploy paths).
- **A caution:** AgentRunbook-C (coding agent over trajectory files) beats
  RAG 72.5 vs 48.5 per vendor — evidence-gathering *mechanism* dominates,
  convergent with our mechanisms-over-brands stance, not evidence for it.

## What it cannot ground

Coding conflict/supersession, invocation, or material coding outcome — web
shopping/forum/admin/ServiceNow-style environments, vendor-run, "Work in
Progress". Scores never importable.

## Next step (bounded)

1. One PDF pass (methods + gotcha/premise items + license/code link);
   record all (owner: goal-5 remainder).
2. If the gotcha-item shape transfers, adapt it to a stale-path probe for
   our supersession cases (design, not a run).
3. Otherwise record as **design reference**.

## Verification status

Existence, ID, authors, scale, and the five abilities **confirmed abstract-level**.
**Licenses verified:** paper CC BY 4.0; code Apache-2.0 (raw LICENSE + API); data
HF Apache-2.0. **Second seat done:** `CORVID-LMEV2-PINCHECK.md` (abstract-level
pin passes; comparator warning endorsed). All numbers **unverified vendor claims —
not citable**; PDF details still to read.
- Verifier: Corvid (abstract pin ✓ 2026-09-15, `CORVID-LMEV2-PINCHECK.md`).

— **muse-drafter**. Phase-B candidate discovery, $0; no score import.
