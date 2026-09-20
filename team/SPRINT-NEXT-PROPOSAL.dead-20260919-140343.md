ANSWER:
| Research question | Current answer | Limitation | Next discriminating step |
|---|---|---|---|
| Does memory improve real work? | **Not established. This interval produced no new evidence that memory improves real work.** The new results measure abstention, benchmark retrieval and stored-state behavior, not completed-task outcomes (`S10-BM25-ABSTAIN2/verdict.json`, `S10-KD-CROSS/verdict.json`, `S10-PI-LCM-HIST/verdict.json`). | No demonstrated reduction in errors or repeated discovery; no demonstrated daily-workflow winner. | Run the pre-registered matched outcome comparison against no memory after private-data authorization and budget/date requirements are satisfied. |
| Can BM25 reject irrelevant queries without losing useful retrievals? | **Neither tested fix succeeds on the ten-case corpus.** The stopword filter rejected 0/5 irrelevant queries and reduced correct retrievals from 5 to 4. The declared margin threshold rejected 2/5 but lost one useful retrieval; none of its three tested thresholds achieved rejection without loss (`S7-BM25-PREFILTER/verdict.json`, `S10-BM25-ABSTAIN2/verdict.json`). | Rejects these configurations on this corpus, not all score-based or abstention mechanisms. | Pre-register a different relevance decision, with held-out cases and both rejection and retrieval-loss criteria. |
| Does combining BM25 with pi-lcm improve retrieval? | **The tested combination adds no benefit on ten cases:** mean set-F1 remains 0.60, with 1/5 retrievals and 5/5 abstentions correct. Requiring pi-lcm to permit retrieval discards BM25’s extra coverage (`S7-COMPOSE/verdict.json`). | One construction; other combinations remain untested. | Declare another construction only with a corpus where additional coverage and acceptable abstention are plausibly achievable. |
| Does pi-lcm need additional protection against false supersession? | **Broader constructed histories reveal a native failure; whether a layer fixes it is now unresolved.** Native false supersession rose from 0/32 on the earlier corpus to 22/33, with 0/13 missed updates. The layer was tested only on the earlier corpus (`S7-STATELAYER/verdict.json`, `S10-PI-LCM-HIST/verdict.json`). | Here, false supersession means a newer write becomes the original query’s top result. These are constructed histories, not daily-work failure rates; this concerns the memory contestant, not stack compaction. | Compare native pi-lcm with the existing thin layer on the unchanged broader corpus, pre-registering false-supersession reduction and missed-update limits. |
| Is the external benchmark’s abstention weakness specific to BM25? | **No among the five tested implementations:** all scored 0/40 abstentions on the same frozen KnowledgeDrift sample. Retrieval ranged from 11/40 to 21/40 and rationale from 3/40 to 5/40; BM25 reproduced its prior results (`S7-KD-WORLDS/verdict.json`, `S10-KD-CROSS/verdict.json`). | Two worlds, three measured families, controlled implementations. The benchmark’s author has a system in its own ranking, and it wins. This does not establish a universal property of ranked retrieval. | Compare a declared implementation capable of declining queries on the same sample, keeping family scores separate. |
| Can competing text prevent useful evidence reaching the model? | **Yes under constructed query-adjacent pressure on five items:** at a 600-character limit, evidence presence fell from 100% to 20% for BM25, 20% to 0% for pi-lcm, and 100% to 60% for the tested claude-mem adapter. Earlier pressure caused no presence loss (`S8-DOOR/verdict.json`, `S9-DOOR-RUNG2/verdict.json`). | Neither daily-work frequency nor task-level harm is measured. Evidence presence and irrelevant delivered bytes are separate measurements. | Measure whether evidence loss increases errors or repeated discovery in matched tasks. |

CHANGED SINCE LAST TIME: Three new verdict files: `S10-BM25-ABSTAIN2/verdict.json` rejects the declared margin configuration; `S10-KD-CROSS/verdict.json` extends the abstention failure to five implementations; `S10-PI-LCM-HIST/verdict.json` overturns the generalization from pi-lcm’s earlier zero-failure result. These narrow research questions, but provide no new real-work benefit evidence.

