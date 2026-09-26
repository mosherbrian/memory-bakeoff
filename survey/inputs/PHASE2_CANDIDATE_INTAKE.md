# Phase 2 candidate intake — ranked, 5 items

Decision Gate B of `research/PHASE2_ROADMAP.md`, produced for the first time in
Gen125. Sources: `research/PHASE2_FIELD_REFRESH_2026-09.md`, reconciled against
`research/PHASE2_ROADMAP_RECONCILIATION.md`.

**Admission rule, from the roadmap:** every row answers "what distinct
architectural question does this answer that our existing evidence has not
already answered?" A candidate that adds no new mechanism is rejected here, by
name, rather than quietly dropped.

**Lanes** (see `research/EVIDENCE_LANES.md`): SYSTEM-SELECTION is primary;
READER-ATTRIBUTION is explanatory. Their metrics are never combined.

---

## 1. Long-context control arm — HIGHEST PRIORITY, and we do not have one

**Distinct question:** does ANY memory system beat simply putting the history in
the context window, on our workload?

**Why first.** EvoMemBench reports that long-context baselines remain highly
competitive and that memory helps most only when context is insufficient or the
task is hard.

**Correction, in two passes.** An earlier draft said "we have measured five
engines against each other and never against the null", and that "every
comparative claim the project has made is therefore unanchored". Both are FALSE.

`results/BASELINE_FINDINGS.md` holds three retrieval baselines - bm25,
dense_lsa, hybrid_rrf - at Hit@5 0.917-0.958. I found that one myself. Review
then found more: engines ARE anchored against those baselines in the same tables
in `results/current_full_core5/summary.md`, and Membukkit was anchored against a
full dense scan. The project has also never claimed "Perseus beat Mem0" - I
invented that example to dramatise a gap smaller than I said it was.

The claim survives in narrowed form, and the baselines document makes the case
better than I did:

> "Simple lexical/LSA retrieval is strong on this small corpus, so a
> sophisticated engine needs to win on temporal correctness, conflict handling,
> multi-hop completeness, procedural success-vs-failure ranking, or learning
> over time, not merely Hit@5."

So the missing arm is not "a baseline" - it is a **LONG-CONTEXT** baseline: put
the history in the window and ask the question, no retrieval step at all. That
is a different null from bm25. bm25 answers "does the engine beat cheap
retrieval"; long-context answers "does retrieval need to happen". EvoMemBench's
result is about the second, and we have never run it.

Note also that all three existing baselines surface stale evidence at
`prohibited@5 = 0.125`, which is the same failure the reader lane studies from
the other end.

It is also the cheapest item here - no new system, no adapter, no admission
gate. It is a configuration of the harness we already run.

**Lane:** system-selection. **Assign:** focused mechanism ablation on
longitudinal-v1. **Cost:** low. **Risk:** it may show the memory systems are not
earning their complexity, which is a result, not a failure.

## 2. EXTEND MemConflict — two engines measured, four not

**Distinct question:** which memory system maintains the CURRENT valid state
after true user updates, end to end, with ingestion and retrieval under test?

**Correction, from the independent accounting of 2026-09-07.** This row first
said "never executed", citing `MEMCONFLICT_PIN.json`'s `Code/` stages as
`not_run`. That reads the wrong thing: those are the benchmark's own UPSTREAM
pipeline stages. **The benchmark itself ran at Gen38** - a full release against a
held-out 27-persona slice no adapter was tuned on:

    Hit@3, held-out slice        perseus   mem0    bm25
    conditional conflict          0.987    0.974   0.915
    DYNAMIC conflict              0.434    0.419   0.226
    static conflict               0.343    0.383   0.312

The dynamic row is this project's actual question, on third-party data, with a
baseline. Both engines roughly double bm25 and **both sit below 44% absolute**;
on static conflict everything lands within seven points of `bm25`. That is real
system-selection evidence and it is not flattering to the category.

