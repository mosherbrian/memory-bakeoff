I have now read the repository thoroughly and recomputed what could be recomputed. Here is my accounting.

---

VERDICT: DEFECTS_MINOR

---

# Independent accounting — Memory Bake-off repository, as of commit `76e5930` (2026-09-07)

**What I did.** Read `STATUS_AND_FINDINGS.md`, `CODEX_HANDOFF.md`, `AGENTS.md`, `ROUND3_FINAL_READOUT.md`, `ROUND3_SUPERSESSION_RESULT.md`, `handoff/CODEX_TO_CHATGPT.md` (all 4,688 lines), `reviews/LEDGER.md` (all 166 rows), `control-plane/*`, `tests/KNOWN_FAILURES.json`, the `research/` directory (137 documents, selectively), and the `results/` tree (236 directories). I re-ran the lineage test gate (245 passed), the full suite (26 failed / 1557 passed / 3 skipped / 5 errors), the sealed-manifest verification (247/247 artifact files match their sha256), the MemBukkit vendor verification (9/9 files), and recomputed headline numbers from raw artifacts where they exist. I did not read the implementer's own accounting and none of this defers to it.

---

## 1. WHAT THIS PROJECT IS FOR

In the repository's own words, it is "a reproducible, coding-flavored benchmark for persistent agent memory systems" (`README.md:5`) that grew into something narrower: a **component evaluation inside a larger agent architecture** (`ARCHITECTURE.md`, §A). Ten memory systems (BM25/TF-IDF/LSA/RRF baselines plus Mem0, agentmemory, Claude-Mem, MemBukkit, Habitus, Hindsight, later Graphiti and "Perseus") are evaluated on a canonical corpus of **50 records / 26 queries** (`results/corpus.json`, verified) plus a 500-record stress variant, with the harness owning ground truth and grading (`STATUS_AND_FINDINGS.md:34`). The emerging thesis is that "long-term agent memory may depend at least as much on memory lifecycle, temporal policy, evidence competition, contamination control, and abstention as on the embedding model itself" (`STATUS_AND_FINDINGS.md:66`). Execution is by an AI implementer under a human "control plane" (`CONTROL_PLANE.md`), with blind AI rival reviewers gating each generation (`reviews/README.md`), across 125 numbered generations in 8 days (git log: first commit 2026-08-30 23:03, last 2026-09-07 09:17; 382 commits, all authored by Brian Mosher).

---

## 2. WHAT IT HAS ACTUALLY PRODUCED

I separate what an outside auditor could verify today from what they could not.

### Replicated / recomputed-from-tree (would survive audit)

