# Phase 2 roadmap, reconciled against actual repository evidence through Gen124

Written for Gen125 under the control-plane instruction of 2026-09-07. The
roadmap being reconciled is `research/PHASE2_ROADMAP.md`, agreed 2026-09-02 and
recovered 2026-09-06 after the conversation that agreed it was orphaned. It is
preserved unedited; this file is the reconciliation, not a rewrite.

**The headline: the roadmap was agreed, immediately lost, and the project then
ran roughly ninety generations doing the thing its step 7 forbids.** Most phases
are not "behind schedule". They were never started, because nobody could see
them.

---

## PHASE A — finish Gen33, then PAUSE the old queue

**Status: half done, then violated for ~90 generations.**

Gen33 completed. The pause did not happen. The roadmap says "Do not immediately
issue Gen34 from the old contestant list"; Gen34 through Gen124 did exactly
that, and `results/` now holds 212 directories and 24 files.

Decision Gate A asked for a short "Round 2 interim findings" note before
admitting more contestants. `ROUND3_FINAL_READOUT.md` and
`ROUND3_SUPERSESSION_RESULT.md` exist and serve that purpose in substance,
though they postdate the gate rather than gating it.

**Consequence, not hypothetical:** the roadmap's own warning - "Do not exhaust
the original contestant list just because it exists" - is precisely what
happened.

## PHASE B — leaderboard and field refresh

**Status: NOT DONE until Gen124, and then only by accident.**

The roadmap names nine benchmark families to inspect: StateMemBench/StateMem,
LongMemEval-V2, Agent Memory Leaderboard, HaluMem, EvoMemBench/EvoArena,
GateMem, STALE, Supersede, and anything new testing dynamic state.

Through Gen123, none of that inspection is in the repository. What exists is
`research/MEMCONFLICT_PIN.json` (Gen36-38) and the Gen124 work.

Gen124 touched three of them, and only because a pilot needed a substrate:

- **StateMemBench** - searched, NOT FOUND. No repo in the paper, nothing on
  HuggingFace. The search is recorded as unfinished in
  `research/BENCHMARK_HARVEST_CHECK.md`, with the checks not run listed.
- **LongMemEval** - adopted as the reader-attribution substrate, content-pinned
  by sha256, `oracle` split.
- **MemConflict** - read from source in `research/PRIOR_ART_READ_FROM_SOURCE.md`.
  Its README states our exact problem; six memory systems are harnessed in it.

The remaining six are still uninspected. **This is the largest genuine gap and
Gen125 must close it**, which is why the control plane ordered the field refresh.

Decision Gate B - a ranked candidate intake answering "what distinct
architectural question would this contestant answer" - has never been produced.
Gen125 produces the first one.

## PHASE C — refresh the contestant roster

**Status: not done. The roster was consumed, not refreshed.**

Measured engines in the repository: Perseus, Mem0, AgentMemory, Hindsight,
Membukkit. Those are the ORIGINAL pool. No candidate discovered after
2026-09-02 has entered.

Deriving contestants from MemConflict was agreed and deferred on 2026-09-06.
That record lives in the implementer's project memory, OUTSIDE this repository,
and cannot be verified from the tree - noted because this document's stated
method is repository evidence, and one citation of mine did not meet it.

## PHASE D — common admission gate before longitudinal-v1

**Status: the machinery exists and is strong; it was built for a different
purpose and has never gated a new contestant.**

Present and working:
- exact version/commit identity - `MEMCONFLICT_PIN.json`, vendor pins
- frozen adapter contracts hashed before first scored query -
  `immutable-evidence-v1`, `scripts/run_gen118_freeze.py`
- provenance and journalling with fsync - `src/memory_bakeoff/evidence.py`
- unrelated-preflight discipline - the Gen118-124 freeze gates

Absent:
- no contestant has passed this gate, because no contestant has been admitted
  since it was built.

The Gen118-124 apparatus is therefore **reusable Phase-D machinery pointed at a
reader experiment**. That is the most useful reframing available of the last
seven generations.

## PHASE E — external benchmark lanes

**Status: PARTLY RUN, and an earlier version of this section said otherwise.**

