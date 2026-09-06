# Gen114 — the reader question, finally measured

**Q4: `REPLICATED_ACROSS_CORES`.** All four cores passed their control gates
9/9 and are interpretable. The effect holds in every one.

Evidence class: `controlled_reader_interference`. Attempt:
`results/gen114/attempt1/`, 60 of 60 calls completed, manifest verifies, raw
requests and responses sealed and hashed **before** anything was parsed.

## The result

**Q1 — does a stale record alongside the current one change the answer? Yes, in
all four cores.**

| condition | cells | outcome |
|---|---|---|
| `CLEAN_CURRENT` | 12 | **12 correct** |
| `CONFLICT_STALE_FIRST` | 12 | **12 contradictory** |
| `CONFLICT_CURRENT_FIRST` | 12 | 9 contradictory, 3 correct |
| `CLEAN_STALE_NEGATIVE_CONTROL` | 12 | 12 correct (control works) |
| `INSUFFICIENT_CONTROL` | 12 | 12 correct abstentions |

Given only the current record the reader is right every time. Add the superseded
version and it contradicts itself in **21 of 24** conflict cells — asserting both
values at once:

```json
{"answer": "27 t/s and 41 t/s after the cache fix",
 "citations": ["REC-B211D4D705", "REC-6E236CCB3A"]}
```

It does not pick the stale value over the current one. It refuses to choose.

**Q2 — does presentation order matter? In one core of four.**

| core | stale first | current first | order effect |
|---|---|---|---|
| `throughput:atlas` | 3 contradictory | 3 contradictory | no |
| `branch:vega` | 3 contradictory | 3 contradictory | no |
| `oncall:kestrel` | 3 contradictory | 3 contradictory | no |
| **`budget:solstice`** | **3 contradictory** | **3 correct** | **yes** |

In `budget:solstice` the identical two records, differing only in sequence,
produce a completely different outcome — contradiction when the stale record
comes first, correct answers when the current one does. The other three cores are
unmoved by order.

**Q3 — does the reader prefer current truth when both are available? No**, in
any core. Not one core has all conflict cells correct.

**Q5/Q6** — the parser and all 20 prompt hashes matched the frozen v4 payload
before the endpoint was touched.

## Why this result is trustworthy where Gen110's was not

Every control passed, and the controls are what make the rest readable:

- `CLEAN_CURRENT` 12/12 — the reader *can* answer these questions.
- `CLEAN_STALE_NEGATIVE_CONTROL` 12/12 — the stale record *can* drive an answer
  when it is the only evidence, so the contradictions are not the reader
  ignoring one record.
- `INSUFFICIENT_CONTROL` 12/12 — it abstains correctly when nothing supports an
  answer, so it is not simply answer-hungry.

The gate was conservative and predeclared: nine of nine exact control cells per
core, or that core reports `NOT_INTERPRETABLE`. Nothing was weakened to reach a
result.

The ruler was frozen and fingerprinted at Gen113 before any of these outputs
existed, its digest and file hash were checked separately against values named
in the instruction, and its behaviour was verified by independent reconstruction
before the first scored call.

## What this does and does not establish

**Establishes:** under this exact pinned configuration — local
`qwen3.6-35b-vulkan-nothink`, temperature 0, seed 0, stateless, one blinded
prompt per call — putting a superseded record beside the current one makes this
reader contradict itself, in all four semantic cores, and in one core the effect
depends on which record appears first.

**Does not establish:** that any tested memory product presents this context or
this order. Gen114 *controls* which benchmark-owned records the reader sees. It
is not raw-product evidence, not full-product evidence, and not a claim about
any other model or configuration. Three repetitions with descriptive counts only
— no significance tests, no thresholds, no post-hoc exclusions.

## Why it matters for the round it came from

Round 3 established that **every** engine co-returns the superseded record
alongside the current one — 192 of 192 — and that only explicit lineage removes
it. The open question was whether that co-return actually costs anything.

It does. On this reader, in this configuration, stale co-return turns a reliably
correct answer into a self-contradicting one.
