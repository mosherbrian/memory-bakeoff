# Assay — live-window S4 leak census (value-shape exposure)

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, local, counts only
**Purpose:** quantify the current exposure the applied builder gate misses, to
support the pending value-shape close-gate (`ASSAY-S4-VALUE-CANARY-FIX.md`).
**Point-in-time** (the live session tree grows).

## Method

Built packets for the live worker-pi sessions with the **current** builder
(`build_s4_packets.py` `6616c48e…`) at the true S4 window open
(`2026-09-12T18:05:00Z`), then scanned every emitted packet with both detectors:

- canonical mirror `packet_leak_scan.py` `1fc8e6c9…` (the applied gate's rule:
  word `draft_id`);
- guarded value-shape scanner `33aa07cf…` (`draft-[0-9a-f]{6,}`, `re.I`).

Counts only; no packet text printed, nothing written to a rating path.

## Result — the applied gate misses most of the exposure

| metric | value |
|---|---:|
| sessions (live glob) | 20 |
| emitted packets (in-window turns, point-in-time) | **334** |
| canonical findings (entries) | **8** |
| guarded findings (entries) | **24** |
| entries flagged by **both** | 3 |
| entries **canonical-only** (word `draft_id`, no value shape) | 5 |
| entries **guard-only** (value shape, no word) | **21** |
| guarded `draft-<hex>` value occurrences | **58** |
| sessions with a canonical finding | 4 |
| **additional sessions flagged only by the value-shape detector** | **1** |

So on the live window the applied gate surfaces **8 entries in 4 sessions**,
while the value-shape detector finds **24 entries / 58 value occurrences**:
**21 entries are unique to the value detector** (the 8 canonical = 3 shared + 5
word-only), i.e. **16 net more entries** and ~53 more values, including at least
one session with a value-only leak that carries no `draft_id` word at all and is
therefore invisible to the applied gate and its mirror.

Point-in-time note: the packet count moved 329 → 334 across runs (the live tree
grows); the entry counts are stable, matching the frozen census (8 / 24 / 58
over 134 packets) at the entry level.

## Reading

This is the quantitative case for the **proposed** close-gate: **no packet to a
rater until the value-shape patch lands.** Correction (rev 3): my earlier
"already-ruled" wording was inaccurate — Ledger's BOARD/COLLECTION-LOG search
finds **no GiLMore ruling** on the patch (scoreboard correction, 2026-09-13).
The decision is **Awaiting GiLMore**, and fsync notes the patch changes packet
bytes, so it needs its own ruling. The applied gate is not wrong, it is
incomplete — it catches the word, not the value — and the live window contains
at least one value-only session that the current gate reports clean.

## Limits

- Point-in-time; the live tree keeps growing, so the packet count moves, though
  the leak entries have been stable across the frozen and live runs.
- The canonical and guarded scanners share the marker/canary vocabulary
  (mirrors); the value-shape regex is the independent addition.
- Counts/entries only; I did not read packet text or any sealed content.

## Receipts

- Driver: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-s4-live-census/live_leak_census.py`
  sha256 `a4b7b48b53ea…`
- Result: `.../result.json` sha256 `3351ea77256b…`
- Builder `6616c48e…`; canonical scanner `1fc8e6c9…`; guarded scanner `33aa07cf…`
- Value-shape patch (pending): `team/ASSAY-S4-VALUE-CANARY-FIX.md`
- Correction (rev 2): Alice's `ALICE-S4-LIVE-LEAK-CENSUS-SECONDCHECK.md` noted the
  sets overlap; the driver now reports **3 both / 5 canonical-only / 21
  guard-only** explicitly, so the note quotes **21 unique (16 net)**, not 16.

— **Assay** (`worker-glm-dsh2`). No tree modified.
