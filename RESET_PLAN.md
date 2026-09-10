**Memory bake-off: executable reset plan**

> **Installed 2026-09-09 as the active reset instruction** on branch
> `reset/practical-pi-20260907`. This copy is the plan as prepared on
> 2026-09-07, unchanged below this block.
>
> **Reconciled base.** The plan was prepared against reviewed commit
> `5d1d6a0159d32f19c58cabee15013ec691bd596a`. Main had advanced by four
> commits when the replacement implementer began; all four were inspected and
> are documentation or built-but-never-run code, so the reset branches from the
> actual main tip, not the older reviewed commit:
>
> - `af88fde` — DECISION_MEMO.md, terminal deliverable with a budget
> - `f01cacf` — `src/memory_bakeoff/longcontext_null.py` + tests — built, never run
> - `00e09a2` — `src/memory_bakeoff/stale_use_penalty.py` + tests — built, never applied
> - `9dfea2c` — materialised `external/MemConflict` and verified it against the Gen36 pin
>
> **Reset branch base:** `9dfea2c3629bd9439554084c19ddffcaaf11d7c8`
> (local ref `baseline/pre-reset-9dfea2c`). No reset branch existed on the
> remote; this branch was created fresh. Current status and decisions live in
> **[RESET_STATUS.md](RESET_STATUS.md)**.

Prepared for Brian Mosher, 7 September 2026. Implementation defaults for the direction Brian accepted in the review-board conversation.

**Outcome:** restore a project Brian can understand and steer, then decide whether one concrete addition improves his existing Pi/Pi-LCM workflow enough to justify a personal trial. A useful outcome may be to retain Pi-LCM alone. This reset does not require a universal product winner, a complete composite architecture, or a publication.

**Start here.** Give this entire file to a fresh replacement implementer in the existing development environment. Its first assignment is R0–R1 below. It must deliver a useful recommendation before running another experiment. Brian makes one pilot-scope decision at that boundary; ordinary implementation and repairs within the selected scope do not require repeated permission.

**Verified starting state**

| Item | State established while preparing this plan |
|---|---|
| Repository | mosherbrian/memory-bakeoff |
| Inspected main commit | 5d1d6a0159d32f19c58cabee15013ec691bd596a |
| Last numbered handoff | Gen125 |
| PENDING.json at that commit | status answered; requested_generation 125; source_generation 124 |
| Old scheduled instruction writers | All five ChatGPT checks at :00, :12, :24, :36 and :48 were successfully paused on 7 September 2026, approximately 19:09 UTC, while this plan was prepared. |
| Host processes and launchers | Not inspected or stopped from this conversation. R0 must establish their state locally. Pausing scheduled checks does not stop an already-running process. |
| Repository implementation | This plan has not been installed in the repository. No host changes or new experiments were performed while preparing it. |

The latest commit corrected the MemConflict inventory in the intake and roadmap reconciliation. The scan-fraction claim has also been retracted. However, the top Gen125 handoff still says MemConflict never ran and calls existing comparisons unanchored; AGENTS.md still contains an obsolete next-work list and inconsistent descriptions of known test failures. Repair the remaining active entry points, not already-corrected copies.

**1. Ownership and authority**

| Role | Default assignment | Responsibility |
|---|---|---|
| Sponsor | Brian | Approve the practical objective, pilot choice and resource trade-offs; decide whether to adopt or continue. His explicit direction outranks project-generated workflow rules. |
| Implementer | Fresh session using a different available implementation model; use Brian's existing Codex setup as the default starting option if quota permits | Own one bounded task, its code, verification, reporting and resource accounting. Record the actual model and harness. This is a trial of the complete setup, not a claim that a model brand is better. |
| Reviewer | GLM-5.3 provisionally, in one separate session | Check the task's decisions, relevant implementation and supporting artifacts; issue one consolidated review and a targeted recheck. It does not write the implementation or select the next project direction. |
| Advisor | ChatGPT in this review-board conversation | Interpret the R1 recommendation and final pilot result when Brian brings them here. No polling, per-commit approvals, or automatic next-generation authoring. |
| Previous implementer | Available only for a bounded factual handover if needed | Identify host locations, running jobs or existing artifacts. No further self-directed repairs or research queue. |

