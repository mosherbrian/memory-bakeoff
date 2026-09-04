# Evidence index

This is a map of what has actually been measured, not a leaderboard. A score is
only comparable inside its own experiment class and evaluated configuration, so
every row carries its class, its caveat, and links to the authoritative write-up
and the machine-readable artifacts behind it.

Round 1 is closed. Its authoritative narrative is
[`research/ROUND1_FINAL_READOUT.md`](research/ROUND1_FINAL_READOUT.md); prefer it
over any older score text elsewhere in this repository. Round 2 is the
engine-independent point-in-time work and the pi-observational-memory
generations. The full generation ledger is
[`handoff/CODEX_TO_CHATGPT.md`](handoff/CODEX_TO_CHATGPT.md).

## Evidence classes

| Class | Meaning |
|---|---|
| `baseline` | Harness-owned deterministic retrieval. Not a product. |
| `controlled_core` | Real upstream code with a shared or replaced component so one variable is isolated. |
| `raw_product` | The real product retrieval path in a documented raw/no-LLM mode. Not normal end-to-end behavior. |
| `full_product_context_production` | The product's own agent-visible context, produced by its own compaction. |
| `no-score diagnostic` | A block, gate, or defect demonstrated. Not a weak score. |

## Round 1 — retrieval, safety, and lifecycle

| System / evaluated configuration | Class | Strongest valid evidence | Lifecycle / safety caveat | Research | Results |
|---|---|---|---|---|---|
| BM25, TF-IDF, dense LSA, hybrid RRF | `baseline` | stress Hit@5: BM25/TF-IDF 0.792, dense 0.583, hybrid 0.708; reader 14/14 for dense LSA and hybrid | deterministic harness anchors, not products | [Round 1 readout](research/ROUND1_FINAL_READOUT.md) | [baseline findings](results/BASELINE_FINDINGS.md), [reader findings](results/READER_FINDINGS.md), [top-k](results/TOPK_FINDINGS.md) |
| Habitus, real pinned core | `controlled_core` | stress Hit@5 0.792, prohibited@5 0.025 | core diagnostic only; no full product claim | [retrieval credit](research/HABITUS_RETRIEVAL_CREDIT.md) | [core](results/habitus_core), [stress](results/habitus_stress) |
| MemBukkit, shared-LSA bucket routing | `controlled_core` | Hit/all-relevant 0.583/0.542 while opening ~32.9% of the bank | routing finding only; not the intended encoder/reranker | [intended model](research/MEMBUKKIT_INTENDED_MODEL_GEN7.md) | [stress LSA](results/membukkit_stress_lsa), [core](results/membukkit_core) |
| MemBukkit, documented fallback | `raw_product` | Hit/all-relevant 0.875/0.750 | intended fine-tuned model repositories unavailable | [fallback](research/MEMBUKKIT_FALLBACK_GEN8.md) | [hybrid 1.0](results/membukkit_hybrid_1.0), [stress](results/membukkit_stress) |
| MemBukkit, intended models | `raw_product` | Stress hit/all-relevant 0.917/0.833 against the fallback pair's 0.875/0.750, with stress MRR 0.449 against 0.554 | configuration-scoped to the intended MemseekAI pair; a matched fallback control ran beside it and reproduced Gen8 exactly | [intended Round1](research/MEMBUKKIT_INTENDED_ROUND1_GEN41.md) | [core](results/membukkit_intended_gen41_product_default_core-r1), [stress](results/membukkit_intended_gen41_product_default_stress-r1) |
| Mem0, `infer=False`, explicit dense+BM25 | `raw_product` | Hit/all-relevant 0.958/0.917; zero non-empty negatives | no LLM update or lifecycle semantics in this lane | [findings](research/MEM0_FINDINGS.md), [gen10](research/MEM0_RAW_PRODUCT_GEN10.md), [lifecycle gen11](research/MEM0_PRODUCT_LIFECYCLE_GEN11.md) | [core r1](results/mem0_raw_product_gen10_core-r1), [stress clean r1](results/mem0_raw_product_gen10_stress-clean-r1) |
| Hindsight v0.9.2, raw/no-LLM learned-reranker path | `raw_product` | Hit/all-relevant 0.833/0.708 | composite DB/model/runtime identity must travel with the row | [findings](research/HINDSIGHT_FINDINGS.md), [reranker gen6](research/HINDSIGHT_LEARNED_RERANKER_GEN6.md), [external Postgres gen5](research/HINDSIGHT_EXTERNAL_POSTGRES_GEN5.md) | [gen4 core r1](results/hindsight_gen4_core_r1), [gen5 external stress r1](results/hindsight_gen5_external_local_stress_r1) |
| agentmemory 0.9.29, isolated native `agentId` | `raw_product` | Hit/all-relevant 1.000/0.958 | **82/500 live memories; 418/450 stress distractors falsely superseded (92.9%)** | [gen13](research/AGENTMEMORY_RAW_PRODUCT_GEN13.md), [findings](research/AGENTMEMORY_FINDINGS.md) | [core r1](results/agentmemory_raw_product_gen13_core-r1), [stress r1](results/agentmemory_raw_product_gen13_stress-r1) |
| agentmemory frozen-context reader | `raw_product` | reader 12/14 core, 11/14 stress over frozen contexts | reader evidence cannot redeem the lifecycle loss above | [reader gen17](research/AGENTMEMORY_READER_GEN17.md) | [gen14 requests](results/agentmemory_raw_product_gen14_reader_requests) |
| Claude-Mem, FTS/semantic policy | `controlled_core` | default 90-day window Hit@5 0.208; window disabled 0.583 | no compression worker; no product score | [findings](research/CLAUDE_MEM_FINDINGS.md) | [core](results/claude_mem_compare_core), [stress](results/claude_mem_compare_stress450) |
| Graphiti, Gen18–20 | `no-score diagnostic` | extraction and lifecycle gates failed; includes a cross-environment false invalidation | no score exists; do not infer one | [gen19](research/GRAPHITI_GEN19_FINDINGS.md), [gen20](research/GRAPHITI_GEN20_FINDINGS.md) | [gen20 json gate](results/graphiti_gen20_json_gate2), [gen18 sentinel](results/graphiti_gen18_sentinel) |
| **Perseus Vault v2.23.2, CLI-write + MCP hybrid recall** | `raw_product` | **Hit/all-relevant 0.958/0.958; prohibited@5 0.108** | **393/500 active after successful writes; 107 distinct-valid active-state losses; historical recoverability unknown** | [gen21](research/PERSEUS_VAULT_GEN21.md), [gen22 lifecycle addendum](research/PERSEUS_VAULT_GEN22_LIFECYCLE_ADDENDUM.md) | [gen22 lifecycle analysis](results/perseus_vault_gen22_lifecycle_analysis.json), [audited core r1](results/perseus_vault_gen21_audited_core_r1), [audited stress r1](results/perseus_vault_gen21_audited_stress_r1) |

