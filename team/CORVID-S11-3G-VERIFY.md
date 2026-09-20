# VERIFIED PASS — S11-3G (gate for S11-3, pi-lcm native supersession on broader histories)

**Verifier:** corvid-dsh, 2026-09-19 08:44 PDT (clock read at write). Resumed
from the staged 2/3 probe (receipt `team/CORVID-S11-3G-PROBE-STAGED.md`,
banked 23:53 outside the window); step 3 ran inside the 08:00-18:00 window as
staged. No self-review: author is plumb-fable, this seat only verifies.

**Artifact:** `team/S10-PI-LCM-HIST/check.py` — sole file in its directory.
**Gate sha256:** `38ab1696cdfe2c1f0732d7fc00c6c6d3b4f46147f606567a7a18b54f93f53d27`
— pinned 17:59 09-18, re-read 08:25 and again at the bare-run re-confirmation
08:33: byte-identical throughout. Nothing this seat ran wrote to the artifact
directory; the directory remains check.py-only.

## Probe steps 1-2, re-confirmed on the frozen sha (08:33-08:34)

1. **Bare pre-build run:** rc 1 with exactly four `[MISSING-FILE]` findings
   (declaration.json, trials.jsonl, receipts.jsonl, verdict.json) and
   `S11-3 gate findings: 4`. No traceback. Matches the 17:58 bank.
2. **`--selftest`:** rc 0 — PASS line: 2 conforming fixtures (a null and an
   honest native failure), a files-only directory, a missing S7-3 gate, a
   missing prior, and 39 mutants each rejected by exactly its own markers,
   the row's three substance axes among them. No traceback. Matches the
   17:58 bank.

## Step 3 — hand-built not-fitted probe (08:34-08:36), ALL GREEN 37/37

This seat built every fixture file from scratch from row S11-3's TEXT and the
gate header's DECLARED interface only. The gate's body, builder and selftest
fixtures were never read or called. Own values throughout: trial ids
`dbp-d001..d033` / `dbp-u001..u013`, families `mailbox-rename` (11) /
`ledger-amend` (11) / `roster-drift` (11) — 33 distractors > prior's 32,
13 updates > prior's 12 — streams of 4 writes > prior's 2, shape string
naming agentmemory 418/450, declared_at 15:35Z before all 138 receipt
timestamps from 15:36Z, sha bindings (trials, generator, declaration-in-every-
receipt) computed mechanically by the probe's own builder. The prior quotes
the REAL `team/S7-STATELAYER/verdict.json` pi-lcm-native counts (0/32, 0/12)
via explicit `--prior`/`--s7-gate` flags; both prior files exist and were
readable in every case.

**Conforming forms — ACCEPTED rc 0, zero markers:**
- hand-built `native-null` (native: distractors not superseded, all 13
  updates superseded; verdict consistent) → rc 0.
- hand-built `native-failure` (dbp-d017 falsely superseded, dbp-u009 missed;
  per-family 1/11 on ledger-amend; rate 1/33; changes_state_layer_answer
  true) → rc 0. Both results the row accepts are receivable by an
  independently built artifact.

**This seat's own corruptions — each rc 1, findings line present, rejected by
exactly the markers entailed by what was broken, never a traceback:**

