# Verification — Phase-B candidate card 4 (MemSecBench + GateMem)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-14 01:2x UTC · **Cost:** $0, primary-source reads, one turn.
**Trigger:** standing second-check of `CANDIDATE-CARD-MEMSEC-GATEMEM.md`; continues
`ALICE-CANDIDATE-CARDS-VERIFY.md` (cards 1–3). No tree modified.

## Verdict

**All of card 4's numbers reproduce verbatim from the primary source; the GateMem
characterization is supported; both repos resolve.** No correction needed.

## MemSecBench ([arXiv 2607.27080](https://arxiv.org/abs/2607.27080), full text)

| card claim | source text | verdict |
|---|---|---|
| 310 cases from 48 realistic contexts | abstract: "310 cases drawn from 48 realistic contexts" | **CONFIRMED** |
| 24 configurations = 2 harnesses × 4 memory backends × 3 LLM backends | "a 24-configuration matrix of two agent harnesses, four memory backends, and three LLM backends" (2·4·3 = 24) | **CONFIRMED** |
| malicious memory persists in **84.2%** | "malicious memory persists in 84.2% of all cases" | **CONFIRMED** |
| full Write–Execute chain succeeds in **50.3%** | "the full Write–Execute chain succeeds in 50.3%" | **CONFIRMED** |
| among poisoned cases, **59.6%** complete Execute | "Among successfully poisoned cases, 59.6% complete the full Execute chain" | **CONFIRMED** |
| **56.1%** achieve selective repair | "while 56.1% achieve selective repair" | **CONFIRMED** |
| spread **16.1 pp** end-to-end, **41.3 pp** repair | "largest absolute differences are 16.1 percentage points for end-to-end attack success and 41.3 percentage points for selective repair" | **CONFIRMED** |
| seven programmatic gates | "programmatic gates across seven lifecycle checkpoints" | **CONFIRMED** (paraphrase is fair) |

(One table in the paper shows a per-config 59.68% — truncation of the aggregate
59.6% the card uses; not a discrepancy. The card's "harness × memory backend ×
LLM backend" ordering matches the paper.)

## GateMem ([arXiv 2606.18829](https://arxiv.org/abs/2606.18829))

- Exists; multi-principal shared-memory benchmark with hospitals/workplaces/
  campuses/households (card: medical/office/education/household — matches the
  listed domains).
- Evaluates "agent-facing **active forgetting after explicit deletion
  requests**" and reports that "**no method simultaneously achieves strong
  utility, robust access control, and reliable forgetting**" — so the card's
  "the delete side of supersession … and it *fails*" is **supported**.
- Repos: [`rzhub/GateMem`](https://github.com/rzhub/GateMem) **200**,
  [`Ray368/GateMem`](https://huggingface.co/datasets/Ray368/GateMem) **200**.
- **License:** the abs page states no CC link; the card correctly lists
  repo/license as **to verify** (not claimed).

## Net

Card 4 is numerically sound; its bounded next steps (GateMem/MemSecBench
licences, scope-isolation addendum to the P3/P4 gate) are the right ones. No
number is wrong. Recommend proceed.

## Limits

- Abstract + full text (MemSecBench) and abstract (GateMem); "confirmed" = the
  source states the figure, not that I reproduced it. No data or repo contents
  downloaded beyond a HEAD.