Perseus holds one of the strongest retrieval results in the field **and** the
largest unexplained active-state loss. Both halves are the result. The frozen
Gen21 artifacts lack the lineage to call that loss destructive deletion, so it
is reported as loss with unknown historical recoverability.

## Round 2 — the point-in-time ruler, pi-observational-memory, and Perseus

The engine-independent ruler is frozen as `longitudinal-v1`:
[framework](research/LONGITUDINAL_POINT_IN_TIME_FRAMEWORK.md),
[fixture](research/LONGITUDINAL_V1_FIXTURE.json),
[manifest](research/LONGITUDINAL_V1_MANIFEST.json).

| Generation | Evaluated profile | Class | Evidence | Caveat | Research | Results |
|---|---|---|---|---|---|---|
| 24 | OM 3.0.4 audit + calibration | `no-score diagnostic` | native `observer.error`: extension ctx stale after session replacement | stop condition; no observation exposed | [gen24](research/OBSERVATIONAL_MEMORY_GEN24.md) | [calibration](results/observational_memory_gen24_calibration) |
| 25 | OM 3.0.4 under persistent Pi RPC | `no-score diagnostic` | three calibrations reached native quiescence; Gen24 stale-context failure avoided | calibration only; no v1 result published | [gen25](research/OBSERVATIONAL_MEMORY_GEN25_RPC.md) | [calibration](results/observational_memory_gen25_rpc_calibration) |
| 26 | OM 3.0.4 longitudinal-v1 ingestion | `raw_product` | 3/3 repetitions, 16/16 barriers, all nine checkpoints | Pi compaction declined; no agent-visible context, no retrieval score | [gen26](research/OBSERVATIONAL_MEMORY_GEN26_LONGITUDINAL.md) | [longitudinal](results/observational_memory_gen26_longitudinal) |
| 27 | OM 3.0.4 `om-context-production-v1` | `full_product_context_production` | 3 repetitions, 40/40 barriers each, 67 native `om.folded` folds; reader 28/36 under the v1 contract | zero wrong answers and zero prohibited hits; all 8 failures were citation-provenance failures under a defective citation contract | [gen27](research/OBSERVATIONAL_MEMORY_GEN27_CONTEXT_PRODUCTION.md) | [context production](results/observational_memory_gen27_context_production) |
| 28 | `om-context-production-v2` citation contract | scorer correction over Gen27 captures | same frozen responses regraded: **33/36**, 11/12 in each repetition | not a new product run and not new fixture exposure; v1 remains 28/36 as historical evidence | [gen28](research/OBSERVATIONAL_MEMORY_GEN28_CITATION_CONTRACT_V2.md) | [citation contract v2](results/observational_memory_gen28_citation_contract_v2) |
| 29 | Perseus Vault v2.23.2, operator CLI write + native hybrid recall | `raw_product` | 3 identical repetitions against `longitudinal-v1`: zero future leakage, exact provenance on every hit, transaction-time belief answered correctly | valid-time is collinear with transaction time in this write path, so every corrected-history and late-history case fails; configuration collapse and stale persistence are real; nothing was lost at 16 records | [gen29](research/PERSEUS_VAULT_GEN29_LONGITUDINAL.md) | [longitudinal](results/perseus_vault_gen29_longitudinal) |
| 30 | Perseus Vault v2.23.2, agent-facing MCP `remember` + admission review | `no-score diagnostic` | post-hoc write-surface ablation, **blocked**: `remember` honours a retroactive `valid_from`, but the approval that makes a record serveable resets it to the approval instant | serveable and retroactive are mutually exclusive in this version, so no independent application-time axis exists to score; Gen29 stands unchanged | [gen30](research/PERSEUS_VAULT_GEN30_MCP_VALID_TIME_ABLATION.md) | [admission probe](results/perseus_vault_gen30_mcp_valid_time) |
| 31 | Hindsight v0.9.2, raw/no-LLM retain + native hybrid recall with learned CPU reranker | `raw_product` | 3 identical repetitions against `longitudinal-v1`: zero future leakage, exact provenance on every hit, and **zero correction failure and zero history erasure** — a vantage-point query reaches the earlier state | scope collapse and belief/truth confusion appear where Perseus had none; the event-time axis (`occurred_*`) is unreachable in the raw profile, so mention time is the only axis | [gen31](research/HINDSIGHT_GEN31_LONGITUDINAL.md) | [longitudinal](results/hindsight_gen31_longitudinal) |
| 32 | Mem0 2.0.19, raw `Memory.add(infer=False)` + embedded Qdrant dense+BM25 | `raw_product` | 3 identical repetitions against `longitudinal-v1`: zero future leakage, exact provenance, and **all seven cross-engine failure classes reproduced in an engine with no temporal retrieval surface at all** | one extra `stale_persistence` (LQ20) is the direct cost of having no as-of filter; Mem0 can filter on scope metadata but the scored Gen10 identity deliberately does not | [gen32](research/MEM0_GEN32_LONGITUDINAL.md) | [longitudinal](results/mem0_gen32_longitudinal) |
| 33 | agentmemory 0.9.29, native remember + smart-search with **write-time supersession enabled** | `raw_product` | 3 identical repetitions: retirement activates twice per run and **halves configuration collapse** (6→3) and reduces false persistence (9→6) | it is the only engine that falsely supersedes (lifecycle `false_supersession` 3); the rule is lexical Jaccard >0.7 over tokens longer than two characters, so `C1`/`C2` are invisible to it | [gen33](research/AGENTMEMORY_GEN33_LONGITUDINAL.md) | [longitudinal](results/agentmemory_gen33_longitudinal) |
| 34 | Round-2 reporting-layer integrity audit (no product run) | `no-score diagnostic` | every cross-engine number rebuilt from leaf evidence through a fail-closed reporting layer; **all Round-2 conclusions survive independent derivation unchanged** | the old summarisers carry 45 default-fallback patterns where missing evidence becomes a number; historical scripts left intact, future publication routes through the common reporter | [gen34](research/ROUND2_REPORTING_INTEGRITY_GEN34.md) | [ledger](results/round2_gen34_integrity) |
| 35 | agentmemory 0.9.29 from one patched build, automatic Jaccard retirement **ON vs OFF** | `controlled_core` (modified-product ablation) | 6 fresh runs, 3 per arm, counterbalanced: the enabled arm reproduces Gen33 exactly and the disabled arm **removes every false supersession** (lifecycle 3 -> 0) and every `history_erasure` and `correction_failure` | with retirement off, `configuration_collapse` returns to 6 and `false_persistence` to 9 — the append-only figures — so retirement traded those failures rather than fixing them; 13 of 20 cases differ and every difference traces to `L001`/`L002`, zero confounds | [gen35](research/AGENTMEMORY_GEN35_RETIREMENT_ABLATION.md) | [ablation](results/agentmemory_gen35_retirement_ablation) |
| 36 | MemConflict `ec51d5d` external-benchmark contract (no product run) | `external-benchmark contract / no contestant score` | released benchmark pinned and measured locally: 30 personas, 1,579 sessions, 3,750 questions, 142,093 ingestible messages; public/scorer-only registry, chronology boundary and three scoring lanes frozen | upstream white-box scoring is LLM-judged, and four paths in its scorer turn an unmeasured metric into 0.0; exact ID-level support is derivable for 3,569 of 3,750 questions and the other 181 are UNMEASURED, not guessed | [gen36](research/MEMCONFLICT_GEN36_CONTRACT.md) | [contract](results/memconflict_gen36_contract) |
| 37 | Perseus Vault v2.23.2 Gen29 identity on MemConflict, 3-persona calibration | `external_benchmark_calibration_raw_product` (development-exposed) | 14,304 writes and 399 questions with zero unmapped provenance, zero empty returns, zero future-session leakage; exact-provenance hit@3 168/380 measured, log-rank@3 0.376 | static conflict is where it fails (6/36) while conditional is free (29/29); the product quarantined 25 writes under its own interference bound, with a native reason on every one | [gen37](research/MEMCONFLICT_GEN37_PERSEUS_MEM0_CALIBRATION.md) | [calibration](results/memconflict_gen37_calibration/perseus) |
| 37 | Mem0 2.0.19 Gen32 raw `infer=False` identity on MemConflict, 3-persona calibration | `external_benchmark_calibration_raw_product` (development-exposed) | same 14,304 writes and 399 questions, same clean contract record; exact-provenance hit@3 180/380 measured, log-rank@3 0.392, and the store holds exactly what was written | static conflict fails here too (10/36); both engines land on rank 1 exactly 107 times from unrelated retrieval stacks, and Mem0 costs 394-402 ms per query against Perseus's 22-26 ms | [gen37](research/MEMCONFLICT_GEN37_PERSEUS_MEM0_CALIBRATION.md) | [calibration](results/memconflict_gen37_calibration/mem0) |
| 38 | Perseus Vault v2.23.2 on MemConflict, **full release**, 27-persona held-out primary | `external_benchmark_full_release_raw_product_exact_provenance` | 30 personas, 142,093 writes, 3,750 questions; held-out exact-provenance hit@3 1,484/3,189 (0.465), log-rank 0.385, and zero unmapped provenance, empty returns or future-session leakage | static conflict is its weakest class at 0.343; its replication gate exposed tie-ordering instability in hybrid RRF (77/399 reorderings, all tie-explained, 2/380 hit@3 changes) | [gen38](research/MEMCONFLICT_GEN38_FULL_RELEASE.md) | [full release](results/memconflict_gen38_full_release/perseus) |
| 38 | Mem0 2.0.19 raw `infer=False` on MemConflict, **full release**, 27-persona held-out primary | `external_benchmark_full_release_raw_product_exact_provenance` | same 30 personas and 142,093 writes; held-out hit@3 1,455/3,189 (0.456), log-rank 0.386; replicated its Gen37 calibration leaves byte-for-byte with zero ordering, score or hit-class differences | static conflict is also its weakest substantive class (0.383 vs dynamic 0.419); it quarantines nothing and still misses 200 static questions whose support was fully admitted | [gen38](research/MEMCONFLICT_GEN38_FULL_RELEASE.md) | [full release](results/memconflict_gen38_full_release/mem0) |
| 38 | Frozen Gen36 BM25 baseline over the full release | `baseline` (context only) | held-out hit@3 909/3,189 (0.285) on the same questions and the same lane | **on static conflict it reaches 0.312 against Perseus's 0.343** — the engines beat it by ~20 points on dynamic questions and by at most 3 on static | [gen38](research/MEMCONFLICT_GEN38_FULL_RELEASE.md) | [baseline](results/memconflict_gen38_full_release/bm25) |

