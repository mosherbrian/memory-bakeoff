# Candidate card — MemSecBench + GateMem (memory security & governance)

**Author:** Corvid (`worker-glm-dsh3`), Phase-B frontier harvest (Sprint-2 goal 5)
**Date:** 2026-09-14 · **Cost:** $0 (abstracts) · **Status:** **candidate
discovery only — no score import.** Card 4 of the named benchmarks in
`RESEARCH-INTELLIGENCE-DIRECTIVE.md`; seeds thread-pool item 5 (the
security/governance arm we do not have).

## Provenance (verified)

| Field | MemSecBench | GateMem |
|---|---|---|
| Title | *MemSecBench: Tracking Agent Memory Poisoning from Persistence to Consequence and Repair* | *GateMem: Benchmarking Memory Governance in Multi-Principal Shared-Memory Agents* |
| Authors | Xuanze Chen, Xukang Xie, Wentao Fu, Jiajun Zhou, Shanqing Yu, Qi Xuan | Zhe Ren, Yibo Yang, Yimeng Chen, Zijun Zhao, Benshuo Fu, Zhihao Shu, Bingjie Zhang, Yangyang Xu, Dandan Guo, Shuicheng Yan |
| ID / date | [arXiv:2607.27080](https://arxiv.org/abs/2607.27080), 2026-07-29, cs.CR | [arXiv:2606.18829](https://arxiv.org/abs/2606.18829), 2026-06-17, cs.LG |
| Artifacts | GateMem code `rzhub/GateMem` — **MIT** (GitHub API, 142★); GateMem data `Ray368/GateMem` — **CC-BY-4.0 in `cardData`** (top-level field null); MemSecBench — no artifact found. Corvid pin 2026-09-15 |

## What they are (from the abstracts)

- **MemSecBench** — a **task-grounded lifecycle-security** benchmark: 310 cases
  from 48 realistic contexts (code/science, daily life, office work), each run
  under a controlled **Write–Execute–Forget** protocol in an isolated runtime
  (harness × memory backend × LLM backend; 24 configs), adjudicated over **seven
  lifecycle checkpoints** (deterministic write check + checkpoint judges +
  programmatic gates). Findings: malicious memory persists in **84.2%** of cases;
  the full Write–Execute chain succeeds in **50.3%**; among poisoned cases,
  **59.6%** complete Execute and **56.1%** achieve selective repair; the spread
  across memory stacks reaches **16.1 pp** end-to-end and **41.3 pp** on repair.
- **GateMem** — **multi-principal shared memory** (medical, office, education,
  household): multiple principals write to one pool and query under different
  roles/scopes. It jointly evaluates utility with state updates, **access control
  across authorization boundaries**, and **active forgetting after deletion**,
  with long multi-party episodes, hidden checkpoints and **leak-target
  annotations**. Finding: no method gets utility + access control + reliable
  forgetting at once; long-context prompting gives the best governance score at
  high token cost, while retrieval/external memory is cheaper but **leaks
  unauthorized or deleted information**.

## Map to our goals — a new cross-cutting dimension

| Goal | Fit | Notes |
|---|---|---|
| **G1 conflict handling** | partial | poisoned/unauthorized state is a conflict class we do not model |
| **G2 supersession** | partial | GateMem's "forget after deletion" is the delete side of supersession — and it *fails*, which is our false-supersession family from the other direction |
| **G3 invocation** | weak | no proactive deadline |
| **G4 material outcome** | partial | leakage/repair is a **harm outcome** beside our prohibited@5 |
| **G5 continuity** | partial | long multi-party / multi-session episodes |
| **New: security & governance** | **strong, but partly covered** | trust labels / principal access control and selective repair are genuinely new; **single-principal scope isolation is already measured and closed** (Gen76/78 — see `CORVID-SCOPE-LEAKAGE-GATE-ADDENDUM.md`), so only the multi-principal axis is net-new |

## What they offer us

- **A threat model for the P3/P4 gate:** MemSecBench's
  **Write→Execute→Forget** chain + checkpoint adjudication is a ready-made shape
  for a *memory-security* companion to our lifecycle gate.
- **GateMem's access-control and leak-target annotations** map onto our gap —
  the directive's "scope like an access-control system" point. **Correction
  (see `CORVID-SCOPE-LEAKAGE-GATE-ADDENDUM.md`):** single-principal scope
  isolation is already measured and closed (Gen76 audit, Gen78 ablation 6/6 →
  0/6 on all three engines), and `frozen_reader.py` already computes
  wrong-scope context/answer rates. The net-new part is **multi-principal /
  role / trust-label** authorization, not scope isolation itself.
- **Leakage as a reported harm:** both show retrieval/external memory can leak
  unauthorized or deleted content; we should report **leakage** alongside
  `prohibited@5` and exact context size, never fold it into a recall score.
- **A discriminating direction for our E-7 result:** agentmemory's
  418/450 false supersession and GateMem's failed active forgetting are the same
  delete/repair failure seen from two sides — a mechanism claim worth testing.

## What it cannot ground

Coding-memory conflict/supersession, proactive invocation timing, or
single-user material outcome. Neither is a coding benchmark; scores are not
importable.

## Next step (bounded)

1. Verify `rzhub/GateMem` + `Ray368/GateMem` licenses and whether a MemSecBench
   artifact exists (owner Corvid; one turn).
2. **Done this pulse:** the scope-isolation + trust-label + leakage-reporting
   addendum is drafted as `team/CORVID-SCOPE-LEAKAGE-GATE-ADDENDUM.md` (design,
   not a run), correcting this card's "scope isolation is absent" to
   "single-principal scope is closed; multi-principal access control is new";
   offer the security arm to Assay's instrument-power register.
3. Optionally add a `leakage` count beside `prohibited@5` in the outcome
   reporting shape.

## Verification status

Existence, abstracts, dates and the GateMem code/data links **confirmed** in this
pass. All quantitative findings are **abstract-level, not reproduced**. Artifacts
confirmed: GateMem code **MIT** (142★) / data **CC-BY-4.0 (`cardData`)**;
MemSecBench **no artifact**. Any future citation
carries version/date/metric under our citation rule.

**Verifier: Alice** (Series A second seat; `ALICE-CANDIDATE-CARD-4-VERIFY.md`) +
**Corvid** abstract pin ✓ 2026-09-15 (`CORVID-MEMSEC-GATEMEM-PINCHECK.md`, artifacts closed).

— **Corvid** (`worker-glm-dsh3`). Phase-B candidate discovery, $0; no score
import.
