# Evidence index

This is a map of what has actually been measured, not a leaderboard. A score is
only comparable inside its own experiment class and evaluated configuration, so
every row carries its class, its caveat, and links to the authoritative write-up
and the machine-readable artifacts behind it.

Round 1 is closed. Its authoritative narrative is
[`research/ROUND1_FINAL_READOUT.md`](research/ROUND1_FINAL_READOUT.md); prefer it
over any older score text elsewhere in this repository.

**The reader layer is OPEN and UNRUN (Gen109).** The contract
`reader-interference-v1` is frozen at
`results/gen109/attempt1/reader_interference_v1.json`; the design is
[`research/PI_READER_INTERFERENCE_DESIGN_GEN109.md`](research/PI_READER_INTERFERENCE_DESIGN_GEN109.md).
**No model has been asked anything** — there is no reader result. Gen85's earlier
reader attempt is
[`QUARANTINED / NOT EVIDENCE`](research/GEN85_READER_QUARANTINE.md).

**Round 3 is closed (Gen107).** Its authoritative narrative is
[`ROUND3_FINAL_READOUT.md`](ROUND3_FINAL_READOUT.md), with the supersession
detail in [`ROUND3_SUPERSESSION_RESULT.md`](ROUND3_SUPERSESSION_RESULT.md) and a
machine-readable source registry at
`results/gen107/attempt1/round3_closure.json`. Prefer those over any older
Round-3 text. Two cautions travel with them: **no Round-3 conclusion is
manifest-verified** (the evidence contract arrived at Gen106, after the evidence
it would have protected), and
[`research/PI_SUPERSESSION_ABLATION_GEN102.md`](research/PI_SUPERSESSION_ABLATION_GEN102.md)
is **superseded** — preserved for history, not to be cited as current. Round 2 is the
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

## The human-direction floor — design frozen, no score

`architecture_human_direction_floor_ablation_design_no_score`. No model, no GPU, no network.

Gen47 left one composer question standing: should the original human instruction remain
addressable after the recent window moves past it, or is it ordinary transcript material? Arm D is
arm C plus exactly that — the first user message, captured verbatim by identity, carried as a
`human_direction` field once the window would drop it.

The integrity property is proven rather than asserted: the two arms compose byte-identical payloads
until the window drops the task, the floor then activates at exactly that request, adds 303 bytes,
never deactivates, and is still verbatim at 100 turns. Arm D is generated from arm C's source so
they cannot drift. A new four-task intent-persistence ruler replaces T1–T4, which are
ceiling-limited for C — including one task whose shipped check is deliberately incomplete, where a
partial fix provably passes the project's own test and fails the hidden verifier. See
`research/PI_HUMAN_DIRECTION_FLOOR_GEN48_DESIGN.md`.

## The human-direction floor, live — a reported negative

`architecture_human_direction_floor_ablation_paired_live`. 24 live runs, four intent-persistence
tasks, three stochastic samples per cell.

Both arms passed 11/12 hidden verifiers. Arm D, carrying the original instruction verbatim once the
recent window drops it, cost more provider bytes (84,911 against 78,682 median) and bought no
task-success improvement. That is the preregistered H3, reported rather than rescued with a
friendlier ruler.

Two things did move without being a success claim: D had zero timeouts against C's two, and reached
control-valid `done` 12/12 against 10/12. The floor was exposed in only 9 of 12 D runs, so a third
of the arm never met the intervention at all — which makes the null weaker evidence than 24 runs
suggests. Both arms recorded one `visible_receipt_false_assurance`, and neither was on the task
built for it: on IP1 the agent updated the stale shipped test, earned a current-tree receipt and
reached control-valid `done` while still failing the hidden requirement. See
`research/PI_HUMAN_DIRECTION_FLOOR_GEN49_LIVE.md`.

## Failure audit — what actually went wrong, and it was not context

`architecture_failure_mechanism_audit_posthoc_no_score`. No model, no GPU, no new runs. Six focal
runs from Gen47 and Gen49, selected by outcome rule and frozen before anything was read.

