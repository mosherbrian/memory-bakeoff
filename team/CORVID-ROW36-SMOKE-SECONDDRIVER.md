# Row-36 post-fix smoke — second-driver re-derivation (36/36, rates confirm the fresh ruling)

**Author:** Corvid (`worker-glm-dsh3`), design seat
**Date:** 2026-09-14 · **Cost:** $0, local, read-only (no live process, no LLM)
**Subject:** `CAIRN-ROW36-SMOKE-POSTFIX-RESULTS.md` and its run artifact
`/tmp/row36-postfix-1842/results.jsonl` (36 rows).

## Method

Re-derived every turn's fire decision **from the corpus + the binding trigger**
(not from Cairn's code path): `tokensOf` (len ≥ 4, trigger `STOPWORDS`, record
**summaries** only) via the same logic in
`scripts/check_invocation_corpus_reachability.py`; turn 1 fires `fresh`, `gap`
cannot fire at smoke cadence. Compared `(fired, reasons, matchedTokens)` against
each row's recorded `got`.

## Result

```
turns = 36   mismatches = 0
filler_plain topic fires = 0/15   ·   fresh fires = 12
moment_topic fires = 6/6
```

- **36/36 agree** with the run's own `got` column, so the post-fix smoke's fire
  decisions reproduce from the corpus and the trigger spec — independently of the
  harness that produced them.
- **`FalseFire = 0/15`** on the shipping definition (`fired(topic)` on
  `filler_plain`; fresh excluded per the 2026-09-14 ruling) — the literal 12/15
  is exactly the 12 structural `fresh` t1 fires.
- **`FBMR_topic = 6/6`**, `NearMissFire` 1/3 (F2 positive, not re-checked here).

## Limits

Re-derives the recorded run from its inputs; it does not re-run the live `pi`
process (Cairn's differential `evaluateFire` replay already covers the TS path,
and my guard covers the Python binding). The `/tmp` run dir is ephemeral, so this
is a point-in-time receipt, not a durable artifact.

— **Corvid** (`worker-glm-dsh3`). $0, read-only.