Use one implementer and one reviewer. Reuse the existing GLM connection settings for a single reviewer session; inspect the local wrapper's configuration if needed, but do not invent a single-model flag or execute a dual-review wrapper to discover one. GLM-5.3-Flash is the fallback if 5.3 is unavailable, with the substitution recorded. Do not invoke the fallback proposer or additional reviewers. If the selected replacement has no quota, use another already-available non-incumbent model in a fresh session and record the substitution before starting; do not launch a model tournament or buy access. Spend at most ten minutes establishing reviewer access before reporting that specific blocker.

Brian's authorization to run something and the scientific status of its result are separate. In particular, a documented human override must not be relabeled as implementer self-authorization. An exploratory result remains exploratory after an authorized run.

**2. Resource envelope and stopping rules**

These are spending ceilings for one reset attempt, not estimates or promises of completion. Review, repair and reporting are included.

| Stage | Aggregate agent-time ceiling | Deliverable |
|---|---:|---|
| R0: stop legacy execution and establish a safe working copy | 0.5 hour | Verified containment and baseline |
| R1: repair active project state and make the next decision concrete | 2.0 hours | Reviewed recommendation and exact pilot specification |
| R2: implement and run the selected small pilot | 4.5 hours | Working reversible integration, item-level results and rollback |
| R3: review the result and deliver a decision | 1.0 hour | Reviewed adopt / retain baseline / unresolved recommendation |
| Total | **8.0 hours** | One completed decision, or an explicit stopped attempt |

Aggregate agent time means elapsed working time for the implementer plus elapsed reviewer time, including tool execution and waits while those sessions are occupied. Count concurrent reviewer work separately. Use existing timestamps and usage receipts; do not build a metering system. Log unavailable token/cost figures as unavailable, not zero. Record machine occupancy separately, with a six-hour ceiling for experiment-related use of the home AI box. Routine use of that box outside this project is not part of the ceiling.

Brian's attention budget is 30 minutes total: up to 5 minutes to launch, 10 minutes for the R1 scope decision, and 15 minutes for the final decision. A request that needs him to debug the process counts against this budget too.

Stop and preserve the work when a stage ceiling is reached. Do not move unused later-stage time into an overrun without Brian changing the budget. If there is no result, report the specific blocker and the completed evidence; do not create a follow-on generation automatically.

For each reviewed deliverable: one initial review, one consolidated repair pass, one targeted recheck. A remaining material defect means narrow the claim or stop that deliverable. It does not mean accept defective work, add a second reviewer, or begin another repair loop. Cosmetic improvements can be carried. Repeated failure does not by itself prove whether the model or the shared setup caused it.

**3. R0 — contain the old loop and preserve the starting state**

Owner: replacement implementer, with a factual host handover from Brian or the previous implementer only if necessary.

1. Locate the actual checkout, host launchers and current inference clients. The inspected scripts reference /var/home/bmosher/pilot-gen45 on the Strix host and /Users/bmosher/source/repos/memory-bakeoff on the Mac. These are historical pointers, not proof of present process state.
2. On the Linux host, inspect the relevant user services/timers, cron entries and process ancestry. The repository names overnight-ordering and converge services; discover any associated after-converge launcher instead of assuming its service name. Stop the parent launchers and relevant experiment clients, and disable any automatic restart schedules for this project. Use exact discovered unit names/PIDs. Do not broadly kill python, Pi, model servers, or unrelated work.
3. Check for a running control-plane conversation or an instruction that arrived during shutdown. Treat any old generation instruction as historical until reconciled with this reset. Never let an old mailbox message start a run automatically.
4. Inspect git status before writing. Preserve uncommitted and untracked work separately; do not clean, reset, stash indiscriminately, or overwrite the incumbent's workspace. Use a separate worktree or clean checkout for the replacement.
5. Fetch main and record the exact actual base commit. The reviewed starting commit is 5d1d6a0159d32f19c58cabee15013ec691bd596a. If main has advanced, inspect that delta once and record which corrections it changes. Do not revert newer work to match this document.
6. Create a local reset branch and preserve a local baseline ref. Use a new branch name if reset/practical-pi-20260907 already exists; never overwrite an existing branch. Start the branch from the reconciled base, not an old experimental worktree.

