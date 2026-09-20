# SPRINT 2 OUTLINE — draft for Brian's assessment (GiLMore, 2026-09-13 ~09:5x; revised ~22:2x per Stratum cold-read, team/COLDREAD-20260913-sprint2-outline.md — stale ask replaced, missing ask added, housekeeping trued up)

**Proposed duration:** 2 working days (Mon-Tue). The trial window closes EOD
Tuesday regardless, so the sprint rides the same clock.
**Theme:** fair comparison + warm start.

## Goals (user stories)

1. **As Brian, I can see all memory systems compared fairly on one frozen
   benchmark.** Kiln finishes the runner composition (in flight) -> Verity
   adapter check -> envelope arithmetic printed at P2 entry -> evaluation runs
   on free/metered lanes -> comparison table v1 (Perseus, Mem0, bm25, + every
   external with a working adapter). P2 entry results already in: 3,351
   questions, baseline arms locked.
2. **As Brian, I get benchmarks for the two things no external benchmark
   measures:** invocation (fire-before-mistake rate on labeled correction
   events) and material outcome (matched tasks with/without memory: time,
   errors, corrections). Source corpus: DONE — your pilot word came, the full
   corpus ran same day (1,250 closed files -> 4,098 unique operator turns;
   270 correction events + 26 repeat-instruction groups; 230 personal turns
   excluded, never persisted), with local-eyeball precision bands per class
   (negation and i_said ~100%, actually ~80%, env_fact_correction ~30-50%,
   wrong ~20-40%; n≈5-8/class). This goal can start Monday.
3. **As Brian, I get the trial window closed cleanly:** S4 adjudication from
   sealed packets (Corvid + Verity, blind), window report, RETRO-2
   (pre-registered) at window end. Window cap: EOD Tuesday.
4. **As Brian, my R2 deployment track stays warm:** day-0 smoke at work
   whenever convenient; rev-2 deploy script frozen and verified; the warm-start
   seed corpus (mined durable facts) lands in the vault before day 1. Pending
   team step: we re-send the verified rev-2 script to your work machine
   before day 1 (zero cost to you) so "whenever convenient" cannot silently
   become day 1.
5. **As Brian, I get a field refresh from the lost roadmap:** Phase-B-style
   harvest of the frontier benchmarks it names — candidate discovery only, no
   score import (roadmap rule). Owners: Corvid + Alice (web-capable turns).
   Status: 4 of the named benchmarks carded so far (MemOps; StreamMemBench;
   STALE + Supersede; MemSecBench + GateMem); 4 remain (StateMemBench,
   LongMemEval-V2, HaluMem, EvoMemBench/EvoArena).

## Housekeeping in-sprint
- QUEUE row 29 prune co-sign: DONE tonight (Verity PASS 21:46,
  VERITY-KNOWN-FAILURES-PRUNE-COSIGN.md). Row 28 (P2-entry second-driver
  verification) is the separate, still-open row.
- AGENTS.md stale test-baseline reference: one-line fix.
- anvil server.py one-liner: unblocks when Cairn's branch lands.
- Repo push: DONE this morning (26 commits, b0b761a..1682c4e).

## Asks of Brian
- Sign-off on this outline (or edits).
- The transcript-mining corpus produced a digest of 324 durable-fact
  candidates (318 unique groups). Decide: read/mark the digest yourself, or
  delegate the curation criteria to the fleet.
- Decide whether a model-assisted second pass over the corpus runs (costs
  metered tokens; we recommend it, precision bands above are eyeball-only).
- Accept the SWE-chat HF gate on the team account (background:
  EXTERNAL-CORPORA-RECOMMENDATION.md).
- R2 day-0 timing.

## What we are NOT doing (roadmap discipline)
- No leaderboard score imports. No "winner" declarations before comparable
  Phase-2 evidence. No composite prototype build until the ablation ladder
  (pi-lcm only / +retrieval / +state / +OM projection / full) is justified.
  The lost roadmap's Phase G composite and Phase H private-corpus endgame are
  sprint 3+ candidates, recorded and deferred.
