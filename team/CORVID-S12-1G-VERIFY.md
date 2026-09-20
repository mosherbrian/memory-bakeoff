# CORVID-S12-1G-VERIFY — verdict of record

**Verdict: VERIFIED FAIL — gate returned to the gate-writer for re-issue.**

Verifier: corvid-dsh (row S12-1G names me; I did not author the gate — it is
plumb-fable's). Claimed 2026-09-19 14:21 PDT after the artifact landed mid-poll
(dir created 14:15:48 empty; `check.py` written 14:20:27). Gate sha pinned at
first read and unchanged through every run below:

```
4c51f0fc0477bdf0463af35c0e557fe647405e92131a1caa198678a0d8404423  check.py
```

## What the gate is

The header (lines 1-16) says it itself: the gate was derived from ROW S12-1G's
text only, **"ROW S12-1 was not supplied"** to the gate-writer — so the gate
enforces nothing about S12-1 and fails closed. Its `main()` bare path is
unconditionally `specification_findings(None) → [MISSING_ROW_S12_1_TEXT] →
exit 1` (lines 444-459). What it delivered instead of a substance gate is a
generic adversarial checker-checker: `--selftest` builds synthetic fixture
checkers (mutations) and proves the harness can accept one conforming checker
and reject 14 defective ones with exactly their expected markers.

## What I ran (all on the pinned sha)

| probe | command | result |
|---|---|---|
| bare run | `python3 check.py` | rc 1, `[MISSING_ROW_S12_1_TEXT]`, no traceback |
| selftest | `python3 check.py --selftest` | rc 0, "accepted the minimal conforming synthetic checker and rejected all 14 deliberately defective checkers with exactly their expected named findings" |
| selftest determinism | twice more | rc 0 both runs |
| arg contract | `check.py --bogus` | rc 1, `[INVALID_ARGUMENTS]`, no traceback |
| **substance-blindness probe** | bare run with cwd = a hand-built textbook-perfect S12-1 build | **rc 1, byte-identical `[MISSING_ROW_S12_1_TEXT]`** |
| **empty-dir control** | bare run with cwd = empty dir | rc 1, byte-identical output |

The probe build was hand-made from ROW S12-1's text alone (my own synthetic
values, never kiln's future build): `declaration.json` with both pre-registered
limits and the frozen trials sha `52289107…367b1d`, sha-bound
`receipts.jsonl`, `verdict.json` with controls, old-beside-new priors, and both
arms' results. **A perfect build and an empty directory are indistinguishable
to this gate.** Independence is trivially satisfied — the gate was written at
14:20:27 when no build artifacts existed anywhere to fit to; the defect is
missing input, not fittedness.

The team exit-contract driver (`team/tools/check_checker_exit_contracts.py`)
covers the 16 declared evidence-integrity guards, not sprint gates, so the
gate's own contract was verified by direct observation: exit 0 only on
selftest, exit 1 always with a named marker, no traceback path
(`CHECK_INTERNAL_ERROR` handler present).

## Why this is a FAIL, not a PASS

Row S12-1G's obligation: "Require every file the row declares, and check the
row's SUBSTANCE rather than counting files." This gate requires no files and
checks no substance. Worse, it breaks the chain it exists to serve: row S12-1's
declared check is `python3 …/S11-LAYER-HIST/check.py` bare — which exits 1
unconditionally, forever, **even after a flawless build**. Stamping VERIFIED
PASS would release a build whose row can never reach done through its declared
check. The check-before-build order therefore holds: **S12-1 is NOT released.**

To be fair to the gate-writer: failing closed on missing input is the honest
move, and the header documents it rather than pretending. The defect is in the
dispatch — S12-1's text sits on the board (QUEUE line 216) and evidently was
not carried to plumb-fable, while the identical wording on S11-3G produced a
substantive gate because it was.

## What the re-issue needs

1. Supply ROW S12-1's text to the gate-writer (board line 216).
2. Keep this delivered harness — the adversarial selftest machinery is sound
   and worth keeping; the re-issued gate should ADD the S12-1 specification:
   declare `declaration.json` / `receipts.jsonl` / `verdict.json` schemas as
   S12-1's text entails them (both pre-registered limits present BEFORE any
   receipt; every receipt sha-bound to the declaration; declared_at preceding
   all receipt timestamps; controls at both ends; old-beside-new quoting the
   S7-STATELAYER and S10-PI-LCM-HIST priors; both arms' numbers recomputed from
   receipts), plus markers for each violation, failing closed exactly as this
   one does when inputs are absent.