Read-only Linux discovery examples; inspect results locally rather than copying raw process command lines into the public repository:

~~~bash
systemctl --user list-units --all --type=service --type=timer --no-pager | rg -i 'overnight-ordering|converge|memory-bakeoff|pilot-gen45|rivals'
systemctl --user list-unit-files --no-pager | rg -i 'overnight-ordering|converge|memory-bakeoff|pilot-gen45|rivals'
ps -eo pid,ppid,etime,args | rg 'scripts/(overnight|converge|after-converge|ring|doorbell|await-instruction)|rivals/(review-generation|propose-generation)'
~~~

Check cron or Mac launch agents only where the actual launch configuration calls for them. Do not turn containment into a general machine audit.

R0 passes when the relevant launchers are inactive, project experiment clients have stopped, local work is preserved, and the replacement has an isolated branch at an identified base. If host containment cannot be verified, R1 may continue read-only; no experiment or repository write should race an incumbent writer.

**4. R1 — make the project legible and deliver the next decision**

This stage is the replacement implementer's first useful delivery. No model/reader experiments, large dataset downloads, dependency upgrades, or benchmark reruns.

Read this plan, the actual AGENTS.md, the recovered PHASE2_ROADMAP.md, the current top handoff, RESULTS.md, and the relevant portions of the current intake. Follow links only to evidence needed for the recommendation. Do not require a full reread of the 4,688-line handoff or all review history.

**Repository changes, in this order:**

| Target | Exact change |
|---|---|
| control-plane/PENDING.json | Preserve the existing provenance fields; set status to paused and add the reset reason and timestamp. This truthfully records suspension; do not falsely mark a new instruction answered. The inspected scheduler stops on any status other than awaiting. This field is not a process kill switch. |
| RESET_PLAN.md | Install this plan as the active reset instruction. Record any reconciled base change. The recovered research roadmap remains historical architectural context. |
| RESET_STATUS.md | Create the single current status and decision page described below. It owns current next actions and resource use. |
| AGENTS.md | Put RESET_PLAN.md and RESET_STATUS.md first in the reading order. Replace the obsolete active queue with the current R1/R2 task. Keep the scientific invariants. Replace mandatory per-generation full-suite/reader-lineage work with the scoped verification policy below for this reset. Reconcile the contradictory known-failure description with KNOWN_FAILURES.json without inventing a fresh suite run. |
| CONTROL_PLANE.md and control-plane/PER_GENERATION_CHECKLIST.md | Add a short, prominent note that the automated generation workflow is suspended and the reset uses direct, bounded handoffs. Retain historical content. Do not invoke consume-instruction, await-instruction, decide, doorbell, ring, converge, after-converge, overnight, or fallback proposing to deliver reset work. |
| STATUS_AND_FINDINGS.md and CODEX_HANDOFF.md | Add a brief current-status pointer to RESET_STATUS.md so their older priorities cannot masquerade as the active queue. Do not rewrite the historical findings. |
| handoff/CODEX_TO_CHATGPT.md | Add a short reset entry linking the current status. Correct or explicitly supersede the active Gen125 claims that MemConflict never ran and existing comparisons are unanchored. Keep the original account recoverable. |
| RESULTS.md | Add a reset entry pointing to the decision page. Correct a remaining bad evidence pointer only if still present and relevant; do not repeat the already-completed scan-fraction retraction. |