OM exposes no natural-language semantic query surface, so no Hit@k or ranking
score exists for it in any generation.

Gen29 is the first Round-2 contestant run against the frozen ruler. Its numbers
answer a different question from Gen27/28 and are not comparable to them: OM has
no query surface and Perseus does.

Gen29, Gen31, Gen32 and Gen33 are the Round-2 contestants so far. Hindsight repairs
exactly what Perseus's collapsed time axis broke and breaks two things Perseus got
right; Mem0, which has no temporal retrieval surface at all, then reproduces all
seven of the classes the first two shared — five of them at identical counts.

Gen33 moved the one variable the other three held fixed. agentmemory retires on its
own, and the trade is visible: configuration collapse halves, false persistence
falls, stale persistence is unchanged, and it becomes the only engine that falsely
supersedes a record that was still true. Neither architecture is safe — append
everything and you cannot say what is current; retire on similarity and you delete
what was true. This is a contrast across products, not a controlled experiment
within one.

**Correction, 2026-09-03, verified in Gen34.** Gen31's originally published
lifecycle numbers were never measured: three SQL queries in its collector failed
silently and returned plausible empty answers, and the "false supersession 0"
claim for the append-only engines was read from the case-level stream, where that
class cannot appear. Gen31 was re-run with a collector that fails loudly — its
case results are byte-identical and its lifecycle is genuinely clean.

