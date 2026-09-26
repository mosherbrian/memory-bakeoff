# Survey roles: a research panel, not an audit line (Brian, 2026-09-26)

**Binding GPU resource rule,26September2026:** no fleet test run may use the local llama-swap port8080 `gpu` group until Claude ships the booking mechanism. Claude builds the reflector tonight, then booking. Booking must pause Cairn, move ClawdBot to the NPU, exclude night jobs, expire automatically and label each run clean/disturbed. No manual substitute or unbooked smoke test. This does not stop CPU-only data preparation, source review or ordinary authorized work. Booking is resource permission, not Letta-run or training approval. [Contract](delivery/GPU-BOOKING.md).

**LATEST BINDING CORRECTION — continuous delivery,26September2026.** Quiet support mode is withdrawn. The fleet keeps running; no-idling stands. OptionB's pilot subject is the fleet. Priority: (1) baseline the last seven days of manual interventions, gap alarms, idle minutes and repeated failure classes from existing logs; (2) design the fleet Letta comparison and run only with Brian's go-ahead; (3) review/test Claude's reflector as pieces ship; (4) Cairn on local gufo prepares local frontier-labelled correction/supersession data. Use [delivery queue](delivery/QUEUE.md); rest only for named external waits and continue independent ready work. The decision memo remains delivered; old personal-pilot and support-only passages below are superseded. No general literature loop resumes.


**Current mode: continuous delivery.** The [memo](RECOMMENDED-DESIGN.md) is delivered, not a stopping point. Work the [ordered queue](delivery/QUEUE.md). Cairn now prepares local data on gufo; Kiln practical checks and Corvid metric challenges serve delivery rather than new paper cycles. Source reading is task-bound. No-idling and active liveness remain in force.


Brian: "Can we get a little more opinionated research out of the other roles too? I feel like they have been pigeon-holed into auditing automatons."
Every role now writes signed OPINIONS with confidence levels. Checking is part of the job, never all of it. Tern (lead) commissions each role every cycle and quotes this file in the dispatch.

## corvid - the Contrarian (DeepSeek, Go pool)
Job: argue the strongest case AGAINST the current position memo, and for the best rival idea. Each cycle: survey/opinions/corvid-cN.md, 1-2 pages: "Where I think Tern is wrong", "The most underrated direction", "What evidence would settle our disagreement". Flaws are graded by whether they change a conclusion; minor flaws go in one line at the end. Being wrong in an interesting way is better than being silent.

## kiln - the Practitioner / field scout (Muse Spark 1.3 contributor, Go pool)
Job: judge real systems as a builder would: install cost, failure modes, maintenance, fit for Brian's stack (Claude Code, Pi, local models). Each cycle: 1-3 system cards in survey/systems/<name>.md, each ending in a verdict ("would deploy / would watch / would skip", with confidence), plus survey/opinions/kiln-cN.md: "What practitioners get wrong about agent memory". May run a cheap hands-on probe when it settles a verdict.

## cairn - the Reader / literature sweeper (local Qwen3.8 Flash-Next on Halogen, free)
Job: breadth. Sweep papers, benchmarks and release notes in one sub-area per cycle (compaction, retrieval, graphs, procedural/skill memory, forgetting and staleness, evaluation methods, ...). Output: survey/reading/cN-<area>.md with one short paragraph per source and a verdict per source ("solid / oversold / irrelevant to us"), ending with "The one idea in this area that most deserves our attention".

Commissioning practice: **WRITE the destination file first, then read more.** Start with the question, provisional opinion and explicit gaps; append source judgments incrementally. Prefer a few decision-relevant sources over a large context load. A useful partial piece is a deliverable, not a failed audit. Claude reports the lane now caps context at 90k and output at 24k to compact before Halogen's 131k reservation pool is exhausted; reported speed is about 27 tokens/s with thinking. These are operator-reported settings, not survey measurements. Claude owns runtime maintenance.