The existing pre-commit hook checks outstanding PENDING status; it does not run the full suite, despite what the old checklist claims. If the actual checkout is awaiting an old request, commit only the truthful pause transition first through the existing hook, then make the reset edits. Do not use --no-verify or disable hooks to get around a gate. The reset changes its operating instructions openly; it does not weaken scientific validity checks.

**What RESET_STATUS.md must contain:**

- A plain-English recommendation of at most 600 words, with evidence links immediately supporting the load-bearing claims.
- The practical gap selected for investigation: targeted historical recall, current/scoped state handling, procedural reuse, or continuity within a bounded working context. Do not silently equate these with one another.
- A compact component map: what Pi-LCM already provides, what the candidate would add, what is still unmeasured, and why that addition could change a coding outcome.
- At most two candidate components considered and one recommended pilot. Prefer a locally runnable path already supported by existing code/evidence. A second candidate belongs in the comparison rationale, not automatically in the experiment.
- The exact implementation files/entry point, local dependencies, rollback action, task selection, validation commands, complete evaluated configuration, and resource limits for R2. Resolve actual host and model IDs during R1; do not leave them as guessed placeholders.
- Completed work, remaining uncertainty, next action, cumulative implementer/reviewer time, experiment-machine time, and Brian's attention used. Use one small table for these figures.

Reuse the original architectural purpose: Pi-LCM remains the lossless substrate; derived state, retrieval and working-context synthesis are different candidate additions. Do not return to the old contestant queue just because adapters exist. A research paper without a runnable path cannot consume this pilot's implementation budget. If no candidate is runnable and justified, recommend retaining the baseline and identify the one missing capability; stop before R2.

**Evidence anchors to verify selectively:**

- Gen38 MemConflict ran Perseus, Mem0 and BM25 on an exact-provenance retrieval lane. It was not an upstream LLM-judged or end-to-end coding result.
- Gen41 ran MemBukkit's intended model pair in a raw-product configuration. Its full distiller/LLM pipeline was not thereby tested.
- Agentmemory's false supersession and Claude-Mem's window ablation are configuration-scoped findings.
- Round 3's explicit-lineage result does not establish a universal product ranking, and its earlier provenance limitations remain.
- Gen124 is exploratory. The 14-item reader holdout remains deferred; R2 does not use it.
- A lost or stale project instruction is not automatically proof that a retrieval component would have prevented the failure.

**R1 review:** give GLM-5.3 the branch's implementation commit, scoped diff, this plan and the evidence supporting the recommendation. Ask it to check (a) whether the question serves Brian's workflow, (b) whether the evidence and inventory are accurately represented, (c) whether the named implementation can fit the R2 budget, and (d) whether the proposed validation could reveal failure. Each blocker needs a source or reproducer and its consequence for the decision. No broad repository audit or new research queue.

Record the review and recheck in reviews/reset-R1.md. Bind them to the reviewed implementation commit and files. Committing a review transcript does not invalidate the review of unchanged implementation files; do not recreate the review-newer-than-HEAD cycle.

Commit the sanitized changes and review record on the reset branch and push that branch through the existing Git remote so the advisor can inspect it. Return its branch URL and exact commit. Do not call the old delivery scripts or automatically merge to main. If publication is unavailable, deliver a patch plus the local commit and label the remote handoff incomplete. The reset branch is the working source for R2; main may retain its older instructions until the reviewed reset is merged through the normal repository process.

R1 passes with a truthful current page, operationally consistent entry points, one executable pilot specification or a justified stop recommendation, and no unresolved material review defect. Present the short recommendation to Brian for the single scope decision. Do not ring the old doorbell or poll for his answer. Stop consuming resources while awaiting that decision.

**5. R2 — implement one addition and test actual workflow value**

