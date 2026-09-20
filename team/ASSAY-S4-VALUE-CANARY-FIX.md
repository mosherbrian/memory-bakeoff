# Assay — validated value-shape canary/redaction patch (S4 leak recall + precision)

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, local, synthetic + frozen packets
**Trigger:** `team/ASSAY-S4-LEAK-CLASSIFICATION.md` (3 value exposures / 5 mentions)
and Alice's `team/ALICE-S4-LEAK-VALUE-ONLY-CENSUS.md` (the `draft_id`-word canary
misses 21 value-carrying entries / 53 values). **Owner:** builder = Kiln/fsync.
**Verdict: valid, ready-to-adopt patch — NOT applied.**

## What the patch does

Both the builder (`build_s4_packets.py`, `6616c48e…`) and the mirror scanner
(`packet_leak_scan.py`, `1fc8e6c9…`) keyed on the literal word `draft_id`.
The patch adds the observed **value shape** and drops the word-only canary:

- add `SECRET_VALUE_RE = re.compile(r"draft-[0-9a-f]{6,}")`;
- **redaction:** `is_memory_traffic` (non-user) and `user_entry_has_draft_secret`
  now also match the value shape, so a value-carrying entry is redacted;
- **detector:** `packet_leaks` / `scan_packet` add the value-shape hit;
- **precision:** remove bare `"draft_id"` from `LEAK_CANARIES` / `SUBSTANCE`
  (the 5 mention-only false positives), keeping `key=record-`,
  `confirmation_code`, and the memory sentinels.

## Power check — 13/13 (predicate + mirror)

| case | canonical | guarded |
|---|---|---|
| non-user `draft-abc123` value, no `draft_id` word | miss | **redact + flag** |
| non-user `draft_id` word only | flag (FP) | **clean** |
| non-user `[recall-nudge]` | flag | flag |
| clean / already-redacted non-user | clean | clean |
| user entry with `draft-abc123` value | miss | **flag** |

`is_memory_traffic` and `packet_leaks` (builder) and `scan_packet` (scanner) all
reproduce the split; no regression on sentinel/clean/redacted inputs.

## All-packet census (134 frozen packets, counts only) — confirms Alice's numbers

| | canonical | guarded |
|---|---:|---:|
| findings (entries) | 8 | **24** |
| `draft-<hex>` value occurrences in flagged entries | 5 | **58** |

Recall moves from **3/24 value-carrying entries (5/58 values)** to
**24/24 (58/58)**, and the 5 word-only false positives are dropped. This
independently reproduces Alice's census exactly.

## Adoption

- `s4-value-canary-builder.diff` — applies cleanly in `implementer/repo`
  (`git apply --check` rc 0).
- `s4-value-canary-scanner.diff` — applies cleanly in `repo-glm-dsh2`.
- Left **unapplied** so the builder and its mirror land together (one-writer
  tree: the builder is Kiln's; the scanner is mine but is kept as a diff so the
  mirror cannot drift mid-flight).

## Limits

- Value shape only (`draft-` + ≥6 hex). A secret in another format is still
  missed; `confirmation_code` remains a word canary because its value shape is
  unverified.
- User entries still carry the `draft_id` word canary (no observed user-side
  false positive); only the non-user detector was narrowed.
- The rerun used the persisted frozen emitted packets; packet bytes are
  unchanged by the gate, and re-running the builder reproduces them.

## Receipts

- Builder diff: `.../s4-value-canary-builder.diff` sha256 `557cb5bbb31a…`
- Scanner diff: `.../s4-value-canary-scanner.diff` sha256 `60c7c14e10fa…`
- Sealed guarded: `.../guarded/build_s4_packets.py` `b211037c2d5d…`,
  `.../guarded/packet_leak_scan.py` `5aa670c496ff…`
- Power check: `.../s4_value_canary_power_check.py` `5e1261c87103…`
- Result: `.../result.json` `65aa02db35d7…`
- Re-run: `python3 s4_value_canary_power_check.py` (rc 0)

## Revision (rev 2, after Alice's second-seat check)

Alice's `team/ALICE-S4-VALUE-CANARY-SECONDCHECK.md` PASSed rev 1 (6/6 hashes,
both diffs apply, census 24/58) and flagged one latent boundary: the regex was
**lowercase-hex only**, so `draft-ABC123` would escape — and because the same
predicate drives redaction, an uppercase value would be emitted unredacted too
(recall *and* privacy). Live exposure on the frozen snapshot is 0.

Fixed: `SECRET_VALUE_RE = re.compile(r"draft-[0-9a-f]{6,}", re.I)` in both
guarded files; power check gained uppercase cases and now passes **15/15**;
census unchanged (24 findings / 58 values).

**Rev-2 hashes (supersede the rev-1 hashes above and in Alice's check):**

- builder diff `ba907167d442…` · scanner diff `7498e3a443f8…`
- guarded `build_s4_packets.py` `568face44b9e…` · `packet_leak_scan.py` `33aa07cf13d9…`
- power check `5e5c5c6883cf…` · result `245674c1a5e2…`
- both diffs still `git apply --check` clean; still **unapplied**.

## End-to-end adoption proof (rev 2)

The predicate check proves the functions; `s4_value_canary_end_to_end.py` drives
the **real builder CLIs** on synthetic sessions and inspects the emitted packets:

| synthetic session | canonical (`6616c48e`) | guarded (`568face4`) |
|---|---|---|
| non-user entry `minted draft-abc123` (no `draft_id` word) | value **present unredacted**, own gate `LEAK-SCAN PASS` (**blind miss**) | entry **redacted** (marker), value absent, gate PASS |
| non-user entry `the draft_id field is set` (mention, no value) | gate **`LEAK-SCAN FAIL`** (false positive) | gate PASS, prose intact |

So on a value-only secret the current builder both leaks it *and* reports clean,
while the guarded build redacts it and stays clean; on a mere mention the
current builder false-alarms and the guarded build does not. Power check 4/4
(two sessions × two builders), rc 0. Receipts: script `b6d13e30f8cc…`, result
`a7fe02b3dc6f…`.

— **Assay** (`worker-glm-dsh2`). No live tree modified.
