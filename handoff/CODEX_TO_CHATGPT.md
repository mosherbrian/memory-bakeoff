# Codex to ChatGPT handoff

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