Begin only after Brian selects the concrete R1 pilot and its trade-offs. That approval covers routine implementation, scoped verification and the runs described here; do not request permission for each commit or test.

**Implementation boundary:** one reversible adapter, extension or configuration change that adds the selected capability to the existing Pi workflow. Identify the actual integration hook in R1. Keep one owner of context composition. Do not replace Pi-LCM, implement the full layered architecture, add a new autonomous controller, or turn the old state/control test fixture into an assumed production component. If the smallest valid integration does not fit, stop and explain the mismatch.

Use isolated test branches, memory stores and sessions. Keep the current daily configuration available for rollback. Verify the integration on one unrelated smoke task before exposing the evaluation cases: the feature is active when enabled, the original path works when disabled, and source references can be resolved. A critical new check must reject one representative bad input through the actual path it protects; no universal mutation-testing project is required.

**Comparison:**

| Arm | Definition |
|---|---|
| A | Brian's existing enhanced Pi-LCM setup, including its normal background compaction and caching/pre-warming behavior |
| B | The identical setup plus the single selected addition |

Hold the coding model, runtime, quantization, context budget, tools, source task snapshots and device configuration fixed. Record any model needed by the memory component as part of B and include its cost. Do not make B win by changing the coding model, starving A of its normal history, disabling A's optimizations, or giving B answer labels or privileged source material.

Use four representative coding-workflow cases selected in R1 from existing tasks or appropriately accessible saved sessions, two repetitions per case per arm: **16 evaluation runs maximum**. Default to existing public cases when cloud-backed agents are involved. Choose small cases with independently checkable outcomes that can plausibly fit the eight-minute limit, covering the selected gap. Suitable examples are resuming work after a session boundary, obeying a revised project-specific decision, avoiding a documented failed approach, or recovering why an earlier alternative was rejected. These are case-selection examples, not a mandate to invent four new synthetic benchmark families.

Select cases before observing treatment outcomes. At least two should present a real opportunity for the chosen memory capability to help. Use two preselected seeds where supported; otherwise record that seeds are unavailable. Alternate A/B then B/A across repetitions, restore the same initial snapshot, and isolate memory stores. No cross-run memory contamination. Record normal cache state and separate one-time preparation from steady operation; do not force repeated full-history prefill as the baseline's normal behavior.

Each run has an eight-minute execution ceiling, including its ordinary memory operations. The 16-run worst case is 128 minutes, leaving part of R2 for integration, verification and analysis. Do not launch a run if it cannot finish within the remaining stage/host budget. A timeout is a recorded timeout, not a reason for an unbudgeted retry. Preserve partial results from interruptions. Resuming an existing run may consume its remaining allowance; starting it over counts as another run.

Use existing project tests and concrete task artifacts as outcome checks. For memory behavior, retain the actual referenced source and trace showing the action taken. The model's claim that it remembered or succeeded is not a score. A genuinely ambiguous outcome stays ambiguous and limits the recommendation; do not create another general-purpose reader grader to force a verdict. Hidden acceptance material belongs outside agent-visible task snapshots and memory input.

**Minimum result columns:** task ID, arm, repetition, configuration reference, success/failure/ambiguous/timeout, stale or wrong-scope action, supporting receipt/source, human corrections, tool calls, available token/usage totals, preparation time and run time. Compute summaries from these rows. Report missing resource measurements explicitly. Keep task outcomes, harmful-memory behavior and resource cost separate.

Private transcripts, task content, outputs revealing private code and detailed evidence stay in a durable local directory outside the public repository, such as ~/.local/share/memory-bakeoff/reset-20260907/. Publish only a deliberately sanitized summary and non-sensitive code/configuration identifiers. Never upload the private corpus to GitHub, Drive or a reviewer service. Remote review can inspect integration code and sanitized results; private traces require local inspection or a redacted excerpt checked before sharing.