1. **agentmemory's write-time Jaccard supersession falsely retires 92.9% of distinct stress facts.** `results/agentmemory_raw_product_gen13_stress-r1/lifecycle.json` records `retired_memory_count: 418`; the corpus has 450 deliberate stress distractors; 418/450 = 92.9%. Three repetitions, identical (`research/AGENTMEMORY_RAW_PRODUCT_GEN13.md`). The same runs show retrieval Hit@5 of 1.000 *because* the hard records were deleted. This is the project's single most valuable product finding, and the project correctly refuses to credit it as retrieval.
2. **Every engine co-returns the superseded record alongside the current one — 192/192.** I recomputed this from `results/replication_gen99/{perseus,hindsight,mem0,agentmemory}.json`: all 192 rows carry `stale_version_interference`. Replicated across four independent semantic cores after a one-core observation (Gen97→Gen99).
3. **Round-3 supersession mechanism results** (`ROUND3_SUPERSESSION_RESULT.md`): Perseus explicit lineage removes stale co-return 48/48; Hindsight state-transition is accepted and recall-identical 0/48; agentmemory's automatic rule fires 12/48, all in one core; Mem0's arm unavailable in the pinned no-LLM profile. Correctly reported as non-commensurable, never summed.
4. **The baseline scoreboard reproduces exactly.** `results/core5/summary.md` and `results/stress4505/summary.md` match every number in `STATUS_AND_FINDINGS.md:69-90` (BM25 0.917/0.792, dense LSA 0.958/0.583, Habitus 0.875/0.792 with prohibited@5 0.025, etc.).
5. **The 56-call real reader trace.** `results/sidecar_reader_trace/` holds exactly 56 requests and 56 responses (counted). BM25 12/14 (both failures omissions), TF-IDF 12/14 including **one confidently repeated prohibited stale deploy command** (rate 0.071), dense LSA and RRF 14/14 (`BUILD_MANIFEST.md`). This is a real, archived, replay-verified observation — though n=14 cases, one model, one pass.
6. **Claude-Mem's default 90-day semantic window collapses Hit@5 to 0.208; removing only the window restores 0.958/0.583, byte-identical to the dense-LSA control.** Recomputed from `results/claude_mem_compare_core/summary.md` and `..._stress450/summary.md`. A clean policy-vs-representation result — in the controlled arm only.
7. **Hindsight v0.9.2 raw/no-LLM**: core 1.000/1.000, stress 0.833/0.708, three identical repetitions (`research/HINDSIGHT_LEARNED_RERANKER_GEN6.md:7`, artifacts under `results/hindsight_gen5_external_local_stress_r*`).
8. **MemBukkit bucket routing preserves stress recall (0.583/0.542) while scanning a fraction of the bank** — the 0.583/0.542 half reproduces from `results/current_stress4505/summary.md` and `results/membukkit_none_0.3/summary.csv`. The "~32.9% of the bank" half does **not** reproduce from any committed measurement (see §5).
9. **Round-2 longitudinal triangulation**: seven failure classes recur across Perseus/Hindsight/Mem0 under append-only ingestion, five at identical aggregate counts (`research/ROUND2_REPORTING_INTEGRITY_GEN34.md:70`).
10. **The sealed-evidence chain is intact.** I verified all 247 manifest-bound files across every gen109–gen123 attempt match their recorded sha256. The MemBukkit vendored core verifies against upstream blob SHAs (ran `scripts/verify_membukkit_vendor.py`: 9/9 OK).
11. **Test accounting is honest.** I ran the authoritative lineage gate: 245 passed, matching `AGENTS.md`. I ran the whole suite: 26 failed / 5 errors, every one matching the pinned clusters in `tests/KNOWN_FAILURES.json` (8 MemBukkit run-provenance, 16+5 absent 182MB MemConflict dataset, 2 frozen-source-drift with a documented clearing condition). Nothing unlisted fails.

### Single observations (real but unreplicated)

- The Habitus prohibited@5 = 0.025 stress result (single run, `results/habitus_stress/summary.csv`).
- The "pi" agent-control experiments: harness-maintained state 12/12 vs model-driven 9/12 over 24 live runs (`research/PI_STATE_CONTROL_GEN47_HARNESS_STATE_LIVE.md`); the quiescent stop-rule series (Gen52–55). Interesting, self-contained, never externally replicated.
- The Gen124 ordering pilot: cleaned n=17, chronological 15/17 vs reversed 12/17 with dates, 14/17 vs 5/17 without, 9-vs-0 discordant, and 12 of 14 wrong answers being the verbatim superseded value (`research/pilot_ordering/PILOT_HEADLINE.json`, computed). The project itself has ruled this **exploratory forever** because the scorer and eligibility rule were repaired during review (`research/EVIDENCE_LANES.md`, `control-plane/GEN125_INSTRUCTION.md` ruling 2).

### Retracted (correctly, and visibly)

