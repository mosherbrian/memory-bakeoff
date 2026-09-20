# Row 36 corpus — binding-trigger reachability check (second seat, goal 2)

**Seat:** Cairn (worker-pi) · **Date:** 2026-09-14 ~12:1x PDT · **Cost:** $0, local, read-only
**Scope:** re-derive the `topic_reachable` labels of `team/invocation-corpus-v1/` under the
**binding** trigger logic — `tokensOf`/`topicMatches` in
`implementer/repo/extensions/pi-change-trigger/index.ts` (tokens len ≥ 4, trigger STOPWORDS,
topic set = record **summaries** only, per `topicsFromNotifyFile`) — not the corpus
selftest's own naive tokenizer (len > 2, different stop list).

## Method

Python re-implementation of `tokensOf` (regex `[a-z0-9][a-z0-9-]{3,}`, same 48-word
STOPWORDS set, verified line-by-line against index.ts:95-110) applied to each scenario's
moment prompt vs its record summaries. Scratch only; committed corpus untouched.

## Result: 11/12 labels hold; S09 is a real defect (confirms Corvid R1)

| scenario | manifest label | binding-trigger match | shared tokens |
|---|---|---|---|
| S01 | topic | fires | service, port |
| S02 | offtopic | no fire | — |
| S03 | topic | fires | results |
| S04 | offtopic | no fire | — |
| S05 | topic | fires | deploy, legacy |
| S06 | offtopic | no fire | — |
| S07 | topic | fires | retry |
| S08 | offtopic | no fire | — |
| **S09** | **topic** | **NO FIRE** | **∅** |
| S10 | offtopic | no fire | — |
| S11 | topic | fires | restart |
| S12 | offtopic | no fire | — |

**S09 (repeated_instruction):** summary `signoff required`; moment prompt
`Ship the queue worker rollout.` — zero shared tokens. The semantic link is
`rollout`, which lives in the record **content** (`every rollout needs a signoff line
from on-call`), but the trigger never reads content — summaries only. So S09 is a
topic moment that **cannot fire on `topic` by construction**: counted as labeled, it is a
guaranteed FBMR miss and the true split is 5 topic-reachable / 7 not, not 6/6.

**Corvid R2 resolved as non-issue:** S02/S04/S06/S08's naive-tokenizer overlaps do not
survive the trigger's len ≥ 4 + stopword filter — all four are correctly unreachable
under the binding check. No change needed.

## Proposed fix (one line, builder's call — corpus is worker-glm-2's artifact)

S09 moment prompt → `Get the signoff line for the queue worker rollout.`
(keeps the family's semantics, adds the summary token `signoff`; re-run selftest +
hashes after). Alternative: relabel S09 offtopic — but that leaves the
repeated_instruction family with no topic moment and breaks the 6/6 split, so the
prompt fix is preferred.

## Consequence for the smoke run

Do not compute FBMR_topic over the 6 labeled topic moments until S09 is fixed or
relabelled — the denominator would carry a structurally unfireable moment.

No S4/S5 figures in this note.
