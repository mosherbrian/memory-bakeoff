**Keep the computed cockpit. Add a small, evidence-backed research view beside it. Do not add an always-on narrator or another management seat.**

Your working design already contains the right division of responsibility: code establishes operational state; a model makes that state understandable. Preserve that. Extend it so the human interface can also explain what the research has established, which beliefs changed, and what follows.

The central architectural rule should be:

> **Human-facing reports are views over versioned evidence and explicit claims. Earlier reports are never their evidentiary foundation.**

I inspected the mission, board, backlog, existing language and research-feed checkers, current status files, and several experiment records. This is a design proposal, not a complete audit; I made no project changes.

**A. Problem model. The fleet has two related failures: difficulty communicating meaning, and difficulty establishing what is true.**

They share causes, but fixing one does not fix the other.

The communication failure happens when information reaches you without the relationships needed to interpret it. “Rank 6” identifies a position in a document; it does not explain the investigation, its purpose, or its current constraint. “Passed” names an outcome without identifying what was tested. “Sprint closed” describes a workflow transition without demonstrating research progress.

The integrity failure happens when the system treats a statement or proxy as the property itself: the word “reject” becomes evidence of independent review; a checker’s self-test becomes evidence that the work is complete; previously completed work becomes new progress.

A fluent editorial agent could make all three errors sound more convincing. That is why this needs more than translation.

The underlying causes are:

| Cause | What it does in this fleet | Required response |
|---|---|---|
| Context asymmetry | Agents operate inside a recent task context; you enter intermittently and across subjects. | Each update supplies the minimum context needed for its claim. |
| Assumed shared state | A rank, filename, or shorthand substitutes for an explanation. | Resolve references to stable names and purposes before publication. |
| Repeated compression | Each handoff preserves the conclusion while dropping conditions, scope, and rationale. | Retrieve evidence directly; preserve qualifications as part of the claim. |
| Emerging project dialect | Efficient local vocabulary becomes the default language everywhere. | Maintain separate machine and human views. |
| Implementation-centered reporting | Building a checker or closing work looks like achieving a research objective. | Separate operational progress, experimental evidence, and demonstrated capability. |
| Lost causal chains | A task inherits urgency from an earlier task whose original justification is forgotten. | Connect active work to a question, the question to a decision, and the decision to the mission. |
| Ambiguous state representation | Prose simultaneously describes work, controls execution, and claims completion. | Use explicit fields for machine decisions; stop inferring them from descriptive text. |
| Summary accumulation | Yesterday’s interpretation becomes today’s “fact.” | Treat summaries as disposable outputs, never authoritative inputs. |
| Attention scarcity | Every technically true event competes with important findings. | Separate significance from urgency; suppress routine narration. |
| Local optimization | Agents finish assigned work without checking whether the owner can understand the resulting project. | Evaluate comprehension and research relevance separately from task completion. |

Several deeper failures deserve explicit treatment.

**First, the agents may not understand the organization as well as their fluency suggests.** The duplicate sprint was not merely information the assistant failed to translate. The assistant itself failed to distinguish inventory from progress. Shared shorthand can conceal shared misunderstanding.

**Second, the current board mixes incompatible kinds of information.** Work identity, historical commentary, commands, review evidence, recurring duties, and state changes coexist in prose. Four parsers then impose different meanings on it. The accidental workers named “83%” and “100%” are symptoms of that representation problem.

**Third, seemingly independent confirmation can share the same blind spot.** Different workers using the same model, specification, and mistaken scoring procedure provide separation of duties, but not necessarily independent evidence. The interface should distinguish another worker checking a result from an independent replication or a differently designed measurement.

**Fourth, quietness is ambiguous.** “Nothing needs you” could mean normal operation, planned shutdown, missing telemetry, a stalled remedy, or a broken alert path. Quiet operation needs visible coverage, not repeated reassurance.

**Fifth, human resignation is an unrecorded failure.** “Whatever” is not comprehension or approval. Fewer clarification questions may mean the interface improved—or that you stopped trying.

**Sixth, the fleet can spend its life improving the machinery that reports its progress.** Your mission is an advance in useful agent memory. The human interface must make it possible to see that the fleet ran well while producing no new evidence of improved agent behavior.

The framing I would change is this: you need both an understandable account of the project and a way to detect when that account is unsupported. The second requirement is what makes this a control surface rather than a newsletter.

**B. Design principles. Preserve technical substance while reducing reconstruction work.**

1. **Lead with a change in the project, its implications, or a decision.** “Ran six checks” is usually supporting evidence.
2. **Separate reported, observed, checked, and interpreted.** Those are different evidentiary states.
3. **Every important claim has a scope.** A result on ten synthetic cases does not silently become a claim about sustained real work.
4. **Make missing mechanisms and missing evidence explicit.** Preserve the success of “NOT WIRED.”
5. **Keep operational truth computable where possible.** Let models explain and interpret; do not let them manufacture completion.
6. **Keep research judgments revisable.** Do not force uncertain findings into operational pass/fail semantics.
7. **Use stable concepts for navigation and identifiers for lookup.** The identifier belongs underneath the human-readable name.
8. **Spend attention according to consequence and timing.** Importance alone does not justify an interruption.
9. **Make reporting failure nonblocking for ordinary research.** Missing prose should not stop valid work; missing evidence may prevent certification.
10. **Build only the context structures that answer demonstrated questions.** Avoid a second project bureaucracy.