**Across five failures, none was caused by missing context.** Two runs finished the work and could
not stop — one made its correct fix at tool call 314 of 584 and never mutated again, the other at
call 6 of 442 while holding a receipt valid for the current tree. One never started, ending with
zero mutations. Two had everything they needed and used it wrongly, including one where the
human-direction floor was active and carrying the instruction verbatim.

That explains Gen49's null directly: in the case the floor was built for, the instruction had not
aged out, so no floor could have helped. The gap these runs expose is knowing when to stop and how
broadly to verify, not what the model can see. Retrieval stays deferred; no failure needed history
that had aged out.

Also recorded here: the Gen47 and Gen49 raw provider streams were deleted by the script that hashed
them, and both manifests wrongly claimed they were retained. Corrected, and the audit was completed
on the committed harness logs. See `research/PI_FAILURE_AUDIT_GEN50.md`.

## Gen51 - evidence retention, and when a run has nothing left to do

`raw-evidence-retention-v1` closes the hole that lost Gen47 and Gen49: archiving and hashing are
separate, hashing never touches the archived bytes, and a manifest may not claim retention until
every file has been re-read after cleanup. Deleting or altering one archived stream now fails the
generation. The only raw streams the programme still holds - Gen45's 24, 176 MB - were re-read
under the new contract and all 24 match their committed digests. Gen47's and Gen49's stay recorded
as lost.

Replaying `normalized_quiescent_completion(K)` offline over all 48 Gen47 and Gen49 runs: **K = 3 is
the most conservative value that never truncates observed progress**, and at every K the rule
catches all five timeout runs while firing on none of the five wrong ones. Those five timeouts kept
going for 56 to 433 tool calls after the point a receipt already said they were done, and all five
ended with a correct tree - so stopping them would have turned five timeouts into five successes
and saved roughly a thousand provider requests, changing no outcome. The savings are concentrated:
between K = 1 and K = 10 the runs that fire drop from 23 to 6 while the work downstream barely
moves.

Arm B had no harness derivation, so its receipts are rebuilt offline and labelled
`offline_reconstructed_observable_receipt` throughout. The reconstruction agrees with all 36
recorded harness receipts, and its call/result pairing matches the harness attribution on
1055 of 1081 results. See `research/PI_EVIDENCE_AND_QUIESCENCE_GEN51.md`.

## Gen52 - the stop rule meets runs it was not calibrated on

Gen51 calibrated a rule for ending a run that has nothing left to do: if the project's own tests
passed, nothing has changed since, and three more actions go by without changing anything, stop.
Gen52 let it actually stop things - 24 live runs, arm C against arm E, where E is C plus that rule
and nothing else. The two arms compose byte-identical context; E's file is generated from C's.

It fired once in twelve runs, and both interesting runs are failures of the rule's definition
rather than of its implementation.

`11-IP1-r1-E` is the task whose shipped test still encodes the old firmware ratio. The agent made
the correct fix, the stale test failed, so it **reverted its own correct fix**, the stale test
passed, and the rule stopped the run on a tree byte-identical to the one it started with. The rule
kept every promise it made - valid receipt, tree unchanged between receipt and stop, no tool killed.
Eligibility just asks that a mutation happened, not that the tree actually changed.

`23-IP1-r2-E` ran the **same passing test command 144 times in a row on an unchanged tree** and
timed out after 900 seconds. The rule never fired, because a passing check re-arms the receipt and
resets the count. A run that idles by repeating the check it already passed is invisible to it.
Gen51's replay over 48 historical runs has the same blind spot and could not have found it: none of
those runs looped on the check itself.

Arm E passed 8 of 12 hidden verifiers to arm C's 11 of 12, but three of E's four failures had no
trigger at all, so in those runs E is C. Medians are indistinguishable - 9.5 against 10 tool calls,
39.4 against 38.5 seconds. Nothing was tuned after exposure.

All 24 raw provider streams are retained: 59,097,996 bytes, archived, verified after cleanup. The
first generation whose model output survives by contract rather than by luck.
See `research/PI_QUIESCENT_COMPLETION_GEN52_LIVE.md`.

## Gen53 - one repair worked, the other never got the chance

Gen52 showed the stop rule failing in two ways: it stopped a run that had reverted its own correct
fix, and it never stopped a run that ran the same passing test 144 times. Gen53 made one change for
each, froze them as `quiescent-completion-toolcall-v2`, and replayed the result over every run on
record - 72 across three generations - with no model, no GPU and no network.