Gen34 then rebuilt every Round-2 cross-engine number from committed leaf evidence
through a fail-closed reporting layer, replaying the frozen lifecycle scorer and
reconciling against stored aggregates. **Every conclusion survived unchanged**,
including the five identical classes and the retirement trade. The append-only
engines' `false_supersession 0` is now MEASURED_ZERO from the lifecycle scorer
rather than absent from the wrong table: the statement is the same, its evidential
basis is entirely different.

Gen35 turned that cross-product contrast into a within-engine intervention. One
runtime gate around three assignments in agentmemory's `remember` path, one built
artifact, both arms run from it, everything else held constant. The enabled arm
reproduces Gen33 case for case; the disabled arm retires nothing. **Retirement did
not fix the append-only failures, it traded them.** Turning it off removes all
three false supersessions and both history classes, and puts configuration
collapse and false persistence back at exactly the numbers the three append-only
engines produced. This is the project's first causal claim, and it is scoped to
this pinned agentmemory system only.

Gen36 opens a second evidence lane and deliberately scores nothing in it. Before
any product meets MemConflict, the benchmark's own meaning is frozen: which fields
a system may see, where each question's history stops, and which of its numbers
were measured. The audit found the same failure the project keeps meeting, this
time in the external scorer: when its LLM judge is unavailable it falls back to a
rule-based path that leaves every retrieval metric at 0.0, so an outage is
published as a retrieval miss. Our lanes are kept separate and unmeasured stays
unmeasured. A benchmark-owned exact-provenance lane credits retrieval by released
session identity for 95% of questions; the rest are marked unmeasurable rather
than assigned a plausible number.

