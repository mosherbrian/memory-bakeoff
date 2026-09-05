# Agent memory architecture

*Post-Gen38 synthesis, 2026-09-04. Base commit `0d26fcd`.*

> **State** tells the agent what to do now. **Memory** tells it what it has learned.
> **History** lets it reconstruct what happened. **Artifacts** establish what is true.
> **Executive reasoning** decides what it means.
>
> **Control** defines what the agent is allowed to do next.
>
> *Don't delete the past just because you stop putting it in every prompt.*
>
> *The system of interest is the composition, not any individual component.*

This document is an architectural **hypothesis**, not a measured result. It records
where thirty-eight generations of measurement have pushed the project's thinking,
and it separates what we measured from what we read and what we infer.

---

## A. The one-page version

The bake-off began as a contest between memory products. It is ending as something
narrower and more useful: **a component evaluation inside a larger agent
architecture.**

Two results forced the change. First, at full external-benchmark scale, two
production memory systems land within a point of each other and within a few points
of a plain BM25 index on exactly the question the benchmark exists to ask — which of
two contradictory statements is currently true. Better retrieval is not what is
missing. Second, an engine that *does* try to decide currentness, by retiring records
on similarity, does not fix the problem; it trades one failure class for another.

If neither better retrieval nor automatic retirement solves currentness, the missing
capability is not inside the memory component at all. It is the surrounding
structure: what the agent is currently doing, what it is allowed to do next, what it
can still recover, and what outranks its own recollection.

## B. Why one giant transcript is the wrong abstraction

The default agent design keeps one growing conversation and hopes the model can find
what it needs in it. That single object is asked to serve five incompatible jobs at
once: current task state, learned knowledge, recoverable history, evidence of truth,
and the reasoning surface itself.

They have different lifetimes, different sizes, different access patterns, and
different authority. Current state must be small and always present. Learned
knowledge must be searchable and selective. History must be complete and is usually
irrelevant. Evidence must be authoritative and is rarely text. Compaction collapses
all five at once, which is why it feels lossy in ways that are hard to name: it is
not "losing detail", it is destroying four different things to make one of them fit.

The alternative is not a better summariser. It is separating the responsibilities.

## C. The layers

Defined by responsibility, lifetime, authority and interface — deliberately not by
product.

**1. Human direction.** Goals, priorities, tradeoffs, changing intent. Nothing below
this layer is entitled to overrule it.

**2. Executive synthesis.** Cross-task and cross-generation reasoning: integrate
evidence, maintain the larger thesis, choose the next question, reconcile tensions
without silently rewriting evidence. Must keep measured evidence, external
literature, and inference distinguishable.

**3. Executable semantics and control.** Workflow rules, invariants, stop conditions,
permissions, legal transitions. This layer says what *may* happen. It should prefer
code, typed state machines and validators over prose, because prose rules are
advisory and code rules are not.

**4. Structured execution state.** A compact sufficient representation of the current
task: phase, goal, open hypotheses, active files and processes, completed
checkpoints, next action, validated receipts. Optimised for *what matters next*, not
for reconstructing the past. Where possible it should reference authoritative
evidence rather than duplicate it.

**5. Current observation and bounded working context.** The latest instruction, tool
result or process output, plus only the recent and retrieved material the next step
needs. Context compression belongs here and nowhere else.

**6. Durable semantic and project memory.** Searchable learned facts, decisions,
conventions, prior failures. Retrieval is selective. Currentness, scope and lifecycle
must be explicit: **semantic similarity is neither truth nor supersession**, which is
the single most expensive lesson in this repository.

**7. Lossless history and evidence log.** Full transcripts, tool traces and
historical states, retained outside normal prompt replay but recoverable for
provenance, debugging and reconstruction.

**8. Authoritative artifacts.** Git, source, benchmark leaves, manifests, test output,
databases, hashes, receipts. These establish truth and **outrank recollection**.

**Side branch, not core: latent/parametric adaptation.** Weight-level overlays may
eventually carry habits or domain steering, but they are opaque, hard to attribute,
and not a substitute for searchable memory or recoverable history. Keep outside the
core stack until evidence warrants promotion.

## D. Authority and flow rules

1. These are responsibilities with flows between them, **not a storage hierarchy**.
2. **Artifacts are the authority bedrock.** A state field like
   `persona_14_complete` should carry or point to a validated leaf digest, never
   become a competing truth source. Gen38's resume rule is the concrete form of this:
   a persona is skipped only when its pins, counts and digest all validate.