**The repeated-check repair works.** Treating a pass on an unchanged tree as silence rather than
news catches that 144-repeat run at every K, about 25 tool calls in instead of 163, and catches all
six recorded runaway runs across all three generations. No K truncates observed progress on any
fully observed trajectory.

**The revert repair does not, and the reason matters.** The rule was told "a tree back at its
starting digest is not finished", but the digest is `git add -A` over the whole worktree, so running
the visible tests creates `__pycache__` and changes it. The reverted run's source ended exactly
where it began - the leaf records the same digest for start and final - yet the digest at the
qualifying check differed by bytecode alone, so the new predicate never engaged. v2 still stops that
run at K=1, 2 and 3, and declines at K=5 and 10 only because the run ran out of calls.

So the mechanical decision rule names K=5, and **the recommendation is against it**: a criterion met
by luck on one run has not been met. Reported and stopped, without inventing a third patch. What the
next brief should settle is whether the tree digest ignores content the project does not track.

Also fixed: the quiescence snapshot is now written on every tool result and survives SIGKILL intact,
closing the evidence gap that left Gen52's one timeout with null eligibility fields. The TypeScript
arm and the Python rule were driven through the same ten traces and disagree nowhere.
See `research/PI_QUIESCENT_COMPLETION_GEN53_REFINEMENT.md`.

## Gen54 - the fingerprint was measuring the wrong thing

Gen53 found that the "a tree back at its starting digest is not finished" rule never engaged, and
suspected the digest. Gen54 confirms it and fixes it. The old fingerprint was `git add -A` over the
whole worktree, so it counted `__pycache__` and `.pytest_cache`: **running the project's own tests
moved the fingerprint on its own**, which is why a run that had reverted itself still looked changed.

`tracked-tree-digest-v1` excludes a frozen list of build artifacts and nothing else. Fingerprinting
only already-tracked files was rejected - it would go blind to a newly added source file, and adding
a module is progress.

The run that forced this, `11-IP1-r1-E`, was reconstructed by replaying its own two recorded edits
onto a fresh copy of the frozen fixture. Both applied cleanly. Initial `732a4b97`, after the correct
fix `df099f72`, after the agent reverted it `732a4b97`, and after running the visible tests the old
fingerprint reads `ed00c99a` while the new one still reads `732a4b97`. That last line is the whole
defect.

Replayed over all 72 recorded runs with each tree rebuilt from its own edits (71 of 72 fully
reconstructable, the exception named): at every K the reverted run is **refused with
`became_eligible` false** rather than merely unreached, the 144-repeat loop is still **caught at
tool index 21 to 30** of a 163-call run, no run is stopped while still making progress, and the
count of runs stopped on a tree equal to their start is **zero**. That was the stated condition for
going live, and it is met for the right reason.

Every K qualifies, so the frozen decision rule's mechanical answer is K=1. The report recommends K=3
instead and flags that as a deviation: K=1's 24 extra firings save about three tool calls each on
runs that had already finished, which spends the whole safety margin for nothing.
See `research/PI_TRACKED_DIGEST_GEN54.md`.

## Gen55 - the corrected stop rule, live

24 live runs, arm C against arm F, where F is C plus the completed controller: v2 semantics, K=3,
the corrected tracked fingerprint, the every-tool-result snapshot, and the safe stop. The model is
never told it exists, and the two arms compose byte-identical first requests on every task.

**It behaved exactly as frozen.** Ten of twelve F runs became eligible, two triggered, and both
triggers independently satisfied every condition: a real mutation, a receipt on the current tracked
tree, a tree differing from its initial value, an idle count of exactly 3, the last visible check
passing, and zero same-batch overshoot. **Zero stops on a tree equal to its start** - the hard
failure that made the first version unusable. No contract violations of any kind.

**The stall it targets is real and recurrent.** All three arm C timeouts are the same shape: finish
the work, then re-run the passing check until the clock kills it - 279, 148 and 149 exact repeats.
Two of the three ended holding a *correct* tree. That is 2,700 seconds spent on work already done,
in the untreated arm, in one generation. Arm F had no timeouts.