Gen85 reader-order effect (quarantined, parse defect); Gen100's kestrel explanation; Gen102's agentmemory supersession number (harness defect, not product); Gen114's headline "stale co-return makes the reader contradict itself 21/24" — retracted at Gen115 when adjudication found 0 explicit contradictions and an undecidable fixture; Gen123's "no order effect" (the attempt's own estimands contradicted it); "nobody measures ordering" (ConflictQA exists); the crude-scorer safety principle (LEDGER #136). The retraction ledger is unusually good: retracted claims are guarded by a test that refuses their return (`tests/test_retracted_claims_stay_retracted.py`).

---

## 3. WHAT IT HAS NOT PRODUCED

Stated as flatly as the findings:

1. **No confirmatory result from the reader-interference line — the project's longest single experimental effort.** Gen109–Gen125: seventeen generations, 41 sealed attempts (19 in Gen118 alone), five actual model runs — Gen110 (no result), Gen114 (retracted), Gen117 (NON_EVIDENCE), Gen122 (NON_EVIDENCE), Gen123 (4/12 cores interpretable, NON_EVIDENCE). The question "does stale co-return change the answer?" is still open. The only data bearing on it is the Gen124 pilot, which is exploratory by the project's own ruling.
2. **No product-mode run for four of the engines.** Mem0's full Qdrant/fastembed/entity/reranker stack, Claude-Mem's compression worker, MemBukkit's intended pretrained models (upstream repos return 401, `research/MEMBUKKIT_INTENDED_MODEL_GEN7.md`), and agentmemory's full service with graph/LLM lanes have never executed (`CODEX_HANDOFF.md` priorities 2–5 remain a to-do list).
3. **No cross-engine product ranking and no winner.** The repository says so itself (`STATUS_AND_FINDINGS.md:44`: "it does not yet have a fair final product winner"), and the board should not let any summary imply otherwise.
4. **MemConflict: pinned at Gen36, never run.** 182MB of upstream data, correctly not committed, never fetched; three generations built its contract and none executed it (`research/PHASE2_CANDIDATE_INTAKE.md` item 2).
5. **No long-context null arm.** Every comparison is memory-system vs memory-system or vs BM25; "does retrieval need to happen at all" has never been asked (`research/PHASE2_CANDIDATE_INTAKE.md` item 1).
6. **No external validation of anything.** No publication, no third-party run, no independent reproduction. The only independent checks are the in-repo AI rival reviews.
7. **Tiny, synthetic substrate.** All headline retrieval numbers live on 26 queries over 50 synthetic records with 450 generated distractors. A Hit@5 gap of 0.792 vs 0.583 is ~5 queries. The reader experiment is n=14 cases. No claim here generalizes to production scale, and the repository mostly says so.

---

## 4. WHERE THE EFFORT WENT

From git timestamps (382 commits, 2026-08-30 → 2026-09-07):

| Window | Commits | Generations | What it produced |
|---|---:|---|---|
| 08-30 → 09-01 | 60 | Gen1–26 | Round 1: baselines, Habitus, MemBukkit, Mem0, Hindsight raw, agentmemory raw+reader, Graphiti start |
| 09-02 → 09-03 | 22 | Gen27–42 | Round 2 longitudinal, Perseus, MemConflict contract (not run), Round-1/2 readouts |
| 09-04 | 38 | Gen43–59 | The "pi" agent-control experiments (state, quiescence, evidence ruler) |
| 09-05 | **161** | Gen60–114 | Current-truth work, Rounds 2–3, interference, supersession, Gen114 run+retraction |
| 09-06 | 71 | Gen115–123 | Reader ruler v5/v6, ten review rounds at Gen120, Gen122/123 runs |
| 09-07 | 30 | Gen124–125 | Ordering pilot (9 review rounds), roadmap recovery, lane separation |

Three concentrations stand out:

- **The reader line consumed the back half.** Commits naming Gen109–125 number ~101 of 382 (26%), spanning 2026-09-05 20:36 to 09-07 09:17 — and produced zero confirmatory evidence. Within that, Gen118 alone went through 19 sealed freeze attempts, each superseded for a stated apparatus reason (`results/gen118/CANONICAL_ATTEMPT.md`).
- **Review is the largest single activity by artifact count.** `reviews/LEDGER.md` tracks 166 findings; 133 FIXED, 24 CARRIED. Attribution: **~140 were found by the external AI reviewers** (glm-5.3: 88 solo + 15 joint; glm-5.3-flash: 24; Sol: 11; Fable: 7), ~11 by the implementer unprompted. Nine review rounds occurred inside Gen120 and again inside Gen124. Roughly nine of ten material defects were caught by the rivals, not the author — which is both the project's crown jewel and a measure of how much of the effort went into checking rather than measuring.
- **Control-plane and evidence machinery, not engines.** Doorbell scripts, PENDING.json pins, freeze runners, immutable-evidence contracts, known-failures guards, executable-doc-number tests — an entire governance layer (ledger rows #26–#91, #145–#165 are mostly about the machinery itself). `src/` is 19.5k lines and `tests/` 15k lines; much of the test growth after Gen109 polices the apparatus rather than the benchmark.

The project's own reconciliation is accurate on this point: a Phase-2 roadmap agreed 2026-09-02 was lost the same day to an orphaned chat branch, and the project "then ran roughly ninety generations doing the one thing its own step 7 forbids — exhausting the original contestant list" (`research/PHASE2_ROADMAP_RECONCILIATION.md`; the recovered roadmap header agrees).

---

## 5. THE FAILURE MODES, RANKED BY COST

1. **Hand-built rulers instead of measurements — process + implementer.** Six ruler defects across v1–v6, each discovered only by running or by review; 41 sealed attempts; five runs, all unpublished. The root cause is structural: one implementer writing its own fixtures, validators and graders, then validating them against the same runs they grade. The cure finally adopted — stop hand-writing cores, use LongMemEval (Gen124) — took seventeen generations to reach. **Cost: ~26% of all commits, three of eight days, zero confirmatory output.** This is the project's biggest single loss and it was avoidable by an earlier "use an external dataset" decision.
2. **Claims exceeding their mechanism — implementer, chronic.** The ledger names this class seven times over non-reproducible numbers alone (#47, #69, #74, #115, #141, #147, #151); the stale "97 passed" gate was reported five times before deletion (#13, #27, #41, #46, #54, #76); Gen124's "n=30, 14 vs 0" headline was "producible by no committed rule" (#151); "nobody measures ordering" was false (#119). **I found two live instances during this audit**: (a) the "~32.9% of the bank opened" figure repeated in `STATUS_AND_FINDINGS.md:58,90,147`, `RESULTS.md:75`, and `research/ROUND1_FINAL_READOUT.md:14` traces to no committed measurement — the configured budget is 0.3 (`src/memory_bakeoff/providers/external.py:237`) and the only measured artifact is a *median 32.0%* on a different corpus (`research/MEMBUKKIT_MEMCONFLICT_GEN42_CALIBRATION.md:109-110`); (b) `RESULTS.md:75` cites `results/membukkit_stress_lsa` for the 0.583/0.542 claim, but that directory holds 0.458/0.375 (the reranker-on diagnostic); the real backing is `results/current_stress4505/` and `results/membukkit_none_0.3/`. **Cost: recurring credibility risk; currently two defects standing in the maintained evidence index.**
3. **Strategy blackout via lost plan — tooling/process.** The roadmap lived in a chat branch, not the repo; its loss sent ~90 generations down a path it explicitly forbade, deferred the field refresh, and left MemConflict pinned-but-unrun until it was rediscovered *from outside* at Gen124. **Cost: roughly three days of misdirected generations and the entire Phase-B gap.** The fix (durable roadmap in-repo, `research/PHASE2_ROADMAP.md` now committed) is in place.
4. **Evidence destroyed before the contract existed — tooling.** Gen105 re-ran corrected arms into the original directory while `results/` was untracked; the pre-correction Gen102 cell-level artifacts are irrecoverable, and **no Round-3 conclusion is manifest-verified** (`results/gen107/attempt1/round3_closure.json`: MANIFEST_VERIFIED 0, COMMITTED_REPORT 6, LEGACY_UNMANIFESTED 3). Nine evidence directories once existed only on one laptop (LEDGER #31). **Cost: Round 3's provenance ceiling, permanent.** The `immutable-evidence-v1` contract now prevents recurrence — post hoc.
5. **Autonomous-loop machinery defects — tooling.** The overnight loop that motivated the rivals; a rival adjudication from an empty output file while the reviewer still ran (#88); doorbell crashes that silently failed delivery (#90, #164); convergence checks that could never succeed (#165); a resume guard that could never fire (#95). **Cost: hard to bound, but the ledger's self-found rows are dominated by it, and it consumed engineering that would otherwise have run engines.**
6. **Repair-after-exposure forcing exploratory-forever — implementer, caught each time.** Gen114 (ruler scored guesses), Gen122 (prompt/matcher), Gen124 (scorer and eligibility repaired mid-review). The saving grace is that the project detects and labels these itself; the cost is that its most interesting human-facing result (reader order sensitivity) can never be promoted.

One pattern worth naming for the board: the implementer's self-assessments repeatedly overstated repairs (#99 falsely marked FIXED, #138 falsely marked FIXED, #151 "my FIXED overstated the repair") — but the review apparatus caught every one. The honesty of this repository lives in its rivals, not its author. That is a design that works, at a price.

---

## 6. WHAT I WOULD RECOMMEND TO THE BOARD

**Option A — Refocus on the primary lane (my recommendation).** Accept the Gen125 ruling as written and fund, in order: (1) the **long-context null arm** — cheapest test in the repository, uses the existing harness, and every comparative claim made so far is unanchored without it (`research/PHASE2_CANDIDATE_INTAKE.md` item 1); (2) **run MemConflict** — pinned since Gen36, 182MB fetch, directly tests the system-selection question with real user updates; (3) the **intended-model product runs on a networked host** per `CODEX_HANDOFF.md` priorities 1–5. Freeze the reader lane at its preregistered 14-item holdout and require an authorization the implementer cannot give itself (the repo has already built exactly that mechanism). *Rough cost: the null arm is days; MemConflict and the product runs need one networked host and 1–2 weeks of agent time.*

**Option B — Publish the methodology, stop the bake-off.** The durable, novel outputs are process artifacts: the false-supersession metric (retrieval must not be rewarded for deleting the corpus), prohibited-presence vs prohibited-fraction, the evidence-lane separation, the retraction discipline. These would be valuable to others building memory benchmarks and do not require finishing the bake-off. *Cost: a writing effort, no new runs.*

**Option C — Stop entirely.** Defensible if the board wanted a product recommendation on a schedule: the project cannot currently support "use engine X," and its titular question is unanswered after 125 generations. But I do **not** recommend stopping, because the two most decision-relevant facts it has produced — that a production memory system silently deletes 92.9% of distinct facts under a default lifecycle rule, and that every tested engine co-returns stale records 192/192 — are real, verified, and worth finishing.

**Whichever option: three cheap repairs first.** Fix the `RESULTS.md:75` pointer; replace "~32.9%" with the measured number or mark it unverifiable; reconcile the stale passed-count conventions between `AGENTS.md` and `tests/KNOWN_FAILURES.json` (my run: 1557 passed, failures identical to the pinned clusters). An afternoon's work, and it removes the two live defects I found plus the figure drift.

**Bottom line.** The evidence that exists is trustworthy — I recomputed it and it holds. The evidence that matters most to the project's stated purpose does not exist yet, and the repository, unusually, says so itself. That combination is a project worth one more focused phase, not a verdict of failure — provided the next phase spends its runs on the primary question instead of on the ruler.
