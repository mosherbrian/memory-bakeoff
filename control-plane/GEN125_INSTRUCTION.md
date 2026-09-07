generation: 125  
source\_generation: 124  
source\_commit: 77b34d9e772c8f35f339b9263f298ab028472b80  
trigger\_pr: none  
status: requested

\# Generation 125 — separate the Phase-2 lanes and resume the roadmap; NO READER RUN

\#\# Plain-English control-plane review

Brian: Gen124 found a real and useful exploratory signal, but it also exposed that we have been mixing two different questions. LongMemEval-oracle asks how much the reader itself is affected by the order in which old and current facts are presented when retrieval is perfect. MemConflict and longitudinal-v1 ask the project’s main architecture question: which memory system actually maintains and returns the right evolving state under realistic ingestion and retrieval.

Both are worth studying, but they are separate evidence classes. The primary Phase-2 track remains memory-system architecture and system selection. The LongMemEval ordering work becomes a focused reader-attribution ablation that can explain failures seen in system tests; it is not the roadmap and it does not get to consume its 14 untouched holdout items yet.

Gen124 remains exploratory. Its cleaned pilot strongly suggests presentation order can make the reader answer with the superseded value, but the scorer and eligibility rules were repaired during review, residual chronology remains in the text, and the final 14 items are the last untouched confirmation set. Preserve that distinction exactly.

The next generation should stop the reader-apparatus loop, reconcile the recovered Phase-2 roadmap through Gen124, perform the overdue field refresh, and produce the deliberately small 3–5-item next-batch intake that Gen123 was supposed to produce.

\#\# Authoritative provenance

Work from exact commit:

\`77b34d9e772c8f35f339b9263f298ab028472b80\`

Before changing anything, read at that exact commit:

\- the top entry of \`handoff/CODEX\_TO\_CHATGPT.md\` and note that it is stale relative to source\_generation 124;  
\- \`handoff/GEN124\_RECAP.md\`;  
\- \`handoff/GEN124\_TECHNICAL.md\`;  
\- \`research/pilot\_ordering/PREREGISTRATION.md\`;  
\- \`research/PHASE2\_ROADMAP.md\` in full;  
\- the Gen124 review entries in \`reviews/LEDGER.md\`, including the final CARRY / hand-over decision;  
\- the pilot artifacts named by the Gen124 recap/technical handoff, including \`research/pilot\_ordering/COMBINED.json\`, \`PILOT\_HEADLINE.json\`, and \`SUBSTRATE\_VERIFY.json\`.

Do not infer Gen124 state from the stale top handoff entry. Use the exact pinned commit and the Gen124 recap/technical artifacts as current repository state.

\#\# Control-plane ruling

1\. \*\*NO READER/MODEL EXPOSURE in Generation 125.\*\* Do not run the 14 untouched LongMemEval holdout items, rerun the 34 pilot items, call the reader endpoint, or spend another holdout merely to validate apparatus.

2\. \*\*Keep Gen124 exploratory forever.\*\* Preserve its pilot responses, journals, computed artifacts, preregistration history, and review record. Do not relabel its counts as benchmark evidence or merge them into any leaderboard.

3\. \*\*Durably separate two lanes:\*\*  
   \- \*\*Primary system-selection lane:\*\* which memory system should we use? Use longitudinal-v1 and/or an external system benchmark such as MemConflict where ingestion, update/supersession, retrieval, provenance, and scope are under test.  
   \- \*\*Reader-attribution lane:\*\* given the same relevant old/current records, how much do order and chronology change the reader’s answer? LongMemEval-oracle belongs here because retrieval is oracle-perfect by construction.

   Never combine the two lanes’ metrics into one score or use reader-ordering performance as a proxy for memory-system quality.

4\. Treat the reader-attribution lane as explanatory, not primary. Its job is to answer questions such as whether a memory system that co-returns stale and current records can still fail even when retrieval recall appears perfect.

5\. \*\*Resume the recovered Phase-2 roadmap now.\*\* Reconcile Phases A–H against actual repository evidence through Gen124. \`research/PHASE2\_ROADMAP\_RECONCILIATION.md\` does not exist at the pinned commit, so create it. Preserve \`research/PHASE2\_ROADMAP.md\` itself as the recovered historical plan.

6\. \*\*Perform the overdue field refresh using fresh primary sources.\*\* Keep the governing question: what systems maintain evolving agent state while preserving lossless history, provenance, scope, recoverable historical belief, semantic recall, and bounded working context? Incorporate the Gen124 corrections: MemConflict is directly relevant to current-valid-state after user updates; ConflictQA is prior art for order-swapped contradictory evidence; LongMemEval-oracle is a reader-isolation substrate, not a system-selection benchmark.

7\. For each retained external benchmark/project, record version/date, task dimensions, evaluator/model assumptions, open/local/self-hostable status, code/reproducibility, whether gains appear architectural versus model/service-driven, and whether the evidence is retrieval-heavy, state-heavy, workflow-heavy, governance-heavy, or reader-attribution-heavy. External scores remain external evidence only.

8\. \*\*Re-rank by distinct mechanism, not popularity.\*\* Revisit at least Membukkit and Claude-Mem, and reassess StateMem, MemStrata, MemOS, AgentRunbook-C, A-Mem, memharness, Attestor, EvoMem, MemConflict-backed testing, and any newer candidate that answers the architecture question better. Reject redundant candidates explicitly.

9\. Produce a ranked \*\*next-batch intake of only 3–5 contestants/ablations\*\*. Every row must answer: “What distinct architectural question does this answer that our existing evidence has not already answered?” Assign each to longitudinal-v1, external system benchmark, focused mechanism ablation, reader-attribution ablation, or reference-implementation reproduction.

10\. The intake must explicitly recommend \*\*DEFER / AUTHORISE LATER / DROP\*\* for the 14-item LongMemEval confirmation run. The default control-plane position is \*\*DEFER\*\*. Do not spend the holdout merely because it exists. If later authorised, preserve the pinned substrate hash, untouched membership, preregistered reader/configuration, paired-item analysis, and diagnostic-vs-confirmatory separation.

11\. Keep Pi/Pi.dev and pi-lcm central. Treat evaluated-system identity as model × inference configuration × harness × harness configuration × tools × environment. The architecture target remains layered: lossless history, explicit lifecycle/state projection, durable semantic retrieval, bounded working-memory synthesis, and one context composer.

12\. Repair current-facing project state. \`handoff/CODEX\_TO\_CHATGPT.md\` must regain a true top entry for the generation being handed back; do not leave Gen122 masquerading as current. Update the review ledger, roadmap reconciliation, field refresh, candidate intake, handoff, and \`control-plane/PENDING.json\` consistently.

\#\# Required outputs

Create or complete at least:

\- \`research/PHASE2\_ROADMAP\_RECONCILIATION.md\`;  
\- \`research/PHASE2\_FIELD\_REFRESH\_2026-09.md\`;  
\- \`research/PHASE2\_CANDIDATE\_INTAKE.md\`;  
\- a durable short note under \`research/\` defining the system-selection vs reader-attribution evidence split and where Gen124 fits;  
\- a corrected top handoff entry that tells Brian what Gen124 taught us, what remains exploratory, which Phase-2 lane is primary, and what the next 3–5 tests should be.

\#\# Completion gate

Generation 125 is complete only if:

\- no reader/model exposure occurred and the 14 untouched LongMemEval items remain untouched;  
\- Gen124 remains explicitly exploratory/non-benchmark evidence;  
\- the system-selection and reader-attribution lanes are durably separated;  
\- the recovered Phase-2 roadmap is reconciled through Gen124 rather than recopied;  
\- the field refresh uses fresh primary sources and separates external evidence from our measurements;  
\- the candidate intake contains only 3–5 architecturally distinct next steps and explicitly ranks them;  
\- the intake explicitly decides whether the 14-item LongMemEval confirmation should be deferred, later authorised, or dropped;  
\- current-facing handoff/project docs no longer imply that reader-apparatus refinement is the roadmap;  
\- relevant tests for changed repository machinery pass, with pre-existing failures reported rather than concealed.

Do not authorise the LongMemEval holdout run in Gen125. First give the control plane the roadmap reconciliation and ranked Phase-2 intake it has been waiting for.  