**The decisive pair** is `IP1-r2`, the slot that in Gen52 ran its passing test 144 times under the
first version. Arm C timed out at 900 seconds and 161 calls; arm F stopped at 83 seconds and 16
calls on the same wrong tree, recording `same_tree_passes_counted_idle: 1` - the repeated pass
counted as silence instead of re-arming. Same outcome, a tenth of the cost.

**Do not read 7/12 against 10/12 as a treatment effect.** Ten of F's twelve runs never triggered, so
in those runs F is C; three of F's five failures are in that group, two never even becoming
eligible. Exactly one run, `IP1-r1-F`, is a candidate for the stop having cost correctness, and that
is not knowable from a live arm.

All 24 raw streams retained and verified after cleanup: 73,080,123 bytes. Runtime 3,624 seconds,
of which 2,700 is the three untreated timeouts.
See `research/PI_QUIESCENT_COMPLETION_GEN55_LIVE.md`.

## Gen56 - the receipt was never the problem; the test was

Two things: the quiescent-completion line is closed in `ARCHITECTURE.md` as an optional harness
guardrail with its limits recorded, and the next question was tested and answered.

That question was whether a wrong result slipping past a passing check is a matter of **scope** -
the agent running one test file instead of the whole suite. Audited across all 72 recorded
intent-persistence runs, with the broadest shipped command frozen from the fixture layout before any
outcome was read: **it is not**. Fourteen runs ended hidden-verifier-wrong while holding a valid
receipt, and in **every one** the broadest test command the project ships also passes on exactly
that tree. Nine of the fourteen had already run the whole suite live. Across all 72 final trees the
broad check failed **zero** times.

The cleanest proof needs no reconstruction: on the **shipped, unmodified** IP4 fixture the project's
own test passes a knowingly incomplete implementation that the hidden verifier rejects.

The counterfactual is therefore blunt - requiring the broadest shipped check would have blocked
**0** false assurances while charging 24 runs an extra check. All four hidden-wrong sentinels are
`visible_artifact_coverage_gap`; **zero** are `narrow_receipt_broader_visible_contradicts`.

So the unresolved problem is visible artifact **coverage**, not command scope: a harness cannot
recover a requirement that no visible test encodes. Recommendation is to design around how stronger
evidence is produced, not to build a validation-breadth gate.

Also frozen, metadata only, changing no control behaviour: `scoped-validation-receipt-v1`, whose
authority statement has exactly one form - *command X exited N on tree Y under configuration Z* -
and which is forbidden by construction from saying a task is correct.
See `research/PI_ARTIFACT_AUTHORITY_GEN56.md`.

## Gen57 - the tests do not cover the change, on the good runs too

Gen56 showed that running a broader test command catches nothing. Gen57 asked the narrower
mechanical question: can visible artifacts alone show that the tests do not exercise or constrain
what the agent changed? Two deterministic probes, no model - did the suite execute the changed
lines, and would it notice if one hunk of the change were undone.

Both work, and both are useless as a warning. They are sensitive - 9 of 10 applicable known-bad runs
flagged - and hopelessly unspecific: they also flag **62.5%** and **76.8%** of the runs that were
*correct*, against a frozen ceiling of 25%. The visible tests in these tasks routinely under-
constrain the change even when the work is right, so structural weakness is the normal condition
rather than a signal.

The sentinels come out backwards, which settles it. The known false assurance is **clean under both
probes** - every changed line executed, its reversion killed - because that agent **edited the
test**, so the suite genuinely constrains the behaviour it implemented. The successful comparator is
**flagged by both** - 43% of lines executed, two surviving reversions. A control built on these
signals would have waved the wrong run through and blocked the right one.

Neither diagnostic meets the screen frozen before any of it was measured, so per that rule no third
heuristic was invented. Stronger evidence must be **produced**, not inferred from tests never
written to cover the change. Gen58 should choose between author-supplied structured traceability and
model-assisted evidence generation, the latter in its own evidence class.

Recorded for free: absence of these signals must never be read as sufficiency - the single cleanest
run under both probes was wrong. Requirement-to-test traceability was deliberately not instantiated,
since the fixtures carry prose requirements but no machine-readable mapping.
See `research/PI_ARTIFACT_COVERAGE_GEN57.md`.

