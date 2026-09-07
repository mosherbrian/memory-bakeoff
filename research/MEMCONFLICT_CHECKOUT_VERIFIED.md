# MemConflict checkout materialised and verified against the Gen36 pin

2026-09-07. `DECISION_MEMO.md` row 5 needs the four unmeasured local engines run
against this benchmark. The dataset was pinned at Gen36 and the checkout has
been absent from the tree ever since; `external/` is gitignored, so nothing was
holding it.

## Verification

    recorded in research/MEMCONFLICT_PIN.json (Gen36)
      upstream   TaoZhen1110/MemConflict @ ec51d5d36e87f7665d1337f3a88cbde95fc2a964
      dataset    Data/Step4_4.jsonl
      bytes      39,671,712
      sha256     8ef9ec8589eccb86f63ab3a819a9180217405351a8d5846866721ea74babe092

    fetched 2026-09-07, same commit
      bytes      39,671,712                                     MATCH
      sha256     8ef9ec8589eccb86f63ab3a819a9180217405351a8d5846866721ea74babe092   MATCH

**The pin recorded a year-old measurement of a third-party artifact and it still
verifies byte for byte.** That is the provenance discipline working: the Gen38
results were computed against exactly these bytes, and anything computed now is
comparable to them without an argument.

## What is present

- `Data/Step4_4.jsonl` — 30 personas, the released benchmark file.
- `Code/` — the upstream construction pipeline, Step1 through Step4 plus
  `run_construction_pipeline.py`. **Construction, not evaluation.** These are the
  stages `MEMCONFLICT_PIN.json` records as `not_run`, and they remain not-run:
  they would REBUILD the benchmark, which is the opposite of what row 5 needs.
- `Evaluation/` — sparse at this commit; our Gen36-38 lane used its own
  adapters, which is why the Gen38 run did not depend on it.

## What this does and does not unblock

**Unblocked:** running Habitus, agentmemory, Hindsight and MemBukkit against the
same frozen contract and the same held-out slice that produced the Gen38 numbers
for perseus and mem0. That is row 5, and it is now a matter of adapter work
rather than of missing data.

**Still blocked, and deliberately:** the upstream LLM-judge lane. The Gen38
record marks it `requires_reader_authorization`, and nothing here changes that.

**Not attempted:** the six upstream harnesses (`a_mem`, `langmem`, `letta`,
`memobase`, `memos`, `memzero`). Those live in the paper's own ablation tree and
each needs its own environment. They are a separate decision from row 5.

## Cost of what was just done

A shallow `--filter=blob:none` clone and a sparse checkout of three paths.
No reader, no GPU, no holdout item, no engine run. The 182 MB figure quoted in
the intake was the full history; the pinned artifacts are 38 MB.
