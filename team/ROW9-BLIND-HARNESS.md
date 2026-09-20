# ROW9-BLIND-HARNESS — blinded rating packs for S2 and S3 (QUEUE row 9)

**Status:** BUILT, self-tested, sample-run on live logs. NOT adopted. No frozen
criterion changes. Built by fsync, 2026-09-12, on GiLMore's go (pre-build
pattern of row 10: instrument before data). Claude lane, $0 metered.

**Plain English first:** two campaign numbers depend on someone's judgment,
and today that someone can see the answer they are judging. This tool builds
a packet that hides the answer, a sealed key that holds it, and a scorer that
joins them only after the rater is done. It also measures whether the hiding
worked.

## Receipt

| Item | Value |
|---|---|
| Script | `team/blind_pack.py` sha256 `e2d91e8129b266d921c43845d5d4bd429883d0dae1740b5b5127582fc73b011f` (rev 2, 2026-09-12 ~20:3x, after Assay's power check; rev 1 was `dc7a53f2…`) — stdlib only, read-only on inputs |
| Self-test | `python3 team/blind_pack.py self-test` → **17/17 PASS** (synthetic sessions; includes a guard-can-fail test: scrubber bypassed → build refuses, writes nothing) |
| Sample s3 | 11 items = 8 agent-confirmed + 3 operator-confirmed. Cross-check: equals the 11 `WRITTEN` confirm results in the session logs. The vault's 12th row is the CLI-seeded canary, not a capture, and is correctly absent. key `89819e29…`, items `c2957f93…` — **built by rev 1 (`dc7a53f2…`), before the rev-2 fixes; it still carries 4 bare confirmer words** (Alice, `ALICE-ROW9-BLIND-HARNESS-RECEIPT-CHECK.md`). Rev-2 rebuild (Assay, `ASSAY-ROW9-REV2-REBUILD.md`, `/tmp/assay-row9-rev2-s3`): 11 items, 0 bare confirmer words, items `d1d95e8b…`, key `d2afe09b…` |
| Sample s2 | 2 supersessions, 0 unsupported, 125 action×pair candidates, **15 kept** at min-overlap 2 (28 at 1, 10 at 3). key `75ba65fe…`, items `587a8c64…` — **built by rev 1**. Rev-2 rebuild: 15 items, items `587a8c64…` byte-identical; key `938b161b…` differs only in the sessions metadata (15 → 20 files) |
| Receipt correction (2026-09-13 ~06:5x) | My error: I updated the script hash to rev 2 but left the sample rows unmarked, so the table read as if rev 2 had built them. Found by Alice, reproduced and rebuilt by Assay. |
| Sample inputs | 15 session files under `~/acp-pi/.pi-agent/sessions/`, window-open `2026-09-12T11:05:00-07:00` (GiL board post), close pinned `2026-09-12T21:30:37Z`, seed `sample-not-for-rating` |
| Sample location | `/tmp/fsync-row9-final-143037/` — builder scratch, **outside team/ on purpose** (S4-ADJUDICATION B1: the rater does not read live-lane content mid-window). Not for rating. |

## Why not S1 (the row's wording)

S1 is a programmatic receipt: new record PRESENT, old ABSENT, status flip. It
has no arms and no judgment, so nothing is hidden and blinding it is a no-op.
S4 is already blind (`S4-ADJUDICATION.md` + `build_s4_packets.py`, verified by
Assay row 1). R2H is already blind (arm-strip). The two judgment calls with
**no** blind procedure are:

- **S3 tightening 1 — T0 misclassification.** The agent picks its own tier;
  Verity samples T0 captures knowing every one is T0.
- **S2 tightening 1 — stale-action detection.** Cairn checks their own
  post-supersession artifacts against the current records.

## What it does

**s3.** Every written capture (content only). Sealed: confirmer, time, key,
draft. Rater labels `T1-ELIGIBLE / T0-OK / UNDECIDABLE` and guesses the
confirmer `AGENT / OPERATOR / UNSURE`. Operator-confirmed records are decoys:
they stop "everything I see is T0" anchoring and are reported apart, never as
a metric.

**s2.** Per supersession: old and new record text as A/B (seeded order), plus
every bash/write/edit action after the old record was written that shares ≥ N
subject tokens with them. The inclusion rule never reads time. Sealed: before
or after the flip, which letter is old. Rater labels
`FOLLOWS-A / FOLLOWS-B / BOTH / NEITHER / EXCLUDED-LOOP-MAINTENANCE / UNDECIDABLE`
and guesses `BEFORE / AFTER / UNSURE`. Before-flip actions are the positive
control: they show whether the rater can see the old convention at all.

**Scrubbed from rated text:** ISO and compact dates, times, unix-ms, record
keys, draft ids, confirmer words, `T0`/`T1`. Items are in hash order.

**score** refuses: a KEY whose sha256 differs from the manifest; any unrated,
unknown, duplicate or off-vocabulary line. It reports s3 misclassified T0
items with n, and s2 control hits, anomalies, current-follows and **stale
candidates** (candidates, not the S2 count). For both it reports the guess
score next to the majority baseline.

## Defects found while building (mine, fixed)

1. **The leak gate refused both first live builds** (11 and 17 hits). Cause:
   its sealed-value set included the packet's own opaque ids. The gate refused
   rather than wrote; I fixed the set, not the gate.
2. **Compact dates passed the scrubber** (`MISSION-20260912`,
   `TRIAL-20260911`: era cues). Found by spot check, not by the self-test.
   Pattern added, plus a self-test assertion.
3. **Most s2 items were Cairn's board posts about the records.** Those are
   loop maintenance, not governed work. Added `EXCLUDED-LOOP-MAINTENANCE`
   (S4 A4 sense). It stays out of the control, stale and current counts.

### Found by a second seat (Assay power check, `team/ASSAY-POWERCHECK-BLINDPACK-BUILDGATE.md`; register rows 3 and 7) — fixed in rev 2

4. **A bare confirmer word leaked.** "The agent decided …" passed the
   scrubber (it matched only `confirmed_by…` forms) and the gate (its
   sealed-value half skips short values like `agent`/`operator`). Fix: the
   scrubber now also replaces bare `agent|operator|human` with `[confirmer]`,
   and the self-test asserts the prose case. Cost: over-scrub in s2 text
   (e.g. "agent dir" → "[confirmer] dir"), accepted.
5. **The scorer crashed on a valid-JSON non-object line** (e.g. `[1, 2]`)
   instead of refusing. Fix: it now refuses with "not a JSON object", and the
   self-test asserts that.

Still true after rev 2, as Assay notes: short categorical sealed values
(`before/after`, `A/B`) stay outside the sealed-value half by design, so
their leak protection is the scrubber plus the guess score, not the gate.
Second-seat re-check of rev 2: done by Assay on 2026-09-12 (`ASSAY-BLINDPACK-REV2-RECHECK.md`).

**Stated so nobody over-reads it:** the leak gate has two halves. The pattern
half only re-runs the scrubber, so it catches a bypassed or edited scrubber
and nothing else. The sealed-value half checks the serialized packet, so it
catches a render path that copies a sealed field. **Neither proves
blindness.** The rater's guess score does.

## Known limits

1. **S3 blindness is weak by construction.** In-window records describe the
   window ("WINDOW OPEN", "workstream B is LIVE") and all decoys predate the
   campaign. 25 era-cue hits remain after scrubbing. Expect the confirmer
   guess to beat baseline. Pre-registered reading: if committed guesses beat
   `majority_baseline`, the S3 rate is reported as "rater not blind to
   confirmer". Labels are not voided, because T1-eligibility is judged from
   content.
2. **Era ≠ tier.** The first T0 self-capture (confirmed 10:52 PDT) predates the
   11:05 window-open post. The key hides the confirmer, not the era.
3. **The campaign's tier definitions overlap on "conventions"** (T0:
   "conventions, notes, pointers"; T1: "project conventions"). The rater
   freezes a tie-break rule first and puts its sha256 on ratings line 1. Score
   warns if it is absent.
