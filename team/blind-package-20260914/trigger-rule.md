# Evidence — the proactive-trigger fire rule (as tested)

The trigger observes each prompt in a fresh per-scenario process and may fire
with one or more **controlled reason tokens**: `{fresh, gap, topic}`.

- **`fresh`** — the first prompt of the process. Fires only on turn 1.
- **`gap`** — at least 30 minutes since the previous prompt. Not reachable when
  turns are minutes apart.
- **`topic`** — the prompt shares at least one token with the scenario's **topic
  set**. The topic set is built from the **record summaries only** (record
  `content` is never read by the trigger). The tokens shared are reported as
  `matched_tokens`.

## Tokenization (exact)

```
tokensOf(text) = (text.toLowerCase().match(/[a-z0-9][a-z0-9-]{3,}/g) ?? [])
                   .filter(t => !STOPWORDS.has(t))
```

So a token qualifies only if it is **4+ characters** of `[a-z0-9-]` and is not a
stopword. `matched_tokens` = the set intersection of `tokensOf(prompt)` and the
topic set.

## STOPWORDS (exact)

```
this that with from into have been will shall they them their there then than
when what which where were been also only over under about after before while
being does done each such some more most other same very upon said create
created decision environment project trial record tool call confirm confirmed
draft pending campaign1 campaign-1 window opening exists never still uses using
used
```

## The judgement asked

For each item in `smoke-firing-decisions.jsonl` (fields: `scenario`, `turn`,
`turn_type`, `prompt`, `record_summaries`, `observed_decision` with `fired`,
`reasons`, `matched_tokens`), decide whether the **observed decision is
consistent with this rule** — i.e. whether it fires/does not fire and reports the
reason and matched tokens the rule produces for that prompt and topic set.
Record `AGREE` or `DISAGREE` per item, with a one-line basis when you disagree.