3. Re-verify from me re-starts the clock: new sha pinned at first read, bare +
   selftest + a not-fitted probe whose corruptions are rejected by exactly
   their entailed markers.

## Board state after this verdict

- S12-1G: VERIFIED FAIL stamped, row stays with plumb-fable for re-issue.
- S12-1: build stays held (no VERIFIED PASS; kiln must not claim).
- S12-2G: hold stamped 14:17; `team/S11-ABSTAIN3/` dir appeared 14:20:31, gate
  file not yet landed at last check — same failure mode is likely if the
  dispatch again omits row S12-2's text; this receipt is the advance notice.

Probe fixtures preserved at `/tmp/corvid-s12-1g-probe/` (perfect-build +
empty control) for the re-verification run.

---

# ADDENDUM 2 — re-issued gate re-verified: VERIFIED FAIL (second round)

**Verdict: VERIFIED FAIL — returned to plumb-fable again.** The re-issue is a
real gate that checks real S12-1 substance, and it is NOT fitted to any
finished build — my probes show it can accept a conforming world and fails
every corruption by exactly its named marker. But it is **un-satisfiable
against the frozen artifacts row S12-1 itself mandates**: no build, however
flawless, can ever make this gate exit 0 in the real tree. Stamping VERIFIED
PASS would again have released a build whose row can never reach done through
its declared check.

Verifier: corvid-dsh (gate is plumb-fable's; I authored neither this gate nor
any build it describes). Claimed 2026-09-19 15:5x PDT after cairn's clock-read
wisp; every run below on this sha, pinned at first read and re-read unchanged
after all runs:

```
1423f216139a268fd75abfb483fb7e27188a1b00da0ed1427a6a67c64726ec8d  check.py
```

(73,305 bytes, written 15:29:21 PDT — matches cairn's facts; NOT round 1's
failed 4c51f0fc…04423.)

## What genuinely improved — and passed

The gate now ENFORCES the row's substance: declaration with both pre-registered
limits (fresh vs explicit redeclaration at m=0.5/k=0.1), a required prediction
before any receipt, preregistration timestamp ordering, five-way sha bindings
(declaration/corpus/layer/generator/harness), $0/no-LLM/no-network/local
resources, both arms observing every frozen candidate, layer receipts
contradicting key-equality rejected, 8 controls bracketing all measurements
with required positive/negative results, native rerun pinned to 22/33 and
0/13, prior counts quoted from pointer-addressed sources beside new counts, a
complete Cartesian sensitivity grid recomputed from counts, the decision
recomputed from both declared limits, two-hats reporting fields, generator
byte-replay, independent key-equality probes of the declared layer, harness
replay identity, and input immutability during replay.

| probe | result |
|---|---|
| bare run (absent build) | rc 1, `[S12-1G:FILE_VERDICT] verdict.json is required`, no traceback — round 1's unconditional `[MISSING_ROW_S12_1_TEXT]` is gone |
| `--selftest` ×3 | rc 0 all runs, byte-identical output: 5 conforming fixtures accepted, 138 distinct negatives rejected by their exact named findings, both-limit boundaries + reduction-unit conflation verified |
| `--bogus` | rc 1, `[S12-1G:CLI]`, no traceback |
| exit-contract driver | `team/tools/check_checker_exit_contracts.py` declares the 16 evidence-integrity guards as its covered set; sprint gates are out of scope, so this gate's contract was verified by direct observation (the four rows above; `CHECK_INTERNAL_ERROR`/`INPUT_ERROR`/`IO_ERROR` handlers present, none observed) |
| **my accept-world** | **rc 0, decision=close_trivial_layer_class** — a world I built from row S12-1's text alone: my own field names (orig/cands/k), my own scopes/values, m=0.6/k=0.05 fresh, my own timestamps and prior-document pointer shapes, generator + a harness that genuinely recomputes layer-arm outcomes through the declared API. Not the gate-author's fixtures. |
| **10 single-corruption mutants** | each rejected by exactly its entailed marker: LAYER_OBSERVATION_RULE, EVENT_COVERAGE, CONTROL_ORDER, NEW_NATIVE_COUNTS, SENSITIVITY_DECISION, PREREGISTRATION_ORDER, RECEIPT_CORPUS_HASH, M_LIMIT, SENSITIVITY_CARTESIAN, CONTROL_COVERAGE |
| **reallayer-world** | an otherwise-conforming world whose LAYER bytes are the REAL `team/S7-STATELAYER/thin_layer.py`: rc 1, `LAYER_EXECUTION` |
| **p1 textbook build, production anchor** | declaration/receipt/verdict binding the REAL frozen digests (corpus 52289107…367b1d, layer c99b2ac7…), real prior pointers (S7 arms/pi-lcm-native + thin-layer, S10 native), real gen_trials.py + run_statelayer.py bindings: rc 1, `[S12-1G:CORPUS_LAYOUT] unresolved JSON pointer: /kind` |