Gen38 ran the whole release: 30 personas, 142,093 writes and 3,750 questions per
engine, with the 27 personas outside the calibration subset as the primary slice.
Both engines had to reproduce their Gen37 calibration leaves before touching it.
Mem0 reproduced them exactly; Perseus did not, and the reason turned out to be its
own hybrid RRF returning tied scores whose order is stable within a run but not
across runs — 77 reorderings, every one explained by identical tied scores, worth
2 of 380 hit@3 classes. The gate was given an explicit tolerance for that before
any held-out persona ran, and the instability is published as its own number.

The pre-registered generalization hypothesis holds: static conflict — an old truth
against a newer contradiction — is the weakest class for Perseus (0.343) and the
weakest substantive class for Mem0 (0.383). The mechanism diagnostic then splits
that failure in two: about a quarter of static misses return the contradiction
without the truth, and a third return neither. Only the first is `false_persistence`;
the rest is simple unreachability. And the frozen BM25 baseline reaches 0.312 on
static against Perseus's 0.343, so on the class the benchmark exists to probe, two
production memory systems are within a few points of a lexical index over the same
history.

Gen37 put two real products against that frozen contract at calibration scale —
three personas, 14,304 writes and 399 questions each, development-exposed and
deliberately not an official score. The contract held: no gold reached either
product, every returned item mapped through its own write receipt, nothing was
retrieved from a session the question could not see, and reads left both stores
byte-identical. The failure both engines share is the interesting part. Questions
that bind a preference to a condition are almost free (29/29 for both), while
questions that ask which of two contradictory statements is true are where both
collapse: 6/36 and 10/36. That is Round 2's `false_persistence` reappearing on a
corpus built by other people, with a different ruler.