**Correction.** This first read "pinned, never run", citing `Code/` stages as
`not_run`. Those are the benchmark's UPSTREAM stages. Gen38 ran a full release
against a held-out 27-persona slice: perseus, mem0 and a bm25 baseline, with
Hit@3 of 0.434 / 0.419 / 0.226 on dynamic conflict - the supersession question.
See `research/MEMCONFLICT_GEN38_FULL_RELEASE.md`.

So Phase E is not unstarted. It is **two engines of six, one slice, never
extended** - which is a much better position than this document first claimed,
and it means the primary lane already has an anchored result.

What remains: four locally harnessed engines, the six upstream harnesses, and
materialising `external/MemConflict`, which is gitignored and absent.

## PHASE F — synthesize the architecture, not the leaderboard

**Status: not started.** No architecture matrix exists. The roadmap correctly
gates this on "enough Phase-2 evidence", which we do not have.

## PHASE G — prototype the composite

**Status: PARTLY BUILT AND ALREADY MEASURED, and an earlier version of this
section said the opposite.**

**Correction.** This section first read "correctly not started" and claimed the
state projection, lifecycle and single context composer "are not" real. That is
false, and it was false in the direction that flatters the rest of this
document's story. Round-1 review of Gen125 found it; I verified every citation
before accepting it.

What actually exists, all committed 2026-09-04/05 - AFTER the roadmap was
agreed, so this is the one phase with rich post-roadmap activity:

- `research/PI_STATE_CONTROL_GEN43_PROTOTYPE.md`
- `research/PI_STATE_CONTROL_GEN44_PILOT_DESIGN.md` - line 68 freezes a
  composition order: `immutable_instructions, control, state, recent_window,
  latest_observation, artifact_refs`. **That is a single context composer**, the
  thing the previous wording denied existed.
- `research/PI_STATE_CONTROL_GEN45_LIVE_PILOT.md` - 24 live paired runs.
- `PI_STATE_CONTROL_GEN46/47` - harness-maintained state, then live, with a
  human-direction floor at Gen49 and a stop rule at Gen52/55.

**And it produced a NEGATIVE result that this document erased:**

    verifier passes    arm A `pi_default_v1`  12/12
                       arm B `pi_state_control_v1`   7/12

The composite lost to stock Pi, using more requests to do it. That is precisely
the evidence a future Phase-G decision needs, and it was already on disk.

**What is still true:** none of it was gated on the Phase B-F evidence the
roadmap demands, so it is Phase-G-*adjacent* work done out of order rather than
Phase G executed. But "not started" was wrong.

**Why this matters beyond the correction:** the "nobody could see the roadmap"
story holds for Phases B, C, D, E, F and H - review verified each independently -
and fails exactly here. A narrative that explains every gap by an external cause
should be checked hardest where it is most convenient, and this is where it
broke.

## PHASE H — realism endgame

**Status: not started, correctly.** Gated on the synthetic and external stages.

---

## Where Gen124 fits

It is **not** a roadmap phase. It is a Phase-D-quality apparatus, built during
an unpaused queue, pointed at a question the roadmap does not name: how much the
READER contributes to failure when retrieval is perfect.

The control plane's Gen125 ruling classifies it correctly as the
reader-attribution lane - explanatory, not primary. See
`research/EVIDENCE_LANES.md`.

Its result stays exploratory forever: 9 vs 0 on 17 items, crude-then-repaired
scorer, residual chronology, and 14 untouched holdout items.

## What this reconciliation changes about priority

1. **Phase B is the bottleneck and always was.** Six benchmark families remain
   uninspected. Everything downstream - roster, admission, matrix - waits on it.
2. **Phase D machinery is finished and idle.** The expensive part of admitting a
   contestant is already built.
3. **Phase E is one un-run benchmark away** from producing system-selection
   evidence, and it is already pinned.
4. The original queue is exhausted, which the roadmap predicted and forbade.

**So the shortest path to the project's actual question is: finish Phase B,
admit 3-5 candidates through the existing Phase-D gate, and run Phase E.**
None of that requires the reader apparatus, and none of it spends the holdout.
