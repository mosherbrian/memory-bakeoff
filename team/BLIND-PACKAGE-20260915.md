# BLIND PACKAGE (round 2) — independent judging (conductor-claude)

**Prepared:** 2026-09-15 · **For:** conductor-claude (S3-4 blind seat) · **Cost:** $0, local.
**What this is:** two sets of items with their evidence attached, for you to judge
**independently**. This file and `team/blind-package-20260915/` contain **no team
verdicts and no result counts** — not a pass/fail, not a rate, not an outcome
label. Your judgements are the only verdicts here.

**Blind rule:** record every verdict in the template below **before** opening any
other `team/` note about these items, and do not copy any figure from elsewhere
into your basis. Judge only from the evidence in
`team/blind-package-20260915/`.

---

## Task A — standard-tier corpus topic-reachability labels

- **Question (per item):** is the scenario's `declared_topic_reachable` label
  consistent with the trigger rule, given the moment prompt and the record
  summaries?
- **Rule / criteria:** `team/blind-package-20260915/trigger-rule.md`.
- **Items:** `team/blind-package-20260915/standard-labels.jsonl` — one item per
  scenario, keyed by `item_id` (`SA-<scenario_id>`). Fields: `scenario_id`,
  `family`, `moment_prompt`, `record_summaries`, `declared_topic_reachable`.
- **Supporting evidence:** `team/blind-package-20260915/standard-corpus.jsonl` —
  the scenario records and turns the rule operates on.
- **Record:** `AGREE` or `DISAGREE` for each `item_id`; a one-line basis only
  when you mark `DISAGREE`.

## Task B — correction-event classifications

- **Question (per item):** is the event's assigned classification (`class` and
  the related §5.1 fields) consistent with the class vocabulary and field
  definitions?
- **Rule / criteria:** `team/blind-package-20260915/class-definitions.md`.
- **Items:** `team/blind-package-20260915/scale-events.jsonl` — one item per
  de-identified event, keyed by `item_id` (`RC2-<event_id prefix>`); each carries
  `class`, `subtype`, `env_fact_kind`, `quoted_speech`, `repeat_group_id`,
  `correction_of_prior_same_fact`, and other structural fields. Raw text is
  absent by construction.
- **Record:** `CONSISTENT` or `INCONSISTENT` for each `item_id`; a one-line basis
  only when you mark `INCONSISTENT`.

---

## Verdict template (fill this in)

```
# BLIND VERDICTS (round 2) — conductor-claude · <date>

## Task A — standard-tier reachability labels
| item_id | AGREE / DISAGREE | basis (only if DISAGREE) |
|---|---|---|
| SA-... | | |

## Task B — correction-event classifications
| item_id | CONSISTENT / INCONSISTENT | basis (only if INCONSISTENT) |
|---|---|---|
| RC2-... | | |
```

## Evidence directory contents (sha256)

| file | sha256 |
|---|---|
| `team/blind-package-20260915/trigger-rule.md` | `92ae1da233cef5edd7a1218f98123fcd4fe7cce5f1478674ac16856ab83a3d30` |
| `team/blind-package-20260915/standard-labels.jsonl` | `c99338ec64c39a20bdfafa95809718d5435ca3661c1129df8ef4a9051c1e1f81` |
| `team/blind-package-20260915/standard-corpus.jsonl` | `2fa0694bf319da9ce357ed3bdae35962c3ff9469aaec71ad122375155a4bcd44` |
| `team/blind-package-20260915/class-definitions.md` | `c7a2354781a15a9c61ce6b8cd164ee9ce3982a581ee5e5ef42677d904248a38a` |
| `team/blind-package-20260915/scale-events.jsonl` | `f9908e012d69039cbd698d5f554cb61331db3621607fe4dfa24010d36e8022cc` |

## Provenance

Task A items are the standard-tier corpus's declared reachability labels, joined
to each scenario's moment prompt and record summaries. Task B items are the
scaled de-identified correction-event bundle (`SPEC-OUTCOME-PROTOCOL.md` §5.1),
re-emitted with an `item_id` added and nothing removed. Neither set carries the
team's verdicts, counts, or labels for these items.

— prepared by Corvid (`worker-glm-dsh3`). $0, local; no raw transcript content.
