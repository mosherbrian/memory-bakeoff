# Requirements for the next reader ruler (Gen115)

Not an implementation. Gen115 forbids writing a repaired ruler, so this states
what the next one must satisfy and what evidence would show it does.

Sources: eight defects recorded against v4; the Gen115 adjudication
(`results/gen115/attempt2/`); the rival reviews of 2026-09-06.

---

## R-1 The fixture must make recency DECIDABLE, or the condition must be renamed

**Defect.** No conflict prompt discloses which record is current. Verified
absent from all 24: `superseded`, `current`, `stale`, `role`, `outdated`,
`latest`, `newer`, `order`. Ids are opaque, there are no timestamps, and no
ordering semantics are declared.

Yet v4 treats `correct_current_answer` as the success state. A reader cannot
select the current value from the records; where it did, it used a temporal
phrase embedded in the record text.

**Asymmetry that makes this worse.** Both cores whose current record carries a
cue (`budget:solstice` "after the resize", `throughput:atlas` "after the cache
fix") are cues on the CURRENT record. Stale records are bare. So the two cores
that look "resolved" may be resolved by wording, not by memory behaviour.

**Requirement.** Either:
- (a) supply an explicit, uniform recency signal (timestamp or declared order)
  on EVERY record in EVERY core, so selection is derivable; or
- (b) keep records undecidable and rename the success state. Under (b),
  reporting both values is CORRECT behaviour and must be scored as such.

Not both. The next fixture must state which it is, before running.

**Evidence:** a test asserting every conflict record carries the same class of
recency marker, or a declaration that none does plus a rubric where
`UNRESOLVED_BOTH` is a pass.

## R-2 One label may not cover several response forms

**Defect.** `mixed_contradictory_answer` covered at least four distinct forms.
Gen115's exploratory read of the same 24: `UNRESOLVED_BOTH` 12,
`TEMPORAL_RECONCILIATION_TO_CURRENT` 6, `CURRENT_ONLY` 3, `AMBIGUOUS` 3.

**Requirement.** Distinguish at minimum: current-only, stale-only, both
unresolved, both reconciled ending at current, both reconciled ending at stale,
explicit simultaneous assertion. A reply that gives a correct chronology ending
at the current value is not a contradiction and must not be counted as one.

**Evidence:** a decision table with one row per form and a worked example.

## R-3 Contradiction must be defined by assertion, not by substring presence

**Defect.** `contains_value` is a substring test with no word boundaries, so
"answer mentions both canonical strings" became the definition of contradiction.

**Requirement.** A contradiction label requires the text to assert two
incompatible states as simultaneously current. Word-boundary matching at
minimum; presence alone is never sufficient.

**Evidence:** fixtures where both values appear and the correct label is NOT
contradiction, including a temporal reconciliation and a quotation.

## R-4 The scoring must not be blind to mention order

**Defect.** 21 of 24 answers list the two values in the order the records appear
in the prompt. v4 has no field for this, so a pure order-of-mention echo was
reported as an order effect on correctness.

**Requirement.** Record context order and answer mention order as separate
fields on every conflict cell, and require any order claim to distinguish them.

**Evidence:** a test that an answer echoing prompt order with no change in
selection produces NO order-effect finding.

## R-5 Repetition must measure something

**Defect.** 19 of 20 cases returned byte-identical text across all three
repetitions. The 60 cells carry 21 unique replies; the 24 conflict cells carry
9. "21 of 24" reads as 24 observations and is closer to 9.

**Requirement.** Either vary something across repetitions (seed, paraphrase,
record order) or report unique-observation counts alongside cell counts. A cell
count may never be published without its unique count.

**Evidence:** the results file carries `unique_observations` per condition.

## R-6 The freeze must cover the code that executes

**Defect.** `run_gen114_reader.py` and `grade_gen114.py` did not exist at the
pinned commit; they first appear in the commit that PUBLISHED the result. The
preflight clean-worktree check filters untracked lines, so it could not see
this. Both reviewers found it independently.

**Requirement.** The runner and grader are hashed into the contract payload, and
the preflight fails on untracked files in the paths it attests.

**Evidence:** a test that adding an untracked file under `scripts/` fails
preflight.

## R-7 Determinism must be verified, not declared

**Defect.** `seed_accepted: true` is hardcoded in the addendum and never read
back from the server. One case varied anyway.

**Requirement.** Read back what the server reports, or drop the claim. Any
observed cross-repetition variation is recorded as a first-class result.

## R-8 The identity check must not compare a thing to itself

**Defect.** `assert_behaviour_identical_to_v3` compared function objects that
were the same objects; `prompt_hashes()`/`fixture_identity()` bound a local
`build_fixture`, so identity did not cover the fixture actually used.

**Requirement.** Cross-version equivalence imports both versions explicitly and
asserts they are distinct objects before comparing behaviour. Identity functions
take the fixture as an argument.

**Evidence:** a test that the equivalence check FAILS when handed one module twice.

## R-9 Grading order

**Defect.** `grade()` consults citations before establishing the answer class.

**Requirement.** Answer class is computed first, from text and core only.
Citation relation is computed after and can never overturn it.

---

## What the next generation may and may not use

**May not.** The four cores, their record texts, questions and all observed
wording are development-exposed. They can never serve as a confirmatory set for
a repaired ruler. Any run using them is exploratory whatever its result.

**May.** The sealed Gen114 corpus remains valid development evidence, and is the
right regression set for R-2, R-3 and R-4: a candidate ruler must produce the
Gen115 category distribution on those 24 replies.

## Attribution

R-1 and R-2 originate with `glm-5.3-flash`; R-1's asymmetry and R-5 with both
rivals; R-6 with both. None were found by the implementer.
