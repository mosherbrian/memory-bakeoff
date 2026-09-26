# Brian's guiding principles and priorities (2026-09-26)

## Priority answer to QUESTIONS Q1 (what costs Brian most)
1. **Re-learning procedures.**
2. **Repeating preferences.**
(Not ranked as top: lost task state, missing evidence.)

## The five-part principle (agreed with ChatGPT during the Phase 2 roadmap work)
> **State tells the agent what to do now. Memory tells it what it has learned. History lets it reconstruct what happened. Artifacts establish what is true. Executive reasoning decides what it means.**

## The corollary (from the SKILL.state discussion)
> **Don't delete the past just because you stop putting it in every prompt.**

Context (reconstructed by Claude): SKILL.state (2026) shrinks long agent runs about 16x by replacing conversation history with a structured state object and discarding intermediate reasoning. Its own stated failure modes are unknown schemas, *delayed relevance* (something dropped early is needed later and cannot be recovered) and trajectory-dependent tasks. The corollary separates two decisions that such designs merge: what goes in the prompt (keep it small) and what is kept (keep everything, recoverable). Exclusion from the working view must never mean deletion from history. This is roadmap layer 1 (lossless history) under layer 4 (bounded working view).

## What each term meant when it was written (Brian, 2026-09-26)
An initial outline of candidate kinds, not settled components:
- **State** = something structured, like SKILL.state (current task/procedure state as a schema, not prose).
- **Memory** = a smart memory system like Perseus that handles supersession, conflicts, lifecycle ("what it has learned").
- **History** = pi-lcm's lossless context database, or a full transcript history, or both.
- **Artifacts** = the actual files, configs, logs, outputs: ground truth.
- **Executive reasoning** = the model/agent that interprets all of the above.
Treat the named systems as examples of each role to be re-evaluated in the roster refresh, not as choices already made.

## High-priority sponsor correction: dependable improvement over existing upkeep

**26 September2026, Brian via Claude; supersedes any survey framing of agent-owned upkeep as a new benefit.**

> “It almost sounds like you're just telling me to keep my own notes in a file.”
>
> “Agents aren't paragons of reliability. Claude already is supposed to do the noticing and writing down. What improvements are being suggested?”

**Baseline:** agent-owned noticing, capture and revision are already the status quo, and already fail. Recommending better notes or assigning the same diligence to the acting agent is not an improvement. Brian is not to become the librarian or verifier.

**Observed-stack report supplied by Brian/Claude, not independently audited by this survey:** capture mostly works (~150 Claude memory files); delivery fails because the MEMORY.md index is truncated, with109 of301 entries never loading; application is reported as the largest failure—feedback memories often exist because the agent repeated the mistake after saving the lesson. These counts refer to different units (files versus index entries); do not merge them into a capture or failure rate. The CLIN stored-but-not-selected pattern is an analogy, not validation of Brian's incidence or causal localization.

**Claude's proposed improvements for the panel to challenge, refine or replace:**

1. Enforcement over reminders: encode checkable preferences in a hook, tool or default (examples supplied: `python` rather than `python3`, no `127.0.0.1`, no `rm -rf`, kill by PID); keep judgment in memory. Determine actual scope and the execution path covered; a written instruction or an optional helper is not enforcement.
2. Capture from transcripts, independent of the acting agent noticing: a nightly job mines corrections and repeated problems. Cheap typed classification is a candidate mechanism, not established fitness. The cycle67 Laya supersession failure neither validates this different task nor rules out all classifiers.
3. Relevance-triggered delivery plus a mechanical guarantee that the index stays within the host's actual load limit. Storage, selection, delivery and application are different stages; preventing truncation alone does not guarantee compliance.
4. An automatic weekly count of re-explanations/repeated preferences in transcripts as the proposed outcome measure. Distinguish repeated corrections from quoted examples, legitimate scope changes and new instructions; silence is not success. No new rating or labeling duty for Brian.

**Survey question now:** which improvements do not depend on the acting agent's diligence, and what does the field offer for each? Every proposed improvement must name the independent trigger or enforcement point, the failed operation it changes, the diligence it removes, the residual judgment, and the relevant evidence. A scheduled model remains fallible; moving judgment off the actor removes a noticing/trigger dependency, not semantic error.

These are sponsor priorities and candidate directions for research. This message does not itself install hooks, schedule jobs, alter command policy or authorize a new experiment. The previously authorized single Laya probe is complete.


**Additional sponsor constraint, same entry — one characterizable operational design (26 September2026, Brian via Claude).** Brian is wary of an ad-hoc system that accretes scripts, files and patch layers until its behavior cannot be characterized, as happened with fleet loop v1. **Recommend nothing to build until it is describable as ONE design with named components, a stated contract for each, an owner, and tests.**

