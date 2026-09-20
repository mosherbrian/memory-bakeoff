# Second-seat check — live S4 leak census (Assay) + "16 more entries" is a net difference

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 14:05 UTC · **Cost:** $0, local, one turn · **Trigger:** standing
second-check of `team/ASSAY-S4-LIVE-LEAK-CENSUS.md`. Counts only, no packet text
reported; nothing written to a rating path.

**Subjects:** driver `live_leak_census.py` (`6b950042…`), result `983867a6…`,
builder `6616c48e…`, canonical scanner `1fc8e6c9…`, guarded scanner `33aa07cf…`.

## Verdict

**PASS / AGREE on the substance and every session-level number** — an independent
live rebuild reproduces 8 canonical findings / 4 sessions and 24 guarded
findings / 1 guard-only session. **One wording correction:** "**16 more
entries**" is the *net* difference of two **overlapping** sets; the number of
entries the value detector uniquely catches is **21** (5 word-only entries are
canonical-only and drop out). The correct exposure statement is **21 entries
invisible to the applied gate (16 net)**, matching my frozen census.

## Independent live rebuild

Method: rebuilt packets for the live worker-pi sessions with the applied builder
at the true window open, then scanned each packet with **both** scanners and
compared the `(session, packet, entry)` sets.

| metric | Assay | my rebuild |
|---|---:|---:|
| sessions | 20 | **20** |
| packets | 329 | **331** (live tree grew — point-in-time) |
| canonical findings (entries) | 8 | **8** |
| sessions canonically flagged | 4 | **4** |
| guarded findings (entries) | 24 | **24** |
| sessions flagged only by the value detector | 1 | **1** |
| guarded value occurrences | 58 | **58** (all inside the 24 flagged entries) |

Set difference (the piece the census headline does not separate):

| | entries |
|---|---:|
| guarded-only (**invisible to the applied gate**) | **21** |
| canonical-only (word-only, no value) | 5 |
| net (24 − 8) | 16 |

So `guarded = canonical(3 with values) + 21 value-only`, and
`canonical = those 3 + 5 word-only`. The 53 "more values" figure is right
(58 − the 5 values in canonical entries, all shared); only the entry count is
mislabeled.

## Hashes

`6b950042…` (driver), `983867a6…` (result), `6616c48e…` (builder),
`1fc8e6c9…` (canonical), `33aa07cf…` (guarded) — all re-hashed, all match.

## Reading (unchanged)

The conclusion stands and is strengthened: the applied gate surfaces 8 entries
in 4 sessions; the value-shape detector shows **21 entries / 53 values** the
gate cannot see, including one session with no `draft_id` word at all. **No
packet should go to a rater before the value-shape patch lands**, and the
close-gate note should say 21 (unique), not 16 (net).

## Limits

- Point-in-time: my packet count is 331 to Assay's 329 (two more in-window
  turns); the leak entries are the same historical set, so the counts are stable
  and the denominators move.
- Both scanners share the marker/canary vocabulary; the value-shape regex is the
  independent addition. My set comparison uses the scanners' own `entry`
  indices, so it is exact for what they flag.
- No content printed, no sealed content read, no live session modified.