Useful precedents support different parts of this design. SRE alerting emphasizes actionable threats and evaluates precision, recall, detection time, and reset behavior. Intelligence-analysis standards distinguish evidence from assumptions and judgments and require meaningful treatment of uncertainty. Provenance models distinguish the thing produced, the activity that produced it, and the responsible actor. These are useful design patterns without requiring their full infrastructures. [Google SRE](https://sre.google/workbook/alerting-on-slos/), [ICD 203](https://www.dni.gov/files/documents/ICD/ICD-203.pdf), [W3C PROV](https://www.w3.org/TR/prov-overview/)

**C. Architectural alternatives. Three approaches are materially different.**

| Dimension | Transcript-reading observer | Evidence-backed views over existing work | Full event-based project system |
|---|---|---|---|
| Mechanism | An agent reads conversations and produces briefings. | Existing tools expose small facts and evidence references; a local editor composes views. | All meaningful transitions enter a structured event store; views and controls derive from it. |
| Comprehension | Can recover nuance and explain unfamiliar topics. | Strong when the evidence packet includes purpose, result, scope, and implications. | Potentially strong, but only if the schema captures meaning. |
| Information loss | High risk of narrative compression and missing discussions. | Lower: claims retain direct evidence links and qualifications. | Low for recorded events; omissions can become invisible. |
| Implementation | Low initial effort. | Modest, incremental changes. | High migration and maintenance effort. |
| Tokens and compute | Repeated context loading; poor fit for your cache economics. | Work proportional to meaningful changes; mostly computed or local. | Cheap queries after substantial instrumentation effort. |
| Latency | Depends on observation cadence and context reconstruction. | Operational state remains immediate; interpretation follows events or questions. | Low once implemented. |
| Robustness | Narrator failure or omission can hide the project. | Computed page survives editor failure; evidence remains directly accessible. | Strong if ingestion and projections work; more infrastructure can fail. |
| Scaling | Degrades with conversation volume and agent count. | Scales with material changes rather than all conversation. | Best at large scale, potentially excessive for five seats. |
| Dependence on agents | High: reports must be findable and intelligible. | Moderate: agents supply intent and interpretation; tools capture execution facts. | High adoption burden; agents must emit correct events. |
| Provenance | Often appended after the explanation. | Part of the claim before the explanation is written. | Excellent for captured events and versioned artifacts. |
| Staleness | Difficult to detect reliably. | Explicit source versions and dependency invalidation. | Explicit event position and ingestion lag. |
| Bureaucracy risk | A new editorial conversation around every task. | Small if metadata attaches to existing work. | Large: schema maintenance can become a project in itself. |
| Characteristic failure | A persuasive central narrator. | A polished claim linked to evidence that does not actually support it. | Precise tracking of the wrong abstractions. |

**Choose the middle approach.** Use transcript reading as a recovery tool. Adopt event-based infrastructure only where repeated failures demonstrate its value.

The recommended system has three distinct responsibilities:

- **Operational state:** what is running, stopped, missing, blocked, or complete.
- **Research state:** what questions are open, what evidence exists, and what conclusions are currently justified.
- **Presentation:** what you need to understand now, expressed clearly with optional depth.

```text
Existing fleet
  conversations | work board | experiments | files | reviews
         |             |            |            |
         |       computed observations and evidence references
         |             +------------+------------+
         |                          |
         |                  Small project index
         |             questions / claims / decisions
         |                links to original evidence
         |                          |
         +---- targeted retrieval --+
                                    |
                    +---------------+----------------+
                    |                                |
             Computed cockpit                Local editorial job
             phases, blockers,               context reconstruction,
             coverage, freshness             explanation, questions
                    |                                |
                    +---------------+----------------+
                                    |
                         Existing page and file viewer
                          overview → explanation
                           → evidence → raw source

Human questions ────────> same index and primary evidence
Important corrections ─> affected claims and published views
```

There is no mandatory pass through an editor for machine communication.

The editor runs when:

- a material result or belief changes;
- an important claim is contradicted or invalidated;
- an authorized decision changes direction;
- an attention-worthy condition changes state;
- a scheduled briefing is due and something material has changed;
- you ask a question.

A two-minute computed refresh does not imply a two-minute model call.

**Responsibilities in the existing five-seat fleet:**

| Component or seat | Responsibility |
|---|---|
| Dispatcher and existing status computation | Capture operational transitions, enforce execution conditions, expose exact blockers. |
| `kiln-flash` | Produce work and identify its result and evidence within the existing completion workflow. |
| `corvid-dsh` | Check evidence and consequential interpretations as part of existing review; preserve dissent. |
| `plumb-fable` | Test the small new control contracts within its existing dispatch limit. No role reviewing ordinary prose. |
| `cairn-pi` | Render explanations locally, resolve references, retrieve context, and request clarification through the existing dispatcher. It still cannot certify results. |
| `anvil-oai` | Event-only consultation for consequential planning or unresolved interpretation. No routine editorial traffic. |

The best description of the added function is **evidence editor**. “Product Owner” gives it too much implied authority over priorities. “Observer” understates its responsibility to investigate missing context. “Chief of staff” captures attention management, but should not imply that its account becomes the sole organizational memory.

It may challenge a report with questions such as:

> “What changed relative to the prior run, and where is that comparison?”

It may not turn an unanswered question into a plausible explanation.

Clarification should ordinarily attach to an already scheduled worker turn. An immediate additional dispatch is justified only when the missing information affects a consequential claim or pending action.

**Disposition of what you built today:**

| Existing mechanism | Decision | What to preserve or change |
|---|---|---|
| **(a) Computed status page** | **KEEP and extend** | Preserve the phase diagram, explicit missing mechanisms, and exact closing conditions. Add evidence coverage and progress since the sprint opened. Distinguish scheduled shutdown from unexpected inactivity. |
| **(b) Gated plain-English summary** | **KEEP the separation; CHANGE the contract** | Keep local rendering, brevity, and lexical checks. Bind the output to an exact fact snapshot. Check fact relationships, not merely number membership. Bound rewrite attempts and provide a computed fallback. |
| **(c) INFORM / REMEDY / DECIDE** | **KEEP and refine** | Retain the categories. Add deadlines, delegated defaults, persistence, and deduplication. A failed remedy does not automatically become a human task. |
| **(d) File chips** | **KEEP** | Use them for evidence packets and explanations with descriptive titles. Resolve them to the correct absolute project paths. Never require remembering an identifier to open supporting material. |
| **(e) External research intake and synthesis** | **KEEP; strengthen meaning and provenance** | Keep the requirement to account for the report. Record a disposition per section. Deduplicate against existing work and identify source overlap. Do not create a candidate merely to prove someone read a section. |

I would **delete the expectation of a newly worded status every 30 minutes when its underlying state has not materially changed**. Keep checking that its dependencies remain current. A freshly touched file is not necessarily fresh information.

I would also delete:

- any use of an earlier summary as the source for a new conclusion;
- duplicate hand-maintained status documents;
- mandatory commentary for routine successful work;
- interpreting a passing language check as evidence of truth or comprehension;
- adding a permanent observer seat.

Your computed-page-plus-translation pair gets three things especially right: it exposes process structure visually, separates facts from rendering, and gives missing mechanisms a state prose cannot soften away. The proposed architecture preserves all three.

There are concrete limits in the current implementation. I supplied the language checker with facts saying 71 of 73 pieces were finished and 29 were confirmed. It accepted “71 of 73 have been confirmed by a second worker.” It also accepted an unsupported declaration that the research had achieved its objective. Its current numerical check can detect unfamiliar numbers, but not changed relationships or unsupported conclusions. [Language checker](/home/bmosher/memory-bake-off/team/tools/check_plain_language.py:85)

Likewise, the research-feed checker verifies section-name presence and an overall disposition, rather than a substantive disposition for every section. That is useful coverage checking, but it does not establish that every section was meaningfully considered. [Synthesis checker](/home/bmosher/memory-bake-off/team/tools/check_intel_synthesis.py:68)

These checks are worth keeping. Their demonstrated guarantees should be named narrowly.

**The cheapest protection against the duplicate-sprint failure is a baseline snapshot and set comparison.**

At sprint admission, capture:

- selected work identities;
- which were already complete;
- the evidence or result versions already present;
- explicitly declared reruns or carried-forward work.

Then compute:

```text
Selected work:                    11
Already complete when selected:    8
Newly completed this sprint:        0
```

The assistant should have seen:

> “The proposed sprint includes eight items already completed. It has not yet produced new results. The selection needs correction.”

Initially, compare existing candidate references and work identities. If identifiers change between sprints, use the originating candidate reference and detect repeated deliverables; do not rely on ranks or row positions.

An intentional rerun remains valid, but needs a new run identity and declared purpose. Prior results cannot count as the new run’s completion.

This is much cheaper than an observer agent. It would have challenged the particular mistaken success claim without needing to understand the whole research program.

**D. Human-facing information model. One page, with different questions at different depths.**

The default page should answer four things:

1. **Does anything require my judgment, and by when?**
2. **What consequential thing changed?**
3. **What is the fleet trying to learn next, and why?**
4. **Is the work proceeding, and how complete is our evidence?**

Keep the phase diagram directly available. Add a compact research view beside or below it:

| Research question | Current answer | Limitation | Next discriminating step |
|---|---|---|---|
| Does combining retrieval methods improve selection? | This tested combination did not. | Result applies to one combination and the frozen cases. | Consider a materially different combination only with a new rationale. |
| Is an extra state layer justified? | The tested layer added no benefit on the measured failure mode. | This does not rule out other state-management needs. | Investigate an unmeasured failure mode before building more machinery. |
| Does selective memory improve real work? | Still unanswered by the proposed outcome experiment. | Retrieval scores do not establish task benefit. | Resolve the experiment’s execution constraints and run the declared comparison. |

Those are supported by the inspected experiment records and proposed outcome design; they are not claims that I independently reran the experiments. [Combination result](/home/bmosher/memory-bake-off/team/S7-COMPOSE/verdict.json), [State-layer result](/home/bmosher/memory-bake-off/team/S7-STATELAYER/verdict.json), [Outcome experiment](/home/bmosher/memory-bake-off/team/S6-ROADMAP/next-experiment.json)

Each finding expands through four levels:

| Level | Contents |
|---|---|
| **Change** | What changed, why it matters, and any essential limitation. Usually one to three sentences. |
| **Explanation** | The question, prior belief, new evidence, interpretation, and resulting action. |
| **Evidence** | Comparison, scope, controls, dissent, review status, and source freshness. |
| **Reconstruction** | Exact inputs, commands, versions, results, discussions, and original files. |

A limitation that reverses the headline’s meaning belongs in the first level. “It improves performance” cannot conceal “only on a benchmark we designed” several clicks down.

This follows the useful HCI pattern of overview followed by selective detail, while retaining relationships and history as navigable information. [Shneiderman’s information-visualization taxonomy](https://drum.lib.umd.edu/items/155a868e-fb83-4115-9899-9187ea8c0498)

Do not create a separate manually maintained document for every perspective. Reuse the mission, roadmap, experiment declarations, and existing evidence ledgers. Generate views from them.

Persist only information that cannot be reliably reconstructed:

- why work was chosen;
- what belief it was intended to test;
- why a decision followed;
- the scope and unresolved limitations of a claim;
- stable descriptions of frequently referenced concepts;
- the evidence relationships needed to recover those explanations.

A glossary is useful as a resolver, not assigned reading. “Rank 6” should resolve to a source-version-specific candidate and then to a stable description. If the rank later changes, the concept must not.

**E. Machine-to-human translation contract. Small semantic additions, mostly captured at existing boundaries.**

Agents do not need to emit a report at every turn.

At work admission, retain three semantic fields:

- **Question or purpose:** what uncertainty or capability this work addresses.
- **Connection:** which existing goal or decision it serves.
- **Expected distinction:** what outcomes would lead to different actions, when relevant.

At a meaningful result or decision, retain:

- **Observation:** what happened, including scope.
- **Evidence:** exact source references.
- **Interpretation:** what the observation supports, including “no change.”
- **Consequence:** what happens next, or what decision is required.
- **Limitation or dissent:** only when material.

Execution facts should be captured by tools, not retyped by agents:

- work and run identity;
- start and observation times;
- check execution and exit status;
- input, output, and checker versions;
- author and reviewer identities;
- receipt existence and review outcome.

Text-only sessions are sufficient. These fields can live in an existing result file or a short fenced block in the completion reply. The dispatcher can extract a narrowly delimited block. Do not parse arbitrary surrounding prose as control instructions.

For example, the existing composition result already contains most of what is needed:

```yaml
question: Does combining the two retrieval methods improve selection?
observation:
  combined_score: 0.600
  stronger_component_score: 0.600
  cases: 10
interpretation: This combination adds no measured benefit.
limitation: Does not test other ways of combining the methods.
next: Do not use this result to justify building the proposed layer.
evidence:
  - /home/bmosher/memory-bake-off/team/S7-COMPOSE/verdict.json
  - /home/bmosher/memory-bake-off/team/S7-COMPOSE/results.jsonl
```

This is a proposed normalized record, not a requirement to rewrite every existing result.

The translation process should be:

1. Resolve the work’s subject and purpose.
2. Retrieve the relevant prior claim or measurement.
3. Read the result and any review or contradiction.
4. Establish whether the result is comparable to the prior evidence.
5. Identify the smallest meaningful change.
6. State its implication and the limitation that matters.
7. Decide whether it belongs in a page, briefing, or interruption.
8. Attach source references to the claims before rendering prose.

If a step fails, the output should narrow accordingly:

> “The worker reports a successful result, but the comparison needed to establish improvement is missing.”

Do not substitute confidence of expression for recovered context.

**Use different contracts for operational facts and research interpretation.**

For operational facts, prefer deterministic sentences or named placeholders:

```text
{completed_count} pieces of work are complete.
{independently_checked_count} have been checked by another worker.
```

A model may add explanation, but cannot swap the predicates attached to those values.

For research interpretation, mechanical validation can check references, required scope, contradictory statuses, and version consistency. It cannot generally prove that evidence entails a scientific conclusion. Consequential interpretations need the existing reviewer’s substantive assessment, plus selective later audits.

Every published claim should retain:

```text
claim
scope
supporting evidence
challenging evidence
interpretation author
review status
source versions
observed time
supersedes / corrected by
```

Do not require all of this to appear in the human message. Most is underneath it.

**Temporal meaning requires more than a timestamp.**

Distinguish:

- when an event reportedly happened;
- when the system observed it;
- when a conclusion was adopted;
- when the underlying evidence changed.

A board’s “done 10:00” string is not an authoritative clock. An output file’s modification time is not proof that the experiment ran then.

Preserve revisions rather than overwriting history:

> “Previously we treated the combination as promising. Today’s test showed that its selection rule discards the extra retrieval coverage. We are dropping this particular combination; the broader idea remains untested.”

When evidence is invalidated, dependent conclusions become “needs reassessment.” They must not remain current merely because nobody edited the summary.

**The telephone-game protection is structural.**

- A daily briefing queries claims and primary evidence, not yesterday’s briefing.
- A weekly account queries the same evidence over a longer interval.
- An editor may use an earlier explanation to discover context, but must follow its references.
- Sources have version identities, so a link to an overwritten file is not enough for historical reconstruction.
- Consequential claims have direct evidence links and counterevidence links.
- Corrections invalidate affected published views.
- The computed page remains usable when the editor fails.
- You can inspect evidence without going through the narrator.
- Occasional audits sample both published claims and suppressed events.

A single editor may produce most prose. It should never be the single authority over truth, visibility, and correction.

**F. Concrete translations and the ten requested scenarios.**

First, three repairs to your actual failed messages.

**“The unexecuted candidates are rank 1, rank 6, and rank 11.”**

Those references resolve to:

> “The three proposals are: testing whether selective memory improves real work; using real coding conversations to study memory failures; and measuring what useful evidence actually reaches the model.”

Then add the applicable status and constraint from the relevant snapshot. The inspected backlog records execution-scope and budget constraints for the first, storage constraints for the second, and a local measurement proposal for the third. Their ranks are unnecessary in the human answer. [Candidate descriptions](/home/bmosher/memory-bake-off/team/BACKLOG-NEXT.md)

**“Unroutable QUEUE row … Fix the seat name…”**

If diagnosis is established:

> “The task reader mistook a comparison table for work assignments. This is an automation defect; it has been assigned for repair.”

Ordinarily, you should receive no phone message. If progress is affected, the page can show the impact and repair state. “Has been assigned” must come from an actual assignment record.

**“460: open (added 2026-0”**

This should fail publication entirely. A line fragment is neither a useful status nor a resolvable human reference. The fallback should show the full task title and current state—or explicitly say the task could not be resolved.

For “golden half,” “canonical again,” and “census half,” the translator must retrieve their definitions and the relevant decision. Without them, a reliable translation is impossible. It should not invent what those terms mean simply to sound helpful.

The following examples combine actual project findings with explicitly marked test scenarios. Proposed machine fields illustrate the architecture; they are not claims that those records already exist.

**1. An experiment confirms an existing hypothesis — actual composition finding.**

The dense result includes:

> “the gate-owning compose gains +0.000 mean set-F1 over the stronger single arm…”

Internal record:

```text
question: Does this combination improve retrieval selection?
prior expectation: No improvement with this selection rule.
observed: Combined score equals stronger component, 0.600.
scope: Ten frozen cases.
belief change: Expected limitation confirmed.
action: Do not pursue this construction on the strength of this result.
source: S7-COMPOSE/verdict.json, linked per-case results
```

You see, in the next briefing:

> “Combining the two retrieval methods in the tested way added no benefit. The selection rule filtered out the extra useful results as well as the unwanted ones. This confirms the predicted limitation of this construction; it does not rule out other combinations.”

No interruption. The result matters because it closes a particular option, not because another experiment finished.

**2. An experiment overturns a belief held for days — replay scenario using the actual prefilter result.**

The real result says:

> “bm25-prefilter still fires on every abstain case…”

For this test, assume the fleet had treated common-word filtering as the likely fix for several days. That belief history is hypothetical; the result is real.

```text
prior claim: Common-word filtering is likely to fix unwanted retrieval.
new evidence: Still returned results on all five should-decline cases.
secondary effect: Correct retrieval fell from five cases to four.
status: Prior proposed explanation no longer adequate.
action: Drop this fix; reassess dependent plans.
```

You see:

> “The proposed common-word filter did not fix unwanted retrieval and made one previously correct retrieval fail. We should stop treating that filter as the remedy. Any plan that depended on it needs revision.”

Expanded view: when the belief was adopted, what evidence supported it, what changed, and which plans depend on it. If this overturns the active direction, it gets prominent placement; it still need not page you if the fleet can revise the plan within its authority.

**3. An uninteresting infrastructure bug is fixed — actual board-parsing failure class.**

```text
kind: infrastructure
cause: Non-work Markdown table interpreted as assignments.
evidence: Reproducer and corrected parser behavior.
impact: Spurious worker-resolution alarms.
research belief change: None.
notification: Suppress after verified repair.
```

You normally see nothing.

If you previously saw the alarm, its existing incident entry becomes:

> “Resolved: the task reader no longer treats comparison tables as assignments.”

No separate celebratory notification.

**4. Three agents disagree about a benchmark — hypothetical disagreement over the actual KnowledgeDrift results.**

```text
shared observation: Retrieval 21/40; appropriate decline 0/40.
view A: Supports the earlier unwanted-retrieval finding.
view B: Selection and grading choices limit generalization.
view C: Measures returned hits, not whether an agent used them.
agreement: These results do not establish improved real-task behavior.
next: Identify the comparison that separates these interpretations.
```

You see:

> “The external cases support the concern that the lexical retriever returns material when it should decline. The disagreement is about how far that finding generalizes: the test samples particular cases and measures retrieval, not improved agent behavior. The next useful check is whether relevant evidence actually reaches the model.”

The expanded view shows each position, its supporting evidence, and the result that would change it. Three votes are not three independent measurements.

The inspected result file itself illustrates why precise sources matter: its headline groups paraphrase with difficult phrasing, while its detailed breakdown reports 10/10 for paraphrase. The interface should preserve the detailed distinction rather than blindly repeat the headline. [Benchmark result](/home/bmosher/memory-bake-off/team/S7-KD-WORLDS/verdict.json)

**5. An unexpected result may be a breakthrough — hypothetical outcome experiment.**

```text
observation: Selective memory improved the declared task outcomes.
scope: Initial matched comparison only.
interpretation: Potential advance in useful memory.
unresolved: Replication, alternative explanations, representative tasks.
action: Preserve inputs; run the declared validation.
attention: High significance, no immediate owner action.
```

You see:

> “The first task-level comparison suggests selective memory may reduce errors and repeated investigation. That would address the project’s central goal. It is an initial result; the fleet is checking whether it survives replication before treating it as an advance.”

The evidence view includes the actual effect sizes, denominators, costs, task selection, adverse outcomes, and uncertainty. If those are missing, the headline must be weaker.

High significance earns prominent visibility. It does not automatically earn a phone interruption.

**6. A task fails repeatedly while agents keep working — hypothetical repeated delivery-measurement failure.**

```text
objective: Measure evidence delivered to the model.
attempts: Three.
failure signature: Same adapter boundary.
new information since last attempt: None.
retry allowance: Exhausted.
action: Park failing branch; perform bounded diagnosis or switch work.
```

You see:

> “The measurement of what reaches the model is stalled at the same adapter boundary. Repeated attempts have added no information. The fleet has stopped repeating that attempt and is diagnosing the boundary; other research can continue.”

This is materially different from “agents are working on it.”

Retries should be limited by repeated failure and lack of new information, not just inactivity. The system should not ask you to debug its adapter.

**7. An agent wants to change research direction — grounded in the actual mission.**

```text
proposal: Prioritize real-task outcomes over further retrieval tuning.
reason: Existing scores do not answer the mission's central question.
displaces: Named tuning work.
authority: Check mission, scope, spend and execution limits.
status: Proposed until authority check completes.
```

Your mission already authorizes the fleet to discover direction within existing resource and access limits. A direction change inside that delegation should normally be reported after an accountable internal decision, not sent for routine approval. [Mission](/home/bmosher/memory-bake-off/MISSION-20260912.md)

You see:

> “The fleet is shifting effort toward whether memory improves real work. Further retrieval tuning would not answer that question. The change postpones the named tuning task and stays within the existing execution and spending limits.”

If the proposed execution exceeds those limits, you instead see a concrete choice, cost, deadline, and fallback. The rest of the fleet continues authorized work.

**8. Twenty routine things and two important things happen — illustrative daily mix using real findings.**

```text
routine events: Twenty, retained but collapsed.
material finding A: Tested composition added no benefit.
material finding B: Tested state layer added no benefit.
grouping: Both affect justification for further construction.
```

You see:

> “Two results narrow what is worth building. The tested retrieval combination added no benefit, and the extra state layer did not improve the measured update behavior. Neither result answers whether memory improves real work; that remains the main unresolved question.”

A collapsed “Routine operations” view remains available. The twenty events receive no twenty-item digest.

**9. You return after three days — illustrative catch-up rendering.**

```text
comparison interval: Explicit start and end.
baseline: Last briefing opened, or requested date—not assumed understanding.
retrieve: Changed claims, decisions, unresolved constraints, current objective.
exclude: Resolved intermediate churn unless it explains a current consequence.
```

You see:

> “The project’s goal is unchanged: demonstrate that memory makes agents better at sustained work. Since your last briefing, the tested retrieval combination and added state layer failed to justify themselves. The next important question is still task-level benefit. Below are the decisions that changed, what remains uncertain, and any constraint that now needs your judgment.”

It should then show the actual dated changes for that interval. It must not concatenate three daily summaries or pretend opening a briefing proves you understood it.

**10. You ask what a cryptic term means and why it matters — actual “delivered-context door.”**

```text
alias: DELIVERED-CONTEXT-DOOR / former backlog rank 11
concept: Measure the exact memory text supplied to the model.
purpose: Separate retrievable evidence from delivered evidence.
relation: Prerequisite measurement for interpreting task outcomes.
source: Candidate description and experiment specification.
```

You see:

> “‘Delivered-context door’ means checking the exact memory text the model receives. A retriever can find the right fact without that fact surviving the final context assembly. This measurement checks whether useful evidence reaches the model and how much irrelevant text accompanies it. It helps explain memory failures; it does not by itself prove better task performance.”

Offer the specification underneath. Do not require learning the alias.

**G. Interaction and interruption policy. Importance and urgency are separate dimensions.**

Retain INFORM, REMEDY, and DECIDE. Add a second classification describing epistemic significance: routine, finding, changed assumption, contradiction, risk, or opportunity.

| Event | Default destination | Reason to interrupt |
|---|---|---|
| Routine successful work | History only | None. |
| Expected research confirmation | Briefing if it changes confidence or closes an option | A time-sensitive consequential decision depends on it. |
| Valid negative experiment | Research view and next briefing | Usually none. |
| Execution failure | REMEDY | Human authority is actually required for the remaining remedy. |
| Changed assumption | Prominent research update; dependent claims flagged | Continuing before review would cause material loss. |
| Newly discovered risk | REMEDY or DECIDE according to authority | Timely human action can change the outcome. |
| Contradictory evidence | Visible disagreement; consequential claims qualified | A pending irreversible decision depends on resolving it. |
| Delegated decision | Decision history and material-change briefing | None solely because it was a decision. |
| New spend or expanded scope | DECIDE when outside existing limits | A genuine deadline exists. |
| Strategic opportunity | Next briefing | The opportunity expires before normal review. |
| Repeated stall | Computed page; bounded recovery | A specific judgment is needed, rather than generic unblocking. |
| Potential breakthrough | Prominent finding with uncertainty | Only an agreed notification preference or immediate decision justifies a page. |
| Important unexplained anomaly | Record, preserve evidence, investigate | Plausible near-term harm requires action. |

A DECIDE item must state:

- the choice;
- why existing delegation does not cover it;
- the recommendation and tradeoff;
- the decision deadline;
- what proceeds meanwhile;
- what happens if you do not respond.

The fallback must stay inside existing authorization. “Continue other work and leave this branch paused” is often appropriate. Silence is not permission to spend.

Failed automatic recovery should route first to a bounded repair task, alternate path, or parked branch. It should not automatically produce “Brian call.”

This reconciles two real requirements: you should not be in the ordinary critical path, but the fleet cannot make every new resource or scope decision on your behalf. Recurring DECIDE requests are evidence that the standing delegation needs improvement.

For natural questions, the retrieval requirements are specific:

| Your question | Required information |
|---|---|
| “Where are we?” | Mission, current research questions, supported answers, active work, material constraints. |
| “What happened today?” | Material observations and decisions in the interval, with routine work collapsed. |
| “Why are we doing this?” | Task → question → decision → mission, plus whether the rationale still holds. |
| “What did that experiment tell us?” | Declared question, comparison, result, controls, scope, interpretation, exclusions. |
| “What should I care about?” | Consequence, urgency, uncertainty, and relevance to your stated goals. |
| “What changed since yesterday?” | Claim and decision differences between two evidence snapshots. |
| “Explain that in English.” | Resolved concepts and causal explanation, with unchanged technical scope. |
| “Are we learning anything important?” | Uncertainty reduced, alternatives eliminated, decisions improved, capability demonstrated—and gaps between them. |

The last answer must be allowed to say:

> “The fleet improved its instrumentation, but this interval produced no new evidence that memory improves real work.”

A project can be operationally healthy and scientifically unproductive. The interface must make that distinction easy to see.

**H. Attack the architecture. Its most dangerous failure is becoming a trusted producer of attractive explanations.**

| Failure | Prevention |
|---|---|
| Evidence links create false credibility | Check whether the evidence supports the actual claim, not just whether the file exists. Review consequential claims substantively. |
| The editor suppresses something important | Keep a suppression record with reasons; sample suppressed events during evaluation. |
| The editor becomes a bottleneck | Computed state and evidence stay available; ordinary execution does not wait for prose. |
| Fresh prose masks old facts | Bind publication to source versions; invalidate by dependency changes, not file-touch time. |
| Missing data looks like success | Display unknown, missing, not executed, failed, and not applicable distinctly. |
| A result file’s headline conflicts with its details | Compare structured results and qualifications; show unresolved inconsistency. |
| The fleet overproduces “important” findings | Rank by effects on goals, decisions, risk, and uncertainty—not author enthusiasm. |
| Quietness becomes invisibility | Show latest observation time, coverage, and planned shutdown state without paging. |
| The glossary becomes another document to memorize | Resolve terms inline and on demand; maintain only useful concepts. |
| The metadata becomes paperwork | Attach it to existing admission and completion artifacts; capture mechanical fields automatically. |
| Dissent becomes an endless debate | Record the competing explanations and the next discriminating test. Avoid vote counting. |
| Repeated rewrites waste local capacity | Limit attempts, report validation failure internally, and fall back to computed statements. |
| Parallel sources amplify the same claim | Track shared experiment and source lineage; multiple retellings do not count as corroboration. |
| The renderer follows instructions embedded in source material | Treat retrieved documents as data; source text cannot change notification or execution policy. |
| Better reporting crowds out research | Measure worker time and displaced implementation work; remove features that do not improve comprehension. |

There is another enforcement issue in the supplied history: **writing a check before implementation does not establish that the check is meaningful or that its author was blind to the implementation.**

Keep three conditions separate:

1. The checker exists and its own validation distinguishes known good and bad examples.
2. The checker runs against the actual deliverable.
3. Another worker assesses the result under the applicable independence rule.

The real artifact check may appropriately fail before implementation. Requiring it to pass before the work starts would reproduce the very confusion between checker readiness and work completion you described.

Restricting the check author’s provided context helps enforce blindness. Scheduling order alone cannot prove it.

For the Markdown board, the eventual target should be one parser with explicit boundaries and fields. Sharing the parser prevents inconsistent readings; separately designed failure examples are still needed to catch mistakes common to every consumer. Four tools agreeing on one bad parse is not independent confirmation.

**I. Implementation plan. Keep the build proportional to demonstrated benefit.**

All proposed project artifacts belong under `/home/bmosher/memory-bake-off`, not the current workspace. The paths below are proposed locations, not files I created.

**Stage 0 — replay existing evidence, with no new production infrastructure.**

Build or change:

- Nothing in the dispatcher.
- Assemble a small fixed set of historical evidence packets from existing transcripts, files, board revisions or backups, and results.
- Include the duplicate sprint, false independent review, a real negative research result, stale information, a routine repair, and an unresolved interpretation.
- Use cairn in bounded runs to create short explanations directly from those packets.
- Require a private sentence-to-source map for evaluation.
- Compare those explanations with the original messages.
- Record which missing information prevented a reliable answer.

Do not clean up the whole archive first. Missing context is an experimental result.

Exit condition: identify whether most comprehension failures arise from presentation, missing relationships, inaccessible evidence, or unreliable state.

**Stage 1 — minimal viable intervention.**

Build or change:

- Add the sprint admission baseline and new-progress comparison.
- Bind each generated summary to an immutable fact snapshot or content identity.
- Render important operational counts and predicates deterministically.
- Make stale or invalid narrative fall back to current computed status.
- Add one compact research section to the existing page, sourced from existing result files.
- Add purpose and belief-change information only to work whose existing artifacts lack it.
- Maintain a small manually reviewed mapping of active research questions to evidence and decisions.
- Publish local synthesis on material changes and on request.
- Add an optional “unclear” or “this looks wrong” response that records the exact displayed snapshot.

A possible home for the small index and evaluation records is:

```text
/home/bmosher/memory-bake-off/team/human-interface/
```

Do not migrate the board or add a database yet. Do not add an observer seat.

Exit condition: the owner can explain current findings and constraints accurately with less effort, without a rise in omissions or unnecessary interruptions.

**Stage 2 — instrument only the gaps Stage 1 exposes.**

Possible additions, each justified by observed failures:

- A single board parser, migrated consumer by consumer after comparison against current behavior.
- Typed operational states instead of keyword classification.
- A small event file for meaningful transitions, written by the existing dispatcher.
- Versioned result and review references.
- A rebuildable SQLite index if file scanning or temporal queries become expensive.
- Explicit claim dependencies where invalidation repeatedly fails to propagate.
- Automated clarification requests for missing consequential evidence.
- A section-to-disposition structure for external research synthesis.
- Separation of active work from archived history once parser behavior is stable.

Use a single writer or atomic file replacement where appropriate. Deduplicate repeated events and tolerate partial writes. A reporting ingestion failure should preserve the last known snapshot with an explicit coverage warning.

Do not add Kafka, a graph database, or embeddings merely because the project concerns memory. Explicit links and ordinary indexed queries should handle this fleet first.

Exit condition: reliable temporal reconstruction, bounded context retrieval, and demonstrably fewer false state claims.

**Stage 3 — mature human interface.**

Build only capabilities that remain useful in evaluation:

- Natural-language questions over the project index and primary evidence.
- Return-after-absence briefings.
- Claim histories showing what changed and why.
- Experiment comparisons that preserve metric definitions and scope.
- Visible disagreement and alternative interpretations.
- Dependency-aware correction of prior statements.
- Notification preferences for significant discoveries.
- A remembered vocabulary preference, with explanations still available on demand.
- Periodic samples of omitted events and unsupported interpretations.
- Measured costs and visibility into time spent on research versus maintaining the fleet.

Do not infer that you know a concept merely because it was shown once. Remember explicit preferences; preserve a short contextual phrase where needed.

**Cost policy throughout:** use computed triggers and local rendering, batch changes, and avoid paid idle observation. Measure cache misses and actual token charges; do not assume the free local model has no throughput or implementation opportunity cost.

The relevant overhead is:

```text
paid cold calls
+ paid warm calls
+ local compute time
+ metadata authoring time
+ review time
+ displaced research work
```

Your supplied 38× cold-call penalty makes repeated remote context reconstruction particularly unattractive. It strengthens the case for a small index and event-triggered work, not for keeping another agent awake.

**J. Evaluation. Measure whether you can reconstruct the right model of the project.**

Readability scores and word counts are insufficient. The interface should be evaluated against questions with evidence-backed answers.

| Metric | How to measure it |
|---|---|
| **Comprehension accuracy** | After reading, explain the objective, result, implication, and remaining uncertainty. Score against a source-grounded rubric. |
| **Change recognition** | Identify what is newly learned and what was already known. |
| **Evidence/interpretation discrimination** | Identify which statements are observations, judgments, and untested possibilities. |
| **Time to understanding** | Time required to answer a fixed set of project questions correctly. |
| **Clarification burden** | Clarifications per briefing, classified by missing context, jargon, ambiguity, or genuine curiosity. |
| **Material omission rate** | Important source events absent or materially understated in the interface. Review sampled suppressed events. |
| **False implication rate** | Correct facts presented in a way that implies unsupported success, independence, causality, or generality. |
| **Interruption precision** | Fraction of interruptions that required timely human attention. |
| **Interruption recall** | Fraction of genuinely time-sensitive human decisions surfaced in time. |
| **Provenance success** | Fraction of sampled claims whose supporting and challenging evidence can be reached and interpreted. |
| **Freshness correctness** | Whether the displayed account matches its stated source version and current validity. |
| **Return comprehension** | After several days away, explain current direction, changed beliefs, and unresolved decisions. |
| **Long-term degradation** | Repeat comparable tests as the project and history grow. |
| **Operating overhead** | Added calls, tokens, local latency, worker effort, and displaced research. |
| **Abandonment** | Count “whatever,” skipped briefings, and cases where you work around the interface. |

Use short teach-back questions sparingly during evaluation, not as a permanent burden. You should not become the test harness for every update.

Build a replay suite from the actual failures:

- independent review claimed without a receipt;
- a checker that only tests itself;
- a missing check confused with a broken check;
- old completed work admitted as new progress;
- future completion timestamps;
- a missing planner described as waiting;
- stale prose attached to a newer fact sheet;
- a finding generalized beyond its experiment;
- correlated evidence presented as independent;
- a material event incorrectly suppressed.

Include correct examples too. A system that marks everything unknown is safe from some false claims but useless.

Set acceptance thresholds before comparing versions. For an initial pilot, reasonable proposed targets are: no unsupported success claims in the replay set, correct recognition of every major changed belief, and a substantial reduction in reading time without worse material omissions. These are design targets, not validated universal numbers.

No LLM should be the sole judge of whether another LLM’s explanation is faithful. Use deterministic checks for measurable facts, a reviewer’s source-grounded rubric, and your ability to explain the consequential parts.

**K. The first experiment: replay the duplicate sprint as a blinded “what actually changed?” test.**

This is the single most informative first trial because the original assistant misunderstood the project before communicating it.

1. **Freeze one evidence packet** from the sprint opening: the proposal, the preceding completed-work state, relevant result files, and the original success report. Use historical material or label any reconstruction clearly.
2. **Give cairn three bounded attempts in fresh contexts:**  
   - the original material used for reporting;  
   - that material plus a request for plain English;  
   - the same material plus the computed distinction between already-complete work and new completion since opening.
3. **Ask for the same output each time:** at most 120 words answering what changed, whether the sprint has produced new progress, and what should happen next. Require source references underneath.
4. **Have corvid check fidelity in an existing review slot.** Randomize the outputs before you read them.
5. **Test comprehension with three questions:** “How much new work happened?”, “What is wrong with the proposed sprint?”, and “Does this need me to unblock it?” Record correctness and reading time.
6. **Use the result to choose the next intervention.** If plain-English prompting remains misleading but the explicit before/after facts produce an accurate answer, implement the baseline comparison first. If the relevant facts cannot be reconstructed, fix evidence capture before improving the renderer.

The success condition is concrete: **the interface must make it difficult for either the assistant or you to mistake previously completed work for new progress.**