3. **State is not history.** State answers "what next"; history exists precisely so
   that what state discards stays recoverable.
4. **Memory may not silently mutate history.** Corrections and supersession must
   preserve lineage.
5. **Control and state are distinct.** Control defines the legal transitions; state
   says where you are inside them. Gen38's calibration gate is control; "persona 17
   of 27" is state.
6. **Executive synthesis must keep provenance.** Measured, read, and inferred are
   three different epistemic statuses and must stay labelled.

## E. Where the studied systems sit

Mapping by role, avoiding false equivalence:

| System | Layer | Note |
|---|---|---|
| Perseus Vault, Mem0, Hindsight, agentmemory, MemBukkit | 6 durable semantic memory | each with its own lifecycle and evidence class |
| pi-observational-memory | 5 working-context production | **not** a semantic query/recovery store |
| context compression (Headroom-style) | 5 bounded working context | efficiency, not durability |
| retained transcripts and tool traces (pi-lcm-style) | 7 lossless history | role, not an implementation claim |
| Git, results leaves, manifests, receipts, control-plane docs | 8 authoritative artifacts | the bake-off's own evidence base |
| state-machine / typed-workflow designs | 3 control | see §F for what is actually verified |
| latent/parametric injection (PLE, n-gram overlays) | side branch | experimental |

**Illustrative example, not evidence.** This project currently runs as an accidental
instance of the model: a human sets direction; a separate model acts as
cross-generation executive synthesis and writes the control plane; an execution agent
runs the generation loop; Git, the results leaves and the Drive mailbox are the
artifacts that settle disputes. It is offered as an analogy only.

## F. The evidence that led here

### F.1 Internal measured evidence (committed artifacts)

All from this repository; the committed leaves and digests are authoritative and this
section is a summary of them, not a new source.

- **Retrieval is not the bottleneck for currentness.** Gen38, full MemConflict
  release, 30 personas and 142,093 writes per engine, 27-persona held-out primary
  slice: Perseus hit@3 **0.465** (dynamic 0.434, static 0.343, conditional 0.987),
  Mem0 **0.456** (0.419 / 0.383 / 0.974), frozen BM25 baseline **0.285** (0.226 /
  **0.312** / 0.914). The engines beat a lexical index by roughly twenty points on
  dynamic questions and by at most three on static ones.
- **No winner between the two engines.** Persona-block bootstrap (seed and resample
  count frozen before reading outcomes): Mem0 − Perseus hit@3 95% interval
  **[−0.0273, +0.0095]** — yet the two disagree on **705 of 3,189** questions at K=3.
  Similar rates, different evidence found.
- **Static failure has at least two mechanisms.** Of Perseus's 324 held-out static
  questions, 86 returned the newer contradiction without the truth and 96 returned
  neither session at all; Mem0's split is the same shape. Only about a quarter is
  competition; a third is plain unreachability.
- **It is a ranking problem, not an availability problem.** Perseus quarantined 199
  writes across the held-out personas under its own interference bound, but 197 of its
  static misses had fully admitted support; Mem0 quarantines nothing and still misses
  200 with fully admitted support.
- **Automatic retirement trades failures rather than fixing them.** Gen35, the
  project's only within-engine causal intervention: disabling agentmemory's Jaccard
  retirement removed every false supersession, history erasure and correction failure,
  and returned configuration collapse to 6 and false persistence to 9 — the same
  figures three append-only engines produced. Similarity is not supersession.
- **Seven failure classes recur across unrelated engines.** Gen29–33 found the same
  classes in Perseus, Hindsight and Mem0, five at identical counts, across systems
  sharing no storage engine, retrieval algorithm or time model.
- **Reporting is where the errors were.** Gen34 rebuilt every Round-2 aggregate from
  leaf evidence: no conclusion changed, but 45 default-fallback patterns were found in
  the older summarisers, each capable of turning "not measured" into a number.
- **Product behaviour is a first-class measurement.** Gen38's replication gate found
  Perseus's hybrid RRF returns tied scores whose order is stable within a run but not
  across runs (77 of 399 reorderings, 2 of 380 hit@3 class changes), while Mem0
  replicated byte-for-byte. Cost projections from a three-persona calibration
  predicted the full release within 2%.

