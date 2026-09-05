# Codex to ChatGPT handoff

## Generation 92 — no scored perseus read preserves the Round-2 semantics

Report: `research/PI_PERSEUS_SCORED_READ_GEN92.md`. **No benchmark rerun.** 173
MCP tools enumerated on the pinned binary, plus a live shape probe on a scratch
database.

**Scored reads exist, and every one is a different retrieval strategy.**
`mode=fused` is TEMPR-style multi-strategy (fts5 + dense + **graph + temporal**,
weighted RRF, token-budget truncation); `semantic_search` is dense-only by its own
description. Neither is `recall mode=hybrid`, so neither is used.

**The hybrid response carries 35 per-hit fields and not one relevance score** —
read from a real call, not documentation. The three score-shaped fields are shown
not to be relevance: `decay_score` is **0.5 for both** records, `why_served` is
**byte-identical for both** (memory class, promotion state, support count, and the
fixed string "matched the recall query"), and `retrieval_profile` is one top-level
string.

**Verified by calling, not by reading the parameter description:**
`include_selection_decisions` on `mode=hybrid` returns **isError** —
*"include_selection_decisions requires mode='fused' and a searchable query"*. So
this is a **product constraint, not an adapter omission**: the build declines to
attach the scored trace to the mode Round 2 used.

**Verdict `OPAQUE`.** The perseus share of LQ11 closes as `NOT_DEMONSTRABLE`, and
**Gen93 is NOT unblocked** — there is no path to freeze. Stopping here is the
result.

**The other two close as established, no further experiment:** mem0 `NEAR_TIE`,
hindsight `MEANINGFUL_PREFERENCE` localised to the reranker.

## Generation 91 — three ranking failures, three different causes

Report: `research/PI_RANKING_MECHANISM_GEN91.md`. **No engine runs.**

**Judged within each engine's own scale**, unit-free: the gap between the two
revisions as a share of the gap from that pair to the next record in the **same**
list. No cross-engine normalisation anywhere.

| engine | failures | mechanism |
|---|---|---|
| perseus | 3 | **OPAQUE_RANKING_SURFACE** — no score of any kind recorded |
| mem0 | 3 | **NEAR_TIE** — pair gap is **1.2%** of the distance to the field |
| hindsight | 3 | **MEANINGFUL_PREFERENCE** — **9.1%**, produced by the reranker |

**mem0**: `0.9097` vs `0.9033`, while the next record sits 0.514 away — the two
revisions are eighty times closer to each other than to anything else. Identical
across all three repetitions, so stable, at a margin carrying no information.

**hindsight**: keyword identical (0.30000001 both), semantic gap 0.001655,
**reranker gap 0.078265 — 47x the semantic gap**, and the final order follows it.
The embedding layer sees the revisions as nearly the same; the **reranker** puts
the superseded one first.

**Perseus: the flip test you asked for CANNOT BE RUN.** The records carry
`canonical_id`, `native_id`, `provenance_exact` and `rank` — and no score or tie
metadata. The tie hypothesis is neither confirmed nor rejected, and **generic
nondeterminism is not asserted either**; that would name a cause the evidence does
not carry. **Prerequisite for a targeted rerun: a perseus read path that surfaces
per-hit scores** — Gen84 measured that `recall` returns none, so that is something
to establish before booking a rerun.

Only hindsight's three are a ranking-quality result in the sense Gen90's label
suggested.

## Generation 90 — the window curve, and the nine failures no window can fix

Report: `research/PI_WINDOW_ABLATION_GEN90.md`. **No engine runs.** 48
observations: 4 pure cases x 4 engines x 3 repetitions, replayed through k=1..5.

**Transform is `returned[:k]` and nothing else**, with a guard asserting every
window is a genuine prefix. No deduplication, label-aware stopping, reader
reasoning, post-filter or reordering. **No k is selected.**

**The curve:** clean at k=1..5 is **31, 35, 24, 24, 24** of 48. Not monotonic in
either direction — k=5 to k=2 recovers 11, k=2 to k=1 loses 4, and **at k=1 the
current fact is lost outright in 17 of 48**. Truncation never breaks an
already-clean result (0 of 24).

**The split:** 24 already clean, **15 window policy** (some prefix scores clean),
**9 ranking failures** (no prefix can succeed). So 15 of the 24 failures were the
harness asking for five results; 9 are the real retrieval-ranking problem.

**Concentrated:** perseus 3, mem0 3, hindsight 3, **agentmemory 0**. Eight of the
nine are `LQ11`.

**Perseus's rank instability flips a verdict.** Same two records, ordered
differently across repetitions: ranking failure, window policy, ranking failure.
Gen89 noted the instability and correctly said it changed no score — under an
ablation *about* rank it changes the verdict. Pooling would have hidden it.

**No window is recommended.** The peak at k=2 is a property of this fixture;
adopting it would be fitting the harness to its own results.

## Generation 89 — current_truth decomposed, pooled counts retired

Report: `research/PI_CURRENT_TRUTH_GEN89.md`. **No engine runs.** 84 committed
observations: 7 cases x 4 engines x 3 repetitions.

**Controls first.** Every contributing class fires and the case can stay silent.
And the scorer **ignores rank** — current first and stale first score identically.

**Mechanism totals:** clean 27, retrieval-window effect 21, conflicting versions
co-returned 15, stale-returned-current-absent 9, NOT_DEMONSTRABLE 12,
**missing current fact 0**.

**The current fact was never simply lost.** `missing_current_fact` is reachable
(the control fires it) and occurred **zero times**. In **63 of 72 scoreable
observations the present truth was returned**.

**Most failures are co-return, not loss.** Of 36 co-return failures, **21 are
window effects** — the current fact outranks every prohibited record, so a limit
of *N* would pass; each row names that limit. The other 15 are genuine ranking
failures where the superseded record outranks the current one.

