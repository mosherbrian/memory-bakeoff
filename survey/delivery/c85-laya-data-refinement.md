# Delivery c85-refinement — duplicate-group splits, balance, and unlabelled controls

**cairn (local gufo) · 26 September 2026 · delivery mode.** Follows Tern's handling correction:
raw data now at **`/tmp/tern-laya-data-c85/`** (0700/0600), nothing raw in the repo. No
teacher/model call, no egress, no training; source IDs preserved; lead wording carried — **local
teacher availability is a bounded-inventory unknown, not global absence**.

## 1. Conversation split alone was not leakage-safe — measured

Exact normalized-text duplicate scan over all candidate texts (messages + both pair sides):
**49 texts recur across different conversations; the largest duplicate group spans 18
conversations** (harness/boilerplate-style repeats). Conversation-level splits would have placed
identical text in train and held-out simultaneously.

**Fix:** union-find merges every conversation sharing an exact text into one **split group**;
splits are assigned at group level. **35 groups** carry all 954 messages + 197 pairs.

## 2. Balanced group splits (was: pairs cal=0)

Deterministic greedy assignment (largest-group-first, group-hash tiebreak) to targets
70/15/15, measured in records:

| set | messages | pairs |
|---|---|---|
| train | 746 | 176 |
| calibration | 101 | 14 |
| heldout | 107 | 7 |

Calibration is no longer empty; held-out pairs remain small (7) — stated, not hidden.

## 3. Matched non-update controls — UNLABELLED, not negatives by fiat

Selection: directive-cue message with **no later strong-correction cue** in its conversation,
length-matched to a pair's "old" text (same conversation first, then same-scope fallback); the initial version assigned its pair's split group. **Superseded by section4:** controls now follow their own conversation/text group; matched-pair co-location is not guaranteed.
**Yield: 19** (9 same-conversation, 10 same-scope). **Honest limit:** the local pool holds only
~157 directive-shaped messages without later corrections; a 1:1 control per 197 pairs is not
reachable without loosening length/scope matching into fabricated similarity — declined. Control
relevance is itself a labeling-time judgment; `relation_hypothesis: possible_still_valid`,
`label: null`.

## 4. Lead split-check failure — fixed and re-verified (same day)

Tern's check found **1 conversation and 2 normalized exact texts crossing splits**. Root cause:
controls were appended **after** grouping and rode their matched pair's split without joining the
union — one control was the same message as a held-out candidate, one same-scope control
duplicated a train candidate's text. **Fix (`finalize_splits.py`):** union-find rebuilt over **all
three files — messages, both pair endpoints, and controls** — before split assignment; controls
now take their own group's split (match metadata kept). **Invariants re-run over all three
files: 0 conversation crossings, 0 exact-text crossings.** Revised splits: messages 746/102/106,
pairs 176/12/9, controls 13/4/2 (train/cal/heldout); 35 groups; labels still 0.

**Limitation, stated instead of a blanket claim:** grouping covers **exact duplicates only**
(case/whitespace-normalized). Near-duplicate and paraphrase leakage is **not tested** — the split
is duplicate-safe, not blanket leakage-safe.

## 5. Artifacts (all in /tmp/tern-laya-data-c85, 0600)

`refined_messages.jsonl` · `refined_pairs.jsonl` · `controls_unlabelled.jsonl` ·
`aggregate_refined.json` (full counts above) · scripts `prepare.py` `refine.py` `controls.py` `finalize_splits.py`
(deterministic, local, re-runnable). Originals kept for provenance; every record retains
source-file sha256-16, conversation id, seq, timestamp, scope, split_group, split.

**Labels present: 0.** Preparation stays useful without a teacher: the shortlist, groups and
splits are exactly what any authorized labeling path — local or Brian-approved — consumes first.

— cairn. Commission: delivery/c85-commission.md + Tern refinement instruction, QUEUE.md D4.
Lead verification: see [current snapshot disposition](c85-laya-grouping-disposition.md#later-cairn-correction-accepted--current-candidate-snapshot). Section2 counts are historical; section4 counts are current.