## Why FAIL: three independent un-satisfiability defects

**A. The corpus layout cannot read the frozen corpus.** `layout.kind` is a
JSON pointer relative to each CANDIDATE (`read_trials` resolves it per
candidate), and JSON pointers cannot ascend. In the frozen
`team/S10-PI-LCM-HIST/trials.jsonl` — whose exact bytes the gate mandates via
the production digest anchor 52289107…367b1d AND byte-exact generator replay —
`kind` exists only at TRIAL level; candidate stream entries carry only
{id, text, ts, role, scope, fact_type}, and role values
("near-neighbor"/"newer"/"original") are not "distractor"/"update". No pointer
resolves. Empirically: `[S12-1G:CORPUS_LAYOUT] unresolved JSON pointer: /kind`
under the best available layout (original=/stream/0, writes=/stream).

**B. The candidate totals cannot match the frozen corpus.** `read_trials`
hardcodes exactly 33 distractor + 13 update CANDIDATES (one per trial), but
the frozen corpus has 3 candidate writes per trial (4-write streams): 99
distractor + 39 update opportunities. No layout can yield 46 candidates from
46 trials — the only per-record lists have 4 (stream) or 3 (jaccard) elements.
The row's 33/13 are TRIAL counts; the gate counts candidate events and pins
them to the trial numbers.

**C. The layer API cannot load the frozen layer.** `execute_layer` resolves
`api.key`/`api.decide` as module-level identifiers (`getattr(module, name)`,
names must be `isidentifier`, so no dotted access) and calls
`key(write)` expecting a tuple. The real `thin_layer.py` — the exact path the
gate fixes and the declaration must sha-bind — exports ONLY the `ThinLayer`
class (staticmethod `key_of`, instance method `decide`); `ThinLayer(record)`
raises TypeError → `LAYER_EXECUTION` always (verified by direct module load:
the sole module-level name is `ThinLayer`; and end-to-end in reallayer-world).
Editing the prior artifact to add module-level wrappers is not available to a
builder: S7-STATELAYER is a completed VERIFIED row and the standing rule forbids
overwriting completed result directories — and it would break the prior's own
sha pins.

Independence/not-fittedness is NOT the defect this round: the gate was written
at 15:29 when no S12-1 build existed anywhere, and my probe world proves it
accepts conforming evidence it was never shown. The defect is that the
gate-writer modeled an imagined artifact shape (per-candidate kind fields,
module-level layer functions — exactly the shapes of its OWN selftest
fixtures) instead of the frozen shapes the row names. The selftest cannot
catch this class: every selftest world is synthetic, so a production interface
that matches no real artifact still passes 5/5 positives and 138/138 negatives.

## What the next re-issue needs

1. Derive the corpus layout from the REAL frozen shape: kind addressed from
   the RECORD (e.g. one trial-level pointer applied to each candidate, plus a
   writes convention that excludes the original — the real streams are
   [original, c1, c2, c3]); count candidate events the real corpus actually
   has (99/39), or declare the observation unit as the trial with a per-trial
   verdict, so 33/13 are the trial counts the row means.
2. `layer_api` must address the REAL exported shape, e.g.
   `{"class": "ThinLayer", "key": "key_of", "decide": "decide",
   "arguments": "writes"}` — instantiate once in the worker, call the bound
   methods, keep the independent key-equality probes at full strength.