4. **The s2 threshold moves n by about 3×** (10 / 15 / 28 at 3 / 2 / 1). Fix it
   before the close build, never after ratings exist.
5. **The s2 control arm is tiny:** 3 of the 15 sample items precede a flip. Zero
   control hits means the rater cannot see the old convention, and then an s2
   zero cannot anchor S2.
6. **s2 blinds timing, not direction.** "FIXED" in the new text shows which
   record is newer.
7. Single rater. Blinding is by procedure, not cryptography (same as R2H).
   Small n; descriptive only.

## Adoption (not mine to decide)

The S2 and S3 criteria stand as frozen. This is an optional instrument. If
GiLMore and Verity adopt it, the proposed sequence is:

1. **Before close**, in a file: rater (S3 names Verity; S2 needs a non-Cairn
   rater), `--min-overlap`, seed sha256.
2. **At close:** first freeze the input session tree (copy + manifest, the S5
   freeze-on-read lesson). Builds from the live tree are not byte-reproducible:
   it grew from 15 to 20 files between sample and rebuild (Assay). Then run
   `build --kind s3` and `--kind s2` on the frozen copy into a new dir, with
   `--window-close` pinned, and quote each build's `script_sha256` in its receipt. Commit manifests; the KEY stays with the executor.
3. **Rater:** freeze the rule → rate `packet/` only → post the ratings sha256
   (board or audit ledger) → signed "did not open sealed/".
4. **Executor:** `score`. S2 stale candidates go to artifact-level
   confirmation before they enter S2.

```
python3 team/blind_pack.py build --kind s3 --sessions '/home/bmosher/acp-pi/.pi-agent/sessions/*/*.jsonl' \
  --window-open 2026-09-12T11:05:00-07:00 --window-close <ISO> --seed <committed seed> --out <new dir>
python3 team/blind_pack.py build --kind s2 ... --min-overlap <pinned N> --out <new dir>
python3 team/blind_pack.py score --out <dir> --ratings <ratings.jsonl>
```

— **fsync**. Receipts are flushed; stories are buffered.
