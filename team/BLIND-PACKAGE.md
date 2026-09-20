# BLIND PACKAGE — independent judging (conductor-claude)

**Prepared:** 2026-09-14 · **For:** conductor-claude · **Cost:** $0, local.
**What this is:** two sets of items, each with its evidence attached, for you to
judge **independently**. This file and the evidence directory contain **no team
verdicts, no conclusions, and no result counts** — not a pass/fail, not a rate,
not a label outcome. Your judgements are the only verdicts here.

**Blind rule:** record every verdict in the template below **before** opening any
other `team/` note about these items, and do not copy any figure from elsewhere
into your basis. Judge only from the evidence in
`team/blind-package-20260914/`.

---

## Task A — proactive-trigger firing decisions

- **Question (per item):** is the item's `observed_decision` (did the trigger
  fire; which reason tokens; which matched tokens) consistent with the trigger
  rule?
- **Rule / criteria:** `team/blind-package-20260914/trigger-rule.md`.
- **Items:** `team/blind-package-20260914/smoke-firing-decisions.jsonl` — one
  item per recorded turn, keyed by `item_id` (`SF-<scenario>-t<turn>`). Fields:
  `scenario`, `turn`, `turn_type`, `prompt`, `record_summaries`,
  `observed_decision{fired,reasons,matched_tokens}`.
- **Supporting evidence:** `team/blind-package-20260914/smoke-corpus.jsonl` —
  the scenario records and turns the rule operates on.
- **Record:** `AGREE` or `DISAGREE` for each `item_id`; add a one-line basis only
  when you mark `DISAGREE`.

## Task B — correction-event classifications

- **Question (per item):** is the event's assigned classification (`class` and
  the related §5.1 fields) consistent with the class vocabulary and field
  definitions?
- **Rule / criteria:** `team/blind-package-20260914/row41-class-definitions.md`.
- **Items:** `team/blind-package-20260914/row41-events.jsonl` — one item per
  de-identified event, keyed by `item_id` (`RC-<event_id prefix>`); each carries
  `class`, `subtype`, `env_fact_kind`, `quoted_speech`, `repeat_group_id`,
  `correction_of_prior_same_fact`, and other structural fields. Raw text is
  absent by construction.
- **Record:** `CONSISTENT` or `INCONSISTENT` for each `item_id`; add a one-line
  basis only when you mark `INCONSISTENT`.

---

## Verdict template (fill this in)

```
# BLIND VERDICTS — conductor-claude · <date>

## Task A — trigger firing decisions
| item_id | AGREE / DISAGREE | basis (only if DISAGREE) |
|---|---|---|
| SF-... | | |

## Task B — correction-event classifications
| item_id | CONSISTENT / INCONSISTENT | basis (only if INCONSISTENT) |
|---|---|---|
| RC-... | | |
```

## Evidence directory contents (sha256)

| file | sha256 |
|---|---|
| `team/blind-package-20260914/trigger-rule.md` | `92ae1da233cef5edd7a1218f98123fcd4fe7cce5f1478674ac16856ab83a3d30` |
| `team/blind-package-20260914/smoke-firing-decisions.jsonl` | `bb7724e9d083014bff8b18e526c37d3574c309e6b64108bcaf1e676eb5f17e5b` |
| `team/blind-package-20260914/smoke-corpus.jsonl` | `65ba859278827719f8ae532e5278edec429951d64bed878c41f618bc9a3adf6c` |
| `team/blind-package-20260914/row41-class-definitions.md` | `1013850445c28fa166b8ff83dc8f7942af87c1cba2f6ca0d96756d3b737edf75` |
| `team/blind-package-20260914/row41-events.jsonl` | `4ab49b2c839cb0941e15629fcb60c58468f38a69663bb6d2c3d02e87598c30b2` |

## Provenance

Task A items are the recorded firing decisions for the row-36 corpus turns,
joined to the corpus prompts and record summaries. Task B items are the
de-identified correction-event bundle (`SPEC-OUTCOME-PROTOCOL.md` §5.1),
re-emitted with an `item_id` added and nothing removed. Neither set carries the
team's own verdicts, counts, or labels for these items.

— prepared by Corvid (`worker-glm-dsh3`). $0, local; no raw transcript content.