3. Keep ALL current machinery — schema, preregistration ordering, sha
   bindings, bracketing controls, grid recomputation, replay identity, the
   adversarial selftest. My battery confirms it works and fails honestly.
4. ADD a selftest case whose corpus and layer fixtures mirror the REAL frozen
   shapes (trial-level kind, 4-write streams, class-based layer) so a
   production-interface defect can never again pass a fully green selftest.

## Board state after this verdict

- S12-1G: VERIFIED FAIL stamped (second round), row returns to plumb-fable.
- S12-1: build stays HELD — no VERIFIED PASS, kiln must not claim.
- Probe fixtures preserved: `/tmp/corvid-s12-1g-reverify/build_and_run.py`
  plus the run/ worlds (accept, m01–m10, reallayer, p1root).

ADDENDUM 3 — 2026-09-20 08:0x PDT (clock read at write): re-run on the
fleet-poller "work is finished and waiting on YOUR check" wake. **No verdict
change: VERIFIED FAIL stands, and no PASS is possible or filed.**

Verifier: corvid-dsh — I authored neither this gate (plumb-fable's) nor any
S12-1 build (there is none). Claimed by standing assignment, not by this seat.

What I re-ran, on this sha pinned at read and re-read after every run:

```
1423f216139a268fd75abfb483fb7e27188a1b00da0ed1427a6a67c64726ec8d  check.py
```
(73,305 B, mtime 2026-09-19 15:29:21 PDT — **unchanged**; the third re-issue
has NOT landed.)

| probe | command | result |
|---|---|---|
| S12-1 declared check (bare) | `python3 S11-LAYER-HIST/check.py` | rc 1, `[S12-1G:FILE_VERDICT] verdict.json is required` — no build to verify |
| S12-1G declared check | `python3 S11-LAYER-HIST/check.py --selftest` | rc 0, 5 conforming / 138 negatives — proves the GATE, not the work |
| rowcheck S12-1 | `rowcheck S12-1 --json` | `check_exit: 1` → gate=fail |
| rowcheck S12-1G | `rowcheck S12-1G --json` | `check_exit: 0` → gate=pass (the `--selftest` false-done) |
| `ls S11-LAYER-HIST/` | — | only `check.py`; no `declaration.json`, `receipts.jsonl`, `verdict.json` |

Nothing to verify exists: S12-1 is unbuilt and HELD (no build artifacts, its
declared check exits 1), and S12-1G's only artifact is the same round-2 gate
this receipt already failed. **Filing VERIFIED PASS here would release a build
whose row can never reach done through its declared check** — the same
chain-breaker ADDENDUM 2 refused. No `CORVID-S12-1-VERIFY.md` is filed either:
S12-1 is not built, and a verdict file for it would be counted by the loop as
an *independent verdict on an unbuilt row* (existence-of-file ≠ independence),
the exact failure this project exists to avoid.

## Why the poller woke this seat (root-caused, not guessed)

The 2026-09-20T15:01:48Z wake is the `verifier-dark` REMEDY of the sprint-close
hold: `SPRINT-CLOSE HELD: S12-* rows are 4 done but only 2 carry an independent
verdict`. Two independent instrument defects make that count wrong:

1. **The dispatch ledger mislabels my verification as production.** Line 69 of
   `~/.local/share/agent-deck/conductor/glm/dispatch.log` records
   `1789854294 4a8787475e71863b111539f29cda2568 producer corvid-dsh` — and
   `4a878747…` is the md5 of row S12-1G's task text. `status_verdict()` therefore
   skips every `CORVID-*S12-1G*VERIFY*` file as a producer's own work, so the
   verdict on disk is invisible to the loop. This is the S11-3G ledgering
   defect (`KILN-S11-3G-VERIFY.md`), live again: **no corvid re-file can clear
   it** — any filename this seat writes is skipped the same way.
2. **S12-1G counts done on `--selftest`.** The declared check in the row is
   `check.py --selftest`, which proves the gate rather than checking the work;
   rowcheck returns pass, so the sprint detector counts the row finished on
   evidence before it is verified. This is the documented `--selftest`
   false-done class (S7-1..S7-4, 2026-09-17).

## What actually unblocks the sprint (not a corvid file)

- **cairn / infra:** correct the ledger — the `4a878747…` entry is a VERIFY
  dispatch recorded as `producer`. Until that is fixed the loop cannot see any
  verdict on S12-1G.
- **plumb-fable:** the third re-issue per ADDENDUM 2's fix list (real corpus
  layout, 99/39 candidate counts or trial-unit observation, class-addressed
  `ThinLayer` API, real-shape selftest fixture). This seat re-verifies the
  moment it lands.
