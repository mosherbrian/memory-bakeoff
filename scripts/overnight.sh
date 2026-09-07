#!/usr/bin/env bash
# Overnight, unattended. Touches ONLY the 34 already-exposed pilot items.
# The held-out 34 are never passed to anything here.
set -uo pipefail
cd /var/home/bmosher/pilot-gen45
echo "=== $(date -Is) arm C/D: dates stripped ==="
python scripts/pilot_ordering.py --no-dates
echo "=== $(date -Is) combined summary ==="
python scripts/summarise_ordering.py
echo "=== $(date -Is) rival re-review after FIX FIRST ==="
RIVALS_OUT=/var/home/bmosher/rivals/reviews/gen124-rereview \
  /var/home/bmosher/rivals/review-generation /var/home/bmosher/pilot-gen45 \
"A previous review of this repository returned DEFECTS_BLOCKING on the Gen123/124 strategy. Read research/PILOT_ORDERING_RESULT.md, research/BENCHMARK_HARVEST_CHECK.md, research/LONGMEMEVAL_SUBSTRATE.md and scripts/pilot_ordering.py as they now stand.

The prior blocking findings were: (1) session dates were left in the prompt, so reversing order did not remove the recency cue; (2) the substrate document claimed 'verified over all 78' for semantics it admitted were unverified; (3) MemConflict was described as vendored when it is gitignored and absent; (4) the frozen five-condition grader cannot run on a two-session item; (5) 'no published work measures ordering' was asserted from a one-paper search.

Your FIRST line must be exactly one of:
VERDICT: SOUND
VERDICT: DEFECTS_MINOR
VERDICT: DEFECTS_BLOCKING

Then from the second line: state for EACH of the five findings above whether it is now repaired, partially repaired, or untouched, quoting the file and line you checked. Then any NEW defect, numbered, most severe first. Attack specifically whether the date-stripping is real or cosmetic given date words remain inside the conversation text, and whether the pilot result is being described with the exploratory status it actually has."
echo "=== $(date -Is) done ==="
