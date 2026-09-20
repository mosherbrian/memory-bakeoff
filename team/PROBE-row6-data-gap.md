# PROBE FINDING — row 6 is data-blocked, not metric-blocked

**Author:** Aletheia (Alice), `worker-glm-dsh` · **Date:** 2026-09-12
**Probe class:** artifact-level verification of a DECISION_MEMO artifact, run
before any generation was spent. **Generation budget cost: zero.**
**Status:** NEGATIVE RESULT, preserved. Not a failure of the metric.

---

## What I set out to test

DECISION_MEMO.md row 6 says:

> What does each system DO with a stale record it returns, scored as a penalty?
> *(metric BUILT and tested, not applied — `src/memory_bakeoff/stale_use_penalty.py`)*

The phrase "BUILT and tested, not applied" implies the remaining work is
**application**. I tested that implication.

## What I found

**1. The metric is genuinely well-formed.** `tests/test_longcontext_null.py`
and `tests/test_stale_use_penalty.py` pass 15/15 in 0.07s. The four-way
disposition (`CURRENT_ANSWERED` / `STALE_USED` / `NEITHER` /
`STALE_USED_WITHOUT_RETRIEVAL`) is coherent, and declining to answer is
correctly not penalised. No defect found in the rule.

**2. The metric cannot be applied to any existing frozen result, because the
field it consumes does not exist in the data.** `score_stale_use` requires
`answer_id: str | None`. An exhaustive search of the repo:

    grep -rln "answer_id" --include=*.py --include=*.json --include=*.csv --include=*.md .
    -> src/memory_bakeoff/stale_use_penalty.py
    -> tests/test_stale_use_penalty.py

The only two files containing `answer_id` are the metric and its own unit test.
The synthetic tests pass because they *construct* the input the real record
never captured.

**3. What the frozen retrieval record actually holds.** The row-1/row-3
comparison sets — `results/agentmemory_compare_core5` and
`results/agentmemory_compare_stress4505`, 8 providers x 26 cases x 2 sets — have
`detail.csv` schemas ending in:

    retrieved_ids, relevant_ids, prohibited_ids

These are **retrieval-level**. They record what was *returned*. They carry no
reader answer at all. Row 1's 192/192 observation ("every engine co-returns the
superseded record") is a claim about return, and that is exactly and only what
was captured.

**4. The one answer-level file is unusable for row 6.**
`results/reader_detail.csv` (56 rows, 9 providers) does have an `answer`
column, but it is **free text**, not IDs —

    Q003,bm25,Staging uses Redis database number 6.,...,"['M005','M036',...]"

— and `stale_use_penalty.py` deliberately scores ids, never text ("text matching
is what made the Gen124 scorer crude"). Applying it would mean rebuilding a
text matcher, which re-commits the exact defect the metric was written to avoid.
It is also 56 cases outside the core comparison sets.

**5. The only ID-level reader data is Gen124** — 17 items, permanent
reader-attribution lane, exploratory, and by the two-lane rule (EVIDENCE_LANES.md)
**never quotable as a system score**. It cannot fill row 6.

## The actual blocking condition, stated exactly

Row 6 is blocked by a **missing capture step**, not by missing effort or a
missing metric. Nobody ever recorded, per case, *which memory id the reader
committed to*. The reader lane scored `pass_answer` against a required fraction
and `prohibited_hits`; it never persisted the reader's choice as an identity.

This is a fresh, independent instance of the program's own standing finding:
**capture is the hole.** It is also a fourth failure mode of the class
`PREREGISTRATION.md` §2 documents — a document describing a run's remaining work
as smaller than it is, because the gap is in what was never written down.

## Bounded options (handed to the implementer lane; I do not write to their tree)

- **Option A — build the capture (small, bounded).** Add one field to the reader
  eval output: the id of the memory the reader's answer commits to, per case.
  Then row 6 becomes an application, as the memo assumed. This is the option that
  makes the memo's own sentence true. Requires re-running the reader over the
  comparison sets — 416 cases — which may or may not fit the remaining budget
  (Gen134 close, rows 4/5 still open).
- **Option B — reframe row 6 honestly.** If no run fits, row 6 should not be
  closed as "not applied"; it should be recorded as *unfillable on existing
  evidence*, so the memo's final confidence statement is accurate.
- **Option C — reuse `reader_detail.csv`.** Rejected on the record: text
  matching, wrong case set, re-commits a logged defect.

## Why I am reporting zero-value

No row was filled. The value is that **row 6's cost was mis-stated in the
terminal deliverable**, and finding that out cost zero generation budget. If
Campaign-1 or the memo's close plan budgets row 6 as "just apply the metric,"
that budget is wrong, and it is wrong in the direction that would have burned a
generation discovering it.

## Reproduction

    cd /var/home/bmosher/memory-bake-off/implementer/repo
    python -m pytest tests/test_longcontext_null.py tests/test_stale_use_penalty.py -q   # 15 passed
    grep -rln "answer_id" --include=*.py --include=*.json --include=*.csv --include=*.md .  # metric + its test only
    head -1 results/agentmemory_compare_core5/detail.csv   # ...retrieved_ids,relevant_ids,prohibited_ids

## Two incidental capture gaps, recorded as datapoints

- `RESET_STATUS.md` (top level) cites `research/EVIDENCE_LANES.md`,
  `research/MEMCONFLICT_GEN38_FULL_RELEASE.md`, `DECISION_MEMO.md` and others by
  bare relative path, but those files live under `implementer/repo/`. A reader
  following the "one current decision page" from the mission root hits four
  dead paths before finding the record. Path-relative-to-which-root was never
  captured. Same class as the `team/` gap.
- As of this writing `team/` contains only `ROLES.md`, while MISSION-20260912.md
  line 17 of the briefing and BRIEFING-20260912.md both name `team/CAMPAIGN-1.md`
  and `team/DECISIONS.md` as the campaign's durable homes. Those do not exist
  yet. Not a defect — flagging the window, since Campaign-1 is due in ~1 day.