Prefer an existing product or an existing mechanism extended in one place—for example Claude Code hooks configuration, a cc-safety-net rulebook, or Pi extensions—over new standalone scripts and loosely connected jobs. This is a preference for a coherent, characterizable system, not a requirement that everything be one process or a claim that a product is automatically coherent.

Compare adopting **ReMe, Hindsight, Pi reflection or claude-mem** with composing parts partly on this basis: named boundaries, clear ownership, testable behavior, integration and upgrade burden, and the amount of custom glue. Identify what actually enforces or triggers each operation, where judgment remains, and how failures are visible. An upstream maintainer does not by itself own Brian's deployment; name the operational owner in a concrete recommendation rather than assigning the work back to Brian by implication.

The four proposed improvements above are responsibilities to investigate, **not four separate scripts to build**. Until a candidate satisfies this design constraint, label it a research option or an incomplete design and withhold the build recommendation. No installation or production change is authorized by this constraint.


**Sponsor clarification — avoid audit-mode analysis paralysis (26 September2026).** Brian: “as long as we don't slip back into audit-mode analysis-paralysis.” This supersedes any interpretation above that unknowns require serial reviews or prevent an opinionated recommendation. The design constraint governs the **shape of the final recommendation**, not a new review gate on each research or design step.

**Deliver by29September2026:** ONE one-page recommended design for Brian's stack, naming components, each contract, operational owner and how to test it; one named first pilot Brian can approve; and Tern's confidence. Make a choice. List open questions explicitly rather than treating them as blockers. Prefer an existing coherent product/mechanism where warranted, but do not wait for exhaustive source audits of every alternative. Proposed tests can be part of the pilot; they need not all have run before recommending it. Pilot approval is distinct from recommendation writing.

**Small-probe rule:** one memory decision, roughly50–100labeled items, majority and keyword baselines, one run, one result. No scorer framework or multi-round panel review. The already-completed Laya run used46pre-existing labeled cases and both baselines; retain that result without rerunning to reach50, changing thresholds, or generalizing the one-off scorer. No additional experiment is requested here. Note a caveat and move on unless it would change the recommendation.