- **Board:** S12-1G's declared check should be the bare run, not `--selftest`.

Until then the sprint is held *correctly*: S12-1 is unbuildable and S12-1G is
not passed. — corvid-dsh

---

# ADDENDUM 4 — THIRD re-issue re-verified: VERIFIED FAIL (third round)

**Verdict: VERIFIED FAIL — returned to plumb-fable / cairn again.** The third
re-issue is a materially better instrument: it enforces the row's substance, it
is NOT fitted to any build (there is none), it fails honestly on bad input, and
two of ADDENDUM 2's three defects are fixed. But it is **still un-satisfiable
against the frozen corpus row S12-1 itself mandates**, on a new condition.

Verifier: corvid-dsh — I authored neither this gate (plumb-fable's) nor any
S12-1 build (none exists). Claimed 2026-09-20 10:53 PDT on the poller's
"work is finished and waiting on YOUR check" wake. Gate sha pinned at first read
and re-read unchanged after every run:

```
24d83b9efa99847d3c694947c8c8a12a9c2cc3a6f8a16661f291685b8539bd5f  check.py
```
(83,743 B, mtime 2026-09-20 10:50:xx PDT — NOT round 2's `1423f216…26ec8d`; the
staged `tmpfz62htm5.tmp` is gone.)

## What passed

| probe | command | result |
|---|---|---|
| bare run (absent build) | `python3 check.py` | rc 1, `FINDING: S12-1G/MISSING_FILE: Required file missing: …/verdict.json`, no traceback |
| arg contract | `check.py --bogus` | rc 1, `FINDING: S12-1G/CLI_USAGE: unrecognized arguments: --bogus`, no traceback |
| `--selftest` ×1 | `check.py --selftest` | rc 0, "4 conforming fixtures accepted; 53 distinct nonconforming fixtures rejected by their own named findings", sha unchanged |
| exit contract | direct observation | `--selftest` rc 0 only; every other path rc 1 with a named `FINDING`; `CHECK_INTERNAL_ERROR`/`INPUT_ERROR`/`IO_ERROR` handlers present, none observed (the `team/tools/check_checker_exit_contracts.py` driver declares the 16 sibling guards, not sprint gates) |

The gate enforces real substance: declared-before-receipt limits with both
pre-registered values, declaration/receipt sha bindings, input immutability,
bracketing controls at both phases, per-trial coverage, frozen-corpus and
generator byte-reproduction, replay identity, native reproduction of the
observed failure, old-beside-new priors, limit-metric identity, two-hats
reporting, local-only execution, and a full sensitivity grid. **Independence is
trivial: the gate predates any build; no build artifacts exist anywhere.**

## Why FAIL: `load_cases` cannot accept the frozen corpus

`load_cases` (check.py ~396-492) demands `used_locations == all_locations`,
where `all_locations` is every JSON location in the corpus whose object carries
BOTH `scope` and `fact_type`, and `used_locations` is the union of each case's
`original` and `write` locations (`kind` is not counted). It separately pins the
case count at exactly 33 distractor + 13 update. Against the real frozen corpus
`team/S10-PI-LCM-HIST/trials.jsonl` — whose exact bytes the gate mandates
(prefix `52289107`, suffix `367b1d`, and their full digest) — the arithmetic
cannot close:

- 46 records, 33 `kind:"distractor"` + 13 `kind:"update"` (matches the row).
- Each record has **5** key-bearing objects: the record root (`scope` +
  `fact_type` present) plus the four `stream[*]` writes. So `all_locations`
  = **230**.
- 46 cases × at most 2 locations each = **92**. `92 ≠ 230`. There is no case
  shape that closes the gap, because adding cases is forbidden by the 33/13
  denominator and each case contributes only its original and write.

Decisive probes, calling the gate's OWN `load_cases` on the real bytes:

| probe (declaration `cases`) | gate's own result |
|---|---|
| original=`/stream/0`, write=`/stream/1`, kind=`/kind`, one case per line | `CORPUS_CASES: Trial references must cover the entire frozen corpus and its writes.` |
| original=root (`""`), write=`/stream/1`, kind=`/kind` | same `CORPUS_CASES` finding |
| original=`/stream/0`, write=`/stream` (whole list) | `WRITE_KEY: A write must be an object.` |

**The mismatch is the shape, and it is exactly ADDENDUM 2's failure class.**
The gate's own selftest corpus (`fixture_trials`, check.py ~1402) is a flat
record `{id, kind, original:{scope,fact_type,…}, write:{scope,fact_type,…},
native_supersedes}` — **2** key-bearing objects per record. `load_cases` ACCEPTS
that shape (46 cases, verified). So 4/4 conforming + 53/53 negatives green
cannot see the defect: every synthetic fixture shares the gate author's imagined
record shape, while the production corpus puts the category at the record level
and the writes in a four-element `stream`.

Also verified fixed from ADDENDUM 2: [B] the denominator is now trial-level
33/13 (not candidate-event 99/39), and [C] the layer/harness are no longer
resolved by hardcoded module-level names — the gate now requires the replay to
actually EXECUTE the declared thin layer and S7 harness (`REPLAY_LAYER_USE` /
`REPLAY_HARNESS_USE` via an execution trace). Both improvements are real.

## What the fourth re-issue needs

1. Define case coverage against the REAL record shape: either (a) one case per
   frozen trial whose `original` = `/stream/0` and whose write set is the
   record's remaining key-bearing writes (so the trial, not the write, is the
   observation unit and 46 cases is correct), or (b) a per-write case set whose
   denominators are the counts the real corpus actually produces
   (46 originals + 184 writes), reported as the row means them.
   Keep `write_key`, the same-record/pairing rules, and the coverage intent.
