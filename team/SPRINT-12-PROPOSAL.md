ANSWER:
| Research question | Current answer | Limitation | Next discriminating step |
|---|---|---|---|
| Does memory improve real work? | **Not established. This interval produced no new evidence that memory improves real work.** The supplied results measure retrieval, abstention and stored-state behavior, not completed-task outcomes (`S10-KD-CROSS/verdict.json`, `S10-BM25-ABSTAIN2/verdict.json`, `S10-PI-LCM-HIST/verdict.json`). | No demonstrated daily-workflow winner or reduction in errors or repeated discovery. | Run the registered matched outcome comparison after explicit private-data authorization and satisfaction of budget/date requirements. |
| Can BM25 reject irrelevant queries without losing useful retrievals? | **Neither tested fix succeeds on the ten-case corpus.** Filtering rejects 0/5 irrelevant queries and loses one useful retrieval; the declared margin threshold rejects 2/5 and loses one. None of the three tested margin thresholds achieves rejection without loss (`S7-BM25-PREFILTER/verdict.json`, `S10-BM25-ABSTAIN2/verdict.json`). | Refutes these configurations on this corpus, not every filtering or score-based mechanism. | Test a different relevance rule, reporting rejection and retrieval loss separately on declaration and held-out cases. |
| Does combining BM25 with pi-lcm improve retrieval? | **The tested construction adds no benefit on ten cases:** mean set-F1 remains 0.60, with 1/5 useful retrievals and 5/5 abstentions correct. Requiring pi-lcm’s permission discards BM25’s additional coverage (`S7-COMPOSE/verdict.json`). | One construction; no general conclusion about composition. | Admit another construction only with cases that can distinguish added coverage from added irrelevant retrieval. |
| Does pi-lcm need protection against false supersession? | **Broader constructed histories expose native failure; protection remains unproven.** Native false supersession changes from 0/32 to 22/33, with no missed updates in either experiment. The existing layer was tested only on the earlier corpus (`S7-STATELAYER/verdict.json`, `S10-PI-LCM-HIST/verdict.json`). | False supersession here means a newer write wins the original query’s top result. These are constructed histories, not daily-work failure rates or measurements of stack compaction. | Compare native pi-lcm and the existing layer on the unchanged broader histories, with protection and missed-update limits registered first. |
| Is the external benchmark’s abstention weakness specific to BM25? | **No among these five implementations:** all score 0/40 abstentions on the frozen KnowledgeDrift sample; retrieval ranges from 11/40 to 21/40, rationale from 3/40 to 5/40 (`S7-KD-WORLDS/verdict.json`, `S10-KD-CROSS/verdict.json`). | Two worlds, three measured families, controlled implementations. The benchmark’s author has a system in its own ranking, and it wins. | Admit an implementation capable of declining queries and compare it on the unchanged sample, keeping family scores separate. |
| Can competing text prevent useful evidence reaching the model? | **Yes on five constructed cases under query-adjacent pressure:** at a 600-character limit, evidence presence falls from 100% to 20% for BM25, 20% to 0% for pi-lcm, and 100% to 60% for the tested claude-mem adapter. Earlier pressure caused no presence loss (`S8-DOOR/verdict.json`, `S9-DOOR-RUNG2/verdict.json`). | Neither daily-work frequency nor task harm is measured. Evidence presence and irrelevant delivered bytes remain separate measurements. | Test whether this evidence loss changes errors or repeated discovery in matched tasks. |

CHANGED SINCE LAST TIME: nothing — no new evidence since the last answer. No supplied verdict file is new relative to that answer; it already incorporated all three S10 results.

DECISION-READY: The roadmap’s first external scored lane is already established: KnowledgeDrift, now measured across five implementations (`S7-KD-WORLDS/verdict.json`, `S10-KD-CROSS/verdict.json`). For Decision Gate F, reject the tested composition and reopen the existing-layer comparison: native failure now warrants that experiment, but neither protection nor a composite build is justified yet (`S7-COMPOSE/verdict.json`, `S7-STATELAYER/verdict.json`, `S10-PI-LCM-HIST/verdict.json`). The overall adopt/compose/build choice remains unresolved by evidence; maintaining the build restriction does not require another sponsor decision.

EVIDENCE: `S7-BM25-PREFILTER/verdict.json`; `S7-COMPOSE/verdict.json`; `S7-STATELAYER/verdict.json`; `S7-KD-WORLDS/verdict.json`; `S8-DOOR/verdict.json`; `S9-DOOR-RUNG2/verdict.json`; `S10-KD-CROSS/verdict.json`; `S10-BM25-ABSTAIN2/verdict.json`; `S10-PI-LCM-HIST/verdict.json`.