The scale guess is also now a measurement. Gen36 estimated 12-40 hours per engine
for the full release; measured, it is 5.8 hours for Perseus and 14.7 hours for
Mem0, with the linear and rate-based projections agreeing to within 2%.

## MemBukkit intended-model path — identity evidence, no score

`product_identity_reproduction_no_score`. Not a result row, not comparable with
anything above it.

MemBukkit was the intended default engine and has carried an asterisk since
Gen7, when its two fine-tuned models were private, the resolver silently
substituted off-the-shelf ones, and the harness failed closed rather than score
a fallback. Both repositories are now public. On the original pinned upstream
commit, with no source change, the intended path loads
`MemseekAI/membukkit-biencoder-v1` at revision `50ab0a1f` and
`MemseekAI/membukkit-reranker-v2` at revision `0b46ab53`, every snapshot file
reconciling to those revisions, and runs a synthetic fixture end to end with
exact provenance and no substitute model anywhere in the trace. A second
process with the network blocked at the socket layer reproduces all eight
queries in identical order from the frozen snapshot, and a whole fresh run
rebuilds both leaf digests byte-identically.

That retires the blocker. It says nothing about quality: no score was produced
and the fixture was built to exercise the path, not to measure it. See
`research/MEMBUKKIT_INTENDED_MODEL_GEN40.md`.

## MemBukkit on the MemConflict calibration slice — development-exposed, not a full release

`external_benchmark_calibration_raw_product_exact_provenance`, three personas, 14,304 writes and
399 questions. Not an official MemConflict score and not comparable with a full-release row.

Hit@3 0.3237 measured over 380 questions, against the committed calibration figures of 0.4421 for
Perseus, 0.4737 for Mem0 and 0.2895 for the BM25 pilot on the same denominator. By class:
conditional 0.6207, dynamic 0.3175, static 0.1389. Contract integrity clean — zero unmapped
provenance, zero future-session leakage, zero write failures, inventory reconciling on all three
personas.

The mechanism result is the reason this ran. MemBukkit opens only part of the bank before its
cross-encoder sees anything, so unreachability and rank loss are separable here in a way they were
not for the first two engines. Of 36 static questions, 6 hit at five and **all 30 misses had their
gold support inside the opened candidate region** — routing exclusion explains none of them. A
third engine, with a different architecture, loses the old truth at the ranking stage while the
record is stored, searchable and already in the candidate set. See
`research/MEMBUKKIT_MEMCONFLICT_GEN42_CALIBRATION.md`.

## First Pi state/control prototype — architecture evidence, no score

`architecture_prototype_no_score`. Not a benchmark row and not comparable with anything above it.

The Gen39 architecture now has a prototype. On the installed Pi, the public `context` extension
hook replaces the message array, so a composed state/control view can stand in for transcript
replay with no Pi core patch — 80 synthetic messages and 46,031 bytes became one message of 413.
On a fixed 59-step synthetic trace with no model involved, history grew 81x while the live context
ended at 2.6% of it, an illegal transition and two unearned completions were refused, a mutated
receipt file invalidated a completed claim, and a restart rebuilt the exact state and history
digests from persisted evidence alone. Whether any of this helps a real coding agent is
deliberately unmeasured. See `research/PI_STATE_CONTROL_GEN43_PROTOTYPE.md`.

