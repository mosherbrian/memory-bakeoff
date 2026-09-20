# CORVID-S12-1-VERIFY — verdict of record

**Verdict: VERIFIED PASS.** S12-1's build is present, its declared check exits
0, its evidence chain reproduces independently, and the measured result is the
honest negative the row's own reasoning predicts. The state-layer question is
**closed on this failure shape**: the tested thin layer does not protect against
the observed native failure.

Verifier: corvid-dsh — row S12-1 names me verifier; I authored neither the
build (kiln-flash's; its worker history is active at 12:50:33, the minute the
build files were written) nor the gate (plumb-fable's, verified PASS by me at
12:4x as `team/CORVID-S12-1G-VERIFY.md` ADDENDUM 5). Verified 2026-09-20 12:5x
PDT.

## Frozen inputs and the gate

| artifact | sha256 |
|---|---|
| `team/S11-LAYER-HIST/check.py` (gate, round 4) | `6cddb062…84f1b8` (56,552 B, mtime 11:37:49) — unchanged through every run |
| `team/S10-PI-LCM-HIST/trials.jsonl` (frozen corpus) | `52289107559502337f83de8b3cb7a2038155853d7373082b3bbb324504367b1d` |
| `team/S7-STATELAYER/thin_layer.py` (existing layer) | `c99b2ac781e5340a63a26d505251f8e8b35e71aa73af97f9bce726e05f09fd27` |
| `team/S11-LAYER-HIST/declaration.json` | `141bda3c…2497f` |
| `team/S11-LAYER-HIST/receipts.jsonl` | `393067a8…ba609` |
| `team/S11-LAYER-HIST/verdict.json` | `1ef671f6…52fef` |

Declared check, run from this seat on the built tree:

```
python3 team/S11-LAYER-HIST/check.py
CLEAN: S12-1 evidence, comparison, decision, and replay verified      rc 0
```

## What I checked, independently of the gate

1. **Prior citation is live and correct.** The declaration's `prior_fields`
   point into the REAL prior verdicts; read directly: S7 `pi-lcm-native`
   0/32/0/12 and `thin-layer` 0/32/0/12, S10 `native` 22/33/0/13. These are the
   row's prior values (S7-3 rule at m=0.5/k=0.1; S10 native 22/33). No number
   imported from a summary.
2. **Pre-registration.** `declared_at` 2026-09-20T12:50:00+00:00 precedes the
   earliest receipt (13:00:00Z); `limits.registration` is `"fresh"` with BOTH
   limits declared (m=0.5, k=0.1) and an explicit prediction (33, 0,
   `same_as_original`) plus a rationale; every one of the 268 receipts carries
   the exact declaration sha256 (0 mismatches).
3. **Generator reproduces the corpus byte-identically.** I ran
   `generate_s12_1.py` myself: stdout sha256 == the frozen corpus sha above.
4. **Replay reproduces the receipts.** I ran
   `harness_s12_1.py thin_layer.py declaration.json` myself: 268 rows, identical
   to `receipts.jsonl` apart from timestamps. The layer arm is not stored — the
   harness recomputes it by executing the REAL `ThinLayer().decide`.
5. **My own recount, from the raw receipts, with my own code** (not the gate's):
   - main native 33 distractors → 22 false supersessions; 13 updates → 0 missed
   - main layer 33 distractors → 33 false supersessions; 13 updates → 0 missed
   - before/after controls (both arms) 32/12 with 0 false supersessions, 0 missed
   - layer-rule violations: 0 (every layer `superseded` == `(scope,fact_type)`
     equality of original and candidate)
   - main ids == the frozen corpus ids for both arms (46/46)
   - reduction = (22/33 − 33/33)/(22/33) = −0.5; missed rate 0.0
   - protection false (m=0.5), safe true (k=0.1) → `close_trivial_layer_class`
   Everything matches `verdict.json` to the digit, including the six-cell
   sensitivity grid (m∈{0,0.5,0.8} × k∈{0,0.1}, reported whole as data, no cell
   picked).
6. **Two hats.** `reporting` names the measured role (bake-off MEMORY contestant)
   and the unmeasured stack-compaction role, `compaction_measured: false`,
   `compaction_conclusion_changed: false`.

## The result, stated plainly

Native pi-lcm fails on the broader frozen corpus (22/33 false supersession) and
the tested key-equality thin layer fails HARDER: because every frozen distractor
candidate carries the original's own (scope, fact_type) key, key equality
supersedes all 33 distractors — a false-supersession rate of 1.0 against native's
0.667, reduction −0.5, below the pre-registered m=0.5. Missed updates are 0, so
the layer is "safe" but not protecting. The row's own honest prediction
(33 false supersessions) was registered BEFORE the run and is what the run
found. **The trivial-layer class is closed on this failure shape.**

## Non-blocking limitations recorded (do not change the verdict)

1. **The native arm is an embedded per-trial decision vector**, not re-executed
   by a native engine in the harness; its aggregate is bound to the verified S10
   prior via `prior_fields`, and the gate re-checks that binding. So this row's
   NEW measurement is the layer arm (genuinely recomputed); the native arm is the
   prior, as the row's own framing states ("native on the broader corpus 22/33 …
   layer on the broader corpus = this row's result"). A future run could
   re-execute the native reader for a fully self-contained artifact.
2. **Chronology is internal, not authenticated.** The declared_at and receipt
   timestamps are written in the same batch as the artifacts; the gate's contract
   explicitly disclaims authenticating historical publication time. Pre-
   registration rests on internal ordering plus the sha binding, the same
   standard prior rows closed under.
3. **Housekeeping:** the builder did not update S12-1's status cell (no
   `claimed:`/`done:` stamp), so the poller closed the row on evidence. kiln-flash
   should stamp the cell so the board reads truthfully; the evidence itself is
   what this verdict rests on.

## Board state after this verdict

- S12-1: VERIFIED PASS. The sprint-12 research question on this shape is
  answered (protection fails; trivial-layer class closed).
- S12-1G: VERIFIED PASS (round 4, ADDENDUM 5).
- Standing instrument defect, not this work's: `dispatch.log` still marks corvid
  a producer of S12-1G, so the poller will not count the S12-1G verdict (but it
  WILL count this S12-1 one — corvid is not a producer of S12-1). The sprint
  close therefore still depends on correcting that ledger line — escalation
  E-13.

Probe fixtures: `/tmp/corvid-s12-1g-r4/`. — corvid-dsh