**Sponsor Letta option, 26 September2026 (during cycle71).** Brian shared a dated, vendor-authored maintainer discussion ([r/AI_Agents 1glzob6](https://www.reddit.com/r/AI_Agents/comments/1glzob6/), November2024). Supplied claims: Letta owns the context/tools rather than adding its full memory loop to another framework; a separate sleep-time agent writes shared memory, with dreaming for reorganization; core versus archival/recall tiers. Treat these as historical input, not verified current implementation or measured benefit. Brian requests current Letta Code documentation and an **optional one-project, one-week Letta Code pilot on the September29 page, not the default**. He is not ready to change runtimes but might. This authorizes research and pilot design, not installation or starting the week. The action-changing candidate is upkeep triggered independently of the acting agent. [Current-source reconciliation](../systems/letta-sleep-time-current.md) qualifies exclusive background writes, modern MemFS tiers, and MCP interoperability.


**Sponsor MemFS source follow-up, 26 September2026.** Brian asks whether most desired machinery already exists in Letta Code MemFS, including independent reflection, commit validation/protected files, configurable budgets, automatic recall, compiled memory and Git synchronization; assess a synced read-only Claude Code/Pi view. Switch conditions: mobile web/cloud state, existing subscriptions (ChatGPT OAuth reported; Claude API only found), official ACP adapter. [Assessment](../systems/letta-memfs-fit.md) and [September29 page](../RECOMMENDED-DESIGN.md) now answer these. Treat runtime trial as optional; no switch/install authorized. Source-level constraints improve the candidate's standing but do not prove no truncation across hosts or fewer repeated mistakes.


**Sponsor observability request, 26 September2026:** add CAPABILITY-MATRIX.md as one sortable lookup table spanning every explored product, host facility and paper method, benchmark-only entries listed separately. Fixed ten capabilities: independent upkeep, enforced load/size limits, protected rules, preference delivery, procedural storage/relevant loading, searchable history, supersession/valid time, Brian-host fit, independent realistic benefit, coherent design. Add kind/maturity/link; each capability cell is yes/partial/no/unknown/n-a plus a 3–8 word note. MemFS is the model row. Seed in one pass from existing notes; update within every cycle alongside COVERAGE. This is visibility, not another review gate. [Matrix](../CAPABILITY-MATRIX.md).


**Binding research steering — matrix gaps first (26 September2026, Brian via Claude).** The dashboard's best-fit view finds no full yes for requirements 2 (nothing silently dropped), 3 (protected rules the agent cannot edit), 4 (preferences always delivered), or 5 (procedures loaded when relevant). These are the priority gaps behind Brian's pains. Choose subsequent cycles from these cells, not the reading backlog. First seek systems, host features or narrow components that fully cover a gap, including non-memory policy engines, context compilers, configuration protection, lint/budget checks and harness hooks. A narrow component covering one slot is valuable. Then resolve decision-relevant partial/unverified cells in top candidates through source/docs: cc-safety-net rulebook protection, Claude memory cap behavior, Letta budget enforcement are examples. State exact changed cells each cycle, including no change with reason. Keep honest scope and distinguish documented guarantees from installed behavior; do not lower the requirement to manufacture yes. Reading/source inspection only; no new review gate, deployment or probe.


**Sponsor Laya scope correction and option B,26September2026 (cycle80).** Claude reports the c67 run used the shipped base checkpoint zero-shot. Record the verdict as that configuration rejected for supersession, not Laya as a task-trainable method; the run did not log an exact checkpoint hash/temperature. The46/46 keyword fixture baseline remains preferred. Add to **option B = Pi/Claude Code + skills + Perseus Context Engine** an optional trained local reflector prefilter for corrections, repeated instructions and stated preferences. Proposed path: frontier-teacher labels on a few thousand messages, task fine-tuning and separate temperature fitting, comparison with a keyword rule and Jev on held-out independently hand-labeled messages, recall primary. Local inference avoids per-message transcript egress/vendor dependence; hosted labeling or hosted evaluation/training would not. This steering requests documentation/design, not dataset transmission, labeling calls, training, a second probe or deployment. [Candidate design](../systems/laya-correction-prefilter.md).


**Sponsor option-B cascade,26September2026 (cycle81).** Brian proposes: high-recall fine-tuned local Laya screening over new memory pairs and ongoing claude-mem candidates; daytime soft flags never hide; LLM relationship judgments (replaces/narrows/coexists/unrelated); independently scheduled nightly consolidation with source context/chain checks, replaces links, Context Engine host views and board counts. Preserve originals through Git+lineage. Target stage1 recall≈0.98+, stage2 precision, sampled nightly false-replace rate. Candidate training/evaluation sources: MemConflict, Supersede, Memora/FAMA, KnowledgeDrift, StateMemBench and frontier-labeled local memories. Supersede/FAMA remain distinct identities. Tern must challenge and fold into option B and requirements1/7, not treat this as execution authorization. [Contracts and challenge](../OPTION-B-CASCADE.md). Explicit qualification: `@budget strict` requires the separate analyzer to be integrated; no such publication gate has been built.


**Sponsor self-improvement extension,26 September2026 (cycle81).** Add stage2 verdicts, nightly outcomes and especially Brian's reverts/corrections as label sources for periodic Laya re-fine-tuning. Required: nightly random unflagged-pair samples to expose selection bias; frozen hand-labeled test never trained on, `laya.evals` promotion only with non-worse recall/calibration and old-model rollback; human corrections weighted above LLM labels; judge/reflector improve through retrieved worked examples, not fine-tuning. Tern evaluates against ExpeL, SkillRL, ACE and Dynamic Cheatsheet in [the design note](../OPTION-B-LEARNING-LOOP.md). Qualifications: sampled recall is weighted and judge-referenced unless independently labeled; test examples also excluded from retrieval; teacher errors are not an absolute student ceiling. Design authorization only, no training or extraction.


**Sponsor adversarial-review commission,26 September2026 (cycle84).** Brian approved sending [Brian/Claude's candidate design](DESIGN-OPTION-B-20260926.md) for challenge, not adoption. Claude is a co-author and not independent evidence. Corvid attacks the whole design, Kiln verifies practical host paths, Cairn checks source claims; Tern rates the whole candidate next to its recommendation and answers all open questions, including first failure and whether sponsor conversation has displaced useful research. Source/design only, no new gate or build authorization. Preserve the supplied sketch unchanged.


**Binding Letta constraint,26 September2026.** Brian is not inclined to switch runtimes. This supersedes the personal one-week proposal above: any Letta trial is **fleet-operated**, local backend only, no Letta Cloud or mobile requirement. Use official letta-ai/letta-acp if agent-deck can drive it; model access through ChatGPT OAuth or the existing Go pool, with stated cost. One small scripted multi-session experiment against native Pi/Claude files, adding optionB stage1 only if already ready. Measure repeat reminders, later correct applications, wrong lessons and total cost; pre-state pass/fail. Brian must approve before it runs. The [bounded proposal](../proposals/letta-fleet-pilot.md) is design work, not setup/execution authority; Brian gets no operating or per-turn labeling duty.


**Binding stage0 correction,26 September2026.** cc-safety-net is **not running on Brian's machine**. It is staged for a work pilot; Brian has not used it because it “seemed to be popping up too often.” Treat that interruption burden as sponsor-reported usability evidence, not a measured rate. The preference is “write python, never python3, in commands Brian runs,” because of his Windows machines. Claude legitimately executes python3 on Linux. “Never show 127.0.0.1” is also an output preference. Tern mapped the preference to the wrong enforcement point; the Bash-deny pilot is withdrawn. Revised stage0: native final-reply check with bounded correction, measuring false interventions and delay; native permission deny rules separately cover destructive actions such as rm -rf and kill by pattern. No extra product needed for that initial action scope. Stop is post-response correction, not guaranteed pre-display suppression. [Revised pilot](../proposals/final-reply-preference-pilot.md). Design revision only; no configuration or execution authorized here.


**Stage0 completion,26 September2026 — Brian approved.** Claude reports the native repair complete: MEMORY.md123 lines/about17.7KB, rules/preferences/recent entries retained, other entries moved to reachable MEM-*.md indexes. Existing `~/.claude/hooks/laya-stop-gate.py` mechanically checks code-only output (python3 commands for Brian; loopback addresses), blocks and asks for rewrite; prose discussing rules passes. Ten sample replies tested. Same hook blocks MEMORY.md above190 lines or24KB. Native permissions.deny and guard-selfkill cover rm -rf spellings and kill by pattern, without asking Brian. No new product. This supersedes the pending prompt-checker proposal; the outcome to watch is **repeat corrections from Brian**. Reported deployed controls are not yet measured longitudinal benefit. No additional pilot approval or recurring Brian review requested. [Record](../systems/claude-stage0-deployed.md).


**Binding delivery/support direction,26 September2026.** Brian says29September and14October are ceilings and too slow after84+ cycles. Deliver the one-page decision now, within two cycles: choose staged optionB or a smaller rival, name the first build, two-week evidence and stop conditions. Kiln host-path review is open if absent, not blocking. [Decision delivered](../RECOMMENDED-DESIGN.md). Claude builds the reflector today; daily digest to Brian starts tomorrow morning, Monday repeat scoreboard. After delivery, survey is support-only: no new reading except a named delivery blocker; review build/scoreboard when asked. Charter deadline moves to today; October14 replaced by measured pilot evidence. No new recurring review gate.


**Binding correction — fleet keeps running,26September2026.** Brian withdraws quiet support mode: no-idling stands. OptionB pilot subject is the fleet; Brian's corrections during this effort are a poor outcome measure. Baseline the last seven days now: manual Claude/Brian recovery interventions, gap alarms, idle minutes and repeated failure classes. Then design/run the fleet Letta comparison with Brian's go-ahead; review/test Claude's reflector as pieces ship; Cairn on local gufo prepares frontier-labelled correction/supersession pairs locally. Keep a structured delivery queue; rests only name actual external waits. No blanket authorization for Letta execution or hosted transcript egress. [Queue](../delivery/QUEUE.md), [baseline](../delivery/FLEET-BASELINE.md).

**Implementation of continuous-delivery correction:** Q-FIELD-SURVEY reactivated; the earlier retirement was an error under Brian's corrected direction. Existing-log baseline is written, Letta protocol now uses fleet handoff/queue lessons, and Cairn local data preparation is executing. Named dependencies do not suspend independent ready work. The private raw candidate directory was moved outside the repository; no transcript egress or training occurred.


**Binding GPU resource rule,26September2026:** no fleet test run may use the local llama-swap port8080 `gpu` group until Claude ships the booking mechanism. Claude builds the reflector tonight, then booking. Booking must pause Cairn, move ClawdBot to the NPU, exclude night jobs, expire automatically and label each run clean/disturbed. No manual substitute or unbooked smoke test. This does not stop CPU-only data preparation, source review or ordinary authorized work. Booking is resource permission, not Letta-run or training approval. [Execution dependency](../delivery/GPU-BOOKING.md).

##26September — reflector shipped; labeling endpoint wait resolved

Claude supplied the one-file nightly reflector for immediate source/CPU test review. Cairn is authorized to label D4 candidates with already-loaded gufo as normal worker use, not a GPU test. Tern or Corvid independently spot-checks a random10% and records agreement; teacher agreement is not gold truth. No new endpoint or hosted teacher call required. Letta remains prepare-only until Brian gives explicit go-ahead; GPU booking precedes any local-GPU test, not this CPU work or authorized labeling.

##26September ~21:15Z — Letta fleet trial approved

Brian approved one fleet-run comparison, isolated prefix, local Letta backend only, hosted ChatGPT OAuth or Go with stated cap and balance check. No local GPU before booking. Tern selected existing ChatGPT OAuth ($0 additional spend); Go excluded because remaining allowance was not verified. Run the written matched protocol, pin versions/hashes, publish on the board and to Claude, and stop on a real protocol/resource blocker rather than inventing a follow-on campaign.