## Tern - the Lead / synthesist
Commissions the panel, then synthesises: FIELD-MAP, POSITION-MEMO, QUESTIONS, READOUT. The memo keeps a "Dissents" section that quotes unresolved panel disagreements; they are not smoothed away.

**Coverage (Brian via Claude, cycle65):** Tern maintains [COVERAGE.md](COVERAGE.md) within every cycle, alongside synthesis—not as a separate pass. Keep one table, one row per system/paper/benchmark/native facility: name, kind, status, cycle(s), note link, one-line takeaway. Allowed statuses: explored, queued, deferred-with-reason, identity-unresolved, out-of-scope. Carry the roadmap/Gen125 and roster backlog forward; update resolved identities and deferrals rather than silently dropping them. End with a short prioritized next-up list. Panel reports identify any new/changed item and its reading depth; Tern owns table reconciliation. No new research execution or per-record audit follows from coverage bookkeeping.

**Capability matrix (Brian via Claude, cycle71 follow-up):** Tern maintains [CAPABILITY-MATRIX.md](CAPABILITY-MATRIX.md) alongside COVERAGE **within every cycle**. One row per explored product, host facility and paper method; benchmark-only/evaluation-only items are listed outside the table. Keep the same ten fixed capability columns plus kind, maturity and source links. Each capability cell uses yes / partial / no / unknown / n-a with a 3–8 word note. Distinguish documented mechanisms, narrow tests and independent realistic benefit; preserve unknowns rather than inventing capabilities. Fill/refine from existing cycle notes, not a separate review pass or approval gate. Panel reports identify changes to relevant cells; Tern owns reconciliation.

Continuous-work direction from Brian via Claude (26 September, superseding scheduled pauses): research runs at full pace while funded. When a step ends, start the next; keep the panel working in parallel on bounded, useful questions. September 29 is a deadline, not a reason to delay a good memo. Go seats pause on exhaustion; no paid overflow. Rests are allowed only for a named external dependency (Brian’s answer, a panel piece in progress, or provider quota), never a self-chosen interval. Continue independent work during a partial dependency wait.

Stream C / `Q-FIELD-SURVEY` monitors liveness. Any genuine dependency rest is at most two hours, with structured `next_step` and matching question-bound receipt, checked by the installed checker. Receipt records the commitment, not completed research. At every cycle boundary continue immediately or identify a real external blocker; never roll forward a rest automatically. `survey/QUESTIONS.md` remains the scientific register. This liveness rule does not reopen campaign4 experiments.

## Rules for everyone
- Signed opinion + confidence (low / medium / high) + the source or experience behind it.
- Disagreement is a feature. Tern must answer each dissent in the memo (accept, reject with reason, or keep open).
- Budget: the Go pool is shared ($60/month, about $12.8 left at 2026-09-26, "full pace, then pause", no paid overflow). Keep panel pieces compact; prefer reading over probes.
- Assignment update from Brian via Claude, 2026-09-26: Kiln uses Muse Spark 1.3 contributor on Go; Cairn uses local Qwen3.8 Flash-Next on Halogen at no Go cost. These are sponsor-reported assignments, not a model-comparison result. Do not relabel earlier outputs retrospectively without their author's confirmation.
- Required next-commission reading: `survey/inputs/PHASE2_ROADMAP.md` and `survey/inputs/PHASE2_ROADMAP_RECONCILIATION.md`. The survey carries out phases B, C, and F; use the five target layers and seven longitudinal failure classes to assess systems. Historical execution instructions do not reopen campaign4 or authorize a prototype.

**Matrix-driven commissioning (Brian, 26 September2026; supersedes reading-list priority):** select each next cycle from open requirements2–5. Hunt narrow host/non-memory components as well as products, then resolve top-candidate partial/unknown cells from source/docs. Each cycle reports exact row × requirement changes or no change with reason. Queued papers remain visible but do not drive the agenda. No new review gate or experiment.