**Why second, restated.** What has NOT run is the rest: four of the six locally
harnessed engines (Habitus, agentmemory, Hindsight, MemBukkit), and all six of
the benchmark's own upstream harnesses (a_mem, langmem, letta, memobase, memos,
mem0). `external/MemConflict` is gitignored and absent, so the 182 MB pinned
dataset must be materialised first. Extending a lane that already has two engines
and a baseline is far cheaper than opening a new one, and the agentmemory
lifecycle result makes including it mandatory rather than optional.

**Lane:** system-selection, external benchmark. **Assign:** Phase E.
**Cost:** medium - the checkout must be materialised and the six harnesses
provisioned. **Prerequisite:** the Phase-D identity discipline we already have.

## 3. Adopt a superseded-memory PENALTY metric (FAMA, from Supersede)

**Distinct question:** are we scoring the use of stale memory as a penalty at
all, rather than only scoring whether the right record was retrieved?

**Why third.** arXiv:2606.27472 introduces FAMA, which explicitly penalises
reliance on superseded or deleted memory. Our scoring has always been
retrieval-shaped; Gen124 is the first time we looked at what the reader DID with
a stale record, and it was a hand check of 14 items.

**Code availability: NOT LOCATED.** A GitHub search for Supersede/Memora
returned nothing relevant. **The metric is adoptable even if the code is not** -
it is a scoring rule, and we can implement it against longitudinal-v1 without
their harness. That is the recommendation: adopt the metric, do not wait for the
repository.

**Lane:** system-selection (scoring change). **Cost:** low-medium.

## 4. HaluMem — stage attribution, extraction vs updating vs QA

**Distinct question:** which STAGE of the memory pipeline fails - extraction,
updating, or answering - rather than which product scores worse overall?

**Why fourth.** `github.com/MemTensor/HaluMem` decomposes the pipeline and
reports that hallucination accumulates at extraction and UPDATING and then
propagates. Our entire architecture thesis - lossless history, then state
projection, then retrieval, then synthesis - is a claim about stages, and we
have never measured one.

Ranked below MemConflict because it answers "where does it break" and
MemConflict answers "which one to use", and the latter is the project's stated
question.

**Lane:** system-selection, external benchmark. **Cost:** medium-high - 1M-token
contexts, 15k memory points; check whether Medium alone suffices.

## 5. GateMem — does "forget this" actually forget?

**Distinct question:** do deletion and scope isolation work, under multiple
principals?

**Why fifth.** Deletion and scope are two of the roadmap's six named properties
and we have measured neither. `github.com/rzhub/GateMem` probes utility, access
control and deletion directly. Lowest rank only because it is a different
question from state maintenance, not a lesser one - and it becomes urgent the
moment any of this touches real user data.

**Lane:** system-selection, governance. **Cost:** medium.

---

## Rejected, by name and with the reason

- **LongMemEval-V2** — REJECTED FOR NOW, not on quality. It is strong and
  current (451 questions, 1,870 trajectories, names dynamic state tracking as a
  first-class ability). But item 2 already answers the system-selection question
  with a benchmark we have pinned, and V2 would duplicate that lane at higher
  cost. Revisit once MemConflict has run. Do NOT let it displace V1-oracle in
  the reader lane: the oracle construction is what makes that lane work.
- **StateMemBench** — CANNOT ADMIT. Not located; see
  `research/BENCHMARK_HARVEST_CHECK.md`. The search is incomplete by its own
  admission and must be finished before this is called released or not.
- **Agent Memory Leaderboard** — NOT A CONTESTANT. Infrastructure. Worth reading
  its shared protocol before we extend our own, and it is the cheapest route to
  discovering systems we have not heard of. Not an intake row.
- **"STALE"** — UNRESOLVED. Named in the roadmap; no benchmark of that name
  located. Renamed, absorbed, or imprecise. Do not cite it until resolved.
### The eight the instruction named that I silently dropped

Review found this: the control-plane instruction named twelve systems to
reassess and I addressed four, dropping eight without a word. The intake's own
rule says rejections are written down BY NAME so a candidate cannot quietly
re-enter later, and I broke it in the document that states it.

