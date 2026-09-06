# Round 3 — final readout

**Status: CLOSED.** No live Round 3 question remains.

Authoritative for the round. Source registry, machine-readable, at
`results/gen107/attempt1/round3_closure.json` with a verifying `MANIFEST.json`.
Supersession detail lives in `ROUND3_SUPERSESSION_RESULT.md`; this document is
the round-level synthesis above it.

---

## 1. The question, and the design

Round 2 measured engines on clean fixtures. Round 3 asked what happens **as
density rises**: put the answer in a store alongside a superseded version of
itself, a record from another scope, and 0, 4, 16 or 64 similar-but-distinct
distractors — then ask.

Frozen before any run: fixture `interference-v1` (Gen95), adapters and per-engine
retrieval budgets (Gen96), replication questions Q1–Q3 with their verdict rules
(Gen98). Each engine keeps **its own budget**: a native result count for perseus,
mem0 and agentmemory; a **token budget** for hindsight, which is not a top-k
window and is never compared to one.

## 2. Fixture-specific observation versus cross-core replication

Gen97 ran one semantic core and produced a headline: perseus loses the target at
64 distractors. Gen99 re-ran the design across **four independent semantic
cores** — `throughput:atlas`, `branch:vega`, `oncall:kestrel`, `budget:solstice`
— against the pre-registered questions.

| Gen98 question | verdict |
|---|---|
| Q1 — does perseus's rank decline with density? | **`FIXTURE_SPECIFIC`** |
| Q2 — does stale-version interference recur? | **`REPLICATED_ACROSS_CORES`** |
| Q3 — do the other three hold their Gen97 shapes? | **`PARTIAL_REPLICATION`** |

**Cores are reported separately and never averaged.** Q3 is partial precisely
because the answer differs by core — agentmemory holds its shape in two of four.
A mean would have erased the finding.

**The one general result of Round 3:** every engine co-returns the superseded
record alongside the current one — **192 of 192** observations, every engine,
core, load and repetition. Gen97 saw it 48 of 48 on one core; Gen99 replicated it.

## 3. Supersession: three mechanism kinds, never one score

Gen100 asked a prior question and got an uncomfortable answer: **three of the
four engines had never been ASKED to express supersession.** No engine lacks a
surface — three were `SURFACE_PRESENT_BUT_UNUSED`, one `ALREADY_EXERCISED`.
The 192/192 was partly a question we had failed to pose.

Gen101 froze honest, product-native bindings. The mechanisms are **not
commensurable**, and combining them would be a category error:

- **`EXPLICIT_LINEAGE`** — an operator names two records and asserts a relation.
- **`STATE_TRANSITION`** — an operator asks for a state change.
- **`PRODUCT_DECIDES`** — the product applies its own rule, unbidden.

Corrected results, per kind, on `interference-v3` under the pinned Gen96
retrieval profile:

| engine | kind | current kept | stale removed | note |
|---|---|---|---|---|
| perseus | `EXPLICIT_LINEAGE` | 48/48 | **48/48** | no mechanisms scored at all; rank rises in 41/48 as the stale record leaves the window |
| hindsight | `STATE_TRANSITION` | 48/48 | **0/48** | not one paired cell differs — same mechanisms, `target_present`, ranks |
| agentmemory | `PRODUCT_DECIDES` | 48/48 | **12/48** | all twelve in `oncall:kestrel`; unpaired by design |
| mem0 | `PRODUCT_DECIDES` | — | — | `NOT_AVAILABLE_IN_PINNED_PROFILE` |

**Read each row on its own terms.** Perseus's lineage works completely and costs
nothing. Hindsight's invalidation is *accepted and recall-identical* — and an
accepted API call is an **operation, not proof of an internal state change**;
whether its store changed is not established, only that recall did not. That is
the same shape as Gen70's `query_timestamp`. AgentMemory keeps current truth
everywhere and suppresses stale records only where its **lexical** Jaccard
threshold is met — sound mechanism, narrow reach, and nothing here tests
paraphrase. Mem0's arm is an **unavailable configuration, not a failed score**:
`infer=True` needs an LLM the pinned profile deliberately excludes.

