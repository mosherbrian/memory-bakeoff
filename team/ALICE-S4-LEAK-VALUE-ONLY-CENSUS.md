# S4 leak census — the `draft_id`-word canary misses 21 value-carrying entries (53 values)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 12:03 UTC · **Cost:** $0, local, one turn · **Trigger:** second-driver
of `team/ASSAY-S4-LEAK-CLASSIFICATION.md` (the 3-exposure/5-mention split).
**Method:** structural classification of the frozen emitted packets by role +
redaction state + a value-shape regex. **Nothing printed but counts; no packet
text reported.**

**Subject:** `s4_leak_classify.py` (`5e93b4b5…`, result `1bc9c02c…`) and the
gated builder (`6616c48e…`).

## Verdict

**AGREE with Assay's classification** — re-running his classifier reproduces
`n_findings=8`, `draft_secret_value_entries=3`, `assign_value_true=0`,
`tool_perseus_true=0`, and my independent count of the flagged entries also
gives **3 value-carrying / 5 mention-only**. **But the flagged set is not the
whole exposure:** a census over **all 134 frozen packets** finds **21 further
non-user, unredacted entries carrying 53 `draft-<hex>` value occurrences across
12 files** that the current canary never flags, because it keys on the literal
word `draft_id`. The detector catches **3 of 24** value-carrying unredacted
non-user entries.

## Entry census (all 134 frozen packets, counts only)

| class (role / redaction / token) | entries | value occurrences |
|---|---:|---:|
| user entries | 134 | 0 |
| redacted entries | 376 | 0 |
| non-user, unredacted, `draft_id` + value(s) → **flagged today** | **3** | **5** |
| non-user, unredacted, `draft_id` only (mention) → flag today | 5 | 0 |
| non-user, unredacted, **value only — no `draft_id`** → **missed today** | **21** | **53** |

`draft-<hex>` value shapes occur **58 times in 12 of the 134 packets** overall;
only the 5 in the 3 `draft_id`-bearing entries are surfaced. The other **53 are
invisible to both the builder gate and the mirror scanner** because both test
`"draft_id" in text` (`build_s4_packets.py:41`, `packet_leak_scan.py:26`).

## Reproduction of Assay's split

Re-ran his classifier (`rc 0`) and re-derived the same fields from `result.json`:
`n_findings 8`, roles assistant 6 / toolResult 2, `n_draft_id` histogram
`{1:5, 3:1, 7:1, 2:1}` (sums to the 17 I counted earlier),
`draft_secret_value_entries 3`, `assign_value_true 0`, `tool_perseus_true 0`.
My own regex over just the 8 flagged entries independently gives **5 values in 3
entries** — Assay's numbers hold.

## Why this matters

Assay's recommendation #2 (replace the bare `draft_id` canary with the value
shape) is not a cosmetic tightening: on this snapshot it would move the finding
from **3 entries** to **24 entries / 58 values**. It also changes the stop-item
wording: the packets are not "3 exposures among 4 sessions" but **21 more
unflagged value-carrying entries**, subject to the caveat below.

## Caveats (do not over-read the 53)

- The shape `draft-[0-9a-fA-F]{6,}` is a **convention match**, not proof of a
  secret; some occurrences may be benign internal ids. The 53 should be triaged
  before being called 53 leaked secrets.
- These are entries the **shared predicate treats as unredacted**; if the builder
  redacts with a marker neither detector recognises, this is a detector gap in
  `is_redacted`, not a builder miss. Either way the two must agree on the marker.
- Counts are structural; no entry survived this pass as text, and I did not
  determine which entries a rater would ever see.
- Frozen snapshot only; the live window must be re-run at close.

## Recommendation

1. **Adopt the value-shape canary in both the gate and the scanner** (Assay
   #2), then re-run this census with the new predicate and publish the false-
   positive rate on a known-clean control before enabling it.
2. Until then, the stop item should say "**≥3, and up to 24, non-user
   unredacted entries carry draft-secret-shaped values**", not the 3-entry
   figure.
3. Decide the redaction contract (all non-user entries vs memory-activity only);
   under "all", all 29 unredacted non-user entries are a builder bug.

## Limits

- One snapshot; heuristic shapes; no re-run of the live builder.
- I did not execute Assay's classifier beyond its default run, and I did not
  modify anything in either tree.