## First paired Pi coding pilot — design frozen, no score

`architecture_pilot_design_no_score`. Nothing here was run against a model.

The A/B experiment that follows Gen43 is now frozen: two arms, four invented fixture repositories
with hidden deterministic verifiers, a counterbalanced 24-run order from a fixed seed, and
measurement and tool-churn definitions written before any result exists. Both arms were verified
inside the installed Pi — arm A passes 33,535 bytes through untouched while arm B returns a
composed 5,991-byte view and cancels compaction — and the local model candidate is pinned by file
hash, server build and device without generating a token. The largest open risk is stated rather
than smoothed: sampling is stochastic with no pinned seed, so repetitions are samples unless that
is fixed before the first live run. See
`research/PI_STATE_CONTROL_GEN44_PILOT_DESIGN.md`.

## First live paired Pi coding pilot — mechanism evidence, four tasks

`architecture_pilot_paired_live`. Twenty-four live runs on a pinned local model. A mechanism
pilot, not a coding benchmark; nothing generalises past these four invented tasks.

Arm A, stock Pi, passed 12/12 verifiers at a 52,638-byte median. Arm B, bounded composed context
plus executable control, passed 7/12 at 64,757 bytes, with three timeouts. So the treatment as
configured cost both success and context.

Two findings matter more than that score. Bounding each request did **not** bound the run: arm B's
per-request context grew 2.6x over 337 requests where arm A's grew 209x over six, and arm B still
used more in total because it needed far more turns. And the control half of the treatment never
ran — zero transitions accepted across all twelve runs, every run ending in phase `inspect`, the
artifact gate never reached — so arm B was in practice a bounded window plus three tools the model
ignored, and its failures cannot be blamed on control gating. See
`research/PI_STATE_CONTROL_GEN45_LIVE_PILOT.md`.

## Harness-maintained state and control — design frozen, no score

`architecture_state_control_ablation_design_no_score`. No model, no GPU, no network.

Gen45's negative result could not be read as a test of the architecture: the control layer accepted
zero transitions across all twelve runs because the model never called its tools. Gen46 freezes the
arm that removes that dependency — identical composer, caps and history treatment, with state and
phase derived by the harness from ordinary visible tool events instead.

Preflight passes on synthetic logs: the loop the model never drove runs on its own
(inspect → plan → implement → validate → implement → validate → done), a mutation after a passing
check invalidates the receipt, the hidden verifier can never become a receipt, state stays inside
its bound, illegal transitions fail closed, and the Python contract and the TypeScript arm that
will run live produce byte-identical summaries from the same event log. Arm B is untouched. The
task-prompt floor and history retrieval are named as deferred hypotheses rather than folded in. See
`research/PI_STATE_CONTROL_GEN46_HARNESS_STATE_DESIGN.md`.

## Harness-maintained state and control, live — the mechanism was the problem

`architecture_state_control_ablation_paired_live`. 24 live runs, same four tasks, same bounded
composer, same model as Gen45. Only who maintains the state changed.

Arm C, with state and phase derived by the harness from visible tool events, passed **12/12** with
zero timeouts and reached a control-valid `done` on every run. Arm B, waiting for the model to
drive the same loop, passed 9/12 with three timeouts and reached `done` on none — it called
`request_transition` zero times in twelve runs, reproducing Gen45 exactly. C also used fewer
provider payload bytes at the median (70,557 against 98,153).

Two tasks carry the finding. On T3, B timed out 3/3 at 3.4 MB median payload while C finished every
run at 198 KB. On T2, B failed 0/3 in both generations while C passed 3/3. So Gen45's negative
result was about state maintenance, not about the bounded view it blamed. See
`research/PI_STATE_CONTROL_GEN47_HARNESS_STATE_LIVE.md`.

## Reading rules

Retrieval, safety, lifecycle, and reader evidence are reported separately and
are never folded into one scalar. Lifecycle loss is never rewarded as retrieval
precision. A `raw_product` row is not a product row. Configuration scope travels
with every number.