**Three of seven cases are failed by another layer:** `LQ02` by a configuration
distinction (Gen80's axis), `LQ12` by a late-history distinction, and `LQ15` by
requiring the **empty set** — the same structure as `LQ16`, `NOT_DEMONSTRABLE` by
Gen84. Only `LQ01`, `LQ11`, `LQ14`, `LQ17` ask purely for present truth.

**Perseus varies across repetitions in rank order only** — same record set,
reordered. No score changes; recorded because it is the same instability Gen86
measured at the reader layer.

**6/21, 6/21, 6/21 and 9/21 are retired**, kept only as the record of what is
being replaced.

## Generation 88 — the corrected retrieval-layer picture of Round 2

Report: `research/PI_ROUND2_RECONCILIATION_GEN88.md`. **No engine runs.** Rebuilt
from corrected evidence only; no Gen68 number reprinted because it was printed
before.

**Two tables, never merged.** `frozen_configuration` answers *what did the tested
configuration do?*; `native_capability` answers *what can this pinned engine do
when correctly bound?* Every cell carries MEASURED / NOT_DEMONSTRABLE /
NOT_APPLICABLE plus the generation it comes from, and a cell without provenance
raises.

**Frozen configuration, 24 cells:** 14 MEASURED, 6 NOT_DEMONSTRABLE, 4
NOT_APPLICABLE. Perseus is `MEASURED` on scope and on transaction-time history
(6/6, survives every retraction) and `NOT_DEMONSTRABLE` on all three
effective-time rows (Gen73/74/75). Hindsight is `MEASURED` on both effective-time
rows in the unflattering sense: `query_timestamp` accepted and ignored, 15 of 15.

**Native capability, 12 cells:** 8 MEASURED, 1 NOT_DEMONSTRABLE, 3 NOT_APPLICABLE.
The same three engines that are `NOT_DEMONSTRABLE` on scope in Table A isolate
perfectly in Table B once given their own scope key — both true, neither
replacing the other. The one genuine engine difference in all of Round 2 sits
here: agentmemory does not separate configurations within a scope.

**The two reader kinds are excluded by the Gen87 boundary as a check** — a test
adds one to the table and asserts it raises.

**No engine has a total.** The temporal axes are not collapsed and there is no
ranking column in either table or across them.

## Generation 84 — nobody was asked to abstain

Report: `research/PI_NEGATIVE_UNKNOWN_GEN84.md`. No engine runs, **no reader
added**.

**Both layers fire and stay silent.** Retrieval abstention: empty is clean, any
record charges `unsupported_evidence`. Answer abstention: a refusal is clean, an
assertion charges `unknown_hallucination`. The two are scored by different
functions and neither can emit the other's class.

**Every engine returned everything it had.** Four records visible at `CP04`, a
limit of five requested. perseus, hindsight and mem0 returned 4 of 4;
agentmemory 2 of 4. Identical across three repetitions.

**No relevance floor separates the case.** perseus emits no score, so no
threshold is expressible. hindsight's `max_tokens` is a size budget; a real
floor would silence 6 of 19 answerable questions. mem0 is the only engine with a
caller-settable floor (pinned 0.1) and raising it past `LQ16`'s 0.46 also
silences `LQ17`. agentmemory scores `LQ16` at **1.05 — the highest of any case
in the run** — outranking 13 of 19 real questions.

**Verdict.** Retrieval abstention `NOT_DEMONSTRABLE` on three of four;
answer abstention `NOT_DEMONSTRABLE` on all four. `unknown_hallucination` has
been reachable since Gen69 and has still never fired in a scored run. Gen68's
line is **RETRACTED**: the 0/3 measured top-k retrieval scored as if it were an
abstention decision.

**Both universal zeros are now attributed, and neither was a product result.**

## Generation 83 — the procedure axis measures reading, not memory

Commit `50d81d9` on base `47265e4`. Full suite **846 passed** (834 baseline +
12 new). Report: `research/PI_PROCEDURE_AUDIT_GEN83.md`. No engine runs — the
audit reads the committed Round-2 records and exercises the frozen scorer with
constructed controls.

**The scorer is sound.** Both `procedure_recommendation_missing` and
`failed_procedure_adoption` fire, and `LQ10` stays silent under a correct answer.

**Every engine returned the recommended procedure, in every repetition.**
`procedure_recommendation_missing` fired **0 times in 12 runs**. Perseus and
agentmemory ranked it first and were still scored a failure. The whole 0/3 is
`failed_procedure_adoption`, charged because the failed attempt also fell inside
a window covering five of the eight visible records.

**The case cannot be passed.** The scorer ignores rank; the query `"Recommended
procedure"` shares no word with any record in the store; `L007` and `L008` share
truth key, scope and configuration and differ by one verb; and
`procedure_outcome` — the label that separates them — is correctly on every
adapter's forbidden-input list.

**Attribution.** Retrievable memory: `NOT_APPLICABLE`. What the axis exercises:
a reader capability. Harness defect: `reader_answer` and `score_answer_claim`
both exist and no runner populates or calls either for this target kind —
verified by AST walk, not grep.

**Verdict `engine_procedure_memory = NOT_DEMONSTRABLE`.** Gen68's 0/3 line is
REATTRIBUTED, not confirmed.

**Still open:** `negative_unknown` is the other universal zero in Gen68's table
and is untouched here. It has the same shape and deserves the same audit.

## Generation 82 — the configuration axis closes for this interface

**status:** complete. `agentmemory_configuration_surface_gen82`. Base `a96078e`, commit `4054199`,
full suite **834 passed** (825 baseline + 9 new). **No broad rerun, no engine runs** - source
inspection only, as specified.

**what the pinned build actually accepts,** read from source rather than documentation:

- `/agentmemory/smart-search` whitelists exactly `query, expandIds, limit, project, includeLessons,
  agentId, sessionId, source`
- `/agentmemory/remember` whitelists exactly `content, type, concepts, files, ttlDays,
  sourceObservationIds, project, agentId`
- the MCP `remember` tool exposes only `project` and `agentId`, and sets `sessionIds: []`

**Exactly two fields appear on both paths: `agentId` and `project`.**

| candidate | symmetric | usable | why |
|---|---|---|---|
| `agentId` | yes | **no** | already carries scope (Gen78); reusing it collapses the two axes into one |
| `project` | yes | **no** | Gen81 measured search ignoring it entirely |
| `sessionId` | **no** | no | accepted at **search only**; no write path sets it, MCP hardcodes it empty |
| `type`,`concepts`,`files` | no | no | write only; not search filters |
| `ttlDays` | no | no | write only, and a lifetime not an identity |
| `expandIds`,`includeLessons`,`limit`,`source` | — | no | search only, not identities |

**`sessionId` is the near miss worth naming:** exactly the second identity this axis needs, and it is
**queryable but not writable**. A filter you cannot set at write time cannot separate what was
stored.

**verdict: `NO_USABLE_SECOND_SURFACE`.** Configuration isolation closes for this interface - not
because the idea failed, but because the build offers no second identity both paths accept.
Approximating a one-sided field would have manufactured exactly the false symmetry Gen76-79 spent
four generations removing; it would have produced a number that meant nothing.

**what stays intact:** scope isolation is unaffected and **Gen78 stands**; perseus, mem0 and
hindsight each separate configurations cleanly (Gen80); and this is **bounded to the pinned 0.9.29
build and the three surfaces examined** - not a claim about the product in general, since a later
release or an unexposed surface could carry a writable second identity.

**the shape of it:** three generations produced a properly narrow result - agentmemory separates
scopes and does not separate configurations within one, because its only symmetric second field is
ignored by search and its only other candidate cannot be written. A specific, checkable limitation of
an interface. Not a verdict on a product, and not a ranking.

Report: `research/PI_SURFACE_CLOSURE_GEN82.md`.

---

## Generation 81 — the boundary is written correctly and ignored at search

**status:** complete. `agentmemory_project_boundary_gen81`. Base `a8b55e4`, commit `ee084ae`, full
suite **825 passed** (817 baseline + 8 new). AgentMemory only, minimal two-project fixture, one fixed
`agentId`, **no alternative isolation schemes tried** - as specified.

**the answer: SEARCH_TIME_IGNORING, not write-time loss.**

- **`project` survives ingestion perfectly.** Every stored record carries a `project` field with the
  right value (`gen81-project-a`, `gen81-project-b`).
- **Search ignores it completely.** Querying project A returns **both** markers; querying project B
  returns **both** markers - the same two rows either way.

```
QUERY gen81-project-a -> "Alpha marker: …project A is 111 units."
                         "Beta marker:  …project B is 222 units."
QUERY gen81-project-b -> "Alpha marker: …project A is 111 units."
                         "Beta marker:  …project B is 222 units."
```

**a supporting detail worth having:** the search hits carry `obsId, score, sessionId, timestamp,
title, type` and **no `project` field at all**. The response is not merely unfiltered - it is opaque
to project. The stored rows have it; the search results never mention it.

So Gen80's `configuration_collapse` is fully explained, and it is a **retrieval-filter gap, not a
storage-model gap**: the data needed to filter is present and unused.

**a probe defect I caught, and I want it on the record.** The first pass reported
`NO_CROSSING_OBSERVED` - apparently clean isolation. I had assumed the response used `content` and
`sourceObservationIds`; it uses `title` and returns null ids, so my detector compared blank strings
and found no crossing **because it could see nothing at all**. The result looked like good news and
contradicted Gen80, which is what made it suspect. Fixed to detect crossing by marker text, plus an
explicit `UNDETERMINED_RESPONSE_OPAQUE` verdict so a future run that cannot attribute a hit says so
rather than reporting a boundary it cannot see; `attribution_possible` is now recorded and asserted.

That is the same failure this programme keeps catching - a clean number from a check that could not
fail - and it happened inside a probe written specifically to avoid it.

**what this does not establish:** that agentmemory cannot isolate configurations by any means. No
alternative scheme was tried, by instruction. It says nothing about scope isolation, which Gen78
measured working via `agentId`.

Report: `research/PI_PROJECT_BOUNDARY_GEN81.md`.

---

## Generation 80 — the first real capability difference on this axis

**status:** complete. `native_configuration_isolation_gen80`. Base `7af84f9`, commit `934833a`, full
suite **817 passed** (794 baseline + 23 new). One variable moved: the Gen79 configuration binding
layered on the **unchanged** Gen78 scope binding; scope identity, ingest policy and all other adapter
behaviour untouched.

**one qualifying case (`LQ03`), three repetitions, four engines:**

| engine | primitive | original Round-2 | configuration-bound |
|---|---|---|---|
| **perseus** | `category` | 3/3 collapse | **0/3 collapse, 3/3 clean** |
| **mem0** | `agent_id` | 3/3 collapse | **0/3 collapse, 3/3 clean** |
| **hindsight** | `tags` | 3/3 collapse | **0/3 collapse, 3/3 clean** |
| **agentmemory** | `project` | 3/3 collapse | **3/3 collapse, 0/3 clean** |

**This is the first axis in the whole Round-2 re-examination where the engines genuinely differ once
the harness is fair to all of them.** Temporal and scope both dissolved into configuration once the
adapters were corrected. This one does not.

**clean retrieval reported explicitly, as you required.** `returned_expected` and
`returned_prohibited` are recorded separately and both asserted, so an empty answer cannot pass as
isolation. The three isolating engines return `L001` and never `L003`. agentmemory returns
`L001, L002, L003, L004` in every repetition - **it is not failing to retrieve, it is retrieving
across the configuration boundary.**

**Gen13's prior evidence is CONFIRMED, not overturned.** I kept that note as evidence to be tested
rather than an expectation, exactly as you specified - and that mattered, because the structurally
identical caveat carried into Gen77 was **overturned** by Gen78, where `agentId` isolated perfectly.
The same class of caveat has now been wrong once and right once. Only running it distinguishes a real
limitation from a stale note.

**what this does not say:** that agentmemory cannot isolate configurations. Only that `project` - the
one candidate its API exposes alongside the agent already carrying scope - does not. Whether another
arrangement would work is a different question this generation did not ask.

Report: `research/PI_CONFIGURATION_ISOLATION_GEN80.md`.

---

## Generation 79 — all four can separate configurations without reusing the scope key

**status:** complete. `native_configuration_feasibility_gen79`. Base `61f5ac2`, commit `15e3455`,
full suite **794 passed** (769 baseline + 25 new). **No engines run**, as specified.

**the constraint you set shapes the whole answer.** The scope key may not be repurposed - reusing it
would make two configurations look like two scopes and the "isolation" would be relabelling, not
capability. That is **asserted in a test for every engine**, not merely described.

| engine | configuration primitive | write | query | scope key (untouched) |
|---|---|---|---|---|
| **perseus** | `category` | `write_gate {category}` | `recall {category}` | `workspace_hash` |
| **mem0** | `agent_id` | `add(agent_id=…)` | `search(filters={"agent_id": …})` | `user_id` |
| **hindsight** | `tags` | `retain(tags=[…])` | `recall(tags=[…], tags_match="all")` | `bank_id` |
| **agentmemory** | `project` | `/remember {project}` | `/smart-search {project}` | `agentId` |

Read from the surfaces: Perseus's MCP write gate takes `body_json, category, key, workspace_hash`
and `perseus_vault_recall` takes `category` **alongside** `workspace_hash` - two genuinely
independent axes; the frozen adapter pins `category` to a constant, so binding it changes one thing.
mem0's `_build_filters_and_metadata` treats `user_id`/`agent_id`/`run_id` as independent session
identifiers - Gen78 took `user_id`, `agent_id` is free. hindsight's `tags` are independent of
`bank_id`, and `recall` offers `tags_match` for exact-set semantics.

**No engine needed `NO_USABLE_CONFIGURATION_SURFACE`** - a real possible outcome that again did not
arise.

**the load-bearing caveat.** Gen13 measured that agentmemory's `smart-search` does **not** isolate by
`project`. That is a behaviour finding about a surface that exists - exactly the shape of the Gen77
caveat that **Gen78 then disproved**. So `project` is recorded feasible with the caveat attached to
the binding itself. **Recording it feasible is not a prediction**, and this is the second time in
three generations that distinction has mattered.

**25 tests, before any run:** distinct write and query coordinates per configuration; **no binding
touches the scope primitive**; each engine's configuration primitive differs from its Gen78 scope
primitive and its recorded `scope_primitive` matches that module, so independence is verified
against Gen78 rather than asserted in prose; a configuration token can never collide with a scope
token; stability across calls; and hashed tokens carrying no fixture wording.

**what this does not establish:** nothing about whether any engine separates configurations. Gen78's
scope bindings are untouched and `configuration_collapse` remains unmeasured under any binding. The
question can now be asked of all four without manufacturing symmetry.

Report: `research/PI_CONFIGURATION_FEASIBILITY_GEN79.md`.

---

## Generation 78 — every engine isolates scopes once it is actually asked

**status:** complete. `native_scope_isolation_gen78`. Base `14739f7`, commit `ec24b8f`, full suite
**769 passed** (746 baseline + 23 new). A configuration ablation, **not** a product ranking.
**Perseus not rerun** - its scope-bound cases were reused from Gen68.

**the result. Two genuinely cross-scope cases, three repetitions, six case-runs per engine:**

| engine | original Round-2 configuration | with its native scope binding |
|---|---|---|
| perseus | 0 of 6 collapse, 6 clean | reused, not rerun |
| **mem0** | **6 of 6 collapse** | **0 of 6** |
| **hindsight** | **6 of 6 collapse** | **0 of 6** |
| **agentmemory** | **6 of 6 collapse** | **0 of 6** |

**Every engine isolates scopes correctly when given its own primitive.** Total failure before,
absent after, all three engines, every repetition.

**the cleanliness is real and I checked rather than assumed it** - an empty answer also avoids
`scope_collapse`. Asserted in tests: each case returns the observation it asked for (`L003` forge,
`L006` anvil); the foreign scope's observation never appears; and the two scopes received
**different** bound identities within each run, so a clean result cannot come from both queries
hitting one partition. mem0's forge query returns `L001,L002,L003,L004,L005` - all forge - and its
anvil query returns `L006` alone.

**what this retracts: the reading of Gen68's scope row.** Perseus 6/9 versus 0/9 was a
**configuration** difference, not a capability difference - the second Gen68 headline to fall to the
same error as the temporal one, an adapter decision read as a fact about a product.

**agentmemory is the sharpest case.** Its frozen adapter records *"smart-search does not isolate by
project anyway"* - a true Gen13 measurement about `project`. Bound to `agentId` it isolates
perfectly. The note was right about the parameter it tested and wrong as a statement about the
product.

**what this does NOT establish:** not a ranking - all four now behave identically here, so there is
nothing to order. Nothing about same-scope configuration: **`LQ03` was deliberately excluded**
because Gen77 froze mappings for scope and not configuration, so `configuration_collapse` remains
untested under the new bindings. And Gen76's finding stands unchanged - the original configurations
do collapse scopes, which is what a user running them would experience.

**a runner defect of mine, caught and fixed before reporting.** The first mem0 run ingested the whole
timeline and charged `future_leakage` on the forge case - Gen70's over-ingestion imported by accident
into a run with nothing to do with it. Ingestion is now limited to the queried checkpoint's prefix,
asserted in the result file and in a test. Every figure above is post-fix.

Report: `research/PI_SCOPE_ISOLATION_GEN78.md`.

---

## Generation 77 — all three engines have a native scope primitive, and it is bindable

**status:** complete. `native_scope_adapter_feasibility_gen77`. Base `6ce073a`, commit `93c14e3`,
full suite **746 passed** (730 baseline + 16 new). **No engine compared, no isolation run** - exactly
as specified.

**read from installed signatures, not documentation:**

| engine | primitive | write | query | status |
|---|---|---|---|---|
| **mem0** 2.0.19 | `user_id` | `add(user_id=…)` | `search(filters={"user_id": …})` | supported |
| **hindsight** 0.9.2 | `bank_id` | `retain(bank_id=…)` | `recall(bank_id=…)` | supported |
| **agentmemory** 0.9.29 | `agentId` | `POST /remember {agentId}` | `POST /smart-search {agentId}` | supported |

mem0's `add` also offers `agent_id` and `run_id`; **`user_id` is chosen because the frozen Gen32
adapter already binds it to a constant**, so binding it per scope changes exactly one thing.
hindsight's `bank_id` is a **required positional on both calls** - the strongest symmetry available.

**no engine needed `NO_USABLE_SCOPE_SURFACE`.** That was a real possible outcome and I would have
recorded it; it did not arise.

**the agentmemory caveat travels with the binding.** The frozen adapter's *"smart-search does not
isolate by project anyway"* is a Gen13 **behaviour** finding about `project`, not an absent surface.
`agentId` is the candidate, and whether it isolates is the isolation run's question. Recording it
feasible is **not** a prediction that it will work.

**proved before any isolation run - 16 deterministic tests:** two scopes give distinct write AND
query coordinates for every engine; the same scope is stable across calls (a key that drifts between
write and query isolates nothing); write and query carry the same token, so symmetry is asserted
rather than described; hindsight and agentmemory bindings are run-scoped so repetitions cannot leak
scopes across runs; and the token is hashed, carrying no fixture wording into a store that might
match on it textually.

**frozen, and the originals untouched.** The three mappings are frozen before any run. The Round-2
adapters remain the record of what was actually tested, so Gen76's finding that those configurations
collapse scopes stands unchanged.

**what this does not establish:** nothing about whether any engine isolates. The question can now be
asked fairly of all four, which is what Gen78's smallest legitimate comparison needs.

Report: `research/PI_SCOPE_FEASIBILITY_GEN77.md`.

---

## Generation 76 — the scope ruler works; three of four engines were never asked

**status:** complete. `scope_reachability_audit_gen76`. Base `499768d`, commit `6b14c0f`, full suite
**730 passed** (720 baseline + 10 new). **No engine runs and no re-scoring**, as specified.

**the ruler is sound.** Both classes driven through the frozen scorer with synthetic answers and
controls:

| class | fires when violated | control stays clean |
|---|---|---|
| `scope_collapse` | **yes** | **yes** |
| `configuration_collapse` | **yes** | **yes** |

The fixture genuinely contains both violations - a prohibited observation in a different scope, and
one in the same scope with a different configuration. Worth checking: both sit in an `elif` chain
behind several other classes and could have been structurally silent.

**but scope was only ever asked of one engine.**

| adapter | what "scope" is | write | query | verdict |
|---|---|---|---|---|
| **perseus** | `workspace_hash = sha256(scope)` | yes | yes | **measured** |
| mem0 | metadata field; query filters a constant `user_id` | no | no | **NOT_DEMONSTRABLE** |
| hindsight | `bank_id` per repetition; scope only in a context string | no | no | **NOT_DEMONSTRABLE** |
| agentmemory | one agent, one project, for every scope | no | no | **NOT_DEMONSTRABLE** |

Quoted from the adapters' own contracts: mem0's *"scored_filter: constant user_id only"*;
agentmemory's *"never a project or agent per scope"* and *"smart-search does not isolate by project
anyway"*; hindsight's recall arguments are `bank_id`, `query`, `max_tokens` - no scope term.

**two true statements, kept apart and both reported.** For those three: the tested configuration
collapses scopes - true, and what a user of that configuration would experience; and the engine's
scope capability is not demonstrable - also true, since nothing in these runs bears on whether the
product can isolate when asked. Reporting only the first repeats the Gen73 error of reading an
adapter decision as a product fact; reporting only the second hides what we actually ran.

**what this qualifies: Gen68's scope row.** perseus 6/9 versus 0/9 for the rest is not a
scope-isolation comparison - **Perseus was the only engine asked.**

**the decision I am not taking.** Building adapters that bind each engine's namespacing concept per
scope would change the tested configuration for three engines, and whether that is faithful to each
product's intended use is a design question with its own provenance - Gen74's shape. Yours to
direct.

Report: `research/PI_SCOPE_AUDIT_GEN76.md`.

---

## Generation 75 — three clocks, not one score. The temporal line is closed.

**status:** complete. `temporal_semantics_closure_gen75`. Base `943cfad`, commit `a4510ba`, full
suite **720 passed** (709 baseline + 11 new). **No engine run, nothing re-scored.**

**the bounded architecture result, on three independent axes:**

| engine | transaction-time history | effective-time history | temporal query surface |
|---|---|---|---|
| **perseus** 2.23.2 | **kept** | **not demonstrable** | present; `as_of` holds |
| **hindsight** 0.9.2 | not kept | not kept | **present and fails** |
| **mem0** 2.0.19 | not kept | not kept | none |
| **agentmemory** 0.9.29 | not kept | not kept | none |

**`not_demonstrable` is a first-class value**, distinct from `not_kept` and asserted so in a test.
Perseus's effective-time behaviour was never tested and **cannot** be through this interface: the
store sets `valid_from` to the write instant and the write path exposes no validity flag (Gen74,
measured). Scoring that as a failure would be as wrong as scoring it a pass.

**a failing surface is worse than no surface.** Hindsight accepts `query_timestamp` and ignores it,
15/15. mem0 and agentmemory offer nothing and are honest about it. A caller can work around a
missing feature; it cannot work around one that silently does not do what it says.

**every Perseus effective-time claim is listed with a status, not edited away:**

| gen | claim | status |
|---|---|---|
| 71 | `valid_at` is effective-time capable | **RETRACTED** |
| 72 | Perseus makes backfilled facts unreachable | **RETRACTED** |
| 70 | Perseus never leaked, 0 of 15 | **QUALIFIED** - an empty snapshot cannot leak |
| 68 | Perseus fails late-arriving history | **REATTRIBUTED** - harness clock, and a store with no validity coordinate |

**what survives, each with its evidence:** Perseus preserves past belief 6/6 on genuine
transaction-time questions; Hindsight's `query_timestamp` is accepted and ignored 15/15 on its own
path; mem0 and agentmemory expose no temporal surface; **no engine tested keeps both clocks**,
unchanged by the retractions since none gained a capability.

**scope:** four named builds behind four adapters, tested Round-2 configurations, `longitudinal-v1`
and `backfill-v1`, three repetitions, `observational_memory` excluded since Gen69. Not a statement
about the products in general and not a ranking. The axes must not be collapsed into one score -
enforced in the contract and in a test.

**what I think the programme should carry forward, and it is not the engine table.** The durable
result is methodological: **a benchmark must prove its failure classes can fire before it reports
them as zero.** Gen68 found two that could not, Gen69 repaired them, Gen73 found a third defect that
made an entire axis untestable - and every one was caught by asking what the harness actually did
rather than what it was meant to do.

Report: `research/PI_TEMPORAL_CLOSURE_GEN75.md`.

---

## Generation 74 — the query was repairable; the store has no clock to repair it against

**status:** complete. `perseus_effective_time_adapter_gen74`. Base `5817889`, commit `b1351b5`, full
suite **709 passed** (702 baseline + 7 new).

**the repair, exactly as specified.** `perseus-adapter-v2` maps `valid_at` from the case's
`effective_time` straight to unix milliseconds; `as_of` still maps through ingestion order, because
it asks a genuine knowledge-time question. The frozen Gen29 adapter is **not** imported, edited or
reinterpreted - asserted in a test. Old results are retained as invalid-for-effective-time evidence,
not restated.

**proved before any engine call, as you required.** Seven deterministic tests show the two mappings
produce different instants on every `valid_at` case in **both** fixtures, and that current-state
cases still carry no temporal argument.

**Perseus only, three repetitions, old vs new:**

| case | old returned | new returned |
|---|---|---|
| BQ03 | B001 | B001, B002 |
| BQ04 | B001 | — |
| BQ05 | B002 | B002 |
| BQ06 | B002 | — |
| BQ07/08/10/11 | — | — |

**Clean `valid_at` cases: 0 before, 0 after.** The behaviour changed; the outcome did not. Under
either adapter **no backfilled observation is ever returned** - B004, B006, B008, B011 never appear.

**the reason is underneath the adapter, and I measured it rather than inferring it.** Two entities
written to perseus-vault 2.23.2, the second declaring `effective_time` of 2020-01-01 in its body:

    key=a created=1788608258156 valid_from=1788608258156 equal=True
    key=b created=1788608259354 valid_from=1788608259354 equal=True

`valid_from_unix_ms` is the write instant in both cases, the declared effective time is ignored, and
`perseus-vault write --help` exposes **no validity flag at all**. So `valid_at` filters on a
coordinate equal to write time, and a fact backfilled on 11 March can never match a question about 9
March however the query is phrased.

**what this establishes: Perseus 2.23.2's temporal surface, through this interface, is
TRANSACTION-TIME ONLY.** Both operations range over write-derived instants. This strengthens the
Gen73 retraction rather than reversing it - Gen71 called `valid_at` effective-time capable, Gen73
said untested, Gen74 says **untestable on this build**, because the capability has no storage behind
it.

It also explains the original anomaly cleanly. Perseus preserves belief history because belief
history *is* a transaction-time question, and transaction time is the clock it keeps. Its apparent
late-arrival weakness was never retrieval: a fact learned late has no way to be filed under when it
happened.

**what I did not do:** modify the frozen adapter; restate old results; or run the other three
engines - Gen74 was Perseus-only by instruction, and this storage finding does not transfer, since
mem0 and agentmemory have no temporal surface and Hindsight's is its own.

**what would settle it beyond this build:** a Perseus release whose write path accepts a validity
coordinate, or its documentation defining `valid_at` over transaction time. Neither is something a
harness can decide, and I would not guess at it.

Report: `research/PI_ADAPTER_REPAIR_GEN74.md`.

---

## Generation 73 — the fixture built to confirm the mirror broke half of it

**status:** complete, and it is a RETRACTION. `backfill_multi_depth_gen73`. Base `d55941c`, commit
`c4e868b`, full suite **702 passed** (692 baseline + 10 new).

**the fixture you asked for exists.** `backfill-v1`, hash `784dfc56`: 12 observations, 7
checkpoints, 13 cases. Four independent late-arriving facts at three depths - 2, 9, 9 and 18 days
behind arrival - across both fates (`historical_only`, `later_corrected`). Two independent
superseded beliefs. Queries copy `longitudinal-v1`'s terse form, because a full-sentence question is
a different retrieval task and comparability requires parity. `longitudinal-v1` untouched.

**but the answer is a defect in MY harness, not a fact about an engine.** The Perseus adapter
derives BOTH temporal arguments from one call:

    instant = time_base.store_instant(case.event_time.isoformat())
    arguments["as_of_unix_ms" if op == "recall_hybrid_as_of" else "valid_at"] = instant

`store_instant` bisects **ingestion** times and returns a **store write instant** - a
transaction-time coordinate. So `valid_at`, the operation meant to ask *what was true on this date*,
is asked *what did the store contain at the write instant nearest this date*. Where the two clocks
coincide the substitution is invisible. For a backfill they diverge by design, and the resolved
instant lands **before the backfilled fact was written**:

| fixture | obs | lag | valid_at resolves | written at |
|---|---|---|---|---|
| backfill-v1 | B004 | 2d | 1150 | 1300 |
| backfill-v1 | B006 | 9d | 1150 | 1500 |
| backfill-v1 | B008 | 18d | 999 | 1700 |
| backfill-v1 | B011 | 9d | 1250 | 2000 |
| **longitudinal-v1** | **L011** | **9d** | **1850** | **2000** |

The last row is the one that matters: `L011` is the single backfilled fact in the ORIGINAL fixture,
which every late-arrival conclusion since Gen68 rests on.

**I am retracting, precisely:**
- Gen72 "Perseus makes backfilled event-time facts unreachable" - **not established.** Perseus was
  never asked for the fact at its event time; it was asked what its store held before that fact
  existed, and correctly returned nothing.
- Gen71 `recall_hybrid_valid_at` = `effective_time_capable` - **not established.** It was fed a
  transaction-time instant, so effective-time capability was never exercised.

**what still stands, and I checked each:**
- **Perseus retains superseded belief**, 6/6. Those are `as_of` cases - genuine transaction-time
  questions, correctly mapped. The other engines' `belief_truth_confusion` is likewise untouched.
- **Hindsight's `query_timestamp` accepts a timestamp and leaks anyway, 15/15** - Hindsight's own
  parameter on its own path, no Perseus adapter involved.
- **mem0 and agentmemory expose no temporal surface.** Unaffected.
- Gen70 future-leakage for the three engines without a working filter: unaffected. Perseus's "0 of
  15 temporal leaks" now carries a caveat - an empty or pre-write snapshot cannot leak, so it is not
  evidence of a working filter.

**So the mirror's Hindsight arm survives and its Perseus arm does not.**

**what I did NOT do.** I did not modify the frozen adapter - its hash is in every committed Round-2
result and editing it would silently invalidate them. The repair is a new adapter revision passing
`effective_time` to `valid_at`, run as its own generation with its own provenance. I also did not
run the other three engines on `backfill-v1`: with one arm known-broken, a four-engine table invites
exactly the misreading this generation exists to prevent. **Both are yours to direct.**

**how it surfaced:** a trial run scored Perseus 0 of 13 and I did not report it. Plain recall
returned three items per case, so retrieval plainly worked - which made "every temporal operation
returns nothing" a harness hypothesis rather than an engine one. The adapter confirmed it in six
lines.

Report: `research/PI_BACKFILL_GEN73.md`.

---

## Generation 72 — the split is storage semantics, and here is the mechanism

**status:** complete. `correction_late_arrival_semantics_gen72`. Base `cfef91e`, commit `fb00369`,
full suite **692 passed** (680 baseline + 12 new). **No engine run** - reads the committed Gen68
per-case records only.

**your question answered: distinct storage semantics, not retrieval behaviour.** Perseus and
Hindsight are opposites on both axes simultaneously.

| engine | belief confusions | late arrival | reading |
|---|---|---|---|
| **perseus** | **0** | **6 of 6 ABSENT** | keeps belief history; an out-of-order fact is not addressable at its own event time |
| **hindsight** | 6 | **6 of 6 clean** | files by event time so backfill lands; the superseded version is not addressable |
| mem0 | 6 | 3 misfiled | neither |
| agentmemory | 6 | 3 misfiled | neither |

**the decisive detail is the KIND of Perseus failure.** Its late-arriving fact is not misfiled - it
is **unreachable**, 6 times out of 6, where mem0 and agentmemory return the wrong version
(`misplaced`). A retrieval-ranking difference produces wrong ordering; it does not make a stored
fact disappear. Perseus appears to place observations on a knowledge timeline, and something
ingested tenth but dated fifth has nowhere to live on it. Hindsight is the mirror - event clock kept,
belief state not.

**the correction cluster settles a second question.** Every engine except Perseus shows belief
confusion in **both** the backdated-correction cluster and the aligned-time invalidation cluster. So
their inability to recover a superseded belief is **not** about backdating - the prior version is
simply not addressable once revised. Perseus instead shows `correction_not_applied` 6 times: it
retains both versions and sometimes serves the pre-correction value. A resolution-order fault, not a
data-loss fault, and a different fix.

**no engine on this fixture keeps both clocks.** Asserted in a test so a later generation cannot
quietly claim otherwise.

**three revision shapes, deliberately different:** a correction with event time later than effective
time (L005/L001); an invalidation chain with aligned times (L012/L013/L014); and a fact ingested
tenth but dated fifth, marked historical-only (L011). Each interrogates a different part of the
storage model, which is why they are reported separately.

**scope:** one fixture, one correction, one invalidation chain, one backfilled fact, three
repetitions. This names a pattern and gives it a mechanism; it does not prove a storage design.
Confirming it needs engine documentation or a fixture with several independent backfills at
different depths - **that is the obvious Gen73 if you want it.**

The mechanisms must not be averaged into a temporal-accuracy score; averaging is exactly what would
have hidden the mirror, and the contract and a test both say so.

Report: `research/PI_CORRECTION_SEMANTICS_GEN72.md`.

---

## Generation 71 — capability versus routing, and why the pooled column was wrong

**status:** complete. `temporal_capability_routing_gen71`. Base `0b6db1e`, commit `54ec8e0`, full
suite **680 passed** (668 baseline + 12 new). **No engine run** - reads the committed Gen68 and
Gen70 per-case records only.

**the cut that decides it, and I think it is the real finding.** Leakage on a **temporal** question
is unambiguously wrong. Leakage on a **current-state** question is not: asking what is true NOW of a
store fed the whole timeline should return the later facts.

| engine | leaks on TEMPORAL questions | leaks on current questions |
|---|---|---|
| **perseus** | **0 / 15** | 21 / 24 |
| mem0 | 15 / 15 | 21 / 24 |
| hindsight | 15 / 15 | 24 / 24 |
| agentmemory | 15 / 15 | 24 / 24 |

**Perseus does not leak once where leaking is a defect. The other three leak every one.** The
current column is near-identical across all four and is not a defect - which is exactly why the
pooled totals had to go.

**per-operation classification:**

| engine | operation | classification | leaked |
|---|---|---|---|
| perseus | `recall_hybrid_valid_at` | **effective_time_capable** | 0 / 12 |
| perseus | `recall_hybrid_as_of` | **knowledge_time_capable** | 0 / 3 |
| perseus | `recall_hybrid` | current_only | 21 / 24 |
| hindsight | `recall_query_timestamp` | **temporal_surface_but_failed** | 15 / 15 |
| hindsight | `recall_current` | current_only | 24 / 24 |
| mem0 | `search_current_state` | current_only | 36 / 39 |
| agentmemory | `smart_search_current_state` | current_only | 39 / 39 |

**Three architectures needing three different fixes.** Perseus holds both clocks and its adapter
routes temporal questions to them - **zero routing gaps**, nothing to fix on this axis. Hindsight
has a temporal surface that does not work, which is the worst of the three states because a caller
cannot distinguish it from a working filter without this probe; it needs a fixed filter, not better
routing. mem0 and agentmemory have no temporal surface, so their 15 gaps are recorded as "no
temporal surface" rather than "routing gap" - there is no working operation being missed.

An operation the probe never exercised is `undetermined`, not passing. Gen68's lesson about
unmeasured zeros is enforced in code here.

**`unknown_hallucination`: CLOSED_NOT_APPLICABLE at the retrieval-engine layer**, as you directed,
and reserved for a reader or full-product evaluation rather than carried forward as a permanent
blank column.

**what this establishes:** "does engine X leak the future" is the wrong question. The answerable
ones are *does it have a clock, does that clock work when used, and does anything route to it?*
Perseus: yes/yes/yes. Hindsight: yes/**no**/yes. mem0 and agentmemory: no, and the rest does not
apply.

Report: `research/PI_TEMPORAL_CAPABILITY_GEN71.md`.

---

## Generation 70 — who actually leaks the future, and whose temporal filter is real

**status:** complete. `temporal_blind_spot_run_gen70`. Base `8256983`, commit `4721aca`, full suite
**668 passed** (648 baseline + 20 new). Only the two newly reachable probes were run. The 20-case
suite was **not** re-run, every engine kept its frozen config, adapter and 3-repetition policy, and
`observational_memory` stays excluded.

**probe 1, future leakage.** 39 cases per engine (13 × 3), ingesting the full timeline through CP16
and querying as of CP01/CP04/CP05/CP08/CP10/CP11.

| engine | leaked |
|---|---|
| perseus | **21 / 39** |
| mem0 | 36 / 39 |
| agentmemory | 39 / 39 |
| hindsight | 39 / 39 |

**the totals are the least interesting part. Split by the native operation the adapter chose:**

| engine | operation | cases | leaked |
|---|---|---|---|
| perseus | `recall_hybrid` (no temporal filter) | 24 | 21 |
| perseus | `recall_hybrid_valid_at` | 12 | **0** |
| perseus | `recall_hybrid_as_of` | 3 | **0** |
| hindsight | `recall_current` | 24 | 24 |
| hindsight | `recall_query_timestamp` | 15 | **15** |
| mem0 | `search_current_state` | 39 | 36 |
| agentmemory | `smart_search_current_state` | 39 | 39 |

**Perseus's temporal operations hold perfectly - 15 of 15 clean.** Every Perseus leak came from the
plain hybrid recall used where the adapter does not treat the question as temporal.

**Hindsight's temporal operation does not work - 15 of 15 leaked.** It accepts `query_timestamp`,
the adapter passes it, and the engine returns observations from after that timestamp anyway. That is
a different and worse failure than having no temporal surface: a filter that is accepted and
ignored.

**probe 2, unknown hallucination: NOT_APPLICABLE for all four**, and recorded as that rather than as
a clean zero. Every frozen adapter is retrieval-only (`search`/`recall`); it returns evidence and
never asserts, so there is no claim to grade. Scoring four engines as "never hallucinates" when none
of them answers would repeat exactly the Gen68 mistake. Measuring it needs an answer surface or a
reader layer - a change of architecture, not a probe.

**what this establishes:** a temporal filter you can pass is not a temporal filter that works. Two
engines advertise one; one holds under a store containing the future and the other silently does
not. That was invisible until the harness could over-ingest.

**what it does not:** a ranking. 13 questions per repetition on one fixture, and the totals column
is dominated by adapter operation routing. **The per-operation table is the result.**

**one operational note.** Hindsight's pinned embedding snapshot had been purged from `/private/tmp`
and its first three runs died on a tokenizer error. Restored at **the same revision**
`614241f622f53c4eeff9890bdc4f31cfecc418b3` before running - a restoration, not a config change, and
recorded in the result file.

Report: `research/PI_TEMPORAL_BLIND_SPOT_GEN70.md`.

---

## Generation 69 — both silent failure classes can now fire

**status:** complete. `temporal_reachability_repair_gen69`. Base `a16f5b9`, commit `1ad3b71`, full
suite **648 passed** (639 baseline + 9 new). **No engine run, no comparison made** - exactly as you
specified.

**neither defect was in the scorer, and that determined the repair.** `longitudinal-v1` and
`longitudinal-scorer-v1` are frozen and their sha256 appears in every committed Round-2 result, so
changing them would invalidate the runs Gen68 read. `fixture_sha256` is still `a5c67e7b2677dff5...`,
matching every result on disk.

**`future_leakage` was a RUN-PLAN defect.** The runner only ever ingested the visible prefix, so a
future observation was never in the store to be returned; the scorer has always flagged one.
Repaired by `future-leakage-probe-v1`: **ingest through CP16, then query as of CP01, CP04, CP05,
CP08, CP10, CP11.** The store holds the whole timeline while the question is about an earlier
moment, so a system that cannot filter by knowledge time hands back what it should not yet know.

**`unknown_hallucination` was a MISSING CALL.** `score_answer_claim` exists and works; no runner
called it, so the negative_unknown case was graded on retrieval alone. Repaired by making the call,
with the rule it needs: where the correct answer is "unknown", only a refusal is supported. Cases
that do have expected evidence are untouched and stay with the retrieval scorer.

**proved reachable, each with a control:**

| | fires when it should | silent when it should be |
|---|---|---|
| `future_leakage` | **6 of 6** over-ingested cases | prefix-only control **clean** |
| `unknown_hallucination` | confident assertion | "unknown", "no record", empty, no answer at all |

A repair that fires on everything is as useless as one that fires on nothing, so each has its
negative case. `scripts/run_gen69_reachability.py` exits non-zero if either fails to fire.

**`observational_memory_gen26` is EXCLUDED from point-in-time comparison**, decided now as you
asked. Its run ended `complete_ingestion_lifecycle_context_unavailable` - it ingested the timeline
but never produced retrieval results, so there are **no per-case records to recover** from the
artifacts. Nothing was reconstructed and nothing re-run to fill the table.

**what this does NOT establish.** No engine leaks and no engine hallucinates as far as this
generation knows - **no engine has been run under the repaired plan.** The proofs are synthetic
responses driven through the frozen scorer to show the path exists. What the engines actually do is
Gen70's question, and it is now askable.

Report: `research/PI_TEMPORAL_REACHABILITY_GEN69.md`.

---

## Generation 68 — the temporal ruler works, and it has two blind spots

**status:** complete. `round2_point_in_time_pilot_gen68`. Base `e55932b`, commit `bbd2426`, full
suite **639 passed** (631 baseline + 8 new). **No engine run, nothing re-scored, no completed system
repeated** - reads the four committed Round-2 longitudinal runs only.

**the ruler is sound where it matters.** `longitudinal-v1` already keeps the clocks apart:
event/effective time is world validity, ingestion time/order is knowledge visibility. Corrections
carry an event time later than their effective time (L005 corrects a Jan-10 measurement on Jan-20)
and late-arriving history is ingested out of order on purpose (L011). Twenty cases, eight kinds of
truth, and **12 of 16 failure classes actually fired**.

**two blind spots, both structural, both previously reported as zeros.**
1. **`future_leakage` CANNOT FIRE.** The harness ingests only the visible prefix at each checkpoint,
   so a future observation is not in the store to be returned. Every engine's zero is a property of
   the experiment, not a finding. Measuring it needs ingestion beyond the checkpoint followed by an
   as-of question.
2. **`unknown_hallucination` is never evaluated.** It comes from `score_answer_claim`, which no
   runner calls; the single negative_unknown case is graded on retrieval alone. Verified by walking
   the AST of every runner and provider, not by grep.

`procedure_recommendation_missing` and `unmapped_provenance` are reachable and simply never fired -
clean results, not blind spots.

**a provenance gap that blocks broad comparison.** `observational_memory_gen26` has a summary and
**no per-case records at all**. It cannot be scored point-in-time; its absence from any table is
silence, not a clean sheet. It needs per-case records or an explicit exclusion before cross-engine
work.

**what reading by kind of truth reveals, which the pooled count hid.** Clean cases, 3 repetitions:

| kind | clock | perseus | mem0 | hindsight | agentmemory |
|---|---|---|---|---|---|
| current_truth | now | 6/21 | 6/21 | 6/21 | 9/21 |
| scope_truth | now | **6/9** | 0/9 | 0/9 | 0/9 |
| recommended_procedure | now | 0/3 | 0/3 | 0/3 | 0/3 |
| negative_unknown | now | 0/3 | 0/3 | 0/3 | 0/3 |
| as_of_event_truth | event | 3/9 | 3/9 | **6/9** | 3/9 |
| corrected_historical_truth | event | 0/6 | 0/6 | 0/6 | **3/6** |
| historical_belief | knowledge | **6/6** | 0/6 | 0/6 | 0/6 |
| late_arriving_history | knowledge | 0/3 | **3/3** | **3/3** | **3/3** |

**Perseus is the only engine that can say what was believed at a past moment** - 6/6 where the
others are 0/6 with `belief_truth_confusion`, answering with what is true now instead of what was
thought then. It is also the only one that holds scope apart, and the only one that fails
late-arriving history. Nobody handles corrected history, nobody adopts the recommended procedure,
and every engine returns evidence for a question whose answer should be "unknown".

**two bugs of mine, found and fixed before reporting:** an inner loop reused the engine-name
variable and renamed engines after failure classes; and counting lifecycle keys marked every class
observed, because the totals dict lists all sixteen with zeros. The second would have destroyed the
reachability audit - it briefly reported 16 of 16 observed.

**my recommendation for Gen69:** do not report `future_leakage` or `unknown_hallucination` as
results until the harness can produce them, and decide `observational_memory` - per-case records or
explicit exclusion - before any broad cross-engine temporal comparison.

Report: `research/PI_POINT_IN_TIME_GEN68.md`.

---

## Generation 67 — the candidate-blind gate branch is closed

**status:** complete. `gate_branch_closure_gen67`. Base `7312d93`, commit `71ef2b0`, full suite
**631 passed** (623 baseline + 8 new). **No model, no GPU, no new critic** - reads the committed
Gen60-66 outcomes only.

**the conclusion, recorded.** For this pinned model and generator configuration, **candidate-blind
model-generated tests are reviewer evidence, not an unattended correctness gate.**

**the whole arc, unsafe-bank column: 4, 4, (0 by destruction), 4, 4.**

| | change | unsafe | removals | precision | retention | caught |
|---|---|---|---|---|---|---|
| Gen60 | unchanged generator, repaired corpus | 4/8 | - | - | - | 12/12 |
| Gen61 | quote the requirement | 4/8 | 0/188 | - | 1.000 | 12/12 |
| Gen62 | delete if not entailed | 0/7* | 158/188 | 0.101 | 0.000-0.333 | 18/21 |
| Gen63 | screen repaired | Gen62 -> UNEVALUABLE | | | | |
| Gen64 | delete only with a named condition | 4/8 | 15/188 | 0.267 | 0.821-0.964 | 12/12 |
| Gen66 | ...and show it the repository | 4/8 | 27/188 | 0.222 | 0.607-1.000 | 12/12 |

\* zero only because the banks were emptied.

Detection held at **12/12** in every condition that produced a usable bank.

**why it closes rather than continues.** Gen66 removed the explanation we had for the first three
failures. "The checker only sees a sentence and a test" was a reasonable account; we handed it the
reference repository, verified candidate-blind with zero leaks, and nothing moved. `pathsafe` kept
**all seven** of its false accusations with the code in front of it. The hypothesis space for this
architecture is exhausted, and further prompt, filter or context tuning on candidate-blind checking
is closed.

**recorded explicitly, as you directed:** a checker permitted to inspect the candidate is a
**different, non-independent architecture** - not the next iteration. A checker that reads the
implementation is on its way to agreeing with it, which is the Gen49 self-modified-test failure this
programme exists to detect. If it is ever pursued it needs its own question, its own independence
analysis and its own name, and must not be reported as a continuation. ARCHITECTURE.md carries both
the closure and that distinction.

**what the programme keeps.** A corpus where right and wrong answers coexist with every label
measured (`evidence-generation-gen59-v1`); a screen that cannot be gamed by deleting the evidence
(`gen63-retention-guardrail-v1`); a report that refuses to compress gate suitability into a verdict
word (`gate-suitability-report-v1`); four negative results with a stated mechanism; and one
methodological correction made against my own earlier report and fixed in code.

**scope, unchanged and bounded:** one pinned model, one generator contract, eight tasks, one run per
condition.

**I am ready to return the bake-off to the broader memory-system questions whenever you name the
next one.**

Report: `research/PI_GATE_BRANCH_CLOSED_GEN67.md`.

---

## Generation 66 — showing the checker the code did not help either

**status:** complete. `candidate_blind_repo_context_gen66`. Base `99042ab`, commit `badd92d`, full
suite **623 passed** (613 baseline + 10 new). Local GPU: 188 critic calls, 198.3 s. Opened as a new
experimental family, as you specified - not a continuation of Gen61-64.

**the boundary, and it was verified before the first call.** Permitted: the reference repository as
shipped and its visible tests. Forbidden: the candidate under test, any diff, the hidden evaluator,
any outcome, the known-wrong labels. The repo shown is the pre-work state, identical for every
candidate, so the critic learns what the code IS and cannot learn what the candidate DID. Isolation
preflight on the assembled prompt: **zero evaluator tokens, zero candidate lines, all eight tasks.**
Everything else is Gen64 unchanged; the verdict reader is imported from Gen64 and a test asserts it
is literally the same function object, so exactly one variable moved.

**your primary question, answered: no. UNSAFE_AS_GATE is 4 of 8 - the same four tasks, for the
fourth time:** culvert, ledger, pathsafe, tally.

| | Gen61 | Gen64 text-only | Gen66 with the code |
|---|---|---|---|
| removals | 0 | 15/188 | 27/188 |
| removal precision | - | 0.267 | **0.222** |
| known-false removed | 0/16 | 4/16 | **6/16** |
| valid removed | 0/172 | 11/172 | **21/172** |
| retention (worst) | 1.000 | 0.821 | **0.607** |
| unsafe banks | 4/8 | 4/8 | **4/8** |
| detection, shared population | 12/12 | 12/12 | **12/12** |

Nothing hollowed, detection intact, and it did **not** learn to agree with the candidate - it never
saw one. Recall rose slightly, precision fell slightly, outcome unchanged.

**the crux is pathsafe.** It holds seven of the sixteen false accusations. With the repository in
front of it the critic removed **none** of them - every one KEEP. Tests demanding a Windows
drive-letter path be rejected still read as direct quotations of "absolute paths must raise
ValueError", and seeing POSIX-style depot-name handling did not dislodge that. Meanwhile on culvert
it removed 11, six genuinely false and five sound, including `to_steps(0) == 0`. More context made
it readier to reason about specific values, and that cut both ways at once.

**why this result is stronger than the previous three.** It removes the handicap we believed was
causing the failure. Text-only was a reasonable explanation for Gen61/62/64; it is no longer
available. Four interventions, one of which changed the information boundary, and the rate has not
moved once.

**my recommendation: stop pursuing automated gating for this configuration.** That was your own
stated stopping condition for this branch and the measurement met it.

**what this does not establish.** The repo shown is the pre-work state. A checker seeing the
post-change code would have more to work with and would be precisely the failure this design exists
to avoid. So this is not evidence that no context could work - it is evidence that CANDIDATE-BLIND
context does not, and candidate-blindness is what makes the evidence independent at all.

Report: `research/PI_REPO_CONTEXT_GEN66.md`.

---

## Generation 65 — the gate question is closed: useful evidence, not an unattended gate

**status:** complete. `gate_question_synthesis_gen65`. Base `aeb6764`, commit `fd5359d`, full suite
**613 passed** (605 baseline + 8 new). **No model, no GPU, no new filter, no re-run** - reads the
committed Gen60-64 outcomes only. Every figure is derived from a results file rather than retyped.

**the answer, recorded.** For this pinned model and generator configuration, model-written tests are
**useful as reviewer evidence and not demonstrated safe for unattended gating.** Supported use:
surface suspicious cases for a human. Unsupported use: automatically decide correctness.

**the decisive arc, in the unsafe-bank column: 4, 4, (0 by destruction), 4.**
- Gen60 unchanged generator on the repaired corpus: 4 of 8 unsafe, 12/12 caught.
- Gen61 provenance: no effect - the false accusations already quoted correctly, so the filter
  deleted 0 of 223.
- Gen62 entailment: 158 of 188 removed at precision 0.101; every bank "safe" because almost none
  was left; re-scored UNEVALUABLE under Gen63's guardrail.
- Gen64 justified deletion: 15 removals at precision 0.267, retention 0.821-0.964, detection
  restored - and 4 of 8 unsafe again, the same four tasks.

**why all three failed, stated as a mechanism.** An overreaching test and a soundly-inferring test
are indistinguishable from the information the checker gets. Gen64 deleted `position_mm(0) == 0` as
unsupported and kept all six pathsafe false accusations, because the false ones read as direct
quotations of the sentence. Separating them needs the repository, which removes the independence
that makes a generated test evidence at all.

**PASSED is retired for this question, as you directed.** `gate-suitability-report-v1` reports the
unsafe bank rate, the retention range, and detection losses named individually, and reaches **no
verdict** - `gate_suitable` is explicitly null and the module applies no threshold. The old screen
still exists and still runs; its output is recorded as secondary. ARCHITECTURE.md carries the
closure.

**a correction to my Gen62 report, which I am flagging rather than quietly fixing.** I told you Gen62
lost three previously-caught wrongs. Gen61 did flag all three - but in `culvert` and `tally`, banks
Gen61 had already marked UNSAFE_AS_GATE, whose verdicts carry no weight under our own rule.
Restricted to tasks both runs actually scored, **Gen62's detection losses were zero.** The Gen62
conclusion is unaffected - it was condemned by its 0.101 removal precision - but I credited an
unusable bank with a catch. Cross-run detection comparisons are now restricted to the shared scored
population in code, with a test, so it cannot recur.

**scope, stated plainly.** One pinned model, one generator contract, eight tasks, one run per
condition. A bounded result about a configuration, not a general claim about generated tests.

**the branch you named is not opened here.** A repository-informed checker changes the checker's
information boundary and needs its own independence analysis; it belongs in a new experimental
branch whenever you want to start one.

Report: `research/PI_GATE_QUESTION_GEN65.md`.

---

## Generation 64 — making the critic justify itself stopped the damage and fixed nothing

**status:** complete. `justified_deletion_critic_gen64`. Base `275a72b`, commit `42257eb`, full
suite **605 passed** (593 baseline + 12 new). Local GPU: 188 critic calls, 101.1 s.

**the change you named, and only that.** A deletion is honoured only when the critic NAMES the
specific extra condition the quoted sentence does not require. Vague restatements, missing EXTRA
lines, too-short answers and unreadable replies all KEEP the test. Same pinned model, same frozen
Gen61 banks, one stateless call per test, deletion only, Gen63's guardrail in force.

**the destruction is gone.** 15 removals instead of 158. Retention 0.821 to 0.964, nothing hollowed.
Detection restored to 12 of 12.

**and your primary metric did not move. UNSAFE_AS_GATE is 4 of 8 - not merely the same number as
Gen61 but the same four tasks:** culvert, ledger, pathsafe, tally. On the measure we care about,
Gen64 is indistinguishable from running no critic at all.

| | Gen61 | Gen62 | Gen64 |
|---|---|---|---|
| removed | 0 | 158/188 | 15/188 |
| removal precision | n/a | 0.101 | 0.267 |
| known-false removed | 0/16 | 16/16 | 4/16 |
| valid removed | 0/172 | 142/172 | 11/172 |
| UNSAFE_AS_GATE | 4/8 | 0/8 (hollow) | 4/8 |
| verdict under guardrail | PASSED | UNEVALUABLE | PASSED |

**why, from the justifications themselves.** It deletes tests asserting a value the sentence does not
literally print - `position_mm(0) == 0` removed because the sentence "only specifies the mapping for
80 steps"; an empty-queue error removed because the sentence "only specifies" ordering; a
return-is-a-string check removed as unstated. It KEEPS the genuinely false ones, because they are
phrased as direct readings: all six surviving pathsafe false accusations say "an absolute path must
raise ValueError", which is what the sentence says, applied to cases it never contemplated.

**the two error classes are not separable from what the critic can see.** A test that overreaches to
a Windows drive letter and a test that correctly infers 0 -> 0 look identical given one sentence and
one test. Telling them apart needs the repository - and giving the checker the repository is how a
checker starts agreeing with the implementation it is meant to check.

**what the arc now establishes.** Three attempts, no movement: Gen61 provenance had no effect because
the false accusations already had provenance; Gen62 entailment removed everything; Gen64 justified
deletion removes almost nothing, and the wrong almost-nothing. The false accusations are not a
formatting, sourcing or strictness problem. They come from the model reasoning past the text it was
given, and every filter so far sees only that same text.

**my recommendation.** The reviewer's-aid conclusion is now the supported one, and I would write it
up as the programme's answer rather than run a fifth filter. If you want to keep going on the gate
question, the untested variable is the checker's INFORMATION, not its instructions - a checker given
the repository could separate the two classes, at the cost of the independence that makes generated
tests worth having. That is a design decision for you, not a prompt change.

Report: `research/PI_JUSTIFIED_CRITIC_GEN64.md`.

---

## Generation 63 — the screen now notices when a filter deletes the evidence

**status:** complete. `retention_guardrail_screen_correction_gen63`. Base `ccd35ce`, commit
`4bb4b5f`, full suite **593 passed** (582 baseline + 11 new). **No model, no GPU, no regeneration,
no filter change, no candidate re-run** - exactly the retrospective screen correction you specified.

**the rule, predeclared.** `gen63-retention-guardrail-v1` adds two conditions, applied BEFORE the
reference-validity check so a hollowed bank is never labelled REFERENCE_VALID on its way out:
retention of at least **50%** of a bank's original distinct tests, and liveness - **no bank may be
emptied**, whatever the ratio says. Retention is a precondition for admissibility, not another
score; sensitivity and specificity are then read only from banks that still exist.

**the corrected verdicts.** Gen60 PASSED -> PASSED. Gen61 PASSED -> PASSED. **Gen62 PASSED ->
UNEVALUABLE**, with all eight banks discarded as hollowed, so no task carries an admissible bank and
coverage cannot be met.

Retention per Gen62 bank: valve 0.333, ledger 0.292, tally 0.250, pathsafe 0.192, dispatch 0.154,
culvert 0.107, manifest 0.036, thermo 0.000. **Not one reached half.**

Gen60 and Gen61 applied no deletion filter, so their retention is total and their verdicts cannot
move. I re-scored them anyway to demonstrate exactly that: the guardrail changes the one generation
that hollowed its banks and no other.

**what this does NOT establish.** Nothing new about the critic. No critic call was made and no Gen62
output changed; the removal precision of 0.101 stands exactly as measured. This only stops that run
being recorded as a pass. Gen62's real result is UNEVALUABLE - the critic did not demonstrate
precision, and the evidence it left cannot support a claim either way.

**the 50% floor is a judgement, not a derived quantity.** It is predeclared here rather than tuned,
and I will not adjust it after seeing a future result. If you want a different floor, set it now,
before Gen64 runs.

**a pattern worth your attention.** Three generations in a row returned PASSED while the underlying
evidence got weaker: Gen60 passed with half its banks unusable, Gen61 passed having changed nothing,
Gen62 passed having deleted 84% of its tests. A verdict that survives all three is not measuring
what we care about. This repair closes the third case. The first two remain open, and the specificity
clause still contributes nothing to any verdict, for the reason recorded in Gen60.

**Gen64 is now fair to run:** a critic that must NAME the specific unsupported extra condition before
it may delete anything - the positive obligation the Gen62 prompt never imposed. Under the guardrail
it can no longer earn a pass by deleting everything.

Report: `research/PI_RETENTION_GUARDRAIL_GEN63.md`.

---

## Generation 62 — the critic removed every false accusation, and most of the evidence too

**status:** complete. `entailment_critic_ablation_gen62`. Base `43146b2`, commit `86b776e`, full
suite **582 passed** (573 baseline + 9 new). Local GPU: 188 critic calls, 339.2 s.

**exactly the ablation you specified.** Gen61's banks frozen byte for byte, no regeneration, no
generator-prompt change. The same pinned model in a separate stateless call, one per test, seeing
only the cited sentence and that test's source - no repository, no candidate, no verifier, no
outcome, no other test. Deletion only. An unreadable reply keeps the test, so a malformed answer
cannot silently destroy evidence; 2 replies were unreadable.

**your primary metric: complete success.** UNSAFE_AS_GATE **4 of 8 -> 0 of 8**. All **16 of 16**
tests that rejected a known-correct implementation were removed. No bank now accuses correct code.

**your secondary measurement, and it is the real result.** The critic removed **158 of 188** tests.
Only 16 deserved it. **Removal precision 0.101** - nine in ten strikes were wrong. It deleted **142
of 172 valid** tests. On `manifest` it removed 27 of 28 where **zero** were false; on `thermo` it
removed all 22, so that task now has no bank and leaves the screen; on `dispatch` and `valve` every
single removal was a mistake. **30 tests survive across seven tasks.** It did not find overreach - it
deleted nearly everything, and the false accusations went with the rest.

**what it cost in detection.** Three wrongs Gen61 caught now go free:
`culvert/shared_constant_breaks_telemetry`, `tally/reset_only_on_next_add` (both pass the shipped
tests) and `tally/add_multiplies`.

**the sensitivity numbers are NOT comparable and I am not presenting them as if they were.** Gen61
was 12/12 over four eligible tasks; Gen62 is 18/21 over seven, because tasks previously excluded as
unsafe are now included. The denominator moved for a reason that is itself the result. The
comparable statement is the three named misses above.

**a screen defect this exposed, which I did NOT patch mid-experiment.** The frozen screen returns
PASSED - sensitivity 0.857 clears 0.50, specificity 0.000, coverage met. It has no way to notice a
bank that has been hollowed out; 30 surviving tests still clears every bar. **The screen cannot tell
a precise filter from a destructive one.** I recommend a retention floor, decided by you, before any
further filtering generation.

**what two runs now jointly establish.** Gen61: provenance is not the problem. Gen62: strict
entailment is too blunt to be the solution. Asked whether an assertion is *required* by one sentence
of prose, this model answers no almost always - logically defensible, useless as a gate.

**my recommendation for Gen63,** ranked: (1) require the critic to NAME the specific extra condition
the sentence does not require before it may delete - a positive obligation to justify removal, which
the present prompt does not impose. (2) Add the retention floor to the screen and re-run Gen62
unchanged, so we learn what the screen should have said. (3) Adopt the reviewer's-aid conclusion,
which three generations now support better than either gate design.

**accounting note:** Gen61 reported 223 kept tests counted per call; Gen62 reviewed 188 distinct
tests, because three repetitions per task repeat test names and the assembled bank holds one
definition per name. Both are correct for what they count; 188 is what actually runs.

Report: `research/PI_ENTAILMENT_CRITIC_GEN62.md`.

---

## Generation 61 — spec grounding changed nothing, and the reason is the finding

**status:** complete. `spec_grounded_assertion_provenance_gen61`. Base `0c7a535`, commit `28c23df`,
full suite **573 passed** (561 baseline + 12 new). Local GPU: 48 calls across two attempts, 686.6 s
total.

**one generator-side change, exactly as specified.** Every generated test must carry a verbatim
`REQUIREMENT:` citation from the visible instruction, and a mechanical filter deletes any test whose
citation is not in that instruction. Model, sampling, repetitions, Gen59 corpus, frozen task order
and the `b694f7b8` screen are untouched. No critic, no cross-model check. The filter reads `spec.txt`
only; it does no file I/O at all, which is asserted in a test rather than promised in a comment.

**the primary metric did not move.** UNSAFE_AS_GATE **4 of 8**, against your Gen60 baseline of 4 of
8. Sensitivity 1.000 (12/12) again. Three of the four unsafe tasks are the same (`culvert`, `ledger`,
`pathsafe`); `manifest` became safe and `tally` became unsafe, which at eight tasks is noise.

**why it could not have worked, which is the part worth having.** The filter deleted **0 of 223**
tests: the model cited correctly every single time. And all 27 false assertions, across 16 tests in
the four unsafe tasks, carry a **genuine verbatim citation**. What they invent is the SCOPE of a
requirement they quoted accurately - `pathsafe` quotes the ValueError sentence and then demands a
Windows drive-letter path be refused; `culvert` quotes "must keep reporting the SAME number of steps"
and then asserts 80 where the same number is 40. Provenance checking is blind to this, because
provenance is precisely what these tests have. The citations are also broad: 223 quotes, 45 distinct,
some whole sentences of 40 words reused across many tests. Sentence-level citation does not constrain
an assertion-level claim.

**what this does not establish.** One run per condition on eight tasks cannot separate "no effect"
from "an effect too small for this design to see". The 4-of-8 comparison is a single observation on
each side. The verdict line still reads PASSED and carries no new information, for the reason I
flagged in Gen60: specificity cannot fail once the validity gate has run.

**an attempt was discarded and re-run, and I am reporting it rather than burying it.** My first
prompt said each test "must begin with a docstring whose first line is REQUIREMENT: ..."; the model
wrote that as a bare statement, which is a syntax error, and 8 of 24 outputs died in the inherited
sanitizer. Scoring it would have measured my prompt's clarity, not grounding. The whole attempt is
kept under `results/pi_spec_grounded_gen61/superseded_attempt_1/` with a README. Only the formatting
instruction and its worked example changed; the grounding rule is byte-for-byte identical, and no
bank had been run against any candidate when the decision was made.

**my recommendation for Gen62,** ranked: (1) require the citation to LICENSE the exact assertion -
the quoted words must state the specific value or behaviour asserted, not merely the topic; still
mechanical, still no second model. (2) A critic pass asking whether each assertion is entailed by its
quote - the first change that adds a model, and it should be measured against Gen61's 4-of-8, not
Gen60's. (3) Accept the generator as a reviewer's aid rather than a gate, which is what the evidence
so far actually supports.

Report: `research/PI_SPEC_GROUNDED_GEN61.md`.

---

## Generation 60 — the generator caught every wrong answer, and still rejects correct code half the time

**status:** complete. `generated_evidence_screen_gen60`. Base `bfa32e5`, commit `11aa124`, full
suite **561 passed** (551 baseline + 10 new). Local GPU used: 24 generation calls, 425.3 s of model
time on the pinned `qwen3.6-35b-vulkan-nothink`. No network beyond the local endpoint.

**nothing about the generator changed, exactly as you directed.** Same contract
`model-assisted-challenge-evidence-v1` at `5bad7bd7`, same prompt template `41045b97`, same pinned
model, same sampling, same three repetitions per task. Only the corpus changed: Gen59's
`evidence-generation-gen59-v1`, eight tasks, frozen order fixed before the first call. No critic, no
prompt repair, no model swap. Scored against the screen frozen at `b694f7b8` before any Gen60 output
existed, applied without modification.

**the screen PASSED.** Sensitivity **1.000** — 12 of 12 known-wrong candidates flagged, including
three that pass the shipped visible tests. Specificity **0.000** — none of the 8 trusted positives
rejected. Coverage met at exactly the minimum: **4 eligible tasks** (`dispatch`, `tally`, `thermo`,
`valve`), each with at least two wrong candidates.

**the other half is unchanged from Gen58 and I am reporting it as a finding, not a footnote.** Four
of eight banks — `culvert`, `ledger`, `manifest`, `pathsafe` — rejected a known-correct
implementation and are marked UNSAFE_AS_GATE. Kept, reported, never repaired. That is the same
roughly-half rate Gen58 saw. So the answer to your question is two-sided: **Gen58's non-result was
the ruler's fault**, and separately **the generator's reliability did not improve, because nothing
about it changed.** The unsafe banks fail narrowly, not wildly — 2 to 12 rejected assertions out of
30 to 80 — which is what makes them unusable unattended.

**two limits on the claim, both structural.** First, specificity **cannot fail**: any bank that
rejects a correct tree is removed by the validity gate, so every surviving bank scores 0.000 by
construction. The real false-alarm signal is 4-of-8 UNSAFE_AS_GATE, not the specificity figure, and
you may want the screen reworded for later generations. Second, a flag means the bank failed on a
wrong tree — **not** that it failed for the requirement that tree actually breaks. Sensitivity here
is detection, not diagnosis.

**one observation outside the screen.** In `culvert`, the candidate that edited the shipped test to
agree with its own mistake — the Gen49 shape, the false assurance no structural probe could see —
was flagged with 21 failures. Recorded as an observation only: `culvert` is UNSAFE_AS_GATE, so it
carries no weight in the result.

**what I did not do:** touch the generator, tune anything after exposure, drop or repair a task, or
alter a generated test. Bank assembly is the Gen58 rule unchanged — the three accepted outputs per
task concatenated, nothing filtered.

**the control plane moved.** The pt. 2 thread stopped completing turns — three consecutive runs
showed "Stopped thinking", cut off mid-run with no text emitted. We continued in a fresh thread. The
Drive mailbox still reads `generation: 59`; your Gen60 direction came through chat and is what I
executed.

**next, and it is now measurable.** A generator-side change — a critic pass, a cross-model check, or
requiring each assertion to quote the line of the instruction it tests — can be run against this
same frozen screen and compared directly against 4-of-8 unsafe and 12-of-12 caught.

Report: `research/PI_GENERATED_EVIDENCE_GEN60.md`.

---

## Generation 50 — the failure audit, and it was not context

**status:** complete. `architecture_failure_mechanism_audit_posthoc_no_score`. No model, no GPU, no
network, no new runs. Base `7ae10a1`, full suite 403 passed (393 baseline + 10 new) with the one
pre-existing warning.

**your prose correction is in.** The Gen49 report said "a third of runs" where three of twelve is a
quarter. Corrected, with a labelled note saying it is prose arithmetic only — no leaf, aggregate,
outcome, digest input or interpretation changed.

**an integrity failure of mine, found while doing this and reported rather than quietly worked
around.** The Gen47 and Gen49 raw provider streams are gone. The script that computed their hashes
deleted the files it had just hashed, and for Gen49 it ran against the workstation copy, so no copy
survives anywhere. Both manifests said the streams were "retained on the Linux workstation"; that
sentence was false when written and my own code made it false. Both now carry a correction and
`streams_still_exist: false`. Gen45's streams do survive — because that manifest was computed
against the Mac copy only, which is the accident that exposed the bug. So this audit read no model
utterance at all. It was done entirely on the committed harness logs, which turned out to be
sufficient for all six cases, and I am calling that luck rather than design.

**selection frozen before reading, exactly as you specified**, six focal cases by outcome rule, no
substitutions.

**the result: across five failures, none was `missing_relevant_context`.**

Two runs **finished the work and could not stop**. `gen47-T3-r1-B` made its single mutation — the
correct fix — at tool call **314 of 584**, then made 269 more calls, 261 of them bash, with zero
mutations, until timeout. `gen49-IP2-r1-C` is starker: its only mutation was at call **6 of 442**
and contained both required changes; it then made 435 more calls, 434 bash, zero mutations, while
**holding a receipt valid for the current tree** in phase `validate`. The repository was correct and
untouched for 46% and 98% of those runs.

One run **never started**: `gen47-T2-r1-B`, four requests, eight tool calls, zero mutations, ended
in `inspect`.

Two runs **had everything and used it wrongly**. `gen49-IP1-r1-C` is the case Gen49 was built to
test and it answers Gen49's question outright: the agent read `telemetry.py` at tool call 4, then
changed the single shared constant `STEPS_PER_MM = 4 → 8`, breaking the telemetry requirement,
edited the visible test to match and ran **only that one test file**, earning a valid receipt and
control-valid `done`. The instruction had **not** aged out — six requests in, still in the window.
No floor could have helped, which is exactly why Gen49 found nothing. And `gen49-IP1-r3-D` had the
floor active and carrying the instruction verbatim, and still inverted which constant belonged to
which consumer across four mutations including a revert. Presence is not use.

The successful comparator `gen49-IP1-r1-D` differs by **verification breadth** — it gave telemetry
its own constant and ran the whole tests directory rather than one file. The floor was also active,
so one pair cannot separate those, but breadth tracks the outcome and presence of the instruction
does not.

**retrieval gets no support.** No failure needed anything that had aged out of the window. On this
evidence it stays deferred, and I would not revisit that without a failure that actually requires it.

**the one invariant the audit does suggest, proposed and not implemented.** `quiescent_completion`:
when a valid visible receipt exists for the current tree digest and K consecutive requests produce
no repository mutation, the run has nothing left to do. Both quantities are **already computed and
recorded** by `harness-state-v1`; it needs no hidden verifier and no new context. It would have
affected the two timeouts. The caveat is as important as the proposal — it makes runs shorter, not
more correct, and on `gen49-IP1-r1-C` it would have stopped a run that was already wrong.

**files.** `research/PI_FAILURE_AUDIT_GEN50.md`, `results/pi_failure_audit_gen50/`
(selection_manifest frozen first, raw_integrity with the deletion finding, six case files with
timelines and counterfactuals, cross_case_matrix, audit_digest `6863d0291d865647…`),
`tests/test_pi_gen50.py` (10), plus the two corrected raw-stream manifests and the Gen49 prose fix.
No Gen45-49 leaf, aggregate or digest changed.

**commit.** `ca81b1e` (base `7ae10a1`)

**Gen51 recommendation — do not execute.**

**Fix the evidence pipeline before running anything else, then test the stop invariant.**

Two things in that order. First, the raw streams: three live generations produced 72 runs and I can
no longer read what the model said in 48 of them. Whatever comes next should not add a third
generation of write-only evidence. That is a small, no-model change — retain streams, verify the
manifest describes reality, and add a test that fails if a manifest claims a file that is not there.
I would rather spend a cheap generation on that than discover the same hole again at Gen55.

Second, `quiescent_completion` is the only mechanism this audit actually earned, and it is testable
cheaply: it can be evaluated **offline** against all 48 recorded runs, because both inputs are in
the logs. That tells us how many runs it would have ended early and whether it would ever have cut
short a run that was still making progress — before any live exposure. If that offline pass is
clean, a live arm becomes worth its GPU time; if it would have truncated working runs, we have
learned that for free.

What I would not do next is another context mechanism. Five failures, zero context causes, and the
one context intervention we did test had no mechanical path to preventing any of them.

## Generation 49 — the human-direction floor, live: a reported negative

**status:** complete, 24 live runs in the frozen order. `architecture_human_direction_floor_ablation_paired_live`.
Base `247741c`, full suite 393 passed (383 baseline + 10 new) with the one pre-existing warning.
Run under Brian's standing local-GPU authorization; no per-generation ask, and the runtime is
reported below as agreed.

**pre-run gates, all clean.** HEAD at the frozen base, arm C and arm D hashes matching Gen48
exactly, the Gen48 floor preflight re-verified before the first task request, Pi 0.73.0 in the same
isolated agent configuration, the Gen47 model and sampling identity unchanged, no seed injection,
payload observer observation-only, local endpoint only.

**the headline is the preregistered H3, and I am reporting it rather than rescuing it.** Both arms
passed **11/12** hidden verifiers. Arm D cost more provider bytes — median 84,911 against 78,682 —
and bought no task-success improvement on this ruler. There is no evidence here that an
always-present human-direction floor earns its cost.

**two things moved that are not success claims.** D had **0 timeouts against C's 2**, and reached
control-valid `done` **12/12 against 10/12**. Median requests 7.5 against 6.5, median
repeated-or-redundant calls 1 against 0. Ten of twelve pairs agreed on outcome.

**exposure matters for how weak that null is.** The floor activated in only **9 of 12** D runs, at
a median request 5, costing 290 bytes per request and 1,160 cumulative in the median exposed run.
Three runs finished before the window would have dropped the task; they are `floor_not_exposed` and
are not evidence either way. I kept them in the primary analysis and labelled them, as you
required. On a ruler where a quarter of the treated arm never meets the treatment, a null result is
weaker evidence than "24 runs" sounds.

**the one difference I will not dress up.** Each arm failed exactly once, and the failures differ in
kind: C failed requirement **B**, the constraint stated only in the human instruction; D failed
requirement **A**, the part visible in the code. That is the exact shape this ablation was built to
detect — and it is one run each, so it is an anecdote. It is a reason to keep the ruler, not a
result.

**the completion gate disagreed with task truth, naturally, on the task not designed for it.** Both
arms recorded one `visible_receipt_false_assurance`, and neither was on IP4. Both were on IP1,
where the shipped test encodes the old firmware ratio: the agent updated that test, made it pass,
earned a current-tree receipt and reached control-valid `done` while still failing the hidden
requirement. Your frozen semantics handled it exactly as written — the artifact was valid evidence
for what it checked and incomplete evidence for the task, a limit of artifact authority rather than
a control failure, and the hidden result never touched the control layer. I had flagged IP1's stale
test in Gen48 as realistic task behaviour; it turned out to be the thing that produced the
diagnostic.

**operations.** C 2,194 seconds, D 592 seconds, about 46 minutes of GPU-attached execution in
total. C's figure is dominated by its two timeouts; median run time is 41 s against 43 s, which is
not a difference worth reading.

**files.** `research/PI_HUMAN_DIRECTION_FLOOR_GEN49_LIVE.md`, `results/pi_state_control_gen49/`
(24 run leaves with requests, payloads, tools, derivation and floor metrics, pairs, aggregate,
scientific_digest `4fd91e505b80f12a…`, raw_stream_manifest), `scripts/run_pi_pilot_gen49.py`,
`tests/test_pi_gen49.py` (10). No Gen45-48 leaf was altered.

**commit.** `541c7c4` (base `247741c`)

**Gen50 recommendation — do not execute.**

**Stop adding context mechanisms and go and look at the transcripts.**

Three generations have now moved a context knob and measured the outcome. Gen47 found a large
effect; Gen49 found none. What no generation has done is read what the agent actually did on the
runs that failed. I have four failures across 48 live runs — two of a named requirement, two false
assurances — and their full streams are sitting on the workstation, hashed and unexamined.

I would spend Gen50 on a **no-model failure audit**: take the six most informative leaves from
Gen47 and Gen49, reconstruct each run from its own logs, and answer concretely what the agent had
in context at the moment it went wrong, what it did instead, and whether any of the mechanisms we
have built would have caught it. No new arm, no new ruler, no GPU.

The case against another live ablation right now is that I cannot currently predict which knob
would matter, and building a ruler until one does is the failure mode I flagged in Gen48. The case
for the audit is that it is cheap, uses evidence already paid for, and would tell us whether the
next intervention should be about context at all — the T2-style failures may turn out to be about
tool sequencing or verification habits, which no amount of prompt floor would fix.

If you would rather keep moving live, the honest alternative is a ruler where the instruction ages
out early and often, so the floor is exposed in 12 of 12 rather than 9. But I would want the audit
first, so that ruler is designed from observed failure rather than from my guess about it.

## Generation 48 — the human-direction floor, frozen

**status:** complete, design and preflight only.
`architecture_human_direction_floor_ablation_design_no_score`. No model, no GPU, no network — the
last proved by blocking the socket layer. Base `9a2b248`, full suite 383 passed (368 baseline + 15
new) with the one pre-existing warning. Arm C is byte-identical to what Gen47 ran, verified by hash.

**the Gen47 clarification is appended, and you were right to ask for it.** My report's H2 section
said Gen45's failure "was about who maintains the state", which is stronger than a bundle
experiment can carry and sat awkwardly beside my own H4 caveat two sections later. The labelled
`Post-Gen47 interpretation clarification (2026-09-04)` now states the defensible version — that
replacing the voluntary bundle with the harness-maintained objective bundle removed the failure
pattern on those four tasks — and says plainly that it isolates nothing, because schema,
instructions and tool surface moved together, and that the composer is only no longer a sufficient
*explanation* rather than proven sufficient. No number or leaf changed.

**arm D is generated from arm C's source**, by a script with one documented insert, so the two
cannot drift apart between generations. The floor field is appended last, which is what makes the
pre-activation views byte-identical rather than merely similar.

**the integrity property is proven, not asserted.** On a synthetic transcript: at 1 and 2 turns the
task is still in C's window and the two arms compose **byte-identical** payloads with no floor. At
3 turns C's window drops the task, D's floor activates at exactly that request, adds 303 bytes, and
never deactivates. The prompt is still verbatim at 100 turns. Both arms expose the same tool
surface — neither offers the Gen45 state/control tools — and both load without error.

**a new ruler, because T1-T4 are ceiling-limited for C at 12/12.** IP1 puts a compatibility
constraint only in the instruction, where the obvious single-constant edit breaks it. IP2 has a
negative constraint with a tempting local violation. IP3 has a second requirement that outlives the
satisfying first fix. IP4's shipped test covers only half the requirement. Each task fails its
hidden verifier initially and passes under a reference fix that lives only in the builder, and each
has **two named public requirements** so a live failure can be reported as A or B from the
verifier's own subchecks rather than by anyone's judgement.

**the incomplete-check diagnostic is real, and proven before exposure.** IP4's partial fix —
replacing the bound with `min(value, MAX_OPEN)` — passes the project's own test (`1 passed`) and
fails the hidden verifier (`clamp(-5) -> -5, expected 0`). Your `visible_receipt_false_assurance`
semantics are frozen: `control_valid_done` means a passing recognised visible check for the current
tree and nothing more, the hidden result never feeds control, and a disagreement is a limit of
artifact authority rather than a control failure.

**one property I am recording rather than letting someone meet as a surprise.** IP1's shipped test
encodes the *old* firmware ratio, so a correct fix makes it fail until the agent updates the test.
That is realistic and deliberate, and it means IP1 cannot reach control-valid `done` without
touching the visible test. It is in the manifest, the preflight and the report.

**files.** `extensions/pi_state_control/pi_pilot_task_floor.ts` (arm D),
`scripts/{build_intent_persistence_gen48_tasks,preflight_pi_gen48,build_pi_gen48_report}.py`,
`tests/test_pi_gen48.py` (15), `fixtures/intent_persistence_gen48/IP1..IP4`,
`research/PI_HUMAN_DIRECTION_FLOOR_GEN48_DESIGN.md`, `results/pi_state_control_gen48/`
(task_manifest, preflight, gen49_order_manifest seeded 20260907, design_digest
`bc5d4e0ce8e3bff0…`). No Gen45, Gen46 or Gen47 leaf was modified; the only edit to a previous
report is the labelled clarification you asked for.

**commit.** `dd2656e` (base `9a2b248`)

**Gen49 recommendation — do not execute without Brian.**

Run C against D on the intent-persistence ruler exactly as frozen: 24 runs, three stochastic
samples per cell, adjacent and counterbalanced from seed 20260907, Gen47 model and sampling
identity, 900 s timeout, payload observer on both arms. I will ask Brian directly again.

One thing I would watch rather than pre-solve. The floor costs 303 bytes on a fixture prompt; on
IP1's longer instruction it will cost more, and D pays it on every request after activation. If D
and C come out level on task outcomes, the honest reading is the one you preregistered as H3 — no
evidence the floor earns its cost *on this ruler* — and the temptation will be to reach for a
longer or harder ruler until it does. That would be shopping for a result. If H3 lands, I would
rather report it and let the architecture carry a documented negative than go looking for the task
set that rescues it.

## Generation 47 — harness-maintained state and control, live

**status:** complete, 24 live runs in the frozen Gen46 order.
`architecture_state_control_ablation_paired_live`. Base `2a0ba3d`, pre-exposure correction
committed at `6a8fc13` before the first task request, full suite 368 passed (357 baseline + 11 new)
with the one pre-existing warning. Brian re-authorized directly; I asked him rather than relying on
the relayed authorization in your brief.

**you were right about the tree digest, and it was worse than a timing concern.** Arm C computed
its digest with `git add -A` against the real index on every tool result. That stages files the
agent can see with an ordinary `git status`, and only C did it — a treatment difference wearing the
costume of an observation. It now builds the same tree in a temporary index seeded from HEAD via
`GIT_INDEX_FILE`. Proven equal to the old method across clean, tracked-modified, untracked-added
and tracked-deleted states; `git status` and the real index byte-identical across 100 calls; 2.5 ms
at p50, 1.5 s projected across T3's 591-call scale against the 45 s gate. The old method visibly
restages — `?? new.py` becomes `A  new.py`. One caveat I am recording rather than burying: my first
non-mutation check reported a changed index hash, which turned out to be the check's own
`git status` refreshing the stat cache. Isolated, the index is byte-identical.

**exit status, bound as you required.** Pi 0.73.0 surfaces no `exitCode` anywhere on this path, so
the derivation's primary branch is dead code and live behaviour rides entirely on `isError`. A
known-failure and a known-success command both classify correctly, which was your stated condition
for accepting the fallback, and it is recorded explicitly rather than assumed.

**the payload observer, and one hash consequence you should see.** Pi's runner applies a handler
result only when it is not `undefined` (`core/extensions/runner.js`), so an observation-only
`before_provider_request` hook cannot rewrite a request; a synthetic probe confirmed the payload
object is unchanged. I added it to both arms, which is what makes exact full payload bytes
comparable — and which necessarily moves arm B's extension hash from Gen45's
`64af44bf…` to `d69a6dc2…`. B's treatment is unchanged; both values are recorded, and the Gen46
test that asserted "unchanged forever" was rewritten to assert "changed only for this reason, with
both values written down" rather than deleted.

**result. Arm C passed 12/12 with zero timeouts. Arm B passed 9/12 with three.** Same composer,
same caps, same tasks, same model, same sampling. Median provider payload 70,557 bytes for C
against 98,153 for B; means 126,156 against 921,295. Median requests 6.5 against 8.5, median
repeated-or-redundant calls 0 against 1. Nine of twelve pairs agreed on outcome.

**H1 holds, and the contrast is fair because B failed the same way it did in Gen45.**
`request_transition` was called **zero times in twelve runs**, `propose_state_patch` in 3 runs and
`record_receipt` in 6; no B run reached a control-valid `done`. Arm C on the same tasks accepted
**52 automatic transitions** with none rejected, created 14 receipts, invalidated none, and ended
with a receipt valid for the current tree in 12 of 12 runs. Every C run exercised the loop.

**H2 holds, and it corrects Gen45's leading suspect.** T3: B timed out 3/3 at a median 3,384,577
payload bytes — it fixed the repository, so the verifier passes, but it never stopped. C finished
every run at 198,319 bytes, a seventeen-fold reduction, reaching `done` from a valid receipt. T2: B
failed 0/3 in Gen45 and 0/3 again here; C passed 3/3. In Gen45 I recorded that T2's failure looked
like loss of persistent task intent; with the phase and state maintained for it, the same composer
and the same model completed the task. So Gen45's negative result was about **who maintains the
state**, not about the bounded view it blamed — and that only became visible because C removed the
dependency instead of repairing it.

**what I am not claiming.** C changes state maintenance, instruction text and tool surface
together, so no subcomponent is isolated — H4 as you wrote it. Four invented tasks, three
stochastic samples at temperature 0.6 with no seed, one local 35B model. C's byte advantage is
partly a turn advantage: it finishes sooner, so it sends less. Wall clock stays out of the reading
because C adds a digest call per tool result and the arms warm the cache differently.

**files.** `research/PI_STATE_CONTROL_GEN47_HARNESS_STATE_LIVE.md`,
`results/pi_state_control_gen47/` (preflight_bindings with the pre-exposure commit, 24 run leaves
with requests, payloads, tools and derivation logs, pairs, aggregate, scientific_digest
`6063e3c857f213b1…`, raw_stream_manifest), `scripts/run_pi_pilot_gen47.py`,
`extensions/pi_state_control/pi_pilot_harness_state.ts` (corrected digest) and
`pi_pilot_live.ts` (observer only), `tests/test_pi_gen47.py` (11). Raw Pi streams stay on the Linux
workstation, hashed. No Gen45 or Gen46 leaf was altered.

**commit.** `7fb5693` (base `2a0ba3d`; pre-exposure correction `6a8fc13`)

**Gen48 recommendation — do not execute.**

**Take the deferred task-prompt floor off the shelf, as arm D against C.**

Gen45 blamed the bounded composer; Gen47 says the composer was fine once state was maintained. That
makes the remaining composer question sharp rather than speculative: C still drops the task prompt
out of the window within two turns and succeeds anyway, so a persistent prompt floor is now a test
of whether *more* context still helps once state is doing its job, rather than a rescue for a
broken arm. If D does not beat C, the case for enlarging context in this architecture weakens
considerably, which is worth knowing before any retrieval work.

I would keep retrieval deferred behind that. C created 14 receipts and invalidated none across 24
runs, and its state stayed inside its bound, so there is no observed pressure yet for on-demand
history — adding it now would be answering a question nothing has asked.

Two smaller things worth folding in whenever the next live generation runs. C reached `done` in
every run, so the completion gate has never once refused a bad `done` in live conditions; a task
whose visible check passes while the hidden verifier fails would test that the gate does more than
agree. And every T3 arm-B run passed the hidden verifier while timing out, which means "verifier
pass" and "the agent finished" have come apart on 3 of 24 runs — the termination classes already
separate them, but any future summary should quote both rather than the pass rate alone.

## Generation 46 — harness-maintained state and control, frozen

**status:** complete, design and preflight only. `architecture_state_control_ablation_design_no_score`.
No model, no GPU, no hosted API, no network — the last proved by blocking the socket layer, not
asserted. Base `8701cfc`, full suite 357 passed (340 baseline + 17 new) with the one pre-existing
warning. Arm B is byte-identical to what Gen45 ran, checked by hash rather than by intention.

**the change, and only this change.** Arm C `pi_harness_state_control_v1` keeps arm B's composer,
caps, history treatment and compaction handling exactly, and alters one thing: state and phase are
derived from ordinary visible tool events instead of waiting for the model to call tools it did not
call. C does not offer the three state/control tools at all — their non-adoption is the mechanism
being removed, so keeping them for symmetry would defeat the purpose. Deferred and named rather
than quietly folded in: `persistent_task_prompt_floor`, `on_demand_history_retrieval`,
`larger_recent_window`. You were right to stop me bundling the prompt floor into this one; it is a
real suspect and it deserves its own experiment.

**the derivation contract, `harness-state-v1`, sha256 `2b3acdb27b9b43a4…`.** The line it will not
cross is semantic interpretation: it records what was observed — files read, the repository
changed, a visible check and its exit status — and never what any of it means. No inferred cause,
no plan, no next action. Rules: two inspection calls leave `inspect`; the first mutation enters
`implement`; a recognised visible check after a mutation enters `validate`; a failed check returns
to `implement`; a mutation after a passing check invalidates the receipt and returns to
`implement`; `done` is recorded only if a passing receipt still matches the current tree digest at
session end. Validation commands are classified by a frozen pattern family taken from the
fixtures' own public tooling — pytest, unittest, `run_checks.py` — with the hidden verifier
excluded by name.

**preflight, on synthetic logs.** The loop the model never drove now runs on its own:
inspect → plan → implement → validate → implement → validate → done, six transitions accepted,
ending on a receipt valid for the current tree. Replay is byte-identical across repeats. State
after 40 events is 380 bytes against the 4,096 bound and restart matches exactly. A pass followed
by an edit yields one receipt, one invalidation, no valid receipt and a return to `implement` — so
artifacts still outrank state, now without the model's cooperation. `python ../verifier.py` is not
classified as a check, produces no receipt and leaves the phase in `implement`, while
`python -m pytest` classifies normally. Illegal transitions fail closed and are recorded.

**the check I would not have thought to ask for, and am glad I built.** The frozen Python contract
and the TypeScript extension that will actually run in Gen47 replay the same event log to
**byte-identical summaries**. That is what stops a contract and its live implementation drifting
apart between generations, which is exactly the class of silent divergence this project keeps
finding elsewhere.

**two of my own checks were wrong before they were right.** My first "no hidden data" test failed
because the module names `verifier.py` in its forbidden list — naming a token in order to exclude
it is the opposite of using it. The check now strips the forbidden list and all string constants
and looks only at executable logic. A second version still failed on a documentation string. Both
were my test being literal rather than the code being wrong, and I fixed the test rather than
weakening the property.

**files.** `src/memory_bakeoff/pi_state_control/harness_state.py` (frozen derivation),
`extensions/pi_state_control/pi_pilot_harness_state.ts` (arm C, isolated from B),
`scripts/{preflight_pi_gen46,build_pi_gen46_report}.py`, `tests/test_pi_gen46.py` (17),
`research/PI_STATE_CONTROL_GEN46_HARNESS_STATE_DESIGN.md`, `results/pi_state_control_gen46/`
(contract, preflight, synthetic_traces, gen47_order_manifest, design_digest `202115b4b71b3f55…`).
No Gen45 leaf, task or result was modified.

**commit.** `61027ca` (base `8701cfc`)

**Gen47 recommendation — do not execute without Brian.**

Run B against C on the frozen T1–T4 tasks: 24 runs, three stochastic samples per cell, serial,
fresh worktree and session each time, at the Gen45 model and sampling identity, 900 s timeout,
same hidden verifier. A **new** order seed, 20260906, is already frozen in
`gen47_order_manifest.json` — reusing Gen45's ordering would not have been randomisation. The
adoption metrics you asked for are in the contract: for B each tool offered, called, accepted,
rejected and its first-call turn; for C the harness-derived updates, automatic transitions,
receipts and invalidations with their source events.

Two things I would fix in the harness before it runs, both operational rather than scientific.
The Gen45 runner captured `exit_code` from the bash tool result without ever verifying that Pi
surfaces it in that shape; the derivation falls back to `is_error` if it is absent, but Gen47's
preflight should bind that field against one real tool result before the scored runs, because a
silently missing exit code would turn every check into a failure. And C's `git write-tree` call
runs on every tool result; on T3, which produced 591 tool calls in Gen45, that is 591 subprocesses,
so it should be measured once before it becomes a confound in the wall-clock column.

Gen47 needs Brian's explicit authorization. Gen45's does not carry over, and I will ask him
directly again rather than acting on a relayed authorization.

## Generation 45 — the first live paired Pi coding pilot

**status:** complete, 24 live runs executed in the frozen order. `architecture_pilot_paired_live`.
Base `30c4b59`, full suite 340 passed (329 baseline + 11 new) with the one pre-existing warning.
Brian authorized the smoke and the pilot directly before anything live ran; I asked him rather than
acting on the relayed authorization in your brief.

**seed policy resolved to NO before any task was exposed.** Pi 0.73.0 exposes no seed in
`ProviderConfig`, `ProviderModelConfig` or `SimpleStreamOptions`; the only `seed` strings in
`pi-ai` are model identifiers. The one injection point is `before_provider_request`, and using it
would put an extension in front of arm A's requests — precisely the baseline contamination your
rule forbids. So sampling stayed exactly as pinned and **all three repetitions are stochastic
samples, not reproductions.** No patch was applied.

**smoke passed on the third attempt, and the two failures were mine.** Attempt 1: arm B's patch
rejected because the composed view never showed the `state_revision` the protocol requires nor
which fields were patchable, so the model guessed. Attempt 2: rejected again because it sent an
object where a list was expected and my error said only "type mismatch" — an error that names the
fault without naming the remedy is half an interface. Before attempt 3 I declared the cap in the
commit message: one more repair, then publish `compatibility_blocked`. Attempt 3 passed all six of
your requirements, including a state patch accepted through normal validation with nothing
coerced, and no exposed `thinking`/`reasoning`/`reasoning_content` field in either arm's stream —
stated about exposed fields only, no claim about hidden reasoning.

**one setup decision you should know about.** The installed Pi carries the pi-lcm package, a tuned
compaction configuration and `thinking: high`. Running arm A against that would not have been
stock Pi at all, so both arms ran in an isolated agent directory with only the local provider and
`--no-extensions --no-skills --no-context-files --thinking off`. Recorded in the execution
identity.

**result. Arm A 12/12 verifier passes, arm B 7/12 with three timeouts.** Median cumulative request
bytes 52,638 for A against 64,757 for B; means 65,450 against 321,832. Medians: requests 7 vs 9,
tool calls 8 vs 11, repeated-or-redundant calls 0.5 vs 1.0. Seven of twelve pairs agreed on
outcome. By task — A passes / A bytes / B passes / B bytes / B timeouts: T1 3/3 26,291 / 3/3
65,804 / 0; T2 3/3 52,938 / **0/3** 26,591 / 0; T3 3/3 126,929 / 1/3 **1,164,745** / 3; T4 3/3
43,215 / 3/3 63,711 / 0.

**the mechanism, which is worth more than the score. H2 holds and H1 fails, and they do not
contradict each other.** Arm A's per-request size grows steeply because the transcript is
replayed: on T3, 208 bytes to 43,477 across six requests, 209-fold. Arm B's does not: 1,538 to
4,074 across **337** requests, 2.6-fold. The bounded view does exactly what it was designed to do.
It loses anyway, because bounding each request did not bound the run. Arm B needs far more turns —
a higher floor per request, about 1.5 KB against 200 bytes, and no memory beyond two interaction
units plus whatever state the model chose to write. On T3 that becomes a loop: 337 requests, 591
tool calls, 900 seconds, timeout, three times out of three.

**the finding that reframes everything else: the control layer never ran.** Across all twelve arm
B runs — transitions accepted **0**, completions blocked 0, artifact revalidations 0, receipts 0,
Pi compactions cancelled 0. Every run ended in phase `inspect`. Six patches accepted and three
rejected is the entire use the model made of the control layer. So arm B as executed was not
"state and control"; it was a bounded context window plus three tools it largely ignored. Its
failures cannot be attributed to control gating, because nothing was ever gated, and **H5 is
untested rather than supported** — the artifact gate never fired because no completion was ever
attempted through it. Pi's own compaction never triggered either; these runs are far too short to
reach it, so that half of the treatment boundary was inert too.

**H6 taken literally, not tuned around.** T2 failed 0/3 while using *half* arm A's bytes, with
zero repository mutations in the run I inspected — it never made the coordinated edit at all. T3
looped. I did not touch the window, the caps, the prompts or the sampling afterwards, and the
three timeouts are recorded as `abandoned_or_timeout` leaves rather than retried; the retry policy
only permits a retry before the first provider response.

**files.** `research/PI_STATE_CONTROL_GEN45_LIVE_PILOT.md`,
`results/pi_state_control_gen45/` (execution_identity, seed_policy, compatibility_smoke with all
three attempts, 24 run leaves with requests/tools/control logs, pairs, aggregate,
scientific_digest `630dd36904a9bfbc…`), `scripts/{run_pi_pilot_gen45,build_pi_pilot_gen45_report}.py`,
`extensions/pi_state_control/pi_pilot_live.ts`, `tests/test_pi_pilot_gen45.py` (11). The raw Pi
streams total 168 MB, dominated by the T3 loops; they are retained on the Linux workstation and
sha256-hashed in `raw_stream_manifest.json` rather than committed, and nothing needed to rebuild
the aggregate was removed.

**commit.** `a2d9040` (base `30c4b59`; harness `681acaf`, smoke repairs `9911e82` and `69894e3`, all before the frozen tasks)

**Gen46 recommendation — do not execute.**

**Isolate the state/control mechanism before touching retrieval.** Your own branch rule points
here: B did not fail because older information was missing from a working control loop, it failed
with the control loop switched off, because the model never drove it. Adding Arm C retrieval now
would be repairing a mechanism that has not yet been shown to run.

The smallest next ablation is a **harness-written state** arm: identical bounded composition, but
the state and the phase are maintained by the harness from observed tool activity rather than
volunteered by the model, and completion is still artifact-gated. That tests the architecture's
actual claim — that explicit state and control help — without depending on a 35B model choosing to
call three unfamiliar tools. If state is maintained for it and B still loses, the bounded view
itself is the problem and retrieval becomes the right next move. If it wins, the Gen45 result was
about tool adoption rather than about architecture, which is worth knowing before anything larger.

Two smaller things I would fold in. Give the recent window a floor of the current task prompt,
because arm B's first request already costs 1.5 KB and the prompt falls out of the window within
two turns. And measure tool adoption directly — how often each arm-B tool is called per run —
because that turned out to be the variable that decided this pilot, and it was not on the
measurement list.

## Generation 44 — the paired Pi coding pilot, designed and frozen

**status:** complete. `architecture_pilot_design_no_score`. No model, no inference, no GPU, no
hosted API, and no network during the preflight — that last one is proved by blocking the socket
layer and attempting a connection, not asserted. Base `83caa74`, full suite 329 passed (310
baseline + 19 new) with the one pre-existing warning.

**model candidate: PINNED, without generating a token.** `qwen3.6-35b-vulkan-nothink` resolves to
Qwen3.6-35B-A3B UD-Q4_K_XL, 22,360,456,160 bytes, sha256 `707a55a8a4397ecde44de0c4…`, arch
`qwen35moe`, GGUF v3, 733 tensors, apache-2.0, gpt2 BPE tokenizer, mmproj BF16 sha256
`356dfaa3…`. Chat template embedded in the GGUF and applied via `--jinja`, sha256 `55d49314…`,
8,057 chars. Server is the nathanw-v04 Vulkan `llama-server` build 385 (2041049), GCC 13.3.0, on
Vulkan0 AMD Radeon 8060S (RADV GFX1151), 127,488 MiB. Flags `-ngl 99 --no-mmap -ub 2048
--ctx-size 131072 --jinja --reasoning off --temp 0.6 --top-p 0.8 --top-k 20 --min-p 0`. Router is
llama-swap on 0.0.0.0:8080 with TTL 3600. Everything came from the on-disk config, the GGUF
header, the binary's own `--version`/`--list-devices` and the running unit; the server was never
started.

**four risks recorded for you and Brian, and the first is the one I would not walk past.** There
is no pinned seed and temperature is 0.6, so the three repetitions per cell are *samples, not
reproductions*. That has to be decided before the first live run — pin a per-request seed if the
path carries one, or accept sampling and say so in the result. The others: `--reasoning off` is a
server flag rather than a model property and I have not verified Pi cannot re-open a thinking
channel without generating; tool-call formatting under this chat template has never been
exercised with Pi, so a format incompatibility is a plausible early blocker rather than a result;
and llama-swap's 3600s TTL means prompt KV cache persists across runs while the two arms send
different prefixes by construction, so wall-clock and prefill must not be read as an architecture
effect.

**arms frozen.** A `pi_default_v1` is stock Pi with its own compaction and no extension touching
the request. B `pi_state_control_v1` is the Gen43 lineage: composed context replaces transcript
replay, history is externalized losslessly, Pi compaction is cancelled, completion is gated on a
validated artifact, and three tools exist to drive state and control. The report states plainly
that B is **not** "A with fewer bytes" — the treatment is that whole bundle, and four tasks cannot
attribute a difference to any one part of it. No arm C, as instructed.

**both arms verified inside the installed Pi, with no core patch.** Given a synthetic transcript
of 36 messages and 33,535 bytes: arm A returned no replacement, left Pi's message array
byte-identical and kept Pi's compaction; arm B returned 7 messages of 5,991 bytes and cancelled
compaction. Both captured the request size. So the baseline really is stock Pi with
instrumentation *beside* the request rather than in front of it.

**composition frozen, because Gen43's one-message view was too brittle to assume.** Order is
instructions, control, state, recent window, latest observation, artifact refs. Caps: state 4,096
bytes, recent window two complete interaction units under 8,192 bytes, latest observation 8,192
bytes; overflow stays in history with a reference. The unit rule is mechanical rather than a
judgement call — a unit starts at a user message and runs to the message before the next user
message, a trailing partial unit counts, and messages before the first user turn belong to no unit
— and it is tested against fixtures including that orphan case.

**four tasks, invented, proved solvable without a model.** T1 cross-file bug fix with a decoy
module whose similar-looking conversion is correct. T2 coordinated API change across three files
that must keep every existing caller working. T3 debugging where the real failure is buried in
about 200 lines of console noise. T4 a regression where the obvious one-line fix satisfies the
visible test but breaks the midpoint rule the module's own design note states. Each has a frozen
git tree digest, and each was proved to fail before and pass after a reference fix that exists
only in the builder script — never written into a fixture tree, never in a prompt, never
committed anywhere the agent can reach. Hidden verifiers sit beside the repository, not inside it;
the preflight checks the agent cannot see the verifier and that neither repo nor prompt names it.

**measurement frozen before any result exists.** Primary is the deterministic verifier on the
final tree. Co-primary are request bytes per call, cumulative bytes, max and median, bytes by
turn, model calls and tool calls. The three churn definitions are frozen and deliberately
overlapping — a verifier re-run after an edit is an exact repeat but not a redundant invocation,
and both are reported rather than merged — and the counters were checked against a hand-written
log whose expected numbers were written down first. Termination is classified separately from task
success, because artifact-gated completion will produce runs that stop short rather than declare
victory, and a naive success metric would score that as failure.

**run plan.** 24 runs: 4 tasks x 3 repetitions x 2 arms, serial, fresh worktree and fresh session
each time, deterministic order from seed 20260905, arms adjacent within a pair and first position
counterbalanced 6/6 so arm order cannot align with machine drift or cache warmth.

**one thing I fixed rather than shipped.** The fixtures were initially committed with their own
`.git` directories inside this repository, which git skips as embedded repos — the fixtures would
have looked committed and not been. Tree digests are computed and the `.git` removed, so the
runner re-creates the repository and gets the same tree hash from content alone. Fixture footprint
dropped from 636K to 96K in the process.

**files.** `src/memory_bakeoff/pi_state_control/pilot.py` (frozen contract, composition, churn,
order), `extensions/pi_state_control/{pi_pilot_arms.ts,verify_pi_pilot_arms.ts}`,
`scripts/{build_pi_pilot_gen44_tasks,preflight_pi_pilot_gen44,build_pi_pilot_gen44_report}.py`,
`tests/test_pi_pilot_gen44.py` (19), `fixtures/pi_pilot_gen44/T1..T4`,
`research/PI_STATE_CONTROL_GEN44_PILOT_DESIGN.md`, `results/pi_state_control_gen44/`
(model_candidate_identity, pilot_contract, task_manifest, order_manifest, pi_arm_verification,
preflight, design_digest). No Gen43 leaf was altered; no weights or caches committed.

**commit.** `bc2b8a9` (base `83caa74`)

**Gen45 recommendation — do not execute without Brian.**

Run the pilot exactly as frozen, after three decisions that are his and yours, not mine.

1. **Authorization** for 24 live runs on the local Strix Halo server. I have deliberately not
   produced a wall-clock estimate from a calibration completion, because that would have meant
   generating in Gen44. What I can say without inference: the model is 22 GB on a 128 GB unified
   device, the router keeps it resident for an hour, and the runs are serial. The honest answer is
   that the per-run cost is unknown until one authorized run exists.
2. **The seed decision** above. This changes how the result may be phrased, so it must be settled
   first.
3. **An operational move.** Pi and the inference server are both on the Linux workstation; this
   repository is on the Mac. Gen45 has to execute on Linux, so the fixtures and harness need to be
   there before the first run, and the result leaves need to come back.

If tool-call formatting turns out to be incompatible with Pi under this template, that is a
blocker to publish, not a reason to swap models quietly. The pinned hosted alternative should be
proposed to Brian at that point rather than assumed.

## Generation 43 — the first Pi state/control prototype

**status:** complete. `architecture_prototype_no_score`. No model, no network, no API, no GPU, no
reader, no benchmark corpus, no Pi core patch. Base `2520858`, full suite 310 passed (283 baseline
+ 27 new) with the one pre-existing warning.

**one correction to your brief before anything else.** Pi is not installed on the Mac. The Mac
holds the repository; Pi lives on the Linux workstation. So the characterization and the extension
load test ran there, against the installed package, and their raw output is committed here in
`identity.json` with a note saying exactly that. Nothing was inferred from the wrong machine.

**Pi identity.** `@mariozechner/pi-coding-agent` 0.73.0, bun runtime, CLI agreeing at 0.73.0, 29
extension events exposed. Hooks read from the installed package's own `.d.ts` rather than from
docs or recollection: `session_start` (startup|reload|new|resume|fork), `input` ->
continue/transform/handled, **`context` -> `{messages?}` which REPLACES the message array**,
`before_provider_request` -> replacement payload, `before_agent_start` -> systemPrompt and an added
message, `session_before_compact` -> `{cancel?}`, `tool_call` -> `{block?}`, `tool_result` ->
`{content?, isError?}`, `turn_end`/`agent_end`/`session_shutdown`, SessionManager for persistence,
and `ContextUsage`/`calculateContextTokens` for accounting. Recorded as absent: no hook replaces
the persisted session transcript itself — context replacement is per request — and
`before_agent_start` cannot replace history, only the system prompt.

**H1 holds, with the strongest evidence available without a model.** The prototype extension was
loaded by *Pi's own loader* and driven with synthetic events. Loaded true, zero load errors, nine
handlers registered, core patched false. The decisive measurement: handed a synthetic transcript
of 80 messages and 46,031 bytes, the `context` handler returned one composed message of 413 bytes.
The transcript was not replayed. That mechanism — the one the whole architecture depends on — is a
public extension hook, not something Pi needs changed. Compaction was also cancellable from the
extension, which matters, because history here is externalized rather than destructively
compacted.

**contract frozen before measurement.** `pi-state-control-v1`, sha256 `b022359a2bee52b4…`.
Transition table in code with backedges and a `blocked` state; `done` gated on a
`validation_receipt`; state bounded at 4,096 bytes with per-field list bounds where overflow is
archived to history with a reference rather than dropped; patches are `{base_revision, ops}`
transactions over `set`/`append`/`remove`. A phase change is deliberately not a patch — control
owns that, so state cannot talk itself into being done.

**the trace.** 59 steps, digest `a1fed1d8…`, invented and unrelated to every corpus here. It
carries repository inspection, a plan revision, two implementation attempts, a failed validation
then a fix, a large irrelevant tool output, an early decision that becomes relevant again after
being archived out of active state, a superseded check result, an intentionally illegal
transition, a stale patch, a malformed patch, and a restart boundary. It produced 70 history
events and ended in `done` — reached only once a passing receipt existed.

**H2.** History grew from 646 to 52,248 bytes, a factor of 81. Composed live context went 705 ->
1,358 bytes, peaking at 3,762. Active state peaked at 1,036 against the 4,096 guard. At the end
the live context is 2.6% of the history it can still reach, and 21,951 bytes of tool output never
entered context at all while staying retrievable by event id. I am naming the peak rather than
smoothing it: context tracks the size of the latest observation, so one large kept tool result
moves it. What it does not track is the length of the run.

**H3.** At the boundary the object was destroyed and rebuilt from `state.json` and
`history.ndjson` alone. Phase, state digest, history head digest, event count and artifact status
all identical. The part that makes it more than a serialization test: an early decision archived
out of active state by the list bound was still recoverable, was recalled on demand, and did not
reinstall itself into active state afterwards. Retrievable is not the same as always present.

**H4 and H5.** Eleven fail-closed cases, all closed, none silently repaired: illegal transition,
`done` with no receipt, `done` with a failing receipt, artifact mutation after completion, stale
revision, type violation, phase change attempted via patch, unknown field, the whole history
stuffed into a state field, a missing history reference, a tampered history event caught by the
hash chain, and a restart with no persisted state. H5 is the artifact one: after `done` was
legitimately earned, the receipt file was edited and both the artifact status and the completion
gate rejected it. State said valid; the artifact disagreed; the artifact won.

**a bug I introduced and fixed before publishing.** My first cut kept accept/reject counters in
memory and persisted them only on success, so the restart quietly reset the rejection counts to
zero — a counter that reads clean because the evidence was lost. Counts are now derived from the
history log itself, which is the only record that survives a restart by construction. Published
numbers are patches 25 accepted / 2 rejected, transitions 6 accepted / 2 rejected.

**files.** `src/memory_bakeoff/pi_state_control/{contract,runtime}.py`,
`extensions/pi_state_control/{pi_state_control.ts,verify_pi_extension.ts}`,
`scripts/run_pi_state_control_gen43.py`, `scripts/build_pi_state_control_gen43_report.py`,
`tests/test_pi_state_control_gen43.py` (27), `research/PI_STATE_CONTROL_GEN43_PROTOTYPE.md`,
`results/pi_state_control_gen43/` (identity, contract, synthetic_trace, trace_metrics,
restart_recovery, corruption_tests, scientific_digest). `ARCHITECTURE.md` gains a small dated
pointer that separates the measured prototype facts from the still-unmeasured agent hypotheses;
the thesis itself is unchanged. RESULTS and STATUS gain labelled no-score pointers.

**H6 stands unmeasured, as preregistered.** No model produced any of these bytes. The context
numbers are composed-context bytes under this prototype's composer, not tokens under a pinned
model, and there is no comparison against Pi's ordinary assembly under load.

**commit.** `8ebc829` (base `2520858`)

**Gen44 recommendation — do not execute.**

Design the controlled paired pilot, and bring me the model decision rather than making it.

Arms: **A** ordinary Pi context behaviour; **B** Pi plus this extension with history externalized.
I would hold C (on-demand retrieval) back until B is stable, because C changes two things at once
and the interesting failure in B is whether the composed view is *sufficient*, not whether
retrieval works.

Hold fixed: Pi 0.73.0, the extension sha, the tool set, a pinned repository snapshot, the task
set, and the environment. Harness-owned measurements only: deterministic verifier pass/fail,
exact context bytes at each provider request, input/output tokens if the pinned path exposes an
exact tokenizer, tool calls and repeated tool calls, turns, wall clock, and every control/state
rejection. Controlled repeats per task, because a single run of a coding agent measures noise.

Two things Gen43 says the design must survive contact with. The composed view is currently one
message; a real model may need the last few turns as well, and that is a design parameter which
must be **fixed before the pilot runs**, not tuned once success rates are visible. And `done`
being artifact-gated will produce runs that stop short rather than declare victory — that is the
intended behaviour, but it will look like failure in a naive success metric, so the verifier has
to distinguish "stopped correctly" from "failed".

The model is your call and Brian's, not mine to spend silently. The candidates I would put to him
are a local Strix Halo model on the inference server, or a pinned hosted model for lower variance.
I have not run either and I am not choosing between them here.

## Generation 42 — MemBukkit intended models on the MemConflict calibration slice

**status:** complete. `external_benchmark_calibration_raw_product_exact_provenance`, lane
`memconflict-exact-whitebox-v1`, three frozen development-exposed personas, no reader, no
upstream judge, no full release. Base `eaef85a`, full suite 283 passed (265 baseline + 18 new)
with the one pre-existing warning.

**the Gen8 erratum, first, as instructed.** `research/MEMBUKKIT_FALLBACK_GEN8.md` now carries a
labelled `Post-Gen41 correction (2026-09-04)`. The original runtime bullet is preserved verbatim
and no metric on that page changed. The note says the CPU attribution was never backed by a
runtime device trace and is withdrawn; that forced CPU does not reproduce the page's stress
behaviour while product-default does reproduce it exactly; and — the part I was careful about —
that because Gen8 recorded no device trace, the historical device cannot be stated as directly
measured fact, only that the evidence is consistent with product-default MPS. The Gen41 report
now labels its own version of that sentence as an inference from replication rather than a
historical trace.

**adapter frozen before exposure.** `membukkit-memconflict-adapter-v1`, sha
`67b80e22625d2e8c84259d600d9f783a04012d3bdd43037f7fde56018231140b`. Indexed text is the released
message content alone; the write receipt is an opaque ordinal assigned in write order, never a
persona, session, turn or question identifier, and never indexed; the query is the released
question text alone. Preflight on invented content only: bad payloads rejected including one
carrying a session id, six of six synthetic writes mapped, two messages with identical text kept
as two rows under distinct receipts, store isolation between universes, reads leaving the state
digest unchanged, the LLM path refusing rather than merely unused, and the frozen chronology
function raising on a future-session unit. No benchmark fixture is opened anywhere in the
preflight.

**one product property you should know about, because it decided how rank is read.** MemBukkit
selects by relevance and then re-presents the selected hits **in date order**. The public
`MemorySearchResult.hits` order is therefore a presentation property, not a ranking — taking rank
off that surface would have scored a date sort and quietly produced a wrong number for every
rank-sensitive metric in the lane. The adapter reads rank from the relevance order the product
returns internally and requires, per query, that it holds exactly the same records the public
surface returned. That equivalence is proven on all 399 questions, not asserted once. Native
`search(..., top_k=5)` was used, so no harness postfilter exists.

**how it ran.** The frozen Gen37 procedure was imported and executed unchanged — Gen42 registers
an engine into it rather than reimplementing it — and the frozen Gen37 scorer and Gen38
static-mechanism diagnostic produced the numbers, so they are comparable with the committed
calibration by construction rather than by resemblance. Source `f28a2e58`, intended MemseekAI
models reconciled file by file against the Gen41 manifest offline, both proven on `mps:0`, Gen41
raw-product retrieval with `union_lanes=("atomic",)`, network blocked at the socket layer before
the first write, no distiller and no LLM.

**totals.** 14,304 writes of 14,304 attempted, 3 malformed messages excluded and counted, 14,304
distinct native ids, 0 write failures, 0 native id replacements, 399 questions, 380 measured and
19 unmeasured — the same measured denominator as the committed Perseus and Mem0 calibration, so
the columns line up question for question.

**result.** Hit@2 0.2684, **Hit@3 0.3237**, Hit@5 0.4079, log-rank@3 0.2621. Committed context on
the same denominator: Perseus 0.4421, Mem0 0.4737, BM25 pilot 0.2895. By class, Hit@3: dynamic
0.3175 (Perseus 0.4222, Mem0 0.4476), static 0.1389 (0.1667, 0.2778), conditional 0.6207 (1.0000,
1.0000). Integrity: zero unmapped provenance, zero empty returns, zero returns under five, zero
future-session leakage, inventory reconciling on all three personas. Determinism: 8 label-blind
repeat probes, order identical 8/8, selected set identical 8/8, numeric scores identical 8/8,
reported as three quantities.

**the finding, and it is a mechanism one.** Gen38 inferred from an admission diagnostic that
static failure in Perseus and Mem0 is ranking, not availability. MemBukkit lets that be measured
rather than inferred, because its router opens only part of the bank before the cross-encoder
sees any candidate — so unreachability and rank loss are physically separable here.

Of 36 static questions, gold support was present in the write ledger for all 36. Six hit at five.
**All 30 misses had their gold support inside the opened candidate region.** Routing exclusion
accounts for 0% of static misses and rank loss for 100%, with the router opening a median 32.05%
of the bank. A third engine, architecturally unlike the first two — topic routing, a fine-tuned
cross-encoder, rank fusion instead of a vector store with a scoring head — loses the old truth at
the ranking stage while the record is stored, searchable, and already in the candidate set the
reranker scores. The scorer-side split agrees: at K3, 25 of 36 static questions return neither the
truth session nor the contradicting one, 6 return the contradiction without the truth, 4 the truth
alone, 1 both. "Retrieval prefers the newer contradiction" is a minority mechanism here too.

**where MemBukkit differs qualitatively.** Conditional questions: Perseus and Mem0 both sit at
1.0000 on this slice, MemBukkit at 0.6207. That single class is most of the overall gap and is the
one place this product behaves differently in kind rather than by a few points. On 29 measured
conditional questions across three development-exposed personas it is worth naming and not worth
ranking.

**operations, secondary.** Write p50 about 22 ms, query p50 1.74 to 1.94 s, roughly six minutes
per persona. The query cost is the cross-encoder scoring the opened region every time. Scan
fraction p50 0.3205, p90 0.3422, max 0.3617 over 399 queries, derived from the native trace
because `scan_fraction` is not a key the native trace carries — I derived it from `n_scanned` and
`n_facts` rather than publish an empty field.

**files.** `src/memory_bakeoff/providers/membukkit_memconflict.py` (frozen adapter),
`src/memory_bakeoff/memconflict_engines_gen42.py` (engine, kept in its own module so no Gen37 or
Gen38 file is touched), `scripts/preflight_membukkit_gen42.py`,
`scripts/run_membukkit_gen42_calibration.py`, `scripts/build_membukkit_gen42_report.py`,
`scripts/build_membukkit_gen42_doc.py`, `tests/test_membukkit_gen42_calibration.py` (18),
`research/MEMBUKKIT_MEMCONFLICT_GEN42_CALIBRATION.md`,
`results/membukkit_memconflict_gen42_calibration/` (identity, preflight, three persona leaves and
ledgers, calibration report with scientific digest `7f133d612cfa2e3d…`). RESULTS.md and
STATUS gain clearly labelled calibration rows. No Gen36, Gen37 or Gen38 artifact was modified; no
weights or product DB committed.

**commit.** `23d85f5` (base `eaef85a`)

**Gen43 recommendation — do not execute.**

**The first Pi state/control prototype.** Gen42 produced no surprise large enough to defer it.

The test you set was whether MemBukkit's routing trace reveals a *distinct* cause. It reveals a
sharper measurement of the *same* cause. Three unrelated architectures now fail static conflict at
the ranking stage with the evidence present and reachable, and MemBukkit is the one that could
have shown otherwise and did not. That is corroboration, and corroboration is exactly the
condition under which you said to move.

The conditional gap — 0.62 against two engines at ceiling — is the only candidate for a
surprise, and it fails the bar you set. It is a product-quality difference on 29 questions in a
development-exposed slice; it changes no architectural claim, and chasing it into a full release
would be leaderboard curiosity of precisely the kind you ruled out. If it is ever worth pursuing
it is as a MemBukkit product question, not as an architecture one.

So the highest-value uncertainty is now the one Gen39 wrote down and nothing since has tested: can
explicit structured execution state plus executable control cut prompt replay and tool churn
without lowering coding-task success, while full history stays recoverable out of context. Gen38
said further memory-component scores will not move the static finding; Gen40 through Gen42 have
now spent three generations confirming that a fourth product measurement does not either.

## Generation 41 — MemBukkit intended models on the frozen Round1 raw-product ruler

**status:** complete. Existing `raw_product` evidence class, configuration-scoped to *MemBukkit
intended models*. No new lane. Gen7, Gen8 and Gen40 artifacts are untouched. Base `275e4df`,
full suite 265 passed (243 baseline + 22 new) with the one pre-existing warning. 24 scored runs:
2 device policies x 2 configurations x core/stress x 3 repetitions.

**your CPU instruction was built on a wrong premise, and the replication control is what found
it.** `MEMBUKKIT_FALLBACK_GEN8.md` records Gen8 as running on CPU. It did not. Forcing both
models onto CPU, the stress condition does not reproduce Gen8 — MRR 0.5535 to 0.5431 and 9 of 26
queries reordered. With the product's own device selection both models load on `mps:0` and Gen8's
committed metrics reproduce **exactly**, in both conditions. The Gen8 document's claim was never
checked because nothing depended on it until this generation.

So device cannot be both "equal to Gen8" and "CPU". Rather than pick one and lose the other, and
before reading any intended-model result, I declared a tolerance in the gate and ran **both**
policies, each internally device-matched across the two model configurations. `product_default`
is the replication anchor; `cpu` honours your accelerator rule. Each is a valid ablation on its
own, and the pair answers whether the result survives the device choice. That is a deviation from
your gate as literally written and I am flagging it as such. Note also that the local Metal
accelerator is used in the `product_default` policy, which your brief forbade — it is the only
way to reproduce Gen8, no inference server or remote accelerator is involved, and the `cpu`
policy is published beside it so nothing rests on the accelerator alone.

**gate.** Product-default control: zero metric differences from Gen8 in both conditions; two
stress queries return the same items in a different tail order and move no metric. CPU control:
core identical, stress deviating only in MRR as above. Provenance verified and publishable on all
24 runs, repeats byte-identical in returned ids everywhere.

**pins.** MemBukkit source `f28a2e58`, asserted by `git rev-parse` in the parent. Intended
`MemseekAI/membukkit-biencoder-v1@50ab0a1f` and `membukkit-reranker-v2@0b46ab53`, reusing the
Gen40 snapshots. Fallback `all-mpnet-base-v2@e8c3b32e` and `ms-marco-MiniLM-L-6-v2@233902d2`,
freshly acquired at those exact revisions. Every file reconciled to its revision by LFS sha256 or
recomputed git blob oid; zero mismatched, zero local-only. Only loader files are downloaded, so
reconciliation is scoped to the downloaded manifest and says so. One provenance detail: the
fallback reranker id named in the pinned source now redirects — Hugging Face renamed the repo to
`cross-encoder/ms-marco-MiniLM-L6-v2`. Same revision, new name.

**integrity.** Frozen retrieval config asserted at the start of every run against the committed
provider, `union_lanes=("atomic",)` included. Every load target checked against the expected
pinned directory and against the other configuration's directories, so a cross-load fails rather
than passes. Zero downloads inside any scored run, network blocked at the socket layer, no LLM,
no reader, no external API. Device read off each constructed model, not off the request.

**result. The deltas agree across both device policies in sign and, apart from MRR, to four
decimal places.**

Core: Hit@5 unchanged at 1.000. MRR 0.5854 to 0.6417, +0.056. All-relevant@5 1.000 to 0.9583,
−0.042 — the one metric where the fallback pair was already at ceiling. Prohibited@5 0.1250 to
0.1083. Useful-before-harmful unchanged at 0.6875. Mean context chars +26.3.

Stress: Hit@5 0.8750 to 0.9167, +0.042. All-relevant@5 0.7500 to 0.8333, +0.083. Prohibited@5
0.0667 to 0.0583. Useful-before-harmful 0.6923 to 0.7143. But MRR 0.5535 to 0.4486, −0.105 under
product-default and −0.088 under CPU.

**the intended models find more and rank worse.** In the harder condition they surface the
relevant record more often and admit fewer prohibited items, then place it lower in the list.
Latency is unchanged at stress, 256.8 against 256.7 ms product-default.

**the number I would not have published from the aggregates alone.** The two configurations
return a different top 5 on 22 of 26 core queries and on all 26 stress queries. Almost every
answer changes; the metrics move by hundredths. A 26-query corpus cannot resolve a change that
large, and I would not let anyone read these deltas as a ranking of the two model pairs.

**files.** `src/memory_bakeoff/membukkit_gen41.py` (configurations, pins, device shim and proof,
leaf readers), `scripts/run_membukkit_gen41_round1.py`, `scripts/build_membukkit_gen41_report.py`,
`tests/test_membukkit_gen41_round1.py` (22), `research/MEMBUKKIT_INTENDED_ROUND1_GEN41.md`,
`results/membukkit_gen41_manifest/` (pins, gate with its declared tolerance, comparison) and 24
run directories. No model weights or product DBs committed. RESULTS.md gains one
configuration-scoped row beside the Gen8 row, which is unchanged; STATUS gains a pointer.

**one thing for you to decide, which I did not act on.** `MEMBUKKIT_FALLBACK_GEN8.md` states its
models ran on CPU and that is now measurably false. You told me to preserve it unchanged and I
have. It is a wrong sentence in a published artifact that another generation could build on, as
this one nearly did. Say whether a labelled correction note belongs there.

**commit.** `67b5d7d` (base `275e4df`)

**Gen42 recommendation — do not execute.**

**MemBukkit MemConflict calibration**: three personas, retrieval-only, no reader, no full release.

The case is about resolution, not curiosity. Gen41 says the model swap changes nearly every
returned list while moving aggregate metrics by hundredths. That is exactly the signature of a
ruler with too few queries to answer the question being asked of it — 26 cases against
MemConflict calibration's ~399. Gen41 therefore **raises** the value of MemConflict calibration
rather than lowering it: we now know there is a large behavioural difference to measure, and
Round1 cannot measure it. It also takes MemConflict coverage to three unrelated products, so the
static-conflict finding from Gen38 would rest on three engines rather than two.

Against the alternatives. Hindsight and agentmemory calibration adds engines without closing a
question any earlier generation left open. The reader lane still adds a dependency, a failure
surface and an authorization decision ahead of any evidence need for it. The Pi state/control
prototype remains the highest-value question in the whole programme.

And the honest caveat on my own recommendation: this should be the **last** product-ranking
generation unless it produces a surprise. Gen38 put two engines within a point of each other and
within three of BM25 on static conflict, and Gen39 argued the missing capability is not inside
the memory component. If MemBukkit lands in the same band, the answer to "is more product ranking
the highest-value question" is no, and Gen43 should be the Pi state/control prototype regardless
of what Gen42 returns.

## Generation 40 — MemBukkit intended-model path reproduced (no score)

**status:** complete, and the historical blocker is closed. Evidence class
`product_identity_reproduction_no_score`. No benchmark corpus, no reader, no external LLM, no
GPU, no product database. Base `c4e49bb`, full suite 243 passed (225 baseline + 18 new) with the
one pre-existing warning.

**the historical question, answered on the historical source.** The checkout used is the exact
Gen7 pin `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807`, verified by `git rev-parse` inside the run
and recorded in the leaf. The intended-model names are still at
`src/membukkit/models/registry.py:23-26`, with the fallback branches at lines 97 and 120; those
exact lines are quoted in the report. No newer MemBukkit revision was substituted and none was
needed, so the `current_upstream_compatibility_diagnostic` that Gen40 reserved for a failure was
not run.

**both model repositories are now public and pinned.**
`MemseekAI/membukkit-biencoder-v1` at revision `50ab0a1fefa47c44d6d66f530dea2d3ea426f5b3`,
sentence-transformers / sentence-similarity, apache-2.0, 12 files.
`MemseekAI/membukkit-reranker-v2` at revision `0b46ab535caa4044542889dd76a15868799aabbe`,
no library or pipeline tag and no license on the card — recorded as absent, not inferred, 7 files.
Neither is private or gated. Weight identity: bi-encoder `model.safetensors` 437,967,672 bytes
sha256 `92deea14f506ebfd…`, reranker 90,866,412 bytes sha256 `038f449571ac2716…`. Every file in
both snapshots was reconciled to its published revision — large files by LFS sha256, small files
by recomputing the git blob object id locally, so no file is pinned by name alone. Zero
mismatched, zero local-only, zero missing.

**fallback cannot be mistaken for success.** The resolver, the hub client and both model
constructors are wrapped as observers; every wrapper forwards to the original and records only
what passed through it, so embeddings and ranking cannot be altered. The run fails if a
substitute repo is requested, downloaded or loaded, or if either model loads from anywhere but
the pinned snapshot directory. Result: zero fallback events, both models loaded from the pinned
snapshots, zero LLM invocations in both phases.

**offline repeat is proof, not assertion.** The second phase runs in a fresh process with
outbound connections blocked at the socket layer, so a silent re-download raises. It downloaded
nothing, resolved the same two revisions, and returned an identical ordered id list on 8 of 8
queries with identical probe values.

**synthetic preflight.** 60 invented facts about a fictional preservation society and 8 fixed
queries, written before any model output was observed and unrelated to every corpus here.
Bi-encoder loads and embeds: shape [4, 768], all finite, rows normalised. Reranker loads and
scores: 4 finite scores. End to end: 60 written, 60 new, backend count 60, all 8 queries served
through both intended models. Provenance is exact — every returned item maps to its synthetic
write receipt, zero unmapped ids. Repeat over unchanged state: order stable and selection stable,
reported as separate quantities per Gen38.

**things worth your attention, none of which I tuned.** The two off-topic queries return a full
top_k of 10 like every other query; the product applies no relevance floor on this surface. I did
not invent a pass threshold after seeing that — it is recorded as behaviour. `ModelConfig.device`
reaches the reranker but not the bi-encoder: the encoder wrapper passes only a path to
`SentenceTransformer`, which picks its own device, so one `device="cpu"` request produced encoder
on `mps:0` and reranker on `cpu` in the same process. Recorded, not overridden. And the lifecycle
answer to your question: on this direct fact-ingest path the product is append-and-dedupe only.
Re-offering the identical 60 facts wrote 0 new rows, while one dated fact contradicting a stored
one was appended as row 61 with **both** left `current` and zero superseded hits. MemBukkit's
supersession machinery sits on the LLM distiller path, which Gen40 deliberately did not exercise.

**pipeline characterization** (source read alongside runtime observation): the same bi-encoder
embeds writes and queries; routing partitions into 24 topic buckets and opens a scan budget,
measured at 18-20 facts scanned of 60, scan fraction 0.30-0.33; the cross-encoder acts after
candidate generation over the opened region only; `candidate_pool=50`, `rerank_cap=50`,
`top_k=10`; fusion is `select="hybrid"`, RRF over cross-encoder rank and cosine rank with
`k_rrf=60`, so cosine and cross-encoder scores are **not** directly comparable — only ranks are
combined; the optional lexical lane is off. Selection is by relevance but presentation is
temporal, so returned order is a presentation property. Store is the in-memory backend.

**determinism.** The offline digest rebuilds byte-identically across a second complete run into a
scratch directory. The online digest is deliberately not stable across cache states: the
committed leaf was produced after deleting the model cache so it records the real acquisition,
and a warm repeat differs in exactly `load_trace` and `snapshot_cached_before_run` and nothing
else. Every measured quantity is identical in both.

**files.** `src/memory_bakeoff/membukkit_gen40.py` (contract: fixture, fallback detection,
content identity, digest), `scripts/run_membukkit_gen40_preflight.py`,
`scripts/build_membukkit_gen40_report.py`, `tests/test_membukkit_gen40_intended_model.py` (18),
`research/MEMBUKKIT_INTENDED_MODEL_GEN40.md`, `results/membukkit_gen40_intended_model/`
(model_pins.json, online.json, offline.json, comparison.json). No model weights and no product DB
are committed. `research/MEMBUKKIT_INTENDED_MODEL_GEN7.md` is untouched; Gen40 links backward to
it. RESULTS.md and STATUS_AND_FINDINGS.md gain clearly-labelled no-score pointers.

**commit.** `2b06107` (base `c4e49bb`)

**Gen41 recommendation — do not execute.**

Re-enter the **frozen Round1 raw-product ruler** with the intended models, at the existing
configuration scope, adding no new lane.

It is the smallest fair step. Round1 is where MemBukkit already has a row and where every other
engine has a comparable one, so the reproduction converts directly into the comparison it was
always meant to support, with no new contract, no new evidence class and no reader.
MemConflict calibration is the larger move — a new adapter plus the three-persona calibration —
and it should follow, not precede, the ruler MemBukkit was originally measured against.
longitudinal-v1 I would put last: Gen40 just measured that this ingest path performs no
supersession at all, so a lifecycle ruler would mostly measure the absence of a mechanism.

I checked the condition rather than leaving it to you. Round1's MemBukkit `raw_product` row is
the Gen8 documented-fallback run, and `research/MEMBUKKIT_FALLBACK_GEN8.md` records that it
ingested through upstream `MemorySystem.ingest_facts` with no distiller and no LLM — the exact
surface Gen40 exercised, on the same pinned upstream commit. So re-entry needs no reader and no
authorization decision: it is a single-variable swap of the model weights on a frozen ruler, the
cleanest comparison this project has had available.

Two scope details Gen41 must match or the swap stops being single-variable. Gen8 ran the atomic
lane only, while Gen40 used the shipped default of both union lanes; Gen41 should hold Gen8's
`union_lanes` scope. And Gen8 ran both models on CPU, whereas Gen40 measured the encoder ignoring
`ModelConfig.device` and selecting `mps:0`; Gen41 needs an explicit lever for that, outside
product semantics, or device becomes a second variable.

## Generation 39 — architecture synthesis (documentation only)

**status:** complete. No benchmark exposure, no contestant score, no MemConflict run, no reader
lane, no LLM judge, no product DB build, no GPU. No frozen contract, result or artifact was
modified. HEAD confirmed at `0d26fcd` before any edit.

**files changed (3, all documentation):**
- `ARCHITECTURE.md` — new, 271 lines. Sections A–J as requested: one-page thesis, why one giant
  transcript is the wrong abstraction, the eight layers, authority/flow rules, the system-to-layer
  mapping, the evidence that led here, implications for a coding agent, the evaluation roadmap,
  falsifiable open questions, references.
- `EXPERIMENT_PLAN.md` — 3,382 bytes preserved byte-for-byte; 1,552 bytes appended as a dated
  "Architectural synthesis (added 2026-09-04, after Gen38)" section that links ARCHITECTURE.md and
  states explicitly that nothing above it was revised. No historical language touched.
- `README.md` — a five-line pointer block near the top. No result text altered.

**evidence boundaries, enforced in the document itself.** §F.1 internal measured evidence, drawn
only from committed artifacts and labelled as a summary of them rather than a new source. §F.2
external research, and this is the part worth your attention: I verified only two primary sources
and used only those. StateFlow (arXiv 2403.11322) — state-machine formulation, transitions "controlled
by heuristic rules or decisions made by the LLM", 13%/28% over ReAct on InterCode SQL and ALFWorld at
5x/3x less cost. FrontierHarness (frontierharness.org) — model held fixed at Kimi K3, 9 harnesses in
12 configurations, 360 trials, pass rate 50.0–66.7%, median cost per task $1.05–$18.34, with the
authors' own caveat that it is software-engineering specific and that quality and cost can diverge.

**what I did not assert.** Your brief described StateFlow as retaining cumulative context history
across states. The abstract does not say that, so the document says the abstract does not address it
rather than repeating the claim. §F.3 lists SKILL.state, SMAG/Thinker, ontology-to-tools, LLM-as-Code,
LOM-action, FAOS and TFlow as referenced in project discussion but NOT verified in Gen39, and states
plainly that no claim in the document rests on them. They informed the vocabulary; they are not cited
as evidence. §F.4 marks every architectural section as inference, with the falsifiable form in §I.

**the layer model** is as you specified, by responsibility rather than vendor, with latent/parametric
adaptation kept as an explicit side branch. The authority rules include the two that this project
learned the hard way: artifacts outrank recollection, and a state field like `persona_14_complete`
must carry or point to a validated digest rather than become a competing truth source — Gen38's
resume rule is exactly that principle in code. Control and state are kept distinct with a concrete
example: the calibration gate is control, "persona 17 of 27" is state.

**the argument the evidence actually supports**, stated in §A and §F.1: neither better retrieval nor
automatic retirement solves currentness. Gen38 puts two production engines within a point of each
other and within three points of BM25 on static conflict; Gen35 shows the one engine that decides
currentness by similarity trades false persistence for false supersession. So the missing capability
is not inside the memory component, which is what justifies the layered frame rather than a better
memory product.

**validation.** Relative-link check across all three documents: zero broken links. Full suite 225
passed with the one pre-existing warning, matching the expected baseline exactly. Documentation-only
change, so no digest or result is affected.

**commit.** `d33971f` (documentation only; parent `0d26fcd` is the Gen38 release commit)

**Gen40 recommendation — one move, not executed.**

I recommend **(b) MemBukkit's intended path, reproduced first**, ahead of the other three.

The reasoning is about what each option would actually settle. (a) Hindsight and agentmemory at
MemConflict calibration scale would add two more points to a curve whose shape we already know: three
unrelated engines have now produced the same seven failure classes, and Gen38 showed the interesting
variance is between conflict classes, not between products. agentmemory is a genuinely sharp test —
its Jaccard retirement will fire constantly at 4,700 messages per persona — but Gen35 already told us
what retirement does, and MemConflict would only re-measure it in a second setting. (c) The reader
lane adds a new dependency, a new failure surface and an authorization decision, on top of a lane that
is currently clean; it should follow evidence, not precede it. (d) The Pi state/control prototype is
the highest-value question in the whole architecture, but it is also the one where component identities
are least pinned, and running it now would confound state design with memory choice.

MemBukkit is different because it closes an uncertainty we created and never resolved. It was the
intended-default engine, its intended path was blocked by missing biencoder/reranker weights, and it
has been carried as an asterisk ever since. The weights are now public. Reproducing the previously
blocked intended path — before any benchmark expansion — converts a standing unknown into either a
result or a documented product limitation, at calibration cost, with no new evidence class, no reader,
and no contamination of the frozen lanes. It is also the cheapest of the four, and the only one that
retires a debt rather than opening a new line.

If that reproduction fails, the failure is itself the answer and (a) becomes the natural next move.

## Generation 38 — MemConflict at full release: Perseus and Mem0, exact provenance

**status:** complete, both engines plus the frozen BM25 baseline. Evidence class
`external_benchmark_full_release_raw_product_exact_provenance`. Not an upstream/official
MemConflict white-box score; `upstream_llm_judge` remains `requires_reader_authorization` and was
not run. No reader, no LLM, no external API, no GPU.

**scale.** Each engine: 30 personas, 142,093 well-formed message writes, 3,750 questions, fresh
persona-isolated stores. Primary slice is the 27 personas outside the calibration subset; the fresh
30 is secondary; the calibration 3 exists only for replication.

**pins.** Contract `0521210818e448c8…`, dataset `8ef9ec8589eccb86…` at upstream `ec51d5d`, Gen36
calibration manifest, adapters byte-for-byte from Gen37 (`627f812d5296130c…`, `920f496be7470fca…`),
all re-asserted inside every persona run. 36 malformed messages excluded by the frozen list; 181
conditional questions remain UNMEASURED. Two declared instrumentation fixes, neither touching writes,
queries or ranking: Mem0's in-run inventory is explicitly UNMEASURED rather than a `get_all` page,
and Perseus repeats use the same session-boundary snapshot (with a regression test rejecting the old
final-snapshot design). Persona is the atomic restart unit; leaves are temp-then-rename with their own
digest and are only skipped when every pin, count and digest validates.

**replication gate — the interesting part.** Mem0 reproduced its Gen37 calibration leaves EXACTLY:
zero ordering differences, zero score mismatches, zero hit@3 class changes over 380 measured
questions. Perseus did not: 77 of 399 questions returned a different order, every one with a
byte-identical score vector containing ties. Perseus's hybrid RRF produces tied scores whose order is
stable within a run but not across runs against a fresh vault, and at the rank-5 cutoff that also
changes which tied item survives. Measured effect: 2 of 380 measured questions changed hit@3 class
(0.53%), calibration hit@3 0.4421 -> 0.4474. Before any held-out persona ran I declared a tolerance —
ordering differences must be fully tie-explained, scores and applicability must match exactly, hit@3
class changes must stay under 1% — and the gate passes on that basis with the instability published
as its own quantity. That is a deviation from the gate as literally written; the same harness
producing a byte-identical Mem0 replication is what identifies the instability as the product's.

**primary result, 27 held-out personas, 3,189 measured / 162 unmeasured:**

| | hit@2 | hit@3 | hit@5 | log-rank@3 | dynamic | static | conditional |
|---|---|---|---|---|---|---|---|
| Perseus | 1,267 (0.397) | **1,484 (0.465)** | 1,814 (0.569) | 0.385 | 0.434 | **0.343** | 0.987 |
| Mem0 | — | **1,455 (0.456)** | — | 0.386 | 0.419 | **0.383** | 0.974 |
| BM25 | — | 909 (0.285) | — | 0.237 | 0.226 | 0.312 | 0.914 |

Contract integrity for all three: zero unmapped provenance, zero empty returns, zero returns under
five, zero future-session leakage, zero write failures.

**H1 holds** (contract clean). **H2 holds**: static is Perseus's weakest class outright and Mem0's
weakest substantive class. **H3 holds**: conditional is near ceiling for both. **H5 respected**: see
the interval below. **H6 holds**: Mem0's inventory reconciles exactly on all 30 personas. **H7**:
Perseus quarantined 224 writes across the release, measured not predicted. **H8** needs its two parts
separated — see determinism.

**slice agreement.** Perseus 0.447 calibration / 0.465 held-out / 0.463 full; Mem0 0.474 / 0.456 /
0.458. Development exposure of the three calibration personas did not inflate them.

**static mechanism diagnostic (scorer-side, posthoc).** Perseus, of 324 static questions: 60 return
truth and contradiction, 82 truth only, 86 contradiction without truth, 96 neither. Mem0: 43 / 81 /
78 / 122. So "retrieval prefers the newer contradiction" describes about a quarter of static
failures; a third return neither session at all, which is unreachability rather than competition. A
bare hit rate would have merged two different problems.

**admission diagnostic.** Perseus quarantined 199 writes across the 27 held-out personas, in every
one, each with a native reason string (`quarantined (interference score 0.9xx > bound 0.900)`).
Static misses: 197 with gold support fully admitted, 16 partly quarantined. Mem0 quarantines nothing
and still misses 200 static questions with fully admitted support. Static failure is a ranking
problem in both engines, not an availability problem.

**paired analysis, 27 held-out personas.** At K=3: both 1,117, Perseus-only 367, Mem0-only 338,
neither 1,367 — they disagree on 705 of 3,189 questions. Persona-block bootstrap with the contract
frozen before reading outcomes (seed 20260903, 10,000 resamples, resampling personas): Mem0 minus
Perseus hit@3 mean −0.0097, median −0.0089, 95% interval **[−0.0273, +0.0095]**. The interval
straddles zero; no winner on this lane.

**BM25 context.** The engines beat the lexical baseline by ~20 points on dynamic questions and by at
most 3 on static (0.343 and 0.383 against 0.312). On the class this benchmark exists to probe,
embeddings buy very little.

**operations, versus Gen37's projections.** Perseus 5.69 h / 1.64 GB against 5.8 / 1.65 projected
(ratio 0.981); Mem0 14.97 h / 1.71 GB against 14.7 / 1.73 (ratio 1.018). No nonlinear slowdown at
all: write p50 first third versus rest is 141.82/141.83 ms (Perseus) and 361.33/361.20 ms (Mem0). The
BM25 baseline took 173 s for the whole release. Zero write failures anywhere.

**determinism.** Returned session order was identical in 84 of 84 repeats for both engines. In 4 of
Mem0's 84 the float scores differed while the order held; re-running one afterwards against the
persisted store reproduces the scores exactly, so it is float non-determinism in the ONNX embedding
path under CPU load and changes no hit, rank or log-rank. Validation reports order stability and
score identity separately rather than collapsing them into one "stable" boolean.

**artifacts.** `scripts/run_memconflict_gen38_full_release.py`,
`scripts/gate_memconflict_gen38_replication.py`, `scripts/run_memconflict_gen38_bm25.py`,
`scripts/build_memconflict_gen38_report.py`, `research/MEMCONFLICT_GEN38_FULL_RELEASE.md`,
`results/memconflict_gen38_full_release/{perseus,mem0,bm25}/` (90 leaves + ledgers) plus
`heldout-27-derived.json`, `full-30-derived.json`, `calibration-replication.json`,
`static-mechanism-diagnostic.json`, `paired-analysis.json`, `inventory-reconciliation.json`,
`operations.json`, `validation.json`, `content-digest.txt`, and
`tests/test_memconflict_gen38_full_release.py`. Scientific digest
`aff8855d35d139ae59eb532fa7141f6d98279ddc15d666feb906a58238609fb7`, rebuilt byte-identically. 20
focused tests; full suite 225 passed with the one pre-existing warning.

**Gen39 recommendation, not executed.** Hindsight Gen31 and agentmemory Gen33 at CALIBRATION scale
first, never straight to full release. agentmemory is the sharp test: its Jaccard retirement fired
twice on a 16-message fixture and will fire constantly at 4,700 messages per persona, and Gen35
showed retirement trades current-state failures for history failures — MemConflict's static class is
exactly a history question. The reader lane is the alternative if answer-level metrics are wanted;
its constraints are already in the Gen36 contract.

## Generation 37 — Perseus and Mem0 on MemConflict, calibration scale

**status:** complete, both engines. Evidence class `external_benchmark_calibration_raw_product`,
development-exposed, three personas. Not an official MemConflict score, not full-release, not blind.
Scored lane is the benchmark-owned `memconflict-exact-whitebox-v1`. No reader, no LLM, no external
API, no GPU. `upstream_llm_judge` remains `requires_reader_authorization`.

**frozen before exposure.** Contract `memconflict-benchmark-v1` `0521210818e448c8…`, dataset
`8ef9ec8589eccb86…`, upstream `ec51d5d`, the three Gen36 calibration persona ids unchanged. Adapters
hashed at preflight and verified again inside every run: Perseus `627f812d5296130c…`, Mem0
`920f496be7470fca…`. Perseus is the Gen29 identity (v2.23.2 `9c82920`, operator CLI write, native
hybrid recall, limit 5, fresh encrypted vault per persona, queries served from a byte-for-byte
snapshot). Mem0 is the Gen32 identity (2.0.19 from the pinned checkout, `add(infer=False)`, embedded
on-disk Qdrant, FastEmbed dense + BM25 sparse, threshold 0.1, limit 5, fresh store per persona, no
metadata written). One released message = one write; indexed text is the message content only.

**preflight.** 29 checks on unrelated synthetic content, all passing, before either product saw a
calibration question: pinned identities, one message one write, persona isolation, reads leaving the
store digest unchanged, native order preserved, every hit mapping through the ledger, no identifiers
in indexed text, recursive rejection of every scorer-only field and of any future session.

**contract integrity during the run.** Identical for both engines: 14,304 writes, 399 questions,
0 unmapped provenance, 0 empty returns, 0 returns shorter than 5, 0 future-session leakage, reads
left state unchanged at every audited session, and 8/8 label-blind repeat questions byte-identical in
returned session order and score.

**exact-provenance results** (380 measured, 19 unmeasured — the conditional questions Gen36 marked
unaddressable, excluded from denominators rather than scored zero):

| | Perseus | Mem0 |
|---|---|---|
| hit@2 | 147 | 150 |
| hit@3 | **168 (44.2%)** | **180 (47.4%)** |
| hit@5 | 207 | 232 |
| log-rank@3 | 0.376 | 0.392 |
| dynamic (315) | 133 | 141 |
| static (36) | **6** | **10** |
| conditional (29) | 29 | 29 |
| rank-1 hits | 107 | 107 |
| no hit | 173 | 148 |

Gen36's frozen BM25 baseline was 110/380 on the same questions. Context only; three
development-exposed personas cannot support a winner claim and nothing was tuned from these outcomes.

**the shared failure is the finding.** Conditional questions are nearly free for both engines and
Mem0 answers all 29 at rank 1: the gold session established the rule and the question names the item.
Static conflict is where both collapse — 6/36 and 10/36 — because the truth was stated long ago and
the contradiction is recent, and similarity has no reason to prefer the older statement. That is
Round 2's `false_persistence` reappearing on a corpus built by other people under a different ruler.
Both engines also land on rank 1 exactly 107 times from unrelated retrieval stacks, then diverge in
the tail.

**inventory, reconciled read-only after the run.** Perseus quarantined 25 of 14,304 writes (0.17%;
5, 11 and 9 per persona), each carrying a native reason string such as
`quarantined (interference score 0.909 > bound 0.900)`. It is a native admission decision, not loss,
and invisible at Round 2's sixteen writes. Mem0 holds exactly what was written — 4,762, 4,844, 4,698,
difference zero.

**a harness defect worth recording.** Mem0's in-run inventory said 20 points against 4,762 writes.
`get_all()` takes `top_k`, defaults to 20, and ignores a `limit` kwarg, so I had captured a page size
and would have published it as a store count. The leaf keeps the misleading number with the
explanation; the true count comes from `client.count(exact=True)` in
`scripts/reconcile_memconflict_gen37_inventory.py`. I did not patch the runner mid-flight because
embedded Qdrant permits one client per store and touching it would have corrupted the live run.

**one earlier self-correction.** The first Perseus pass was stopped and rerun. Its determinism check
re-queried a snapshot taken after all 53 sessions while the original query had seen only sessions
0..i, so it compared two different stores and reported instability that was my bug. The repeat now
runs immediately, against the same open snapshot.

**measured scale, replacing Gen36's guess of 0.3-1.0 s/write and 12-40 h/engine:**

| | Perseus | Mem0 |
|---|---|---|
| write p50 | 143 ms | 348-359 ms |
| query p50 | 22-26 ms | 394-402 ms |
| calibration wall | 0.58 h | 1.47 h |
| writes/sec | 6.88 | 2.71 |
| store per persona | ~55 MB | ~58 MB |
| projected full release | 5.8 h, 1.65 GB | 14.7 h, 1.73 GB |

Write latency was flat across personas and across a store growing to ~4,800 records, so there is no
nonlinear slowdown at this scale. The linear-10x and rate-based projections agree within 2% for both
engines.

**Gen38 recommendation, not executed.** One full-release pass for Perseus first, then Mem0, serially:
about 20.5 hours total and 3.4 GB. Feasibility decides the order, not accuracy. One retrieval pass
per engine with targeted repeats — every label-blind repeat was identical, so tripling 3,750 queries
buys nothing. Hindsight and agentmemory stay behind this pass. Two operational notes: Mem0's queries
cost ~25 minutes of the release against Perseus's ~90 seconds, already inside the projection; and
embedded Qdrant's one-client-per-store rule means Mem0 personas must open strictly in sequence, so a
parallel-persona design needs separate processes.

**artifacts.** `src/memory_bakeoff/providers/perseus_memconflict.py`,
`src/memory_bakeoff/providers/mem0_memconflict.py`, `src/memory_bakeoff/memconflict_engines.py`,
`scripts/preflight_memconflict_gen37_products.py`, `scripts/run_memconflict_gen37_calibration.py`,
`scripts/build_memconflict_gen37_report.py`,
`scripts/reconcile_memconflict_gen37_inventory.py`,
`research/MEMCONFLICT_GEN37_PERSEUS_MEM0_CALIBRATION.md`,
`results/memconflict_gen37_calibration/{perseus,mem0}/` leaves and ledgers, plus
`exact-provenance-derived.json`, `operations.json`, `inventory-reconciliation.json`,
`validation.json`, `content-digest.txt`, and `tests/test_memconflict_gen37_products.py`.

Scientific digest `63dafdf6bbc51dce3bc6f5b6dd47e912b7ab28f3d30a113acdf6d7cb80778f12`, reproduced byte
for byte; wall-clock measurements live outside the hashed content in `operations.json`. 20 focused
tests; full suite 205 passed with the one pre-existing warning.

## Generation 36 — MemConflict external-benchmark contract (no contestant score)

**status:** complete. No product ran, no reader, no LLM, no external API, no GPU. Round-1,
Round-2, `longitudinal-v1`, the Gen34 ledger and the Gen35 ablation are untouched.

**pin.** `TaoZhen1110/MemConflict@ec51d5d36e87f7665d1337f3a88cbde95fc2a964`, checked out under
gitignored `external/` (39 MB dataset not vendored). `Data/Step4_4.jsonl` blob
`6dcbf9e536ea3e5d…`, sha256 `8ef9ec8589eccb86f63ab3a819a9180217405351a8d5846866721ea74babe092`.
Evaluation files we depend on are hashed in `research/MEMCONFLICT_PIN.json`:
`eval_scoring.py` blob `6a763871a7d6ca6c…`, `eval_memzero.py` blob `d66a6b2abf4d5f96…`,
`llm_request.py` blob `145cc2261c45820c…`. Construction/generation stages were not run.

**measured locally.** 30 personas; 1,579 sessions (900 update, 510 chitchat, 139 initial_reveal,
30 future_plan); 3,750 questions (2,946 dynamic, 360 static, 444 conditional); 51–54 sessions and
107–144 questions per persona; 71,060 turns; 142,093 well-formed dialogue messages; 28,623,378
characters. Token counts omitted as tokenizer-specific rather than repeated from the paper.

**a defect in the release, counted not dropped.** 36 dialogue messages are malformed — 29 use the
role name as the key so carry neither `role` nor `content`, 5 lack a role, 2 lack content. They are
excluded from ingestion with their exact provenance IDs listed. A silently shrinking corpus is
indistinguishable from a system that forgot.

**registry.** Public: profile blocks, `Session_ID`, `Date`, `Session_Dialogue`, question text.
Scorer-only: `answer`, `conflict_type`, `ability_target`, `difficulty`, `Updated_Attributes`,
`Revealed_Attributes`, `Static_Conflict_Information`, `Conditional_Conflict_Information`,
`Others_Dynamic_Information`, `Question_Trigger_Types`, `Event_Types`, `Session_Outline`,
`Session_Type`, `metadata`, `token_cost`. `Session_Type` is scorer-only deliberately: update versus
chitchat tells a system which sessions carry state changes, which is the measurement.
`assert_public_only()` walks payloads recursively; five adversarial injections are tested.

**chronology, from source not assumption.** `eval_memzero.py` adds session i's dialogue then answers
session i's questions, so the allowed prefix is sessions 0..i inclusive. A future-session unit is
rejected by `assert_within_boundary()`, proven in the pilot.

**upstream scoring audit — the important part.** Primary K 3, variants 2 and 5; two black-box and two
white-box metrics per conflict type; log-rank is `1/log2(rank+1)`. The white-box metrics are
LLM-JUDGED: the judge sees retrieved memory strings and `created_at` values and returns a support
rank, so no released identifier enters that decision. Four fail-open paths turn "not measured" into a
number: `build_missing_answer_result` returns all metrics 0.0; `evaluate_question_with_llm` catches
every exception and returns None, and the rule-based fallback then leaves ALL white-box metrics at
0.0 — an API outage is published as a retrieval miss; `parse_llm_metric_result` uses
`.get(metric_key, 0)`; `parse_support_rank` returns 0 on any parse failure. This is the Gen31 defect
in upstream code, on the metric the benchmark exists to measure. We do not reproduce it: all four are
UNMEASURED here, and the lanes `upstream_llm_judge`, `upstream_rule_fallback` and
`exact_provenance_whitebox` are never merged. The official lane is
`requires_reader_authorization` and was not run.

**exact-provenance fork, resolved per conflict type.** 3,569 of 3,750 questions (95.2%) map to gold
support sessions using released identifiers only. Dynamic 2,946/2,946: the updated state is
established by the question's own session via `Updated_Attributes`. Static 360/360: each question
session holds exactly one `Point_B`, whose `Conflict_ID` names exactly one `Point_A` truth session.
Conditional 263 exact: the session establishes rule `R_n` and the question addresses `R_{n-1}`,
located by released `Rule_ID` order. Conditional 181 UNMEASURED: multi-rule sessions where the
question-to-rule pairing is not determined by any released identifier — I did not invent one. The
predecessor rule is corroborated 263/263 by the predecessor `Item` string appearing in the question
or gold answer, used as an independent check and never as the mapping mechanism. A unit with
identical text under a different session earns nothing; that is a test.

**diagnostic pilot, no contestant.** Calibration subset only, seven checks passing: null gives
MEASURED_ZERO where gold exists and UNMEASURED only where it does not; the existing BM25 baseline
earns hit@3 on 110/380 scored questions, so the metric is reachable and unsaturated; a future-session
provider is rejected; a gold answer in a payload is rejected; a conflict label in a payload is
rejected. An oracle exists only inside scorer unit tests, proving rank 1 / hit 1.0 / log-rank 1.0.

**calibration.** Personas whose SHA-256 digest is divisible by 5, chosen with no reference to any
label: 3 of 30, about 380 questions, frozen before any outcome was inspected and permanently
development-exposed. The release itself is unmodified; held-out is a reporting slice.

**Gen37 proposal, not executed.** Scale is the finding: 4,736 messages and 125 questions per persona
means 142,093 writes and 3,750 queries per engine, against Round 2's 16 writes. At 0.3–1.0 s per
write — an estimate, since the products were never timed per write — that is 12–40 hours per engine
for the full release, 2–7 days for four. Recommended order: Perseus Gen29 and Mem0 Gen32 first (both
ingest plain text, identity carries over unchanged), then Hindsight Gen31 (carries over, `occurred_*`
still unreachable), then agentmemory Gen33, which is the interesting one because its Jaccard
retirement will fire far more often at 4,736 messages than at 16. OM excluded: no natural semantic
query surface, so forcing it would measure the adapter. One retrieval pass per engine with targeted
repeats, not mechanical tripling: all four were deterministic at retrieval level across Round 2.

**artifacts.** `src/memory_bakeoff/memconflict.py`, `scripts/build_memconflict_contract.py`,
`scripts/preflight_memconflict_gen36.py`, `research/MEMCONFLICT_GEN36_CONTRACT.md`,
`research/MEMCONFLICT_PIN.json`, `results/memconflict_gen36_contract/`,
`results/memconflict_gen36_pilot/`, `tests/test_memconflict_gen36_contract.py`. Contract
`memconflict-benchmark-v1` hash `0521210818e448c8f189dacc33e287b15525f89d63f39cb627f9cdc7a3dccd28`;
contract digest `057dd9587f61ce5e9d2100ec21e3bd7800d8115a091626384afd9efa9900410e`; pilot digest
`68ca5fcfa360e4b655dca71c304f909481713b0465fcd5061defe79aa7a788e7`. Both reproduce byte for byte.
21 focused tests; full suite 185 passed, one pre-existing warning.

## Generation 35 — agentmemory retirement ablation (controlled_core)

**status:** complete. Both gates passed; the causal claim is scoped to this pinned engine.

**what varied.** One runtime gate around the three supersession-state assignments in
`src/functions/remember.ts` (`supersededId`, `supersededVersion`, `supersededMemory`),
keyed on `AGENTMEMORY_EXPERIMENT_DISABLE_AUTO_SUPERSESSION`. Candidate scan, Jaccard
computation, the >0.7 threshold, the loop `break`, memory creation, indexing,
embeddings, retrieval and service architecture are untouched. Patch artifact
`research/patches/agentmemory-gen35-retirement-flag.patch`, sha256
`1aee426efd2460f4f2b77094082b8442ec44bc0ec9017d06c2b3d9d417b57c6d`; pre-patch source
`e14b5c946d08843a…`, post-patch `a1e4d56aab1be354…`; upstream commit
`e04ba88819c365c9acf9d6661ea802143e728bd6`, package 0.9.29. Both arms execute one
built artifact in `external/agentmemory-gen35`; the runner fails if any environment
variable other than `AGENT_ID` and the flag differs, and fails if the flag never varies.
Adapter contract `a06482525d718dd…`, fixture `a5c67e7b2677dff…` and scorer
`1dd831e80b3769a…` unchanged.

**preflight, unrelated synthetic content.** 12/12 pass. Above-threshold pair: ON retires
exactly one row, OFF retires nothing and leaves no parent, no supersedes, version 1. ON
on the patched build is row-for-row identical to the *unpatched* pinned build on the same
pair. Below-threshold pair: identical shape, identical ranking, identical scores in both
arms. OFF still writes and indexes normally. No LLM credentials, local embeddings, no GPU.

**gates.** Manipulation: every ON repetition reproduces the Gen33 pattern natively — two
supersessions, `L001 -> L003` false, `L002 -> L004` legitimate, 14 live / 2 retired at
CP16; every OFF repetition has zero supersessions, zero retired, 16 live. Control
replication: the fresh ON repetitions match Gen33 leaf evidence on product events and
classification, case classes per case, case totals, lifecycle totals, and canonical
returned-id ordering for all 20 cases.

**result** (per repetition; all three repetitions per arm identical, so aggregate is 3x):

| stream | class | ON | OFF | delta |
|---|---|---|---|---|
| lifecycle | `false_supersession` | 1 | 0 | -1 |
| case | `history_erasure` | 2 | 0 | -2 |
| case | `correction_failure` | 1 | 0 | -1 |
| case | `missing_required_truth` | 2 | 1 | -1 |
| case | `configuration_collapse` | 1 | 2 | +1 |
| case | `false_persistence` | 2 | 3 | +1 |
| case | `stale_persistence` | 4 | 5 | +1 |
| case | `belief_truth_confusion` | 2 | 2 | 0 |
| case | `scope_collapse` | 2 | 2 | 0 |
| case | `failed_procedure_adoption` | 1 | 1 | 0 |
| case | `late_history_corruption` | 1 | 1 | 0 |
| case | `unsupported_evidence` | 2 | 2 | 0 |

**hypotheses.** H1 supported: lifecycle `false_supersession` 3 -> 0 in aggregate. H2
supported in direction: with retirement off, `configuration_collapse` returns to 6 and
`false_persistence` to 9 in aggregate — exactly the append-only engines' figures, so
retirement was buying those reductions. H3 traced case by case: `history_erasure` and
`correction_failure` exist only in ON and are caused by `L001`/`L002` becoming
unreachable. H4 measured: `stale_persistence` 4 -> 5 per repetition. H5: five classes are
unchanged across arms and are not attributable to retirement in this engine.

**difference trace.** 13 of 20 cases differ in returned sequence or classification.
Every one is explained by the presence in OFF of `L001` or `L002`. Zero possible
confounds. LQ04 and LQ06 stop failing in OFF because corrected history is reachable;
LQ02, LQ05 and LQ07 start failing because the superseded configuration and the stale
fact still compete.

**reading.** Retirement did not fix the append-only failures, it traded them. Every
failure it removed from the current-state classes it re-created in the history classes,
on the same fixture, on the same ruler, in the same engine. Similarity is not
supersession.

**reporting.** Gen34 primitives throughout: typed CASE/LIFECYCLE/PRODUCT_EVENT streams,
no summary.json consumed, missing evidence raises. `false_supersession` comes only from
the lifecycle scorer replay, reconciled against the product's own retirement events.
Ablation contract `gen35-ablation-v1`; content digest
`073baaab3ac3c6eaac084c3f96d264c37acc974c514d2aa8185f1725a9b81e52`, reproduced byte for
byte across two completely independent sets of six runs. Gen33 and the Gen34 four-engine
ledger are untouched.

**tests.** 16 focused Gen35 tests; full suite 164 passed, 1 pre-existing warning.

**notes for the next generation.** The patch leaves one benign asymmetry worth recording:
`nearMatch` is reported in the response when a sub-threshold candidate was seen before the
>0.7 candidate broke the loop. In ON it is suppressed by `!supersededId`; in OFF it can
surface. It is a response hint only, never acted on, and it does not touch storage,
indexing or ranking.

 - generation: 34
 - base_commit: `bbfc8c99573c61408f5c5e26d6bd4e11d0119a36`
 - result_commit: `60d86874f6df8b4e852b80d9727c7050c64b4568`
 - implementer: Claude (Claude Code, Opus 5) on the Mac over SSH. No product run, no engine or database service, no reader, no LLM, no GPU — pure offline Python over committed normalized evidence.
 - status: complete_reporting_integrity_audit_all_conclusions_survive
 - objective/summary: Rebuilt every Round-2 cross-engine number from committed leaf evidence through a new fail-closed reporting layer, and re-derived every published conclusion independently. **Nothing moved.** The conclusions were right; what they had been missing was a derivation path that could have proven them wrong.
 - constraints/results: Contract `round2-reporting-v1`, hash `9673f1d98091e89fec9758425fc640f7fe8addc84e885ad64edc1cab3b82b149`, distinguishing four streams (`case_scorer`, `lifecycle_scorer`, `product_lifecycle_event`, `capability_diagnostic`) with a closed registry giving every failure class its legal source; `false_supersession` is lifecycle-only and asking the case stream for it RAISES. Measurement is tri-state — `PRESENT(n)`, `MEASURED_ZERO`, `UNMEASURED` — and an UNMEASURED value carries no integer at all, so it cannot be summed by accident; a missing key, absent file, failed parse or absent stream becomes UNMEASURED, never 0. Every helper raises; there is no equivalent of the old `sql()` that turned an exception into `""`, `[]`, `{}`, `0` or `False`. All twelve repetitions (four engines × three runs) passed schema validation — exactly 20 cases with no duplicates or unknown ids, exactly 9 checkpoints, complete lifecycle fields. Case totals were recomputed from `cases[].failure_classes` case by case; lifecycle totals by calling the FROZEN `score_lifecycle_state` on each checkpoint's normalized state; both reconciled against stored aggregates with disagreement fatal and named by engine/repetition/class. Stored `summary.json` files were verification targets, never inputs, and a test proves a deliberately corrupted summary is caught rather than propagated. **Independent derivation results: the seven preregistered classes recur in all three append-only engines TRUE; the five identical across them are exactly `configuration_collapse`, `failed_procedure_adoption`, `false_persistence`, `late_history_corruption`, `unsupported_evidence`; lifecycle `false_supersession` is Perseus 0, Hindsight 0, Mem0 0, agentmemory 3; unique to the retiring engine TRUE; retirement halves configuration collapse TRUE (6→3); retirement reduces false persistence TRUE (9→6).** Your A/B/C classification: (A) always valid — every case-level result across all four engines, and Gen33's activation evidence, `L001→L003` false and `L002→L004` legitimate, unaffected; (B) corrected but substantively unchanged — Gen31's lifecycle, whose corrected rerun is genuinely clean with byte-identical case results; **(C) provenance changed — "the append-only engines never falsely supersede" was published from the case-level stream where that class cannot appear, and is now MEASURED_ZERO from the lifecycle scorer. Same sentence, entirely different evidence.** Summariser audit: **45 default-fallback patterns** across the six Round-2 scripts (`.get(key, 0)`, `or "0"`, `or []`, bare excepts), `summarise_gen33.py` alone holding 17, and all three summarisers embed `datetime.now()` in hashed content so none can produce a stable digest. Historical scripts left intact for reproducibility with defects documented; future publication routes through the common reporter, which has no fail-open paths and regenerated byte-identically across consecutive runs at content digest `edbae67b09769e7165a6ec1199d8f2adcaca6e8e25ee5c2191c4fad495495d51`. Every aggregate cell carries lineage to engine → repetition file → stream → case ids. Artifacts: `src/memory_bakeoff/round2_reporting.py`, `scripts/build_round2_ledger.py`, `research/ROUND2_REPORTING_INTEGRITY_GEN34.md`, `results/round2_gen34_integrity/` (evidence-ledger, four-engine-derived, validation, content-digest), `tests/test_round2_reporting_integrity.py` with 14 adversarial tests each naming a specific failure from 2026-09-03, and a Gen34 row plus verified correction note in `RESULTS.md`. Tests: 148 passed, one existing warning — 118 at the start of Gen31, so thirty new tests, the last fourteen existing solely to make tonight's reporting failures impossible to repeat.
 - questions: One observation and one open item. The observation is that the audit found the defect concentrated exactly where nobody was looking: the frozen ruler, the adapters and the product identities all carried hashes, pinned commits and tests, and none of them failed all night — every error was in the layer that compares and presents. That asymmetry seems worth generalising beyond this benchmark. The open item is that Gen34 hardens reporting but does not change the fact that Round-2's architectural contrast is still ACROSS products rather than within one: isolating retirement properly needs a single engine with it switchable, and none of the four gives us that. If Round 2 is heading toward a conclusion about append-versus-retire as a design choice, that limitation is now the binding one, not the reporting layer.

 - generation: 33
 - base_commit: `b8f99084a0e03a4833379c19467b76364f4a7f57`
 - result_commit: `955394b8922b20c6ffdce7837c4431d3ea20386e`
 - correction_commit: `7a20e7a`
 - implementer: Claude (Claude Code, Opus 5) on the Mac over SSH. No reader, no LLM call, no inference-server GPU.
 - status: complete_raw_product_longitudinal_native_retirement_activated_with_gen31_lifecycle_correction
 - CORRECTION FIRST, because it touches what you reasoned from: **Gen31's published lifecycle numbers were never measured, and the "false_supersession 0" claim for the append-only engines was read from the wrong scorer stream.** Three queries in the Gen31 lifecycle collector were failing silently — `document_id` read from `documents` when it lives on `memory_units`, a `state` column that does not exist in that schema (curation is the `invalidated_memory_units` side table), and a `sql()` helper returning an empty string on failure instead of raising. Every one produced a plausible answer: all records reported inactive, zero invalidations. In a benchmark about memory loss, a failed query reads as "nothing was lost". Separately, `false_supersession` is a LIFECYCLE class scored by `score_lifecycle_state`; it never appears in the case-level table I was aggregating, so "0" was structurally guaranteed rather than observed. Gen31 has been re-run with a collector that raises on failure and asserts all sixteen markers per checkpoint: **its case results are byte-identical to what was published, and its lifecycle is genuinely clean.** Your architectural reasoning holds — the append-only trio really does never falsely supersede — but for two generations that rested on a number nobody had measured. All four summaries now carry both scorer streams separately with an explicit never-merge note, and a regression test enforces it.
 - objective/summary: Ran agentmemory 0.9.29 as the fourth Round-2 contestant in its exact Gen13 raw identity with the product's OWN write-time supersession left enabled — the one architectural variable Gen29, Gen31 and Gen32 all held fixed — across three fresh repetitions against the frozen ruler.
 - constraints/results: Identity reproduced exactly: upstream `e04ba888`, package 0.9.29, local q8 `Xenova/all-MiniLM-L6-v2` via `@huggingface/transformers` 4.2.0, native cosine+BM25 RRF, LLM extractor and consolidation and graph extraction and auto-compress and learned reranking all disabled with every API key blanked in the service environment. Fresh iii data directory and distinct `agentId` per repetition, one project namespace, never a project or agent per scope. Ruler unchanged; adapter `agentmemory-longitudinal-adapter-v1` contract `a06482525d718dd…` frozen before the first scored query. **TREATMENT ACTIVATION, measured per ingestion step rather than inferred: retirement fires exactly twice per repetition, identically in all three — step 3 `L001` retired by `L003` (FALSE supersession), step 4 `L002` retired by `L004` (LEGITIMATE).** Predicted before running: an offline replica of the pinned tokenizer scored those two pairs at Jaccard 1.000 and every other pair at 0.600 or below. The rule is strict lexical Jaccard >0.7 over whitespace tokens longer than two characters, case- and punctuation-sensitive, one predecessor per write, never across a project boundary; the retired row keeps `isLatest=false`, stays in KV and leaves the search index, so absence from search is not deletion — all validated live on unrelated synthetic data first. **`C1`/`C2` and `21`/`29` are two-character tokens the tokenizer discards, so "Nimbus Forge C1 measured 21 t/s" and the C2 measurement are the same sentence to it.** The same rule therefore produced one correct retirement and one wrong one from an identical score of 1.000. Three repetitions, identical totals, provenance exact: `stale_persistence` 12, `false_persistence` 6, `history_erasure` 6, `scope_collapse` 6, `belief_truth_confusion` 6, `missing_required_truth` 6, `unsupported_evidence` 6, `configuration_collapse` 3, `correction_failure` 3, `failed_procedure_adoption` 3, `late_history_corruption` 3. Lifecycle, scored separately: **`false_supersession` 3** — agreeing exactly with the harness's independent classification of the product's own retirements, two measurements taken different ways reaching the same answer. **Four-engine contrast: retirement HALVES configuration collapse (6→3) and reduces false persistence (9→6), leaves stale persistence unchanged (12), and makes agentmemory the only engine that falsely supersedes (0 in all three append-only engines).** `history_erasure` and `correction_failure` are shared with Perseus but absent from Hindsight and Mem0, reached by two unrelated mechanisms — Perseus by collapsing its time axis, agentmemory by removing rows from the index — so they are NOT reported as introduced by retirement. Artifacts: `research/AGENTMEMORY_GEN33_LONGITUDINAL.md`, `results/agentmemory_gen33_longitudinal/` with three repetition JSONs, `src/memory_bakeoff/providers/agentmemory_longitudinal.py`, `scripts/preflight_agentmemory_gen33.py`, `scripts/run_agentmemory_gen33_longitudinal.py`, `scripts/summarise_gen33.py`, `tests/test_agentmemory_gen33_longitudinal.py`, and a Round-2 agentmemory row in `RESULTS.md`. Tests: 134 passed, one existing warning.
 - questions: Two. First, the honest reading of Round 2 so far is that neither architecture is safe — append everything and the store cannot say which statement is current; retire on similarity and it deletes what was true — and that this is a contrast ACROSS products rather than a controlled experiment within one, since agentmemory differs in storage, retrieval, embeddings and service architecture as well as in retirement. If you want the retirement variable isolated properly, the only clean way I can see is a single engine with its retirement switchable, which none of the four gives us. Second, a methodological note worth acting on: across five engine profiles every error found tonight was in the code that compares, aggregates and presents results, never in the runs themselves, which have been deterministic and provenance-exact throughout. The frozen ruler and adapters get tests and hashes; the summarisers get neither. If Round 2 is going to carry conclusions this far, the reporting layer probably deserves the same treatment as the measurement layer.

 - generation: 32
 - base_commit: `0f28e6bfe46f4b997d1a33c6f45c4f0994760b84`
 - result_commit: `a3f4ef3baaab8fcae2151cdc4996e462dbf3a949`
 - implementer: Claude (Claude Code, Opus 5) on the Mac over SSH. No reader, no LLM call, no inference-server GPU.
 - status: complete_raw_product_longitudinal_no_temporal_surface
 - objective/summary: Ran Mem0 2.0.19 raw `Memory.add(..., infer=False)` as the third Round-2 contestant against the frozen `longitudinal-v1` ruler in its exact Gen10 identity, three fresh repetitions, as the preregistered test of whether the seven failure classes shared by Gen29 Perseus and Gen31 Hindsight recur in a third architecture. **They all do — in an engine that has no temporal retrieval surface whatsoever.**
 - constraints/results: Identity reproduced exactly with nothing substituted: upstream `19cb89af`, package 2.0.19 editable from that checkout, FastEmbed 0.8.0 `thenlper/gte-large` resolved to `qdrant/gte-large-onnx` snapshot `770e825c…` (1024-D) with sparse `Qdrant/bm25` `22b8d2af…`, ONNX Runtime 1.29.0, embedded qdrant-client 1.19.0 on-disk with a fresh path and collection per repetition, spaCy absent so entity boosts stay inactive, constant `user_id=memory-bakeoff`, threshold 0.1, top-k 5. Ruler unchanged (`a5c67e7b…`, `1dd831e8…`); adapter `mem0-longitudinal-adapter-v1` contract `f41e15212b435346fb50b7794ead1bd00898a4bf89db433cb89b98891502ac6d` frozen before the first scored query. Mem0 constructs an OpenAI client at init even for `infer=False` — the Gen10 provider already used a placeholder key for exactly this reason — and the preflight proves it is never called by refusing the process a socket during a raw add rather than asserting it. **Native semantics, measured on unrelated synthetic data first: there is no temporal retrieval surface at all. The only time-shaped APIs are `update`, `_update_memory` and `history`, which are mutation and audit; `metadata.timestamp` is opaque payload that does not participate in ranking.** Raw `add` never dedupes or merges (seven adds, seven points); one `history` row per add gives native ingest lineage neither prior engine offered; reads are side-effect-free with identical order, identical scores and unchanged point counts. Mem0 CAN filter on metadata such as `scope`, which would very likely suppress `scope_collapse`; Gen10's scored identity filtered on the constant `user_id` alone, so that capability is recorded as unscored evidence and excluded from the scored path, and `configuration` is deliberately not carried as a fifth metadata field because Gen10 did not carry it — a test asserts both refusals. Three repetitions, identical totals, zero variance, provenance exact on every returned item: `stale_persistence` 15, `false_persistence` 9, `configuration_collapse` 6, `scope_collapse` 6, `belief_truth_confusion` 6, `unsupported_evidence` 6, `failed_procedure_adoption` 3, `late_history_corruption` 3, `missing_required_truth` 3. Clean: `future_leakage` 0, `unmapped_provenance` 0, `false_supersession` 0, `procedure_recommendation_missing` 0. **Three-engine contrast: five classes land at IDENTICAL counts across Perseus, Hindsight and Mem0 — false_persistence 9, configuration_collapse 6, failed_procedure_adoption 3, late_history_corruption 3, unsupported_evidence 6 — across three products sharing no storage engine, no retrieval algorithm and no time model.** Every difference is explainable by one architectural choice each: Perseus partitions by workspace so never collapses scope but collapses application time onto transaction time; Hindsight and Mem0 keep one namespace and let ranking decide, so both collapse scope; and Mem0's single extra failure is `stale_persistence` on **LQ20**, an `as_of_event_truth` case Perseus answered with `valid_at` and Hindsight with `query_timestamp` — the extra failure is the direct cost of having no temporal filter. Reproducibility hazard recorded: FastEmbed 0.8.0 warns `thenlper/gte-large` now uses mean pooling rather than CLS, so this identity holds only at this pin. Round-1 contrast: the same Mem0 configuration scored stress Hit/all-relevant 0.958/0.917 — excellent relevance sitting on top of seven longitudinal failure classes. Artifacts: `research/MEM0_GEN32_LONGITUDINAL.md`, `results/mem0_gen32_longitudinal/summary.json` plus three repetition JSONs, `src/memory_bakeoff/providers/mem0_longitudinal.py`, `scripts/preflight_mem0_gen32.py`, `scripts/run_mem0_gen32_longitudinal.py`, `scripts/summarise_gen32.py`, `tests/test_mem0_gen32_longitudinal.py`, and a new Round-2 Mem0 row in `RESULTS.md`. Tests: 126 passed, one existing warning.
 - questions: I have written the result as evidence CONSISTENT WITH the append-only-without-retirement explanation, not proof, and a test enforces that the published interpretation states its own limits. The reason for the caution is that all three profiles also share this harness, this ruler, and a no-retirement constraint the generations themselves imposed — so the retirement half of the hypothesis has never actually been varied. Your own instinct was right: agentmemory is the informative counterexample, because it retires aggressively on its own and Round 1 measured it falsely superseding 418 of 450 stress distractors. If it shows the seven classes drop while `false_supersession` explodes, that is close to a controlled contrast on the one variable nobody has moved yet. Separately, three engines in a row have now depended on pinned model artifacts living in temp directories — Hindsight's E5 snapshot under `/private/tmp`, Mem0's two FastEmbed snapshots under `/var/folders/...` — and any routine cleanup would present as an identity blocker rather than a missing file. Worth deciding whether we copy those into durable storage before Round 2 goes further.

 - generation: 31
 - base_commit: `5816fb93e5eea9dc9a0ac04eb99da4eefa9600ef`
 - result_commit: `5110460ea0c7bcfa0cc46401267f9d4634ad73bf`
 - status: complete_raw_product_longitudinal_mention_time_axis_only
 - implementer: Claude (Claude Code, Opus 5) on the Mac over SSH. No reader, no LLM, no inference-server GPU.
 - objective/summary: Ran Hindsight v0.9.2 as the next Round-2 contestant against the frozen `longitudinal-v1` ruler in its exact Round-1 raw/no-LLM learned-reranker identity — three fresh repetitions, 16 ordinary `retain` calls in canonical order, nine checkpoints, 20 cases through native hybrid recall — and produced the first paired Round-2 contrast against Perseus Gen29.
 - constraints/results: Identity reproduced exactly and nothing substituted: Hindsight 0.9.2 (`all`/`api-slim`/`client`/`embed`), source `ebad4782`, `HINDSIGHT_API_LLM_PROVIDER=none` plus the harness's own explicit `HINDSIGHT_RAW_LLM_PROVIDER=none` declaration, ONNX `multilingual-e5-small` at the pinned snapshot `614241f622f53c4eeff9890bdc4f31cfecc418b3` (384 dims, mean pooling, normalized, E5 prefixes), local CPU `cross-encoder/ms-marco-MiniLM-L-6-v2`, Homebrew PostgreSQL 17.11 + pgvector 0.8.6 with a fresh database and bank per repetition, top-k 5, `nofile` 8192. Ruler unchanged (`a5c67e7b…`, `1dd831e8…`); adapter `hindsight-longitudinal-adapter-v1` contract `c9025733aa894fa5abac43632e9dc916c37e526065d089a882257427c14d60ff` frozen before the first scored query, routing only on target kind, event time and scope. **The temporal finding: Hindsight distinguishes `mentioned_at` from an `occurred_start`/`occurred_end` application-time range, but only the first is reachable in this profile.** Raw `retain` takes one per-item `timestamp` which becomes `mentioned_at` and is preserved exactly; `occurred_*` is written only by LLM fact extraction (`engine/reflect/prompts.py` teaches the model to emit it), by the transfer importer replaying "exactly the steps retain runs after LLM extraction" from an already-extracted archive, or by `PATCH .../memories/{id}` — the curate endpoint whose request model also carries `state: "invalidated"` and supersession reasons, which would be precisely the truth-driven lifecycle help constraint 8 forbids. So mention time is the honest axis; that is a capability boundary of the raw profile, not a setup failure, and a different shape from Gen30 where the axis existed and was destroyed on activation. One consequence is favourable: because `retain` accepts an explicit timestamp, the store timeline IS the fixture timeline, so unlike Gen29 no time-base mapping was needed. Read side effects were measured, not assumed: identical document order on repeat, every table count and content digest across `documents`/`memory_units`/`chunks`/`memory_links` byte-identical before and after reads, and at most `8.45e-09` drift in the fused `final` score with reranker/semantic/keyword components exactly equal — float noise in fusion, not feedback; scored queries therefore ran against the live checkpoint store with that measurement as the evidence. (An earlier version of that check reported reads as non-identical; it compared whole score payloads and the 1e-9 jitter made two identical rankings look different.) Three repetitions produced identical failure totals — zero variance. Per repetition: `stale_persistence` 4, `false_persistence` 3, `configuration_collapse` 2, `scope_collapse` 2, `belief_truth_confusion` 2, `unsupported_evidence` 2, `failed_procedure_adoption` 1, `late_history_corruption` 1, `missing_required_truth` 1. Clean across all 60 case-runs: **`future_leakage` 0, `unmapped_provenance` 0, `false_supersession` 0, `procedure_recommendation_missing` 0, and — the headline — `correction_failure` 0 and `history_erasure` 0**. Provenance was exact for every returned item; ingest produced one document, one memory unit and one chunk per observation with no splitting, and in raw mode the graph arm is link-based rather than entity-based (36 memory links, zero entities). **Paired contrast with Gen29, capability surfaces only and deliberately not a scalar leaderboard: Hindsight repairs exactly what Perseus's collapsed time axis broke — correction failure 12→0, history erasure 9→0 — and breaks two things Perseus got right, scope collapse 0→6 (Perseus enforced scope with native workspaces; Hindsight carries it as ordinary metadata in one shared bank, as constraint 9 required) and belief/truth confusion 0→6 (Perseus had no usable second axis to confuse; Hindsight has one and mixes them). Seven classes appear in BOTH — stale persistence, configuration collapse, failed-procedure adoption, late-history corruption, false persistence, missing required truth, unsupported evidence — which on this evidence look like properties of ordinary append-only ingestion without retirement rather than of either engine.** Artifacts: `research/HINDSIGHT_GEN31_LONGITUDINAL.md`, `results/hindsight_gen31_longitudinal/summary.json` plus three repetition JSONs, `src/memory_bakeoff/providers/hindsight_longitudinal.py`, `scripts/preflight_hindsight_gen31.sh`, `scripts/gen31_repetition.py`, `scripts/run_hindsight_gen31_longitudinal.sh`, `scripts/summarise_gen31.py`, `tests/test_hindsight_gen31_longitudinal.py`, and a new Round-2 Hindsight row in `RESULTS.md` leaving the Round-1 row intact. Databases, service logs and caches stay local. Tests: 118 passed, one existing warning, `node` on PATH.
 - questions: Two, both about where the shared failures point. First, the seven classes common to Perseus and Hindsight are the most interesting result so far and neither engine's time model explains them; if you want that isolated, the cheapest next profile is a third architecture rather than another temporal variant — Mem0's `infer=False` raw lane scored well in Round 1 and needs no GPU. Second, `occurred_*` is genuinely reachable in Hindsight's LLM ingestion mode, so a full-product Hindsight profile would answer whether a real application-time axis fixes the corrected-history cases the way Gen30 could not test for Perseus; that one does need an LLM, so it needs Brian's GPU and your explicit go-ahead before I would touch it.

 - generation: 30
 - base_commit: `237151c8487d68b775177888413ab4ec07ce84ba`
 - result_commit: `f90c34eedf84042261bf55d7b16eee9abb050ca2`
 - status: blocked_valid_time_reset_by_admission_approval
 - implementer: Claude (Claude Code, Opus 5) on the Mac over SSH. No reader, no LLM, no inference-server GPU.
 - objective/summary: Attempted the Gen30 write-surface ablation — same v2.23.2 engine, same frozen ruler, same Gen29 query adapter, changing only the ingestion surface to the agent-facing MCP `remember` path so Perseus could receive a real `valid_from_unix_ms`. The ablation is blocked: the one documented step that makes an agent-facing record serveable is also the step that destroys the variable under test. No longitudinal score is published and Gen29 stands unchanged as the authoritative Perseus profile.
 - constraints/results: Identity re-verified before anything else — binary SHA-256 `49a44809611729e4…` from release tarball `e9b0912c…`, reports `perseus-vault 2.23.2 (9c82920)`; fixture `a5c67e7b…`, scorer `1dd831e8…`, and the Gen29 query adapter contract `09f2414e…` all unchanged, with tests asserting it. The documented admission chain was established from the product's own refusals, on unrelated synthetic data only: (1) `perseus_vault_agent` must register the agent or the manifest is refused; (2) `perseus_vault_authority_set` in `enforce` mode for that agent and workspace, granting `memory.read`/`write`/`propose`/`commit`/`admission.review`/`admission.source` — too narrow a capability list and the writes themselves are refused; (3) `PERSEUS_VAULT_ADMISSION_SOURCE_HMAC_KEY` configured on the server or the approval refuses to sign its source attestation; (4) `perseus_vault_remember` with a full admission envelope satisfying `evaluate()` (`authorization_scope == workspace_hash`, `task_relevance_bps >= 5000`, not instruction-bearing, not contradicts-authoritative, `source_trust=authoritative`, `validated`, a `source_event_id`, and `actor_identity == agent_id`); (5) `perseus_vault_admission_decide(approve)`. Every field is constant or public-derived, so it is a single uniform policy — but it is a DIFFERENT trust class from Gen29's operator CLI write, and is reported as such. **The blocking measurement, one row, before and after each step in a single run: `remember` persists the requested retroactive `valid_from` exactly (T−200 days) but leaves the record `proposed` and invisible to recall; `admission_decide(approve)` makes it `active` and recallable and resets `valid_from` to the approval instant, a full 200-day shift; a second `remember` restores the retroactive value and simultaneously returns the record to `proposed`.** Serveable and retroactive are therefore mutually exclusive in v2.23.2, so the independent application-time axis Gen30 exists to test cannot be established through this surface. Root cause confirmed in pinned source: `models::Entity` carries no `valid_from_unix_ms`/`valid_to_unix_ms` field — those columns are written by the `remember` path but not held by the struct — and `admission_decide` clones the stored entity, flips status to active and re-persists it, rewriting application time to the write default. Any read-mutate-write path loses application time the same way. I did not score the profile in this state: every record would have carried `valid_from` equal to its approval instant, the axes would have been collinear again, and the failure profile would have landed near Gen29's for an entirely different reason — reporting that as a one-variable valid-time ablation would have been false. Artifacts: `research/PERSEUS_VAULT_GEN30_MCP_VALID_TIME_ABLATION.md`, `results/perseus_vault_gen30_mcp_valid_time/summary.json` (machine-readable, `scored_longitudinal_result_published: false`, `post_hoc_ablation: true`), the reproducible probe `scripts/probe_perseus_gen30_admission`, `tests/test_perseus_gen30_admission.py`, and a distinct `no-score diagnostic` Gen30 row in `RESULTS.md` beside the untouched Gen29 and Round-1 rows. No v1 name, value, query phrasing, ID or transition label reached the probe; no explicit supersede/update/delete/retract/invalidate/archive/maintenance call was made. Tests: 110 passed, one existing warning, `node` on PATH.
 - questions: Your decision on where to take this. Four options as I see them. (a) Score the MCP path anyway as a pure TRUST-CLASS ablation with valid time declared collapsed and the axis explicitly out of scope — honest, but it answers a smaller question than Gen30 asked. (b) Treat the approval-time reset as the Perseus finding for Round 2, keep Gen29 as the Perseus longitudinal record, and move to the next engine. (c) Test whether a later Perseus release fixes the entity round-trip, as a separate identity — outside the pinned profile and it would need its own base. (d) Re-open the explicit-`supersede` profile you deferred, since that is now the only remaining Perseus surface that could express correction without depending on application time. My own read is (b) with (d) queued behind it: the reset is a genuine product-level finding about agent-facing writes, and no amount of adapter work on our side can route around it.

 - generation: 29
 - base_commit: `3e855b0f7308772880463b2564b08fca73862883`
 - result_commit: `29cbf6028cb60ee0372fd9f6f4f271f3175903fb`
 - status: complete_raw_product_longitudinal_transaction_time_supported_valid_time_unreachable_by_operator_write
 - implementer: Claude (Claude Code, Opus 5) on the Mac over SSH. No reader, no LLM, no inference-server GPU was used at any point.
 - objective/summary: Ran Perseus Vault v2.23.2 as the first Round-2 contestant against the frozen `longitudinal-v1` ruler in its Gen21 raw-product identity — ordinary operator CLI `write` plus native hybrid recall — across three fresh repetitions, nine checkpoints and the 20 frozen cases, and measured what the product preserves and returns when facts evolve, scopes coexist, corrections arrive late and historical truth differs from current truth.
 - constraints/results: Identity was reproduced exactly, not rebuilt: the Gen21 binary was gone from the machine, but it came from the immutable published release, so the tarball was re-fetched and its SHA-256 verified byte-identical to the recorded `e9b0912c…` (binary reports `perseus-vault 2.23.2 (9c82920)`, source commit `9c829207`). Ruler unchanged and re-verified before the first write and after the last repetition: fixture `a5c67e7b…`, scorer `1dd831e8…`. Adapter `perseus-longitudinal-adapter-v1`, contract `09f2414e1e02784176016cdbe2ffda799cf24c2812a9a0c9a3c5342ecea9a4e2`, frozen before the first scored query and routing on public coordinates only (target kind, event time, scope); a test asserts no write envelope or recall argument carries expected/prohibited ids, truth keys, transition labels, lineage or rationale. Semantics were audited on unrelated synthetic data first: `perseus_vault_bitemporal` takes `tx_at_unix_ms` (not `as_of_unix_ms`), `as_of`/`valid_at` both resolve to the earlier body inside the earlier period, and — critically — `perseus_vault_recall` accepts `as_of_unix_ms` and `valid_at` inline, so the temporal axes are reachable through search rather than only entity-addressed lookup. Query side effects were measured rather than assumed: source shows `apply_recall_side_effects` bumping `retrieval_count`/`last_accessed`/decay with a buffer→working promotion, but the hybrid recall path did NOT fire it (counts, layer, decay and the database file hash all unchanged after a three-hit recall); the one observed increment came from an in-place CLI **write**. Scored queries nevertheless ran against a byte-for-byte vault snapshot per checkpoint, so isolation is belt-and-braces rather than load-bearing. **The decisive finding: ordinary CLI `write` has no valid-time parameter and sets `valid_from_unix_ms` to the write instant, so in this evaluated identity the application-time axis is collinear with transaction time and carries no independent information.** The MCP `remember` path does expose `valid_from_unix_ms` for retroactive facts, but constraint 6 required the Gen21 operator-write identity, so the capability exists and is simply unreachable from the scored write path — a profile limitation, not an engine limitation. Three repetitions produced identical failure profiles (zero variance). Per repetition: `correction_failure` 4, `stale_persistence` 4, `false_persistence` 3, `history_erasure` 3, `configuration_collapse` 2, `missing_required_truth` 2, `unsupported_evidence` 2, `failed_procedure_adoption` 1, `late_history_corruption` 1. Clean across all 60 case-runs: **`future_leakage` 0, `unmapped_provenance` 0, `scope_collapse` 0, `false_supersession` 0, `belief_truth_confusion` 0**. Checkpoint discipline held absolutely and every returned item carried an exact native-ID-to-canonical mapping with an agreeing body marker. Both `historical_belief` cases passed on the transaction-time axis. Every valid-time case failed, which follows directly from the collinear axes. Configuration collapse is real and new: C1 and C2 coexist in one Forge workspace by design and hybrid recall returned both for a configuration-specific question — Round 1 never asked a question that could see this. Lifecycle: all 16 receipts mapped to live entities at the final checkpoint (16 active, 0 archived, 16 distinct validity starts, 3 workspaces), so ordinary consolidation dropped and merged nothing; this bounds rather than contradicts Round 1's 107 distinct-valid active-state losses at 500 records, and no absence was observed so nothing is called deletion. Artifacts: `research/PERSEUS_VAULT_GEN29_LONGITUDINAL.md`, `results/perseus_vault_gen29_longitudinal/summary.json` plus three per-repetition JSONs, `src/memory_bakeoff/providers/perseus_longitudinal.py`, `scripts/preflight_perseus_gen29`, `scripts/run_perseus_gen29_longitudinal`, `tests/test_perseus_gen29_longitudinal.py`, and a distinct Round-2 Perseus row in `RESULTS.md` that leaves the Round-1 row intact. Raw vaults, keys and encrypted stores stay local and untracked. Tests: 105 passed, one existing warning, `node` on PATH.
 - questions: One decision for the next Perseus profile. The valid-time axis is only reachable through the agent-facing MCP `remember` write, which carries an admission envelope and a different trust class from the operator CLI write Gen21 scored. Running it would measure the product's real bitemporal capability but would change the evaluated composite and break comparability with Gen21 and with this generation. Say whether a Gen30 should add that as a SEPARATE identity alongside this one, rather than replacing it. Separately, `configuration_collapse` and `stale_persistence` here are honest ordinary-write behaviour; if you want to know whether Perseus can avoid them, that needs a profile where the caller is permitted explicit `supersede`, which Gen29 deliberately forbade.

 - generation: 28
 - base_commit: `2b0b6e2a4be5549d9097fccd9c2441165731d729`
 - result_commit: `15e02c79e505913949924a4d455a76bf5dad0711`
 - status: complete_citation_contract_v2_regrade_over_frozen_gen27_captures
 - implementer: Claude (Claude Code, Opus 5) on the Mac over SSH, second generation in the seat. No product, model, or network call was made in this generation.
 - objective/summary: Closed the Gen27 citation-contract defect as a new versioned contract `om-context-production-v2` applied to the frozen Gen27/v1 captures and the exact frozen reader responses, and made the repository's evidence discoverable from the top level so results such as Perseus are no longer reachable only through handoff archaeology.
 - constraints/results: v1 is untouched and still hashes to `cce9fdf4…` (fixture) and `f69068bb…` (scorer); its published Gen27 numbers stay 0.750/0.833/0.750, 28/36, as historical evidence under the defective contract. v2 identity is `om-context-production-v2` / `om-context-production-scorer-v2`, contract SHA-256 `f6250dc2acb3b168eb994261763d931b671ff9236bf57370484aa6722b331286`, inheriting v1's answer rules unchanged and altering only citation resolution. Prefixes are parsed, never stripped: `obs-<native-id>` and `ref-<native-id>` must match a role the frozen fold actually assigned that ID, and unknown prefixes, unknown IDs, non-12-hex IDs, contradicted roles and role-disagreeing bare IDs all fail closed, with no text-similarity inference anywhere. The substantive finding is that **OM re-emits a promoted observation as a same-ID reflection** — 7, 5 and 4 dual-role IDs in the three folds, identical content, the reflection listing itself as its own supporting observation — so a grader assigning one type per ID would have rejected `ref-36fe2ec6b897` in repetition 1 as a type mismatch and scored this generation lower for the wrong reason; v2 therefore treats a role as one of possibly several the capture assigns. Before regrading, each repetition is rebuilt from its own `om.folded` record through `sourceEntryIds` and `supportingObservationIds` and must reproduce that repetition's v1 support map exactly, or the regrade refuses to run; it reproduces it in all three, and the regrade also refuses if the capture's recorded v1 fixture or scorer hash differs from the frozen module. Result, verified rather than assumed: repetition 1 9/12 → **11/12** (recovered Q08, Q10; Q05 still fails), repetition 2 10/12 → **11/12** (recovered Q10; Q03 still fails), repetition 3 9/12 → **11/12** (recovered Q03, Q10; Q07 still fails); aggregate v1 28/36 (0.778) → v2 **33/36 (0.917)** with zero regressions, matching the recorded Gen27 diagnostic by a stricter route. Per-repetition SHA-256 fingerprints of the ordered stored responses, the typed projection and the captured rendered context are recorded in the summary, along with `model_or_product_calls_in_gen28=false`, which a focused test enforces by refusing the regrade a socket. New artifacts: `src/memory_bakeoff/om_citation_contract_v2.py`, `scripts/regrade_observational_memory_gen28_v2`, `research/OBSERVATIONAL_MEMORY_GEN28_CITATION_CONTRACT_V2.md`, `results/observational_memory_gen28_citation_contract_v2/summary.json` (sanitized: hashes and counts only, no answer or context text), and `tests/test_om_citation_contract_v2.py`. Discoverability: `RESULTS.md` is a new maintained evidence index covering Round-1 baselines, Habitus, MemBukkit, Mem0, Hindsight, agentmemory, Claude-Mem, Graphiti and Perseus plus Round-2 Gen24-28, each row carrying evidence class, headline evidence, lifecycle/safety caveat and direct links; Perseus carries both its 0.958/0.958 retrieval result and its 107 distinct-valid active-state losses with historical recoverability unknown; `research/ROUND1_FINAL_READOUT.md` is linked as the authoritative Round-1 view. `tests/test_results_index.py` parses the index itself and fails on any missing local path, on a missing major profile, and on an entry point that stops linking the index. Stale entry-point metadata is corrected: the STATUS snapshot is 2026-09-02 with the current test count, the Hindsight row now reads `raw_product scored` at stress Hit/all-relevant 0.833/0.708, the README's sandbox section is marked superseded, and the 45-test gate in `AGENTS.md` and `CODEX_HANDOFF.md` is updated. No memory engine, private corpus, MemConflict or `longitudinal-v1` work occurred and no `MemoryProvider` was implemented. Tests: 97 passed, one existing warning; `node` must be on PATH.
 - questions: One judgement call is recorded rather than assumed: v2 accepts a bare native ID when every role it holds agrees on the anchor set, which is true in all three frozen repetitions, so backward compatibility costs nothing here — say if you would rather bare IDs fail closed in a future profile. The dual-role ID behaviour is a product observation from three folds only; it is documented, not scored, and OM still has no natural-language semantic query surface. `om-context-production-v1` remains exposed, so any future OM context-production run needs a new unexposed fixture rather than a rerun of this one.

 - generation: 27
 - base_commit: `9866a14d8f9fb8fa6649238884ec839c20fdbd50`
 - result_commit: `2af7d00c283dc45db00eb606dc84eb1e2498a77c`
 - status: complete_context_production_v1_scored_citation_contract_open
 - implementer: Implementer changed hands for this generation. Codex executed the three repetitions and the excluded attempts on 2026-09-02 and then stopped at its usage limit before writing anything up; Claude (Claude Code, Opus 5, driving the same Mac over SSH) verified those runs against the raw `.control-plane` traces and session JSONLs field by field, re-ran the test gate, and authored and committed this generation's research document, results summary and handoff entry. No run was re-executed and no frozen artifact was altered. Hello, Sol — happy to hold the implementer seat while the ChatGPT quota recovers; say if you want the envelope, the verification depth or the excluded-attempt reporting done differently.
 - objective/summary: Completed three frozen `om-context-production-v1` repetitions that score the agent-visible context pi-observational-memory 3.0.4 produces for itself, using the product's native `om.folded` compaction instead of Pi auto-compaction, graded by an offline reader withheld from the live process until after capture.
 - constraints/results: The harness lane was frozen at `2e9d1bd`; all three published repetitions ran under it with a clean tree. Identity: OM 3.0.4 / `ce9fc982`, Pi 0.81.0, Node v26.8.1, `qwen3.6-35b-vulkan-nothink` with thinking off at `http://strix-halo.local:8080/v1` for both the foreground session and the reader; fixture `om-context-production-v1` `cce9fdf494ad6965897646beff1ef535d4aeb73ba81f3ea83e6fe68e1218acdc` and scorer `om-context-production-scorer-v1` `f69068bbb3a76bf9ca64edeb3a5b14411538d6e4494211d765efa82e50e702bd`, both reverified against the live module after execution; `operator_compaction` false, with all 67 native folds carrying `fromHook` true. Each repetition drove 40 deterministic public turns, passed 40/40 barriers, mapped all 16 anchors to native entry IDs, and captured one fold projection: 23 folds / 9,670 chars / 43 entries, 23 folds / 9,894 chars / 45 entries, and 21 folds / 7,391 chars / 34 entries. Reader pass rates are 0.750, 0.833 and 0.750, i.e. 28 of 36 graded cases. Gen26's `Nothing to compact (session too small)` decline is now explained rather than bypassed: OM folds continuously and measured session size before each fold stayed between 20,729 and 27,282 tokens, so Pi's own auto-compaction threshold is never reached. Answer quality and provenance quality diverge and are reported separately: across all 36 cases there were zero `missing_required` and zero `prohibited_hits`, and every one of the 8 failures is a citation-provenance failure (8 `unsupported_citation`, 5 of which also carried `invalid_citations`). A citation-contract defect is recorded but deliberately NOT applied: `reader_prompt` asks for `obs-`/`ref-` prefixed OM IDs while `grade_reader` keys the projection support map by the bare native entry ID, so Q10 failed in all three repetitions while citing `obs-82e397393ad2`, whose bare ID maps to its required anchor A04 in every repetition; re-grading the stored responses through the unchanged `grade_reader` with only that prefix stripped yields 11/12 in all three repetitions, leaving one genuine `unsupported_citation` each (Q05, Q03, Q07). Four earlier launches are excluded and unscored: one exited before creating a run directory, one was rejected by the turn-1 barrier and caused the launch guard to widen from 2 s to 15 s in `2e9d1bd`, one was refused for a pre-created output directory, and one was backgrounded and reaped by the shell. OM still exposes no natural-language query surface, so no Hit@k, ranking or lifecycle score is published, and the `om-context-production-v1` fixture is now exposed. See `research/OBSERVATIONAL_MEMORY_GEN27_CONTEXT_PRODUCTION.md` and `results/observational_memory_gen27_context_production/summary.json`. Tests: 85 passed, one existing warning; `node` must be on `PATH` or two agentmemory core tests fail on environment rather than on logic.
 - questions: The published Gen27 numbers stay 0.750/0.833/0.750 because the lane is frozen and a grader change would invalidate comparability. Decide whether the citation contract is corrected in place — normalizing `obs-`/`ref-` inside `grade_reader`, or removing the prefix instruction from `reader_prompt` — and whether that correction requires an `om-context-production-v2` fixture and a fresh run, given that v1 is now exposed and the diagnostic regrade implies 11/12 in all three repetitions.

 - generation: 26
 - base_commit: `49179a3aa2fe020066ecb6a9f729926b025b42dd`
 - result_commit: `f8c3aa9de03af2da1538a69be772918b8d656589`
 - status: complete_ingestion_lifecycle_context_unavailable
 - objective/summary: Completed three fresh pi-observational-memory 3.0.4 longitudinal-v1 ingestion/lifecycle repetitions under Pi 0.81 persistent RPC with a tested per-observation native quiescence barrier.
 - constraints/results: Gen25's public-v1 exposure metadata is corrected without rewriting history: exposed true, no valid result published, partial attempt excluded. All Gen26 repetitions passed 16/16 barriers and captured all nine checkpoints with stable session identities and no stale-context error. OM generated observations/reflections and native drops; pool/drops remain conservative lifecycle evidence, not factual truth/deletion. Pi RPC compaction cleanly declined at checkpoints 8 and 16 in every repetition (`Nothing to compact (session too small)`), so no rendered agent-visible context or 20-case context-exposure diagnostic exists. OM has no native natural-language query surface: no retrieval, reader, or generic score is published. See `research/OBSERVATIONAL_MEMORY_GEN26_LONGITUDINAL.md` and `results/observational_memory_gen26_longitudinal/summary.json`. Tests: 80 passed, one existing warning.
 - questions: Treat this as valid driver/lifecycle evidence, but not a completed context or retrieval benchmark. A future profile would need an independently justified workload that native Pi will compact, without changing this frozen result.

 - generation: 25
 - base_commit: `278dd1e3199f23e45d30bbe875e739cb50200a22`
 - result_commit: `d85401e6529772dd4069e7d4dbb76ff5de811fd5`
 - status: calibration_passed_longitudinal_v1_result_not_published
 - objective/summary: Tested exact pi-observational-memory 3.0.4 under Pi 0.81.0's installed persistent RPC JSONL surface. Three isolated garden-journal calibrations reached native OM quiescence with stable session identities and no Gen24 stale-context error.
 - constraints/results: Pi `agent_settled` preceded OM background work, so the controller retains the same process until observer → reflector → dropper terminal evidence and a stable same-process `get_entries` leaf. All three repetitions passed (`observer.records`, `reflector.result`, `dropper.waiting_for_reflection`); no second Pi inspector ran. The v1 ruler API reverified canonical hashes `a5c67e…` / `1dd831…`; formatted JSON byte hashing is not the frozen identity. A later partial public-observation v1 process was not checkpoint-quiescent and is excluded: no v1 result rows, retrieval, lifecycle, or reader score is published. No PR #58/source change, other engine, or private corpus was used. See `research/OBSERVATIONAL_MEMORY_GEN25_RPC.md` and `results/observational_memory_gen25_rpc_calibration/summary.json`. Tests: 76 passed, one existing warning.
 - questions: A future authorized continuation should use a fresh persistent-RPC profile and enforce native-pipeline completion between each v1 observation/checkpoint before attempting complete repetitions. The calibration supports driver sensitivity; it is not a longitudinal product score.

 - generation: 24
 - base_commit: `ed28e828ab81f31ab05365c1a2f5a7efccdb9956`
 - result_commit: `d41759d`
 - status: blocked_native_quiescence_after_calibration
 - objective/summary: Audited exact pi-observational-memory 3.0.4 / `ce9fc982` and completed only unrelated public calibration. No longitudinal-v1 observation was exposed; no other engine, reader, private corpus, or Round-1 work ran.
 - constraints/results: Pi 0.81.0 and LAN `qwen3.6-35b-vulkan-nothink` at `http://strix-halo.local:8080/v1` were frozen; Pi returned `CALIBRATION_OK`. Real `turn_end` observer appended four native observations, then OM debug trace logged `observer.error`: “This extension ctx is stale after session replacement or reload.” This prevents trustworthy quiescence and is the stop condition. Source audit confirms V3 observations/reflections/drop tombstones, model-free compaction, exact-ID provenance recall, and no semantic query retrieval. Active pool/drop state cannot mean factual truth/deletion. Raw v1 query retrieval is N/A rather than fabricated. v1 hashes unchanged. See `research/OBSERVATIONAL_MEMORY_GEN24.md`, `results/observational_memory_gen24_calibration/trace.json`. Tests: 73 passed, one pre-existing warning.
 - questions: Decide whether a future separately identified OM profile may use an upstream fixed commit after this stale-context defect is resolved. Do not rerun frozen 3.0.4 or treat exact-ID recall/context as semantic retrieval.

<!-- Historical Gen23 handoff; retained for audit, not current control-plane state.
 - generation: 23
 - base_commit: `30171d410a3ca1935d073e950f8d1205df226328`
 - result_commit: `3e03b46`
 - status: complete_longitudinal_v1_frozen
 - objective/summary: Hardened and froze the Round-2 engine-independent longitudinal ruler before any contestant run. No memory engine, reader, MemConflict, or private corpus was run; Round 1 artifacts were not changed.
 - constraints/results: `longitudinal-v1` now has 16 publication-safe observations, 9 ingestion checkpoints, and 20 cases. Canonical fixture SHA-256 is `a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd`; scorer/result-contract SHA-256 is `1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34`. It separates event/effective world time from ingestion transaction-time; AS_OF has Jan-10 Forge/C1 before/after-correction cases (21 then 24), while historical belief remains 21 and corrected history 24. Configuration selection is distinct from scoped throughput truth. Aurora's late Feb-5 evidence shares the branch timeline but cannot replace current Feb-10 branch truth. Lifecycle scoring separately accepts native-normalized active/historical/disposition/unknown evidence and detects false supersession without claiming deletion. The frozen taxonomy covers exact future leakage, scope/config collapse, correction/belief failures, procedure omission vs adoption, late-history corruption, retrieval unsupported evidence, unmapped provenance, and reader-only unknown hallucination. Result contract freezes cutoff/rank/native filters/exact provenance/lifecycle evidence; private truth fields never reach adapters. Fixture/manifest: `research/LONGITUDINAL_V1_FIXTURE.json`, `research/LONGITUDINAL_V1_MANIFEST.json`; note: `research/LONGITUDINAL_POINT_IN_TIME_FRAMEWORK.md`. Tests: 72 passed, one pre-existing metadata deprecation warning.
 - questions: Gen24 may authorize the first Round-2 contestant against this exact v1 only. Any future semantic change requires longitudinal-v2; do not modify v1 after a contestant runs.

-->

<!-- Historical Gen22 handoff; retained for audit, not current control-plane state.
 - generation: 22
 - base_commit: `0295ca9aefebe7e3e9fedec1dfde9472f7b8c707`
 - result_commit: `b1f8a7f`
 - status: complete_round1_closure_and_longitudinal_ruler
 - objective/summary: Completed Generation 22 without a product rerun or private-corpus ingestion. Phase A classified frozen Perseus Gen21 stress state loss and formally closed Round 1. Phase B added a public, engine-independent checkpoint/event-time/configuration truth fixture and test-only oracle for Round 2.
 - constraints/results: Read-only Perseus analysis over all three audited Gen21 stress artifacts found exactly the same 107 receipt-mapped IDs absent from each active scan: 500 successful receipts, 393 active, 107/500 (21.4%) active-state loss. All are stress-only, distinct valid scope-qualified records under frozen harness truth; class `false_consolidation_distinct_valid`. They are not core correction pairs, required answers, or duplicates. The frozen scans show `archived_entities=0`, `total_history_rows=0`, no archive reasons/links, and no captured source→survivor lineage, so deletion versus hidden historical recoverability is explicitly `unknown_unattributed_state_loss`; no absorber is invented. Retrieval stays unchanged (core 1.000/1.000, stress 0.958/0.958, prohibited 0.108). `research/PERSEUS_VAULT_GEN22_LIFECYCLE_ADDENDUM.md`, `research/ROUND1_FINAL_READOUT.md`, and `results/perseus_vault_gen22_lifecycle_analysis.json` record this without altering Gen21 artifacts. The new `memory_bakeoff.longitudinal` fixture has three sanitized storylines, explicit event/effective/reference/ingestion time and configuration scope, checkpoint-prefix replay, distinct historical-belief vs corrected-historical-truth oracle targets, a late-arriving history case, and named non-scalar failure metrics. No engine adapter is embedded in it. Tests: 70 passed, one pre-existing metadata deprecation warning.
 - questions: Round 1 is now closed. The next authorized work can use the synthetic ruler for a new round; private transcript characterization must remain metadata-only until an explicit, leakage-safe plan is approved.
-->

<!-- Historical Gen21 handoff; retained for audit, not current control-plane state.
 - generation: 21
 - base_commit: `2a96b1cca99694d05dc0b87fd6a62f22704bb48e`
 - result_commit: `02490da`
 - status: complete_raw_product_with_lifecycle_caveat
 - objective/summary: Completed the authorized late Round-1 Perseus Vault v2.23.2 raw-product evaluation only. The frozen corpus/scorer were unchanged; no prior engine, Graphiti, reader, private corpus, or Gen22 fixture was touched.
 - constraints/results: Official Apple-Silicon v2.23.2 archive SHA-256 matched GitHub (`e9b091…920dcb`), source commit `9c829207…`. Evaluated identity: documented operator CLI `write` seed + native MCP hybrid recall, bundled quantized all-MiniLM-L6-v2 384-D, encrypted SQLite fresh per run, generic `benchmark_record`, key `record-<ID>`, SHA-256 scope workspace, no explicit correction/maintenance/decay/capture. MCP `remember` without admission is non-serveable, so it was not substituted. Exact native ID/body provenance and workspace isolation preflight passed. Three audited core runs: Hit/all-relevant 1.000, prohibited 0.117, 50/50 active. Three audited stress runs: Hit/all-relevant 0.958, prohibited 0.108, but 500 native receipts led to only 393 active records after ordinary writes (107 native write-time consolidations). Explicit `supersede(M011,M012)` and as_of/history, plus valid_at/bitemporal, smoke-tested as real capability only. Tests: 67 passed, one existing warning. See `research/PERSEUS_VAULT_GEN21.md` and audited result directories.
 - questions: Round 1 can close after this late entrant, but interpret Perseus retrieval alongside its reproducible 107/500 stress state loss. Gen22 should freeze the engine-independent longitudinal/bitemporal fixture; do not credit the Gen21 capability smoke as head-to-head temporal performance.
-->

<!-- Historical Gen20 handoff; retained for audit, not current control-plane state.
 - generation: 20
 - base_commit: `4d1ac23e5e95028c3b23ac6f9b799fee9c18d694`
 - result_commit: `8211596`
 - status: blocked_structured_episode_second_gate
 - objective/summary: Completed the one authorized, separately labeled Graphiti `EpisodeType.json` structured-episode profile. The canonical M035 first gate passed with a native fact edge and exact episode provenance. The required fixed eight-record second gate then failed on false lifecycle behavior and missing procedure evidence. No lifecycle/point-in-time sentinel, 50/500 score, reader run, other engine, or private corpus action occurred.
 - constraints/results: Frozen profile: Graphiti OSS v0.29.3 / Gen19 general schema unchanged; LAN `qwen3.6-35b-vulkan-nothink`, local Ollama `nomic-embed-text` 768-D, embedded FalkorDB Lite. The deterministic JSON envelope copies only canonical ID, assertion text, reference time, scope, and constant source kind—no triples, relation/object/type hints, truth status, correction links, or query terms. M035 native JSON extraction created the exact preview-Redis `USES` fact with native episode provenance. In the second gate, M036 (development Redis DB 3) also invalidated the distinct M035 frontend-preview Redis fact: false cross-environment invalidation. M024 (failed direct-edit procedure) yielded no fact edge. M012 also lacked a stable direct current-coordinator fact. These are native trace observations, not harness filtering or repair. Full tests: 66 passed, one existing warning. See `research/GRAPHITI_GEN20_STRUCTURED_PROFILE.md`, `research/GRAPHITI_GEN20_FINDINGS.md`, `results/graphiti_gen20_json_m035_gate/trace.json`, and `results/graphiti_gen20_json_gate2/trace.json`.
 - questions: Treat Gen20 as a no-score blocked configured-product profile. Do not tune its envelope/schema/model or run its lifecycle/temporal/score phases. Decide whether a distinct future Graphiti profile with independently justified environment/procedure representation is in scope, while preserving this evidence.

-->

<!-- Historical Gen19 handoff; retained for audit, not current control-plane state.
 - generation: 19
 - base_commit: `5bd23f9`
 - result_commit: `a72e78c`
 - status: blocked_configured_schema_extraction
 - objective/summary: Froze and exercised the approved general Graphiti configured-product schema, then stopped at its required first extraction gate. No 50/500 score, reader run, lifecycle sentinel, or point-in-time sentinel was run.
 - constraints/results: The schema uses Graphiti's supported entity/edge customization only: ArtifactResource, SystemComponent, Configuration, Environment, ProcedureCommand, MeasurementResult, DecisionConclusion, and one general relation family. With the real 35B LAN LLM, local Nomic embeddings, and embedded FalkorDB, the publication-safe branch assertion still extracted only `release/alpha` as ArtifactResource and native edge extraction returned `[]`; `alpha` was not modeled as Configuration. This is exact native trace evidence, not a harness repair failure. Per Gen19 stop condition, larger temporal/lifecycle diagnostics were not run. Full tests: 64 passed, one existing warning. See `research/GRAPHITI_GEN19_SCHEMA.md`, `research/GRAPHITI_GEN19_FINDINGS.md`, and `results/graphiti_gen19_schema_trace/trace.json`.
 - questions: Decide whether a distinct, genuinely general supported structured-episode ingestion profile for single-entity assertions is in scope to evaluate. Do not tune this frozen schema from the observed failure, use hand-authored triples/edges, or run a score.

-->

<!-- Historical Gen18 handoff; retained for audit, not current control-plane state.
 - generation: 18
 - base_commit: `5fce6b5`
 - result_commit: `c01714b`
 - status: decision_needed_schema_configured_profile
 - objective/summary: Completed the authorized Graphiti OSS source/runtime preflight and all approved non-score LAN-model sentinels. No benchmark score, reader evaluation, or unrelated engine run occurred.
 - constraints/results: Exact upstream is Graphiti v0.29.3 / `021d3a57d511f21b10adaf7fa923bd5c1fce5e9d`, with supported embedded FalkorDB Lite (FalkorDB 4.18.3) and local Ollama nomic-embed-text (768-D). LAN `qwen3.8-27b-vulkan` and `qwen3.6-35b-vulkan-nothink` through `http://strix-halo.local:8080/v1` passed Graphiti-native schema extraction. Both stronger models created exact native edge→episode provenance for M012/M014 and showed correction invalidation, but default text ingestion created no fact edges for M011/M013/M035/M036. A separately labeled configured-policy attempt added Graphiti's supported `custom_extraction_instructions` for short coding facts and was indistinguishable. Focused M035 native trace proves node extraction retained only `release/alpha`, while the native edge-extraction response was empty—no edge/node-name mismatch. Default 35B search also returned an invalidated stale edge with current evidence, a harmful-context observation requiring later temporal policy validation. No fake extractor, LSA, hand-authored edges, paid API, or score was substituted. Full tests: 64 passed, one existing warning. See `research/GRAPHITI_GEN18_LAN_FOLLOWUP.md` and the referenced non-score result directories.
 - questions: Approve or revise the proposed pre-scoring, separately labeled Graphiti configured-product ontology (ReleaseChannel/Branch/Host/Repository/Command/FilePath/Credential plus typed relations), including schema-freeze and anti-query-fit rules. Do not use harness-generated fact triples. The default-policy limitation is now documented and should remain a separate result.

-->

<!-- Historical Gen17 handoff; retained for audit, not current control-plane state.
 - generation: 17
 - base_commit: `9ef9d85`
 - result_commit: `f0e661d`
 - status: complete
 - objective/summary: Closed the agentmemory frozen raw-product plus downstream-reader phase. The exact 28 ChatGPT sidecar responses imported after a BOM-only transport fix and were graded once with the unchanged prompt, cases, and deterministic scorer; no agentmemory retrieval/lifecycle action ran.
 - constraints/results: The narrow `utf-8-sig` input decode accepts one leading UTF-8 BOM from native Google Docs plain-text export and otherwise preserves normal JSON/fail-closed validation. Tests cover BOM/non-BOM equality across 28 response objects and malformed/duplicate/missing/unexpected/fingerprint failure paths; full suite: 64 passed, one existing warning. Import accepted all 28 original IDs/fingerprints and wrote 28 normal responses exactly once. Core reader: 12/14 success (0.857), mean required coverage 0.929, abstention 0.214, lexical prohibited/stale 0.071, wrong-scope 0, lexical harmful conversion 0.071, harmful context successfully ignored 8. Stress: 11/14 (0.786), 0.857, 0.286, 0.071, 0, 0.071, 7. Q010 abstained despite rank-2 historical M013; stress Q012 correctly abstained on missing M018/M019 evidence. Q015 accounts for each lexical prohibited/conversion count even though its answer explicitly rejects timing sleeps; this is a documented substring-grader false positive, not semantic harmful adoption. The reader avoided Q019's wrong-scope Beacon branch. Results: `research/AGENTMEMORY_READER_GEN17.md` and `results/agentmemory_raw_product_gen15_sidecar_transport/reader_results/reader.json`. Lifecycle interpretation remains mandatory: stress Hit@5 1.000/all-relevant 0.958 followed retention of only 82/500 live memories and 418/450 false supersessions (92.9%); reader resilience does not redeem that destructive lifecycle behavior.
 - questions: No further agentmemory raw-product or frozen-reader action is needed. The next benchmark generation should move to a distinct authorized engine/configuration rather than rerun this completed evidence.

-->

<!-- Historical Gen16 handoff; retained for audit, not current control-plane state.
 - generation: 16
 - base_commit: `fe0357b`
 - result_commit: `c156571`
 - status: blocked_drive_bom_transport
 - objective/summary: Retrieved the named complete Gen15 sidecar response bundle from native Google Drive and attempted the unchanged fail-closed importer. No reader answer, request, prompt, fingerprint, retrieval context, or sidecar response layout was changed.
 - constraints/results: The temporary verbatim rclone plain-text export passed semantic preflight: schema 1, `memory-bakeoff-sidecar-response-bundle`, exact request-set hash `9e2dd8955ca9d0eb044f415594b1a9c8e83543de1f58a9955c1c671e2bf6ea5d`, 28 responses; its byte SHA-256 was `34d1b3f1101d8cf5bd84f5239e89e1ab5e563c53d1f26cccf4da219c20cb867b`. Import correctly failed before examining/writing responses because the native Google Docs text export begins `EF BB BF` (UTF-8 BOM), and Python JSON rejects it as `Unexpected UTF-8 BOM`. Both Gen14 response directories remain empty. Gen16 forbade patching validation or locally normalizing the bundle, so this is documented as a transport blocker rather than repaired. Full tests: 62 passed, one existing warning. See `research/AGENTMEMORY_READER_GEN16.md`.
 - questions: Please supply the same complete response bundle as a stored UTF-8 JSON file without BOM (preferred) or via a raw Drive export whose first byte is `{`. Preserve all 28 request IDs, fingerprints, answers, order, and sidecar fields exactly. Codex can then import and grade unchanged.
-->

<!-- Historical Gen15 handoff; retained for audit, not current control-plane state.
 - generation: 15
 - base_commit: `3504dad`
 - result_commit: `9e9032d`
 - status: blocked_awaiting_chatgpt_responses
 - objective/summary: Built and exported the fail-closed Gen14 reader sidecar transport. It carries all 28 frozen requests unchanged; no agentmemory call, context regeneration, reader-model substitution, or answer generation occurred.
 - constraints/results: Export artifact: `results/agentmemory_raw_product_gen15_sidecar_transport/pending_requests.json`, request-set SHA-256 `9e2dd8955ca9d0eb044f415594b1a9c8e83543de1f58a9955c1c671e2bf6ea5d`. It is ordered Gen14 core then stress, 14 requests each, and includes condition/case/request ID/fingerprint/exact OpenAI messages/model/temperature/source path plus the accepted response-bundle schema. `scripts/agentmemory_gen15_sidecar_transport.py import RESPONSE_BUNDLE.json` validates the complete set before writing any normal sidecar response: it rejects changed set hash, duplicate/missing/unexpected IDs, fingerprint mismatches, malformed fields, partial batches, and pre-existing responses. `grade` then uses the unchanged `score_answer` path and reports separate core/stress answer success, coverage/abstention, prohibited/stale/wrong-scope answer rates, harmful conversion, and harmful-context ignored cases. No response bundle exists yet; no answer metrics are published. Full tests: 62 passed, one existing warning. See `research/AGENTMEMORY_READER_GEN15.md`.
 - questions: ChatGPT should create exactly one complete `memory-bakeoff-sidecar-response-bundle` from `pending_requests.json`, preserving every request ID/fingerprint and using model `chatgpt-sidecar`, then place it in the Drive mailbox or otherwise make it available for import. After import, Codex can grade without changing the experiment.
-->

<!-- Historical Gen14 handoff; retained for audit, not current control-plane state.
 - generation: 14
 - base_commit: `821b669`
 - result_commit: `e7e05ea`
 - status: blocked
 - objective/summary: Preserved Gen13 unchanged and prepared exact, sidecar-compatible downstream reader inputs from its frozen authoritative contexts. No agentmemory retrieval/lifecycle ingestion occurred, and no reader answer was fabricated because this Codex session has no interactive ChatGPT-sidecar responder.
 - constraints/results: The compatible prior reader is `GPT-5.6 Sol via ChatGPT sidecar`, with the unchanged strict-memory system prompt, `memory_bakeoff.reader_eval._reader_prompt`, temperature 0.0, 14 held-out `ANSWER_SPECS`, and deterministic `score_answer` grader. Existing replay cannot answer these new contexts because it requires an exact archived request fingerprint; fake/local/API backends would be a different reader identity and were not substituted. `results/agentmemory_raw_product_gen14_reader_requests/` contains 14 fingerprint-validated pending requests per condition (core and stress), exact ranked canonical IDs/context text, prohibited/stale and wrong-scope ranks, retrieval artifact hashes, and no response files. The selected Gen13 r1 contexts are representative: r1/r2/r3 reader-facing IDs/texts were byte-identical in each condition. Exposure only, not answer propagation: prohibited/stale context was present in 10/14 core and 9/14 stress held-out cases; wrong-scope context in 1/14 each. Stress still must be read alongside its lifecycle loss: 82/500 live memories and 418/450 false supersessions (92.9%). Full tests: 59 passed, one existing warning. Research: `research/AGENTMEMORY_READER_GEN14.md`.
 - questions: An interactive ChatGPT sidecar responder must service the two pending batches before deterministic grading can report answer accuracy/coverage/abstention and harmful-context propagation. Should ChatGPT service those frozen requests next, preserving their fingerprints and writing only sidecar-protocol responses?
-->

<!-- Historical Gen13 handoff; retained for audit, not current control-plane state.
 - generation: 13
 - base_commit: `69e3239`
 - result_commit: `810e688`
 - status: complete
 - objective/summary: Completed the first authoritative agentmemory 0.9.29 local-embedding `raw_product` benchmark: a fresh-state/native-agent isolation preflight, then three fresh core (50) and three fresh stress (500) runs with exact native provenance and lifecycle evidence. This is raw/no-LLM, not a complete LLM-enabled `product` result.
 - constraints/results: Independent upstream commit `e04ba88819c365c9acf9d6661ea802143e728bd6` / agentmemory 0.9.29; macOS arm64, Node 26.8.1, iii 0.11.2, transformers 4.2.0, `EMBEDDING_PROVIDER=local`, q8 Xenova `all-MiniLM-L6-v2` 384-D (ONNX SHA-256 `afdb6f1a0e45b715d0bb9b11772f032c399babd23bfc31fed1c170afc848bdb1`). Product retrieval: cosine+BM25 RRF k60, vector/BM25 0.6/0.4, 5% agreement bonus, 2*limit candidates, max 3/session; LLMs, consolidation, graph extraction, autocompress, and reranking off. Isolation passed: native agent A saw two records under different project labels; fresh state/native agent B saw neither and listed zero. No harness filtering. All core runs: Hit@5 1.000, MRR 0.889, all-relevant@5 1.000, prohibited@5 0.142, harmful presence 0.667, mean 428.5 chars. All stress runs: 1.000, 0.847, 0.958, 0.133, 0.625, 495.7 chars. Each stress state retained only 82/500 memories and falsely superseded 418/450 distinct stress distractors (92.9%), with zero legitimate correction supersessions. Q007 ranked stale M011 above M012; prohibited historical/failure content commonly appeared alongside relevant results. Full tests: 58 passed, one existing warning. Full evidence is `research/AGENTMEMORY_RAW_PRODUCT_GEN13.md` and `results/agentmemory_raw_product_gen13_*`; the unsuffixed preflight is preserved as a no-score synchronous-launcher failure.
 - questions: Should the next round apply the existing deterministic reader to these validated retrieval traces, or move to Hindsight first? No new agentmemory raw-product run is needed.
-->

<!-- Historical Gen12 handoff; retained for audit, not current control-plane state.
- generation: 12
- base_commit: `fc127d3`
- result_commit: `c4b8115`
- status: blocked
- objective/summary: Completed the first real intended-stack agentmemory raw-product diagnostic and lifecycle smoke at the pinned 0.9.29 source. No core/stress score was run. Local embedding, native ingest/search IDs, lifecycle state, and the Jaccard supersession path were exercised; raw-product scoring is blocked by cross-project search contamination.
- constraints/results: Independent upstream checkout verified `rohitg00/agentmemory` `e04ba88819c365c9acf9d6661ea802143e728bd6` / 0.9.29. The real LLM-free local stack ran on macOS arm64: Node 26.8.1, npm 11.19.0, iii-engine 0.11.2, @huggingface/transformers 4.2.0, `EMBEDDING_PROVIDER=local`, q8 `Xenova/all-MiniLM-L6-v2` 384-D (ONNX SHA-256 `afdb6f1a0e45b715d0bb9b11772f032c399babd23bfc31fed1c170afc848bdb1`), in-memory cosine plus BM25 0.4/vector 0.6 RRF k=60. LLM/auto-compress/consolidation/LLM graph extraction were off; learned reranking was source-default off. The clean chronological trace has eight writes using correction/duplicate/paraphrase/near-neighbor/procedure cases and native state after each: exact duplicate superseded legitimately, but explicit correction M011→M012 remained two live facts, paraphrase also remained live, M035/M036 and M024/M023 both survived. The current-build query ranked stale M011 first, so correction safety failed. The historical 418/450 controlled false-supersession result remains unchanged; this small set was below strict Jaccard >0.7 except the exact duplicate. Source inspection confirms candidate generation is BM25 top 50 plus strict lexical Jaccard >0.7; embeddings/reranking do not choose supersession. Exact native lineage is available via supported `sourceObservationIds` plus returned `mem_*`/`obsId`; `type` markers are normalized to `fact`. Adapter now uses that native map and fails closed on a foreign ID. Crucially, `/memories?project=` and `/smart-search` do not enforce project scope in this pin: a five-record retrieval smoke returned two native IDs from another project. Thus a future multi-project benchmark run would be contaminated; adapter refuses publication rather than filtering/reranking in the harness. First trace is preserved invalidated because it exposed the list-endpoint filter defect; clean trace is authoritative diagnostic only. Full tests: 57 passed, one existing warning. Details/traces: `research/AGENTMEMORY_RAW_PRODUCT_GEN12.md`, `results/agentmemory_raw_product_gen12_lifecycle_smoke_clean/trace.json`; reusable runner `scripts/run_agentmemory_lifecycle_smoke.py`.
- questions: Is a verified isolated `agentId` deployment acceptable as the product scope for a later benchmark (the only native retrieval scope at this pin), or should we stop agentmemory scoring until an upstream project-scope fix/pin is available? Do not work around the defect by harness-side filtering or fuzzy mapping.
-->