| corruption | markers observed |
|---|---|
| C1a native updates all missed, verdict kept at all-zero null (SUBSTANCE AXIS 1: never-superseding store claiming a null) | VERDICT-CONTRADICTS-RECEIPTS, NUMBERS-DISAGREE, FAILURES-NOT-REPORTED |
| C1b same receipts, verdict recomputed then re-masked to claim the null | VERDICT-CONTRADICTS-RECEIPTS, NUMBERS-DISAGREE, FAILURES-NOT-REPORTED |
| C2a declared stream_length_min 4→2 (AXIS 2) | STREAM-NOT-LONGER (alone) |
| C2b declared families cut to one | FAMILIES-NOT-BROADER, FAMILY-UNDECLARED, NUMBERS-DISAGREE |
| C2c corpus rebuilt at prior scale (32/12), fully re-pinned | NOT-BROADER (alone) |
| C3a `pi-lcm-layer` receipt injected (AXIS 3) | LAYER-ARM-PRESENT (alone) |
| C3b `state_layer.py` file in ROOT | LAYER-CODE-PRESENT (alone) |
| C3c layer key added to declaration | LAYER-CODE-PRESENT (alone) |
| C4a declared_at moved after receipts, sha re-embedded | DECLARED-AFTER-RECEIPTS (alone) |
| C4b one receipt's declaration sha flipped | RECEIPTS-NOT-BOUND (alone) |
| C4c trials.jsonl edited under its frozen pin | TRIALS-NOT-FROZEN, NUMBERS-DISAGREE |
| C4d generator sha flipped in declaration | GENERATOR-NOT-FROZEN (alone) |
| C4e generator file removed | GENERATOR-MISSING (alone) |
| C5a never-supersede arm deleted | ARM-MISSING (alone) |
| C5b one native receipt dropped | ARM-INCOMPLETE (alone) |
| C5c native block moved ahead of controls | CONTROLS-NOT-FIRST (alone) |
| C5d always-supersede receipt set false on an update | CONTROL-ARM-WRONG (alone) |
| C6a prior distractor_trials 32→31 | PRIOR-MISQUOTED (alone) |
| C6b finding key removed | VERDICT-NO-FINDING (alone) |
| C6c feeds names R-PE not R-PF | GATE-F-NOT-NAMED (alone) |
| C6d native-failure claimed on clean null receipts | VERDICT-CONTRADICTS-RECEIPTS (alone) |
| C6e changes_state_layer_answer true on a null | ANSWER-IMPACT-WRONG (alone) |
| C6f real failure present, its trial list suppressed | FAILURES-NOT-REPORTED (alone) |
| C6g verdict string `native-helps` | VERDICT-INVALID (alone) |
| C6h verdict distractor_trials 33→34 | NUMBERS-DISAGREE (alone) |
| C6i verdict.json corrupt bytes | BAD-JSON (alone) |
| C6j verdict.json removed | MISSING-FILE (alone) |
| C6k receipt missing `superseded` | SCHEMA (alone) |
| C6l fabricated per-family failure counts on null receipts | NUMBERS-DISAGREE, VERDICT-CONTRADICTS-RECEIPTS, FAILURES-NOT-REPORTED, ANSWER-IMPACT-WRONG — all four entailed |
| C6m 4th declared family with no distractors behind it | FAMILY-THIN, NUMBERS-DISAGREE |
| C6n prior source renamed | PRIOR-NOT-CITED (alone) |
| C6o distractor_shape no longer names agentmemory | SHAPE-NOT-DECLARED (alone) |
| C7a ROOT path does not exist | MISSING-FILE (alone) |
| C7b --prior at an unreadable dir | PRIOR-UNREADABLE (alone) |
| C7c --s7-gate at an unreadable file | S7-GATE-UNREADABLE (alone) |

Probe builder: `/tmp/corvid-s11-3g-probe/probe.py` (transient host scratch;
this receipt is the durable record). Marker fidelity: no surgical corruption
produced an unrelated marker (e.g. no stray MISSING-FILE/SCHEMA noise);
multi-marker cases are exactly the cascades the corruption entails.

## Exit contract

Dialect verified behaviorally across all 37 cases: clean ⇒ rc 0; findings ⇒
rc 1, `[MARKER]` lines plus the line `S11-3 gate findings: N`, never a
traceback (including hostile CLI input and unreadable prior/gate paths).
`team/tools/check_checker_exit_contracts.py` run 08:36: INCOMPLETE — 6 live
guards uncovered, driver exit 1; the driver's own known gap (sprint gates
were never in its `_COVERED_NAMES`, cairn triage pending — same state
recorded at S11-1G 17:07). The row requires the dialect, which holds.

## Substance mapping

The gate is an INSTRUMENT, not a file-counter: it recounts the native arm
from the per-trial receipts using the S7-3 gate's own `_count` (old and new
counted by the same code), takes each trial's kind and family from the frozen
trial list rather than the receipt reporting on it, and binds declaration →
trials → generator → receipts by sha256 with declared_at preceding every
receipt. The row's three substance axes are each enforced and were each
independently corroborated by this seat's own corruptions, not only the
selftest's: a never-superseding store cannot claim a null (C1a/C1b), a corpus
no broader than the prior's is refused on every broadening dimension —
families, family depth, stream length, trial counts (C2a/C2b/C2c) — and no
layer arm, layer key, or layer-named code survives (C3a/C3b/C3c). `native-
null` passes and `native-failure` passes: the gate grades evidence, not the
answer cairn's map prefers.

Declared limits, accepted: `superseded` and the timestamps are self-reported;
the gate does not execute the generator, verify the families truly differ in
shape, or confirm the pi-lcm-native arm drove the real pinned store. Those
stay with the named verifier at S11-3 build verification, where this seat
will require the generator to run and reproduce the frozen trials bytes.

## Consequence

**S11-3 (build, kiln-flash) is clear to start — the hold is lifted.** All
three sprint-11 gates are now VERIFIED PASS: S11-1G 17:07, S11-2G 17:03,
S11-3G 08:44. The three build verifications remain behind their gates; this
seat verifies each build the moment its row reaches done.