Local storage alone is insufficient: reading private text into a cloud model's tool output also sends it off the host. A private-corpus pilot therefore requires local model execution and local evidence inspection; a cloud-backed replacement or reviewer must not read those inputs or traces. If that path is not already available, use the public cases for this reset and leave private-corpus evaluation for a later decision. Do not spend this budget building a redaction or data-export system.

If a bug is discovered after evaluation exposure, preserve the runs, record the defect and stop new evaluation calls. The data may still support a narrow exploratory observation. Do not repair the rule, rescore until favorable, or automatically regenerate cases. The remaining decision may properly be unresolved.

**6. R3 — review the outcome and choose**

Owner: implementer for synthesis; the same reviewer for one result review and targeted recheck. Include this time in R3's one-hour ceiling. Store the review in reviews/reset-R3.md, tied to the reviewed code and result snapshot.

Review the complete four-case paired table, not only averages or favorable examples. Check configuration equivalence, actual feature activation, source/receipt accuracy, arithmetic, resource accounting and whether the recommendation exceeds the evidence. Existing benchmark results and this workflow pilot remain separate evidence classes.

Use these default decision rules, finalized with Brian at R1 before runs:

- **Recommend a limited personal trial:** B fixes at least one predeclared practical failure in both repetitions, adds no regression in the other checked cases, and introduces no stale-state, scope or provenance defect. It must fit the reset's absolute resource limits and the additional overhead Brian accepted at R1. If no other overhead limit is chosen there, use 25% for median run time and available token usage over paired successful runs; label unavailable or insufficient cost comparisons unresolved rather than passing them. This is a pragmatic trial threshold, not a statistical claim.
- **Retain baseline:** no repeatable practical gain appears, a meaningful regression occurs, or the added complexity/cost is not justified. Do not add contestants merely to avoid this outcome.
- **Unresolved:** integration, evaluator ambiguity, resource limits or mixed repeats prevent a supported decision. State the exact missing observation and preserve the work. Another attempt needs a new explicit budget and rationale.

Update RESET_STATUS.md with an executive result of at most 600 words, the paired table, limitations, cumulative costs, and the precise next action. Add a short index/handoff pointer; do not copy the same numerical account into multiple documents. Deliver the reviewed branch/commit and the concrete install/disable instructions appropriate to that implementation. If stopped, deliver what is complete and the rollback state.

A recommendation for personal use is not team rollout approval. Keep broader rollout, more benchmarks and publication as separate later decisions.

**7. Verification and reporting conventions for the reset**

- Preserve old sealed artifacts and the distinction among baseline, controlled-core, raw-product and product evidence. Do not relabel historical NON_EVIDENCE or repair historical artifacts in place.
- R0/R1 documentation-only changes need direct source/diff checks. Run existing focused tests only where a changed document or field is actually consumed by code. Do not rerun the whole historical suite to edit a status page.
- For R2 code, run the focused tests that cover the changed boundary and one relevant regression path. Before changing existing scoring/benchmark semantics, run the required baseline and stop to reconsider scope; this reset is designed to avoid such a change.
- Do not disable installed hooks or access controls. An unexpectedly enforced legacy workflow gate is a specific implementation issue to resolve transparently within the existing budget, not a reason to claim tests passed or bypass them.
- Match known failures by actual test identity and cause when relevant. Do not copy an old pass count and call it a current run. Do not rebuild tests for unrelated historical experiments.
- At stage boundaries and after each substantial unit of active work, provide at most 150 words covering: the practical question, what actually changed or ran, what the evidence supports, and the next action/decision. Put paths and detail behind links. State plainly when nothing useful has changed.
- No automated prose-compliance test, additional dashboard, new reporting schema service, hourly status bot, or documentation cleanup programme. The reviewer checks that Brian could make the stated decision from the report.

**8. Ready-to-use instruction for the replacement implementer**

Attach this file with the following message. It starts R0–R1; it does not launch the pilot.

