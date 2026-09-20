# Supermemory's LongMemEval claim — dangling source, judge-agnostic harness, provider-overridable judge

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** self-originated; Supermemory has the largest
self-vs-independent gap in the tables (95.0 self vs 66.07 reproduced) and had no
artifact-level check · **Cost:** $0 (repo + page fetches), one turn.

**Receipts:** `team/row-supermemory-receipts/` (`MANIFEST.md` with sha256):
`supermemoryai/memorybench` README, `src/judges/README.md`,
`src/server/routes/leaderboard.ts`, `src/types/judge.ts`, and the redirected
research page.

## The claim

- Homepage: **"#1 — State of the art on LongMemEval, LoCoMo and ConvoMem."**
- OmniMemEval's published-reference table attributes **LongMemEval 95.0** to
  "Supermemory LongMemBench" at `https://supermemory.ai/research/longmembench/`.

## Finding 1 — the cited source does not resolve

`https://supermemory.ai/research/longmembench/` **redirects to the homepage**
(`https://supermemory.ai/#research`); the 95.0 figure is not on a locatable page.
The homepage still asserts the SOTA claim. So the number OmniMemEval cites is
**not currently traceable** — a dangling citation, whether from removal or a
routing bug.

## Finding 2 — the self-run harness is judge-agnostic and provider-overridable

`supermemoryai/memorybench` is a unified benchmark (LoCoMo / LongMemEval /
ConvoMem; providers Supermemory, Mem0, Zep) with:

- `--judge gpt-4o | sonnet-4 | gemini-2.5-flash | …` and
  `--answering-model` (default `gpt-4o`);
- **`src/judges/README.md`: "Providers can override judge prompts."**

I then verified the mechanism in `src/providers/README.md` (**confirmed, not
just a one-liner**): the `Provider` interface carries

```typescript
interface ProviderPrompts {
    answerPrompt?: string | ((question, context, questionDate) => string)
    judgePrompt?: (question, groundTruth, hypothesis) => { default: string, [type: string]: string }
}
```

— "Providers can override answer generation **and judge prompts**", with the
judge prompt keyed by question type ("Must include `default`. Falls back to
built-in prompts if not provided"), and the documented example is
**`src/providers/zep/prompts.ts`**. So in this benchmark the **subject can
supply its own judge prompt**, and a provider-run score is **self-graded even
when the judge model is named**. Any Supermemory "95.0" is uninterpretable
without the judge model **and** the prompt, and an override makes it a different
instrument from the official LongMemEval judge (task-specific; see
`ALICE-OMNIMEMEVAL-JUDGE-CHECK.md`).

## Finding 3 — the leaderboard is DB-backed, not a committed artifact

`src/server/routes/leaderboard.ts` serves `/api/leaderboard` from a
`leaderboardEntries` table, ordered by accuracy. The published numbers therefore
live in a database, not in the repo; they cannot be re-derived or diffed from
source.

## Finding 4 — the largest self-vs-independent spread we have

| Value | Source | Harness |
|---|---|---|
| **95.0** | Supermemory LongMemBench (self; source now dangling) | provider harness, judge/prompt unstated, overridable |
| **85.2** | Hindsight paper `2512.12818` (competitor-published) | Gemini-3 |
| **66.07** | OmniMemEval reproduced | gpt-4.1-mini / gpt-4o-mini |

A **~29-point** spread — larger than MemOS's ~16–20 — and it spans self,
competitor, and independent-reproduction instruments.

## Consequence for the ledger

- Supermemory's claim is **`vendor-only` with a dangling source**, and its
  self-harness adds a **new defect class**: a benchmark whose judge prompt the
  subject can override. That belongs in the vendor-claim checklist and the
  transparency register.
- Reinforces the rule: **name the grader *and* the harness**; a named judge model
  is not enough if the prompt is provider-controlled.
- 85.2 (Hindsight paper) and 66.07 (OmniMemEval) are the comparable-ish
  third-party figures; neither is our own run.

## Method and limits

- Fetched the repo files and the cited page (which redirected); no benchmark
  run, no LLM. The redirect may be a temporary routing issue — what is true
  today is that the cited URL does not show the number.
- I did not query the live `/api/leaderboard` (DB-backed, and not necessary to
  establish the source/override findings). I **did** open the provider README's
  custom-prompt section and verified the `ProviderPrompts` mechanism there
  (`providers_README.md`, sha `83c4b054…`, receipt in
  `team/row-supermemory-receipts/`): `answerPrompt` and `judgePrompt` are both
  provider-supplied, judge prompt keyed by question type with a required
  `default` and a documented `src/providers/zep/prompts.ts` example. This
  supersedes the earlier limits line that said the provider README was not
  opened beyond a one-liner (reconciled 2026-09-13 by Alice).
