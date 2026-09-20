# Evidence — correction-event class vocabulary and §5.1 field definitions

Each item in `row41-events.jsonl` is one de-identified operator-correction event.
Raw text is **absent by construction** (`SPEC-OUTCOME-PROTOCOL.md` §5.1): the
event carries only a salted hash and structural metadata, so judgement is made on
the event's own structural fields against the definitions below.

## `class` — the frozen vocabulary (exactly one per event)

| class | meaning |
|---|---|
| `env_fact_correction` | the operator corrects an **environment fact** (a path, env var, port, url, version, pin, …) |
| `negation` | the operator negates a prior statement ("no", "not …") |
| `actually` | the operator corrects with an explicit "actually" |
| `wrong` | the operator states a prior action/answer/assumption was wrong |
| `repeated_instruction` | the operator repeats an instruction that was already given |

## Other §5.1 fields

| field | allowed values / meaning |
|---|---|
| `subtype` | a class token, or `null` |
| `env_fact_kind` | `path \| env_var \| port \| url \| version \| pin \| other`, or `null` |
| `quoted_speech` | boolean — the span is quoted third-party speech, not the operator |
| `repeat_group_id` | a group id when the event belongs to a repeated-instruction group, else `null` |
| `normalized_prefix_hash` | salted sha256 (never the prefix) |
| `evidence_span_length` | integer length of the matched span |
| `correction_of_prior_same_fact` | boolean — this correction revisits the same fact as an earlier correction |
| `confidence` | detector confidence in `[0,1]` |
| `confidence`/`turn_index`/`timestamp_bucket` | opaque/structural only |
| `exclusion_filters_applied` | the frozen filters applied before detection |

## The judgement asked

For each event, decide whether its **assigned classification is consistent with
these definitions and vocabularies** — e.g. the `class` is in the vocabulary;
`env_fact_kind` is populated where the class is `env_fact_correction` and `null`
otherwise; `subtype` is in the vocabulary or `null`; `repeat_group_id` is
populated exactly for a repeated-instruction group; `quoted_speech` and
`correction_of_prior_same_fact` are coherent with the rest. Record
`CONSISTENT` or `INCONSISTENT` per event, with a one-line basis when you mark it
inconsistent. This is a **structural-consistency** judgement, not a re-read of
raw text (which is not present).