2. ADD a selftest fixture whose corpus mirrors the REAL shape (record-level
   `kind`, a `stream` of four writes, root carries `scope`+`fact_type`) so a
   production-shape mismatch can never again pass a fully green selftest.
3. Keep the rest of the machinery — schema, preregistration, sha bindings,
   bracketing controls, grid recomputation, generator byte-reproduction, replay
   identity, execution-trace layer/harness checks, and the 53 named negatives.

## Board state after this verdict

- S12-1G: VERIFIED FAIL (third round), returns to plumb-fable/cairn.
- S12-1: build stays HELD — no VERIFIED PASS, kiln must not claim.
- Probe fixtures: `/tmp/corvid-s12-1g-r3/` (`probe_cases.py`,
  `probe_fixture_shape.py`, and their output).

*(Rounds 1 and 2 above retained as history.)* — corvid-dsh

---

# ADDENDUM 5 — FOURTH re-issue re-verified: VERIFIED PASS

**Verdict: VERIFIED PASS — the gate now genuinely checks S12-1's substance and
is satisfiable against the real frozen artifacts. S12-1 is RELEASED to
kiln-flash.** Three substantive rejections preceded this; the fourth is a real
instrument, and the fourth-round gate's own author discarded a larger attempt
because it failed its own selftest, so this is the last attempt that passed.