~~~text
We are restarting memory-bakeoff under the attached reset plan. Brian has accepted
the direction: replace the autonomous lead session, use one reviewer, restore a
clear practical objective, and spend a bounded budget to reach a useful decision.

You are the replacement implementer. Execute R0 and R1 only. Your combined budget
for them is 2.5 aggregate agent-hours, including review and repairs. Keep raw
private material local. No experiment, reader call, holdout exposure, benchmark
rerun, dependency upgrade, or new orchestration framework in this assignment.

First verify that old host launchers cannot continue the previous generation
queue. Five scheduled ChatGPT instruction checks have already been paused; that
does not prove the local jobs are stopped. Preserve existing local changes and
work in an isolated branch. Reconcile current main with reviewed commit
5d1d6a0159d32f19c58cabee15013ec691bd596a; do not overwrite newer work.

Install RESET_PLAN.md and make RESET_STATUS.md the one current decision page.
Apply the limited repository-entry-point repairs specified in R1. Preserve
scientific safeguards and historical artifacts; retire the old automatic
handoff/review routine for this reset without bypassing installed hooks.

Deliver a recommendation based on existing evidence: what Pi-LCM already
provides, which ONE practical gap deserves attention, the best runnable addition
to test, why existing findings support that choice, and the exact bounded R2
implementation and comparison. At most two candidates may be considered.
Selecting no addition is an acceptable supported recommendation.

Use one GLM-5.3 review of the relevant decisions, diff and sources, followed by
one consolidated repair and one targeted recheck. Do not call the dual-review
or next-generation scripts. Record the reviewed implementation commit; adding
the review transcript must not restart review of unchanged implementation.

Return the <=600-word recommendation, evidence links, reviewed branch/commit,
time/usage account, exact pilot specification and a <=150-word plain-English
handoff. Then stop for Brian's one pilot-scope decision. If budget, quota, host
access or a material defect prevents completion, preserve the work and report
the precise blocker without spawning another loop.
~~~

**Source record**

This plan uses the three original accounting artifacts, Claude Fable's supplied assessment, Brian's review-board discussion, and direct repository inspection. The accounting artifacts described commit 76e5930; implementation preparation checked the later commit below. The plan's budgets and pilot limits are new operating defaults, not findings from the old experiments.

- [Implementation starting commit](https://github.com/mosherbrian/memory-bakeoff/commit/5d1d6a0159d32f19c58cabee15013ec691bd596a)
- [Recovered architectural roadmap](https://github.com/mosherbrian/memory-bakeoff/blob/5d1d6a0159d32f19c58cabee15013ec691bd596a/research/PHASE2_ROADMAP.md)
- [Gen125 instruction and deferred reader lane](https://github.com/mosherbrian/memory-bakeoff/blob/5d1d6a0159d32f19c58cabee15013ec691bd596a/control-plane/GEN125_INSTRUCTION.md)
- [Gen38 exact-provenance MemConflict report](https://github.com/mosherbrian/memory-bakeoff/blob/5d1d6a0159d32f19c58cabee15013ec691bd596a/research/MEMCONFLICT_GEN38_FULL_RELEASE.md)
- [Gen41 intended-model MemBukkit report](https://github.com/mosherbrian/memory-bakeoff/blob/5d1d6a0159d32f19c58cabee15013ec691bd596a/research/MEMBUKKIT_INTENDED_ROUND1_GEN41.md)
- [Actual pre-commit hook](https://github.com/mosherbrian/memory-bakeoff/blob/5d1d6a0159d32f19c58cabee15013ec691bd596a/.githooks/pre-commit)
- [Current handoff](https://github.com/mosherbrian/memory-bakeoff/blob/5d1d6a0159d32f19c58cabee15013ec691bd596a/handoff/CODEX_TO_CHATGPT.md)
- [Current agent instructions](https://github.com/mosherbrian/memory-bakeoff/blob/5d1d6a0159d32f19c58cabee15013ec691bd596a/AGENTS.md)
