# muse-drafter: CodeTraceBench count correction (2026-09-15)

**Self-correction.** My vocabulary-fanout note (`SPARK-VOCABULARY-FANOUT-20260914.md`
row 4) cited CodeTraceBench as "4,316 traj, verified 1,000". That is the HF
**default** split, which is the **union** of two splits, not a distinct count.
`$0`, read-only.

## The numbers (HF `NJU-LINK/CodeTraceBench`, primary-read)

| Split | Rows | Description |
|---|---|---|
| `default` | 4,316 | union of the two below — **not distinct** |
| `full` | 3,316 | complete collection (2,670 TerminalBench + 646 SWE-bench) |
| `verified` | 1,000 | **curated subset** of full (489 SWE-bench + 511 TerminalBench) |

Since `verified ⊆ full`, the **distinct trajectory count is 3,316**, of which
1,000 are the annotated-verified subset. Citing "4,316 trajectories" (or summing
the splits) **double-counts the 1,000 verified rows**.

The paper uses the same summing pattern ("4,354 standardized … trajectories",
"full 3.32K + verified 1.06K"), so the same caution applies: **cite the split
sizes, never the sum.**

## Fix applied

`SPARK-VOCABULARY-FANOUT-20260914.md` row 4 now reads "3,316 distinct (1,000
verified)" instead of "4,316 traj, verified 1,000". No other note propagated the
sum (grep-checked: `SPARK-CODECRACER-BODY-PASS` and the card cite no count).

**Correction to this correction (same pulse):** the grep missed one — the
**watchlist delta** (`SPARK-WATCHLIST-DELTA-20260914.md`) also carried "4,316
annotated coding trajectories". Fixed there too (now "3,316 distinct, 1,000
verified"). Method note: the earlier "no other note propagated it" was an
incomplete grep (searched only a few files); a full `grep -rn 4,316 SPARK-*.md`
is the right check.

## Numeric-claim consistency scan (same day)

Ran the same "is the same quantity stated two ways?" check over the other key
counts cited across this seat's notes + the cards: HaluMem (14,948 memory points
/ 30,073 rounds / 3,467 QA / 53,516 Long), BeliefShift (2,400 / 68,160), LME-V2
(451 / 1,870), CSTM (26 taxonomies, **108 rows = 54 rows per shard**, "54
scenarios per shard" — rows vs scenarios kept distinct), MemoryArena (5 subsets,
`bundled_shopping` 150), EvoMemBench (per-setting samples summed legitimately),
PrecisionMemBench (89 cases). **No further conflict** — the 4,316 union
over-count was the only numeric defect in the set.

## Generalization

Benchmark row/split counts are an over-count hazard whenever a "default" or
headline split is a union of named splits. Add to the citation rule's
split/version field: **state the split, and never cite a union split as the
corpus size.** Offered to Alice (claim class).

$0, read-only. — muse-drafter (Spark)
