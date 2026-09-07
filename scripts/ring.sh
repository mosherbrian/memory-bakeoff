#!/usr/bin/env bash
set -uo pipefail
cd /var/home/bmosher/pilot-gen45
RIVALS_OUT=/var/home/bmosher/rivals/reviews/gen124-round3 \
  /var/home/bmosher/rivals/review-generation /var/home/bmosher/pilot-gen45 \
"Third review of this generation. Two prior reviews returned DEFECTS_BLOCKING. Read handoff/GEN124_RECAP.md, handoff/GEN124_TECHNICAL.md, research/pilot_ordering/PILOT_ORDERING_RESULT.md, research/pilot_ordering/PREREGISTRATION.md, research/pilot_ordering/SUBSTRATE_VERIFY.json and reviews/LEDGER.md rows 118-134.

Round 2 findings were: the 'part nobody has published' contradiction inside the retracting document; 'closed-pool grading is reusable'; the holdout called preregistered with no registered rule and unfrozen membership; the instruction 'as of the most recent conversation' being itself a recency cue; and the crude scorer's noise floor sitting at the discordant count.

Your FIRST line must be exactly one of:
VERDICT: SOUND
VERDICT: DEFECTS_MINOR
VERDICT: DEFECTS_BLOCKING

Then state for EACH round-2 finding whether it is repaired, partially repaired, or untouched, quoting file and line. Then any NEW defect, numbered, most severe first.

Attack specifically: (a) is the exclusion of 10 items genuinely outcome-independent, or is it post-hoc cleaning that happens to remove the one counter-example; (b) does PREREGISTRATION.md actually bind, or does it leave a door open; (c) is the claim 'scorer crudeness cannot manufacture a direction' correct, or can you construct a case where it can; (d) is the recap honest about what is and is not established."