Assessed now, honestly - including where the assessment is thin:

- **MemOS** (`github.com/MemTensor/MemOS`) — **STRONGEST OF THE EIGHT, admit to
  the next intake round.** A memory operating system treating memory as a
  first-class resource; MemCube abstraction over parametric, activation and
  plaintext memory in three layers. Claims 35.24% token savings. Distinct
  architectural question: *does treating memory as an OS-level resource with a
  unified abstraction beat per-product memory design?* Same group as HaluMem,
  which is a reason to read both together. Not admitted THIS round only because
  five rows is the cap and it duplicates no existing row's lane cleanly - it is
  a system, and rows 2 and 4 already load the system-selection lane.
- **A-Mem** — **NOT SEPARATELY ADMITTED, and this is a merge not a rejection.**
  It is already one of the six harnesses inside MemConflict (`eval_a_mem.py`),
  so intake row 2 measures it. Running it separately would duplicate.
- **MemHarness** (arXiv:2607.28272, "Memory Is Reconstructed, Not Replayed") —
  **DEFER, genuinely interesting.** Agents actively reconstruct past experience
  from present context rather than replaying stored text. That is a different
  mechanism from everything we have measured. It loses this round to items with
  released harnesses.
- **AgentRunbook-C** — **DEFER.** Augments a coding-agent harness with workflow
  documents and query-time artifacts; reported 72.5% accuracy and 32% faster
  than Codex. It answers a workflow-reuse question, not a state-maintenance one,
  and workflow reuse is not the roadmap's governing question.
- **StateMem** — **CANNOT ADMIT.** The method from the StateMemBench paper; the
  benchmark is unlocatable, and nothing found suggests the method was released
  separately. Same status as its benchmark.
- **MemStrata** — **NOT LOCATED.** No result under that name. Either renamed,
  private, or the name in the instruction is imprecise. Do not cite it.
- **Attestor** — **NOT LOCATED.** Same.
- **EvoMem** — **NOT LOCATED** as a system. Search returns EvoMemBench, which is
  a different object and is handled in the field refresh. Possibly the
  instruction means the benchmark.

**Three of the eight could not be found at all.** That is recorded rather than
smoothed over: it may mean my search was too shallow, and it must not be read as
"these do not exist".

- **Membukkit and Claude-Mem re-rank** — the control plane asked for these to be
  revisited. Both are already measured here and neither answers a question the
  five rows above do not, so neither earns an intake slot this round. Claude-Mem
  remains a live TRIAL (since 2026-08-31) and its evidence should be collected
  from that trial rather than by a new contest.

---

## The 14-item LongMemEval holdout: DEFER

**Decision: DEFER.** Matching the control-plane default, and for reasons that
stand on their own:

1. **It answers the explanatory lane's question, not the primary one.** Nothing
   in the five rows above needs it. Spending it now buys a confirmation of a
   reader effect while the system-selection question is still unanswered.
2. **It is unrenewable.** Once run, those items can never again be a clean
   confirmation set, under any rule.
3. **Its own preregistration says nobody has authorised it**, and the author
   cannot authorise himself (LEDGER 117, 158).
4. **The pilot already did its job.** Its stated purpose was to decide whether a
   registered run is worth its cost. It decided: yes, eventually, and not first.

**If later authorised**, preserve: the pinned substrate sha256
`821a2034d219ab45846873dd14c14f12cfe7776e73527a483f9dac095d38620c`, the untouched
membership, the preregistered reader and configuration, the paired-item McNemar
analysis, and the diagnostic-versus-confirmatory separation. All are already
fixed in `research/pilot_ordering/PREREGISTRATION.md` with an amendment log.

**The strongest argument for eventually running it** is item 1 above: if the
long-context control arm shows memory systems barely beating the null, then
knowing how much of the residual failure is the READER's fault becomes the
question that decides whether better memory can help at all.
