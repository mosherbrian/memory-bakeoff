# Assay power check — blind_pack build-time leak gate (closes register gap #1)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~20:5x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — instrument power checks
**Target:** `team/blind_pack.py` build-time leak gate, sealed-value half
(QUEUE row 9, fsync; pending adoption). Synthetic session only.

## What the gate claims

Its own comment (`blind_pack.py:259-262`): the hidden-value half *"checks the
serialized packet, so it also catches a render path that copies a sealed
field."* The hidden set is
`{v in key fields | len(v) >= 8 and any(ch.isdigit() for ch in v)}` plus session
filenames.

## Probe

Built a synthetic s3 capture whose record body carries the **confirmer word in
prose** — `"The agent decided the deploy target is staging."` — and a control
using the canonical form `"confirmed_by=agent"`. Both builds return rc 0; then
scanned the emitted `items.jsonl`.

| Input | Build | Bare `agent` in packet |
|---|---|---|
| prose: "The agent decided …" | wrote (rc 0) | **yes — leaked** |
| control: "confirmed_by=agent" | wrote (rc 0) | no (scrubbed to `[confirmer]`) |

## Finding — two layers miss the short sealed values

1. The **scrubber's** confirmer pattern matches `confirmed_by…`,
   `allowAgentConfirmed`, and `agent confirm…`, but **not a bare `agent`** in
   prose.
2. The **gate's hidden-value half** would be the backstop, but its filter
   (`len >= 8` **and** a digit) excludes `confirmed_by` ∈ {`agent`,`operator`} —
   exactly the short categorical sealed value. The same exclusion applies to
   `timing` ∈ {`before`,`after`} and `old_is` ∈ {`A`,`B`}.

So the build gate reports OK on a packet that reveals the confirmer. This is a
second leak channel in the same family as the era cues fsync already documented
(S3 blindness is weak by construction); it does not make S3 *more* blind. The
gate's stated coverage is what is wrong.

## Fix options

- Scrub bare confirmer words in rated text (`\b(?:agent|operator|human)\b` →
  `[confirmer]`), accepting over-scrub in S3 where the word is a direct tell; or
- add a gate check that flags `agent|operator` in the packet for review.
- Do **not** simply drop the length/digit filter: `A/B` and `before/after` would
  false-positive everywhere. Confirmer is the cleanly fixable one.

## Limits

- Synthetic; this bounds the gate's coverage, not any live packet. The hidden
  set deliberately trades recall for precision, so the fix is targeted.
- Separate from the scorer-guard crash (`ASSAY-POWERCHECK-BLINDPACK-SCORER.md`).

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/blind_pack_build_gate_power_check.py`
  sha256 `e11a3c2aec4df4bd4ea5ae84e5eb4b9f01bed9cdaa2b1fb2d9ab2f9d0b6bd62e`
- Result: `.../sealed-blindpack-buildgate-20260912/result.json`
  sha256 `1e05cb2c2af1e2f20f5a3ca8d673293d70b36d75e8aab1efbb006bd4d5fd2311`
- Re-run: `python3 scripts/verify-20260912-assay-row1/blind_pack_build_gate_power_check.py`

— **Assay** (worker-glm-dsh2).
