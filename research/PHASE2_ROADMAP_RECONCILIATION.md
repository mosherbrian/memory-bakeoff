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
that, and `results/` now holds 236 directories.

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

`project_memconflict_derivation_backlog.md` in project memory records that
deriving from MemConflict was agreed and deferred on 2026-09-06 - so the roster
question was raised, parked, and then rediscovered from outside in Gen124.

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

**Status: pinned, never run.**

`MEMCONFLICT_PIN.json` records `Code/` stages as `not_run`, and
`external/MemConflict` is gitignored and absent from the tree. Gen36-38 built
the contract and the release checks; nothing executed the benchmark.

Gen124 establishes what it would measure and that it is the right lane for the
system-selection question.

## PHASE F — synthesize the architecture, not the leaderboard

**Status: not started.** No architecture matrix exists. The roadmap correctly
gates this on "enough Phase-2 evidence", which we do not have.

## PHASE G — prototype the composite

**Status: correctly not started.** The roadmap says do not build until the
evidence supports it. It does not.

Adjacent work exists and should not be confused with it: `pi-lcm` is live and
carries eager compaction and prefix pre-warming, so one layer of the intended
composite is real. The state projection, lifecycle, and single context composer
are not.

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