DECISION-READY: Reject the tested BM25 margin configuration and retain the rejection of the tested composition. Reopen the state-layer comparison: an observed native failure now justifies testing protection, but does not establish that protection works or justify a composite build. Keep the Phase G build restriction; the broader adopt/compose/build choice remains unresolved (`S10-BM25-ABSTAIN2/verdict.json`, `S7-COMPOSE/verdict.json`, `S7-STATELAYER/verdict.json`, `S10-PI-LCM-HIST/verdict.json`). The roadmap’s first external scored lane already exists—KnowledgeDrift—and now includes five implementations (`S7-KD-WORLDS/verdict.json`, `S10-KD-CROSS/verdict.json`).

EVIDENCE: `S7-BM25-PREFILTER/verdict.json`; `S7-COMPOSE/verdict.json`; `S7-STATELAYER/verdict.json`; `S7-KD-WORLDS/verdict.json`; `S8-DOOR/verdict.json`; `S9-DOOR-RUNG2/verdict.json`; `S10-BM25-ABSTAIN2/verdict.json`; `S10-KD-CROSS/verdict.json`; `S10-PI-LCM-HIST/verdict.json`.

SELECT: none
SPRINT-GOAL: Admit no research sprint until the candidate list contains unfinished work that can change an open research answer.
WHY: Ranks 13–15 are completed comparisons; the backlog’s “never admitted” claim is stale. Ranks 16–18 are startable at $0, but protect reporting and infrastructure rather than discriminate among memory approaches, so another deferral is an explicit decision to keep them outside this research sprint. The strongest next comparison—testing protection against the newly observed pi-lcm failure—is missing from the ranked list and cannot be silently substituted. The two-hour target does not justify repeating completed work or counting maintenance as research; private-work and date-dependent candidates remain excluded.
OUTLINE:

## 1. THEME

Update the candidate list around the newly demonstrated pi-lcm failure before committing another research sprint.

## 2. GOALS

No implementation goals are admitted. Corvid-dsh should refresh the candidate list, and cairn-pi should resolve ordinary research choices, so the next selection offers an unfinished, runnable comparison with a declared success criterion and cost.

This planning action is not a new research result or a substitute two-hour sprint.

## 3. WHO

Kiln-flash implements admitted work one task at a time; corvid-dsh independently checks it. No one checks their own work.

## 4. NOT DOING

- **Ranks 13–15:** already completed; repeating them would count old evidence as new progress.
- **Ranks 16–18:** unfinished and unblocked, but reporting and infrastructure maintenance; retain their existing order in a separate maintenance queue.
- **Real-work outcome experiment and its build:** private sessions require Brian’s explicit authorization, which cannot be defaulted. Default: no private-data access; cost cap $0; on 2026-09-20 continue non-private planning if he is silent. Any later experiment must declare the serving model and its memory-use check before running.
- **Full SWE-chat acquisition:** the recorded 17 GB free cannot hold the projected 39.3 GB. Cairn-pi should decide sampling instead of parking that choice on Brian: proposed default is a sample capped at 1 GB and $0, with planning proceeding on 2026-09-19; acquisition still requires the stated A1–A3 co-sign conditions.
- **Standing R&D watch:** cannot start before 2026-09-20.
- **Keep-warm rerun:** requires the OpenCode Go reset followed by a full steady-pattern day; that dependency is not demonstrated.
- **Gate C batch and composition-corpus choices:** these are ordinary research decisions, not owner blockers. Cairn-pi should own them instead of waiting for furloughed GiLMore or Brian; default is a refreshed mechanism-justified proposal on 2026-09-19, capped at $0.
- **Gate F composite build:** evidence does not yet choose a destination. Cairn-pi’s default on 2026-09-19 should be to retain the build restriction and commission the narrower protection comparison for ranking, capped at $0.
- **Guard-failure triage:** cairn-pi should own the existing operational handoff instead of escalating it to Brian; default is local triage on 2026-09-19, capped at $0, reported separately from research.
- **Metered work during the free window:** defer anything that can wait. Subsequent authorized work must fit the aggregate $5 all-in envelope, stopping and reporting when spending touches $5; spending beyond it requires explicit authorization.