### F.2 External research (verified against primary sources for this document)

- **StateFlow** (arXiv [2403.11322](https://arxiv.org/abs/2403.11322)) formulates
  task-solving as a state machine, separating "process grounding" from "sub-task
  solving", with transitions "controlled by heuristic rules or decisions made by the
  LLM". Reported: 13% and 28% higher success than ReAct on InterCode SQL and ALFWorld
  at 5× and 3× less cost. *The abstract does not state whether cumulative context is
  retained across states; we do not assert that it does or does not.*
- **FrontierHarness** ([frontierharness.org](https://frontierharness.org/)) holds the
  model fixed (Kimi K3) and varies only the harness across 9 harnesses in 12
  configurations, 360 trials. Pass rate spans **50.0% to 66.7%** and median cost per
  task spans **$1.05 to $18.34**. The authors caution that the results are
  software-engineering/terminal specific and that "quality and cost can diverge".
  This is external evidence that composition changes realised performance; it is **not**
  a score for our stack.

### F.3 Referenced in project discussion but *not* verified here

SKILL.state, SMAG/Thinker, ontology-to-tools, LLM-as-Code, LOM-action, FAOS, TFlow.
These informed the layer vocabulary but were **not** checked against primary sources
in Gen39, so no claim in this document rests on them. They are listed so a later
reader knows what to verify, not as evidence.

### F.4 Architectural inference

Everything in §B, §C, §D and §G is inference. It is consistent with §F.1 and §F.2 but
is not measured. The falsifiable form is in §I.

## G. Implications for a coding agent

- **Give the loop a state object, not a longer transcript.** Phase, goal, next action,
  validated receipts. Small, always present, pointing at artifacts.
- **Put invariants in code.** Gen38's gates — calibration before held-out, digest
  validation before skipping a persona, refusing to run under a drifted adapter hash —
  worked because they were executable, not because they were written down.
- **Keep history out of the prompt but not out of existence.** Compaction should move
  material to layer 7, never destroy it.
- **Do not ask the memory layer to adjudicate truth.** It is measurably bad at it, and
  the engine that tries hardest trades one failure for another.
- **Let artifacts win.** When state, memory and a hash disagree, the hash is right.

## H. Evaluation roadmap (design only)

**Component tests** continue as they are: frozen evidence classes, calibration before
full release, exact provenance, fail-closed reporting.

**A state/control experiment in Pi**, holding model, runtime and task snapshot fixed,
comparing (a) ordinary history plus compaction, (b) explicit structured execution
state, (c) structured state plus durable history retrieval. Measure task success,
token and context cost, redundant tool and reasoning churn, recovery after compaction
or restart, and state corruption or overwrite failures.

**Composition tests only after component identities are pinned.** The evaluated unit
is model × inference config × harness × state/control configuration × memory and
history components × tools and environment. Reader answer-quality lanes stay separate
from exact-provenance retrieval lanes. FrontierHarness-style external tasks may
eventually serve as a composition ruler, but need controlled configs and repeats; one
small sample supports no leaderboard claim.

## I. Open questions, stated so they can fail

1. Can a small structured execution state reduce prompt replay and tool churn
   **without** lowering task success?
2. Does retaining full history out-of-context and retrieving on demand preserve
   continuity better than summary-only compaction?
3. Can durable memory answer currentness questions without sacrificing historical
   recoverability — or is that trade fundamental, as Gen35 suggests?
4. Does executable control reduce procedural errors compared with prompt-only rules?
5. Does a layered composition beat the best single memory product on real Pi coding
   tasks at equal model, context and tool budgets?
6. What actually belongs in always-present state versus retrieved memory versus
   artifacts?

Question 3 is the one this repository is closest to answering, and the current
evidence points at "the trade is real".

## J. References

Primary sources verified for this document:

- Wu, Yue, Zhang, Wang, Wu. *StateFlow: Enhancing LLM Task-Solving through
  State-Driven Workflows*. arXiv:2403.11322. <https://arxiv.org/abs/2403.11322>
- *FrontierHarness* evaluation report. <https://frontierharness.org/>

Internal evidence, authoritative:

- `RESULTS.md` — the evidence index, one row per generation.
- `research/MEMCONFLICT_GEN38_FULL_RELEASE.md` and
  `results/memconflict_gen38_full_release/` — the full-release lane.
- `research/AGENTMEMORY_GEN35_RETIREMENT_ABLATION.md` — the retirement intervention.
- `research/ROUND2_REPORTING_INTEGRITY_GEN34.md` — the reporting audit.
- `research/MEMCONFLICT_GEN36_CONTRACT.md` — the external-benchmark contract.
- `EXPERIMENT_PLAN.md` — the original staged plan, preserved as written.


## First prototype (added 2026-09-04, after Gen42)

The layer separations above now have a working prototype on the installed Pi, reported in
`research/PI_STATE_CONTROL_GEN43_PROTOTYPE.md`. Evidence class
`architecture_prototype_no_score`.

Measured, on a fixed synthetic trace with no model involved:

- Pi's public `context` extension hook returns a replacement message array, so the live context
  can be composed rather than replayed **without patching or forking Pi core**. A synthetic
  80-message transcript was replaced by one composed message, 46,031 bytes down to 413.
- Executable control refused an illegal transition and refused `done` twice: once with no
  receipt, once with a failing one. `done` was reached only after a passing receipt existed.
- Editing the receipt's file after completion invalidated the claim. Artifacts outranked state.
- Across the trace, history grew 81x while the composed live context ended at 2.6% of it and
  active state stayed under its bound. Old detail moved out of replay rather than being deleted,
  and an archived decision was recalled on demand without becoming permanently resident.
- Restart rebuilt the exact phase, state digest and history head from persisted evidence alone.

Still unmeasured, and not implied by any of the above: whether this design improves coding-task
success, reduces tool churn, or saves tokens under a live model. That is a paired experiment with
model, harness and task held fixed, not a prototype.

---

## Measured evidence appended 2026-09-04, after Gen55 and Gen56

This section records what has been measured since the Gen39 hypotheses were written. It does not
rewrite them, and it does not upgrade any earlier inference to fact.

### Quiescent completion is a closed line: an optional harness guardrail

**It is a termination control, not a task-correctness mechanism.**

Demonstrated form: `quiescent-completion-toolcall-v2` at K = 3 tool calls, on
`tracked-tree-digest-v1`. A receipt is valid only on the current tracked tree; a passing check on a
tree that already holds a valid receipt counts as idle rather than re-arming; an exact revert to the
initial tracked tree is never eligible; and the stop waits for an in-flight tool batch to drain.

Gen55 live evidence on the intent-persistence ruler: 2 of 12 treated runs triggered, with **zero**
contract violations and **zero** stops on a tracked tree equal to its initial tree. The treated arm
had **no** timeouts against the baseline's **three**, and totals were 132 against 709 tool calls and
516 against 3,108 seconds. The benefit was concentrated entirely in runs that stalled.

Two limits travel with that result and must not be dropped:

- **A valid visible receipt can exist on a wrong tree.** The controller stops such a run faster. It
  does not make the tree correct. Both Gen55 triggers were on trees the hidden verifier rejected.
- **Live treatment exposure was only 2 of 12.** No broad effect size may be generalised from this.

### Artifact authority is proposition-scoped

The earlier slogan that artifacts establish truth must be read narrowly, and this is now measured
rather than argued.

**A passing artifact establishes only the proposition it actually checks, on the tree and
configuration it checked.** It does not establish task truth.

The evidence: Gen49's false assurances, Gen55's two wrong-tree stops, and the Gen56 audit of all 72
intent-persistence runs. In that audit, 14 runs ended hidden-verifier-wrong while holding a valid
visible receipt, and in **every one** the broadest shipped visible validation also passed. Nine of
those fourteen had already run the project-wide check live. Across all 72 final trees the broadest
shipped visible check never once failed. On the IP4 fixture the shipped visible test passes a known
partial implementation that the hidden verifier rejects.

So the gap is not the *scope of the command*. It is the *coverage of the visible artifact*. A
harness cannot recover a requirement that no visible test encodes.

### Unchanged by Gen51-56

Gen50 audited five failures and found **zero** `missing_relevant_context`. Nothing in Gen51 through
Gen56 revives retrieval, a prompt floor, or a larger context window.

### Open question carried forward

How should artifact and receipt authority be scoped so that control can distinguish *this check
passed* from *the task is sufficiently verified* — given that, on this ruler, no amount of command
breadth closes that gap?

## Generated evidence as a gate — CLOSED (2026-09-05, Gen60-65)

Measured, not asserted. On the `evidence-generation-gen59-v1` corpus with the
pinned local model, tests written by a model from the visible instruction alone
catch wrong implementations well (12 of 12, including three that pass the
shipped tests) and reject known-correct code in **half the tasks**.

Three interventions failed to move that rate: requiring each test to quote its
requirement (no effect - the false accusations already quoted correctly);
deleting anything not entailed by the quote (removed 158 of 188 tests at
precision 0.101); and deleting only with a named extra condition (15 removals,
precision 0.267, unsafe rate back to 4 of 8 on the same four tasks).

The cause is informational: an overreaching test and a soundly-inferring test are
indistinguishable given one requirement sentence and one test. Separating them
requires the repository, which removes the independence that makes generated
tests worth having.

**Conclusion: use generated tests to surface suspicious cases for a reviewer, not
to decide correctness automatically.** PASSED is retired as the headline for this
question; report the unsafe bank rate, retention range and named detection losses
instead (`gate-suitability-report-v1`).

A repository-informed checker was then tried (Gen66) as its own branch, with the
critic shown the pre-work repository and verified candidate-blind: **the unsafe
rate stayed at 4 of 8, the same four tasks**, and the `pathsafe` bank kept all
seven of its false accusations with the code in view. Removing the information
handicap removed the explanation for the earlier failures without changing the
result.

**The candidate-blind gate branch is CLOSED (Gen67).** Further prompt, filter or
context tuning on this architecture is closed. A checker permitted to inspect the
candidate is a different, non-independent architecture - a checker that reads the
implementation is on its way to agreeing with it, which is the Gen49 failure this
programme exists to detect - and must not be reported as the next iteration of
this experiment.

## Reader-layer capabilities — CLOSED (2026-09-05, Gen83-87)

Two rows of Gen68's table were zero for every engine, and neither survived
inspection as a product result.

`recommended_procedure` asked which of two attempts to adopt. **Every engine
returned the recommendation, in every repetition** — twelve of twelve. The zero
was `failed_procedure_adoption`, charged because the failed attempt also fell
inside a window covering five of eight records, on a query sharing no word with
anything in the store (Gen83).

`negative_unknown` asked a question with no answer. At that checkpoint the store
held four records and the adapters requested five. **Refusing was never on the
menu**, no engine but mem0 exposes a relevance floor, and no setting of any floor
separates the case — on agentmemory the unanswerable question scores higher than
any other case in the run (Gen84).

**Neither question can be answered by a store.** One requires reading two records
and inferring which to adopt; the other requires deciding to decline. Both are
reader capabilities, and Round 2 had no reader: `reader_answer` and
`score_answer_claim` existed and no runner ever populated or called either.

A reader was then added on its own branch, over frozen retrieval, changing exactly
one architectural component (Gen85-86). With an explicit decision channel —
`ADOPT: <id|NONE>` and `ANSWER: UNKNOWN|ASSERTED`, scored alone, with supporting
and contrasting citations recorded and never scored — across **506 orderings**,
every feasible permutation of all six distinct evidence sets:

- **unknown abstention: 100% correct and fully order-stable**, on every set. No
  engine difference.
- **procedure adoption: 470 of 480 correct.** Only perseus's evidence set is fully
  order-stable (120/120); the 114/118/118 spread across the others is inside
  ordering noise and is not an engine difference.
- **`failed_procedure_adoption` fired zero times in 480 orderings.**

Two intermediate findings were retracted by later controls and are kept on record
rather than edited away: Gen85's citation contract failed a correct
recommendation for citing the counterexample it argued against, and its
`ORDER_EFFECT` verdict on abstention did not survive the repaired channel — the
same 24 orderings that gave 10 abstentions give 24.

**The Gen85→86 improvement is NOT attributed causally.** That contract changed
both the scoring and the elicitation, and no fourth contract was run to separate
them.

**The rule this leaves.** `recommended_procedure` and `negative_unknown` are
**reader/full-product capabilities, not retrieval-engine metrics**. They stay
`NOT_DEMONSTRABLE` at the retrieval layer permanently, because a retriever was
never the thing being asked. Future tables must not mix the layers, and
`assert_no_layer_mixing` in `layer_boundary.py` fails closed if one does. The
reader branch stays architecturally separate from retrieval-only main.