## Gen58 - asking a second reader for harder tests

Every route so far tried to squeeze more meaning out of the tests that already exist, and all of
them failed. So Gen58 asked a model to write *additional* tests, given only the original instruction
and the starting code, never anyone's solution. Twelve generations, four tasks, three attempts each.

**The experiment cannot answer its own question, and that is the finding.** Half the generated banks
are wrong: on IP1 and IP3 the bank rejects a trusted correct implementation that predates this
experiment, inventing unit and sign conventions the instruction never stated. Those banks are
`UNSAFE_AS_GATE` however much they catch. And the two banks that *are* trustworthy - IP2 and IP4 -
cover the only two tasks containing **no wrong work at all**. Every historical failure sits in IP1
and IP3. The population where the evidence is sound and the population with something to catch are
disjoint, so the frozen screen is **unevaluable**, not failed.

Where the banks are valid the specificity is perfect: **0 of 36** correct trees challenged. Where
they are invalid they flag **16 of 16** and **18 of 18** - rejecting seven correct runs and the
trusted reference. A bank that fails everything is broken, not strict.

The sentinel pairing fails accordingly: the generated tests do catch `gen49-IP1-r1-C`, the
structurally-clean false assurance, but the same bank also rejects `gen49-IP1-r1-D`, the successful
comparator, and the reference itself.

**One genuine positive.** On IP4, a reference-valid bank, the generated tests catch the recorded
partial fix that the project's shipped test passes, naming the negative-clamp requirement the
visible suite never checks. That is the first time in this line that anything produced evidence the
visible artifact lacked.

Also disclosed: my first frozen sanitizer counted only top-level `test_*` functions, so nine valid
outputs written as `class Test…` methods were rejected. Found before any bank touched any tree, so
the fix could not be outcome-informed; per the brief the run was **discarded and regenerated**, with
the superseded outputs quarantined and labelled rather than reused.
See `research/PI_MODEL_ASSISTED_EVIDENCE_GEN58.md`.

## Gen59 - building a ruler where right and wrong answers live side by side

Gen58 could not be scored: every faulty implementation on record lived in tasks whose generated
tests also rejected known-good code, and the tasks where the generated tests were trustworthy had no
faulty work in them. So Gen59 does not touch the generator - it builds the missing measuring stick.

Eight new tasks (`evidence-generation-gen59-v1`), each with **two genuinely different correct
implementations** and **three wrong ones**, where at least two of the wrongs **pass the project's own
shipped tests**. All eight were admitted: **24 known-wrong candidates, 18 of which slip past the
shipped tests**, across seven kinds of mistake. The bar was six tasks, eighteen wrongs, twelve
slip-throughs.

Every `passes_visible` label was treated as a prediction and measured: each of the 40 candidates was
materialised and run against both the shipped tests and the hidden verifier, and a task was admitted
only when measurement agreed with design.

**Three corrections, all caught by measurement.** Two were harness bugs that made the ruler look
broken when it was not - candidate trees with no git repo, so every digest came back empty and all
positives looked identical; and the verifier run as a script, so nothing imported and *every*
positive appeared to fail. The third was a real design error: `ledger` and `thermo` rested on float
midpoint rounding, but 2.345 is stored above the midpoint, so Python's `round` already gives 2.35 and
the "wrong" candidates were correct. Rebuilt `ledger` on decimal strings and removed the rounding
clause from `thermo` entirely, rather than weakening the invariant.

Isolation is mechanically demonstrated on the prompt a future generator would actually receive:
zero occurrences of any evaluator token, and the truth package outside every generator-visible path.

The Gen60 screen is frozen at `b694f7b8...` before any generated output exists, including the
explicit **UNEVALUABLE** branch that Gen58 lacked. Gen60 must re-test the *same* Gen58 generator on
this ruler; changing the model or adding a critic now would confound a corpus repair with a
generator repair.
See `research/PI_EVIDENCE_RULER_GEN59.md`.

## Reading rules

Retrieval, safety, lifecycle, and reader evidence are reported separately and
are never folded into one scalar. Lifecycle loss is never rewarded as retrieval
precision. A `raw_product` row is not a product row. Configuration scope travels
with every number.
