# AMB's top external row, checked — Chronos 0.956 is the Claude Opus 4.6 config

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** follow-up to `ALICE-AMB-EXTERNAL-ROWS.md`;
Chronos 0.956 is the row that contradicts Hindsight's "highest score of any
memory system" · **Cost:** $0 (two arXiv fetches), one turn.

**Receipts:** `team/row-chronos-receipts/` (`MANIFEST.md` with sha256): the
Chronos paper (`arXiv:2603.16862`, "Chronos: Temporal-Aware Conversational
Agents with Structured Event Retrieval for Long-Term Memory") abs + HTML + text.

## Finding 1 — the number is faithfully sourced, but it is the strong-model config

The paper evaluates on **LongMemEval-S (500 questions)** and reports two configs:

| Config | Generation model | LongMemEval-S |
|---|---|---|
| **Chronos Low** | **GPT-4o** (to match compared systems) | **92.60%** |
| **Chronos High** | **Claude Opus 4.6** | **95.60%** |

AMB's external row **Chronos 0.956 is Chronos High — the Claude Opus 4.6
configuration**, not the GPT-4o-matched 92.60. So AMB sourced it correctly; the
number is simply not the paper's like-for-like figure.

## Finding 2 — Mastra is from the same strong-model table

The paper's Table 2 ("systems with more advanced LLMs on LongMemEval") gives:

| System | Overall | Footnote |
|---|---|---|
| Chronos High (Ours) | 95.60 | Claude Opus 4.6 |
| Honcho | 92.60 | † category-level not reported |
| **Mastra** | **92.80** | |
| Supermemory | 85.20 | |
| **Hindsight** | **91.40** | ‡ *"Evaluated with an OSS-120B judge model; results are not directly comparable to systems evaluated with the official benchmark judge."* |

AMB's Mastra 0.928 is this row. And the paper independently attributes
**Hindsight 91.40 to an OSS-120B judge**, matching both the Hindsight Technical
Report's 91.4 and MemBukkit's "judge swapped" caveat.

## Finding 3 — the "highest" comparison is not matched

So AMB's top two rows compare **different answerer models**:

| AMB row | Number | Answerer |
|---|---|---|
| Chronos | 0.956 | Claude Opus 4.6 |
| Hindsight | 0.946 | Gemini 3.1 Pro |

The paper's matched GPT-4o number for Chronos is **92.60** — below Hindsight's
94.6. So the honest statement is: **Hindsight's "highest score of any memory
system" is contradicted only inside a non-matched comparison**, and no matched
head-to-head exists at the top of AMB's table. AMB itself labels these rows
"not directly comparable." The `contradicted` entry for the "highest" wording
should carry that caveat, or be downgraded to "not established."

## Finding 4 — the Chronos paper documents judge variability

The paper uses LongMemEval's **category-routed LLM judge** and reports manual
inspection of specific failures where it believes the judge was wrong (e.g.
`6d550036`, `75f70248`), "highlighting LLM-as-judge variability." That is a
third independent source (after the Mem0 paper and MemBukkit) flagging the
benchmark's judge as the unstable part — evidence for the "name the grader"
rule rather than a defect.

## What this gives the ledger

- AMB's external registry is **faithful to its sources** — the Chronos and
  Mastra rows reproduce the Chronos paper's Table 2 exactly.
- But the top of the leaderboard **mixes model tiers**: Chronos High
  (Opus 4.6) vs Hindsight (Gemini 3.1 Pro) vs the paper's GPT-4o reference
  (Chronos 92.6). Any portfolio comparison must pin the answerer, not just the
  system.
- The Chronos paper is a clean, citable attribution for **Hindsight 91.4 =
  OSS-120B judge**, which the collision register can use instead of MemBukkit's
  secondhand note.

## Method and limits

- Read the paper's HTML full text (stripped) and extracted the config statements
  and Table 2 verbatim; no benchmark, engine, or LLM run.
- I did not verify Chronos's 95.60 beyond the paper's own report (self-reported),
  nor open the dataset-repo issues it cites about judge variability.