## 4. Product behaviour versus harness defects

The round's sharpest lesson is about our own instrument.

`observations_for` took `set(visible_ids(...))` and then iterated the fixture,
discarding the resolver's sequence. **Gen102 ran the v2 ingest order while
reporting itself as v3.** Gen104 located it by tracing identity end to end;
Gen105 found the same idiom at **five independent sites**, one of which
(`gen102_hindsight_arms.py`) also read v3.

Blast radius, measured rather than assumed:

| fixture | cases whose ingest order the defect changed |
|---|---|
| `interference-v1` (Gen97) | **0 / 4** |
| `interference-v2` (Gen99) | **0 / 16** |
| `interference-v3` (Gen102) | **16 / 16** |

**Gen97 and Gen99 stand.** The defect could only bite where resolver order
differs from construction order, and in v1 and v2 they coincide. Only v3 work
was affected, and it has been re-measured.

### Retracted and superseded

| claim | retracted by | why |
|---|---|---|
| Gen85's reader-order effect | Gen85 | a `CITE` parse defect scored inline replies UNPARSED; attempt quarantined |
| Gen100's kestrel explanation | Gen102 | the v3 repair was predicted to fix it and did not — right answer, wrong mechanism |
| Gen102's agentmemory result | Gen104 | harness, not product; current record present 48/48 |
| Gen103's named suspect (provenance mapping) | Gen104 | the mapping was sound; naming a likely area is still a guess |

`research/PI_SUPERSESSION_ABLATION_GEN102.md` is **superseded and preserved**,
carrying a pointer to the canonical account. Nothing was deleted.

## 5. What backs each claim — and what does not

| evidence class | meaning | count |
|---|---|---|
| `MANIFEST_VERIFIED` | sha256 recorded and checkable under `immutable-evidence-v1` | **0** |
| `COMMITTED_REPORT` | aggregate committed and reproducible; cells not manifested | **6** |
| `LEGACY_UNMANIFESTED` | predates the contract; provenance unprovable | **3** |

**No Round 3 conclusion is manifest-verified.** The contract arrived at Gen106,
after the evidence it would have protected.

**The provenance loss, stated plainly.** Gen105 re-ran corrected arms into the
directory the original run had used, and `results/` was untracked. The
pre-correction Gen102 cell-level artefacts were **destroyed**. Aggregates
reproduce exactly — Gen102's 16/16 and 0/16 are in the committed report and both
came back — but **no old-versus-new cell-level diff is recoverable**. These
artefacts are not reconstructed, and no manifest is back-dated over them. That
failure is what `immutable-evidence-v1` now prevents: attempt-scoped paths, a
write that refuses to overwrite, and a hash per artefact.

## 6. What Round 3 does NOT establish

- **No cross-engine ranking.** The engines were never scored against each other
  on a common ruler; budgets differ by design.
- **No supersession score.** Three mechanism kinds are not commensurable.
- **Nothing about semantic supersession.** AgentMemory's rule is lexical and the
  fixtures never tested paraphrase.
- **Nothing outside the pinned Gen96 profiles.** Every result is
  configuration-scoped truth.
- **Nothing about whether stale co-return harms an answer.** That is a reader
  question and Round 3 never asked it.

## 7. The next line — one recommendation

**Go to the reader layer.** Round 3's one general result is that every engine
co-returns stale records, and only explicit lineage removes them. Whether that
co-return actually *changes an answer* is untested: Gen85 attempted it and was
quarantined for a parse defect, so the question is open and the fixture work
already exists.

The parked items **P1** (SKILL.state / structured operational state) and **P2**
(observational semantic state) are now *eligible* — Round 3 supplies the direct
supersession and interference evidence they were waiting on. They are **named
here and deliberately not opened**; see `handoff/PARKED_FUTURE_RESEARCH.md`.