Verifier: corvid-dsh — I authored neither this gate (plumb-fable's) nor any
S12-1 build (none exists). Verified 2026-09-20 12:3x–12:4x PDT. Gate sha pinned
at first read and re-read unchanged after every run:

```
6cddb06271b669aabc7248f662dd0b16ae1670330c7209b10a2b08507884f1b8  check.py
```
(56,552 B, mtime 2026-09-20 11:37:49 PDT.)

## Declared checks, run from this seat

| probe | command | result |
|---|---|---|
| bare run (absent build) | `python3 check.py` | rc 1, `FINDING[MISSING_FILE]: …/declaration.json`, no traceback |
| arg contract | `check.py --bogus` | rc 1, `FINDING[ARGUMENTS]: unrecognized arguments: --bogus`, no traceback |
| `--selftest` | `check.py --selftest` | rc 0: "conforming fixture accepted; 72 distinct named rejections verified; production pin, both-limit decisions, and exit contract verified" |
| exit contract | direct observation | `--selftest` rc 0 only; every other path rc 1 with a named `FINDING`; no traceback path |

## The decisive test: a real-shape conforming world is ACCEPTED

Rounds 2 and 3 failed because the gate was **un-satisfiable** against the frozen
artifacts. I rebuilt the round-3 test and ran it again, then constructed a full
conforming artifact against the **real** frozen corpus and the **real** thin
layer, and ran the gate's own `_validate` end-to-end:

- root: real `team/S10-PI-LCM-HIST/trials.jsonl` (sha `52289107…367b1d`), real
  `team/S7-STATELAYER/thin_layer.py`, both real prior verdicts, the real
  two-roles policy.
- declaration `trial_fields` = {id:`/trial_id`, kind:`/kind`,
  original:`/stream/0`, candidate:`/stream/1`} — i.e. the corpus's ACTUAL shape
  (record-level `kind`, writes in a four-element `stream`), not a flat
  `original`/`write` fixture record.
- 46 main receipts per arm covering every frozen trial; layer decisions computed
  by executing the REAL `ThinLayer.decide` through the gate's own replay driver;
  priors read from the real S7/S10 verdicts; both endpoint controls 32/12.
- **Result: ACCEPTED, rc 0 (clean).** ADDENDUM 4's coverage objection (round 3's
  `used_locations == all_locations` demanded 230 locations) is gone — coverage is
  now per trial (46), which is exactly the real shape.

**Not fitted, independently:** my probe world shares nothing with the gate
author's synthetic `fixture()` (his is a flat `{id,kind,original,candidate}`
record; mine is the production stream record), and the gate accepts both. The
gate was also written before any S12-1 build exists.

## My own corruption battery on the real path (not the author's fixtures)

| mutation I applied to the conforming world | gate's own finding |
|---|---|
| limits.reduction_metric set to an absolute metric | `REDUCTION_METRIC` |
| one main receipt dropped | `ARM_COVERAGE` (expected 46 unique trials) |
| a layer receipt's superseded flipped | `LAYER_RULE` (key equality) |
| receipt rebound to different declaration bytes | `DECLARATION_BINDING` |
| generator emits nothing | `GENERATOR_REPLAY` (byte-identical regen) |
| harness never calls the real `layer.decide` | `LAYER_EXECUTION` |
| frozen corpus value altered | `DISTRACTOR_KEY` |
| verdict layer count altered | `NEW_LAYER_BROADER` |
| prediction out of range | `PREDICTION` |
| corpus byte flip to invalid JSON | `INVALID_JSON` |

Every one rejected by exactly its entailed marker, no traceback.

## ADDENDUM 4's three conditions, checked

1. **Coverage defined against the real record shape — MET.** `trial_fields`
   pointer extraction + per-trial main coverage (46 == frozen ids per arm), and
   my real-stream-shape world passes.
2. **Selftest fixture mirrors the production shape — NOT MET (non-blocking).**
   `fixture()` still builds a flat `{id,kind,original,candidate}` record with
   `trial_fields` pointing at those flat fields, so a green selftest still would
   not catch a production-shape mismatch by itself. It matters less now because
   the gate is shape-agnostic and I proved the real shape independently, but the
   hardening ask stands as a residual.
3. **All machinery kept — MET.** Preregistration with both limits, sha bindings,
   endpoint controls, phase order, layer-key rule, priors, sensitivity grid,
   generator byte-reproduction, replay identity, execution-trace layer/harness
   use, two-hats reporting, local-only, and the named-negative selftest.

## State after this verdict

- S12-1G: VERIFIED PASS (fourth round). **S12-1 is released** — kiln-flash may
  claim and build it; the build must close through the bare declared check.
- Residual (non-blocking): the selftest fixture does not mirror the production
  stream shape (condition 2 above); recommend the gate-writer add one.
- Standing instrument defect, not this gate's: the dispatch ledger still marks
  corvid as a producer of S12-1G (`dispatch.log` line 74), so the poller's
  `status_verdict()` will not count THIS verdict — see escalation E-13. A green
  gate and a filed verdict do not unblock the sprint until that line is fixed.
- Round 3 rejected what its author had already discarded a larger attempt for;
  rounds 1–3 were unsatisfiable-shape defects, and this receipt is the record of
  four substantive rounds, stated plainly.

Probe fixtures: `/tmp/corvid-s12-1g-r4/` (`probe_e2e.py`, `probe_mutations.py`).

*(All earlier rounds retained above.)* — corvid-dsh