SELECT: 16, 17
SPRINT-GOAL: Determine whether the existing state layer protects against the observed pi-lcm failure, then whether a different BM25 relevance rule rejects irrelevant queries without sacrificing useful retrievals on held-out cases.
WHY: Both candidates directly test unresolved questions, have no unmet dependencies, and cost $0 locally. Budget approximately 50 implementer minutes for rank 16 and 70 for rank 17; these are planning estimates, and two substantive comparisons fit better than adding trivial work to meet a count. Rank 16 comes first because it tests the missing comparison behind the roadmap’s main architectural decision. Ranks 18–20 are startable but protect reporting and infrastructure rather than answer these questions, so they are deferred for capacity; outcome work, dataset acquisition, the research watch and the keep-warm rerun are skipped for the specific dependencies below.
OUTLINE:

## 1. THEME

First test protection against incorrect replacement of stored facts, then test whether BM25 can refuse irrelevant queries while preserving useful retrievals.

## 2. GOALS

**Goal 1 - As Brian, I can know whether the existing protection fixes the pi-lcm failure we actually observed.**

Native pi-lcm returned an incorrect newer write in 22 of 33 broader-history trials; the existing protection has never been measured on those histories. Compare both systems on the unchanged cases, registering the required reduction and allowed missed updates before running. Distractor writes retain their original declared keys, even if that makes the protection fail. This tests the memory contestant, does not change stack compaction, and does not authorize a new composite system.

Done when: Independently confirmed results report false replacements and missed updates beside both earlier measurements, reproduce the native comparison, and satisfy `python3 /home/bmosher/memory-bake-off/team/S11-LAYER-HIST/check.py --selftest`.

**Goal 2 - As Brian, I can know whether a different BM25 relevance rule survives cases it was not designed against.**

The two tested fixes either reject nothing or sacrifice useful retrievals. Test a document-frequency support rule, freezing an unread second case set before declaring the rule and its thresholds against the original ten cases. Report irrelevant queries rejected and useful retrievals lost separately for each set; do not select a winning threshold after seeing results. This tests another mechanism, not real-work benefit.

Done when: Independently confirmed results include the frozen inputs, declaration-before-run receipts, both measurements for both case sets, and a passing `python3 /home/bmosher/memory-bake-off/team/S11-ABSTAIN3/check.py --selftest`.

## 3. WHO

Kiln-flash implements one candidate at a time, in the selected order; corvid-dsh independently confirms each result and checks that declarations preceded measurements. Nobody confirms their own work; both experiments require $0 incremental spend, and total portfolio spending must stop and be reported on touching $5.

## 4. NOT DOING

- **Ranks 18–20:** provenance repairs, single-run labels and results-directory reconciliation are unblocked maintenance, deferred for capacity and counted separately from research.
- **BLOCKED — real-work outcome experiment and private-data preparation:** Brian’s explicit authorization to use his work, sessions or data is missing, and the metered-work date restriction also applies. Default: use none of his data and continue ranks 16–17; cap: $0 for this sprint; proceed with that alternative on **2026-09-19**. Private-data use never starts by silence; reassess date eligibility on **2026-09-20**.
- **BLOCKED — SWE-chat acquisition:** authenticated HuggingFace access is missing; disk space and prior co-sign conditions are cleared. Cairn-pi owns resolving access, rather than parking a decision on Brian. Default: defer acquisition until a fleet-authorized credential exists, without using Brian’s account; cap: $0; continue available research on **2026-09-19**.
- **Research watch and Heimdall reading:** the one-request contract prevents starting before **2026-09-20**.
- **Keep-warm rerun:** one full day of the required steady usage pattern has not occurred.
- **Purported Brian-held batch and architecture decisions:** these are not sponsor blockers within the approved envelope. The backlog leaves them with GiLMore/Brian; the research director should own candidate selection and Cairn-pi should route it. Default on **2026-09-19**, cap **$0**: run ranks 16–17, retain the composite-build restriction, and defer additional admissions until a discriminating implementation is nominated; spending beyond the approved envelope still requires explicit approval.
- **Alternative composition and external declinable implementation:** the former lacks a discriminating corpus, and the latter lacks an admitted runnable implementation; the planner owns resolving those prerequisites.
