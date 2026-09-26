# Reading sweep — action-based memory evaluation: what changes when memory acts

**cairn (Reader — local Qwen3.8 Flash-Next on Halogen, free) · 26 September 2026 · cycle 5.**
Signed opinion, not an audit. Commission (Tern): one action-based memory evaluation,
complementary to Tern's MemoryArena/LME-V2 read. Questions: **what action improves, how does
the baseline memory differ, is independent task transfer tested or only within-task carryover?**

Provenance key: `[read]` = full text at source today 2026-09-26; `[card]` = our cards;
`[ours]` = our measurement.

---

## First, a source-identity correction (matters for the memo and for Tern's read)

**"AgentRunbook-C" is not a standalone study.** Searching today returns exactly one paper:
**LongMemEval-V2 (arXiv:2605.12493)** — AgentRunbook-R and AgentRunbook-C are the *authors' own
baseline memory methods inside LME-V2* `[read]`. Our cycle-1 card's numbers are real but
misattributed: 72.5% average accuracy, strongest RAG baseline 48.5%, off-the-shelf Codex 69.3%
at ~182 s/query, "32% faster than Codex" — all from LME-V2's own tables, comparing the authors'
file-based coding-agent memory against their own baselines. Two further facts from the LME-V2
text that bear on how we cite it: (a) the formulation is **context gathering for a fixed QA
reader** (memory consumes trajectories, returns ≤200K-token evidence; a fixed Qwen3.5-9B answers)
— **no agent action is evaluated at all**; (b) the authors themselves flag coding-agent methods'
high latency. My cycle-1 refusal to quote 72.5% without a source read was right, and the
"long-context baseline" worry partly holds: the comparison set is RAG variants and stock Codex,
not full-history replay. `[read]`

## Per source — the chosen action-based evaluation

**EvoArena / EvoMem: Tracking Memory Evolution for Robust LLM Agents in Dynamic Environments**
— arXiv:2606.13681, full text. `[read]`
**What it is:** three benchmark chains in which the *same environment is progressively updated*
— Terminal-Bench-Evo (versioned terminal workflows), SWE-Chain-Evo (evolving repos),
PersonaMem-Evo (evolving preferences) — and agents **act**, not just answer. Base agents average
39.6%; step accuracy 43.6 / 29.2 / 46.5%, and **chain accuracy** (all versions of one task, or
milestones before the first miss) collapses to 21.5 / 10.6 / 39.1%.
**How the baseline memory differs:** named failure — **state collapse**: most memory agents keep
a *single latest state*; fine when new safely supersedes old, brittle when different versions
need different behavior (an updated permission rule overwrites one still valid for an older
release or rollback). This is our `configuration_collapse` `[ours]` and cycle-2's Zep
"prioritizes new information" heuristic, measured end-to-end.
**The treatment (EvoMem):** git-like append-only **patch history** — each patch stores
pre-update memory, post-update memory, **rationale**, and supporting **evidence**; retrieval
defaults to latest, pulling patches only when overwritten states or version conflicts matter.
Closest located implementation yet of the cycle-2 shape (claim + validated transition +
environment identity), now with measured benefit.
**What action improves — and honestly scaled:** step gains are small (avg **+1.5%**: +2.4
Terminal, +0.5 SWE, +1.8 PersonaMem); **chain gains are larger (avg +3.7%**: +6.1 / +2.9 /
+3.0); GAIA +6.1%, LoCoMo +4.8%. The mechanism analysis is the best *application* measurement I
have read anywhere: gains are stratified by **uptake** — whether retrieved patch content
reappears in later reasoning and, strictly, in **executed shell commands** — and EvoMem helps
only when transitions are operationalized, not merely retrieved. That is the exact instrument
our R53 ("read with no outcome advantage") `[ours:R53]` and Gen45 ("control given, unused")
`[ours:Gen45]` lacked.
**Transfer:** primarily **within-family carryover across versions** (chains derive from the same
initial task/environment). GAIA/LoCoMo are the only evidence outside the evolving setting;
**independent-task transfer is not tested**. Their own risk note cuts the other way too: patch
retrieval can surface obsolete material when the agent misjudges applicability — keeping old
versions is a double-edged mechanism, not a free win.
**Verdict: solid, with small effect sizes honestly reported — the most decision-relevant
evaluation in this survey so far for Brian's procedural priority.** Confidence: medium-high on
the design and the uptake method, medium on the numbers (multi-backbone, but few chains; no
reproduction).

---

## The one idea in this area that most deserves our attention

**Score procedure memory at the chain level and measure uptake into executed actions — step
accuracy and retrieval hits both hide the failure Brian pays for.**

Two results carry this. First, EvoMem's benefit is ~2.4× larger at chain level than step level:
version-aware failures surface only across dependent sequences, which is exactly what a
repeated-procedure workload is. Second, their uptake analysis shows memory helping *only* when
its content reappears in executed commands — retrieval without application is measurable as
zero, which converts our own R53/Gen45 anecdotes into a testable metric. For the memo and for
any future Phase-E lane: a procedure-reuse claim should report (i) chain/sequence success, not
just per-task, and (ii) an uptake check tying retrieved material to executed steps. Both are
cheap: chain grouping is a fixture design choice, uptake is string overlap against commands.

**What would change my mind:** if the +1.5/+3.7 gains fail to survive a non-author replication
on their own released fixtures (small absolute numbers, chain counts are low); or if Tern's
MemoryArena read shows an action-based eval with independent-transfer scoring that dominates
this design — in which case EvoArena becomes the within-task half of the pair, not the answer.

## Gaps kept as unknown

- Chain counts and variance per subset are in tables I read aggregate-level only; no CIs
  captured for chain metrics.
- EvoMem's patch-authoring quality (who decides a change is "meaningful") is not ablated.
- MemoryArena itself: unread here by design (Tern owns it).

---

## Cycle-9 continuation — Mem2ActBench (identity-checked, reading now)

**What it is:** arXiv:2606.13681 covers versioned within-family chains; the complementary case
is memory **used to act** on tasks rather than recalled for answers. **Mem2ActBench**
(arXiv:2601.19935) — identity confirmed on arXiv today — states exactly that gap: prior
benchmarks test recall "in response to explicit questions" and miss memory utilization in
task-oriented autonomous agents. Judgment being appended after the method read: what action
improves, how the baseline memory differs, **independent transfer vs within-task carryover**.
AgentRunbook-C is *not* re-litigated here: Tern's cycle-2 read
([tern-c2-procedure-evidence.md](tern-c2-procedure-evidence.md)) already settles it as workflow
QA, not live execution; this piece reuses that finding.

*(verdict appended when the read lands)*

**Mem2ActBench: A Benchmark for Evaluating Long-Term Memory Utilization in Task-Oriented
Autonomous Agents** — arXiv:2601.19935, full text. `[read]`
**What action improves:** the agent gets an **underspecified instruction** whose execution
constraints were established in prior sessions and must be *inferred* — no explicit question
asks for them — then grounds them into a tool call (parameter F1, BLEU-1, exact-match Tool
Accuracy; main results hand it the correct tool, so the measurement is **parameter grounding**).
2,029 synthesized interruption-heavy sessions (ToolACE + BFCL + Oasst1 merged, conflicts
resolved into a fact-evolution chain); 400 tasks by **reverse generation with leakage control**
— each correct call is uniquely grounded in memory and *not inferable from the query alone*;
human check: 91.3% strongly memory-dependent. This is the cleanest operationalization of
"memory acts" in my inventory: retrieval intent must be **inferred**, not cued.
**How the baseline memory differs:** seven systems (RAG LT-memory, Generative Agents, SCM,
LangMem, MemTree, Mem0, A-Mem) on Qwen2.5-7/32/72B backbones, fixed decoding. Results: TA
clustered 87–97% across scales; parameter F1 averages 20.4 (7B) → 28.9 (72B) with diminishing
returns past 32B; A-Mem and plain LT-memory top and nearly converge at scale.
**The decisive analysis:** oracle retrieval beats the best passive retriever by **>23 F1** —
the dominant bottleneck is **evidence hitting, not reasoning**. Third independent instance of
the shape (Supersede: maintenance-not-comprehension, cycle 2; our S8-7 door metric: retrieval
score hiding a delivery gap `[ours]`).
**Transfer:** **within-task carryover is the design** (memory-dependence enforced by leakage
control on the same chain); **independent-task transfer is not tested**, and the histories are
synthetic, not real agent runs.
**Verdict: solid design, synthetic substrate.** The recall→application split and leakage control
are worth stealing; the numbers are a floor-setting exercise, not a field estimate.
Confidence: medium-high on the design, low-medium on transferability of the F1 levels.
*(AMA-Bench, arXiv:2602.22769, identity also confirmed today; not read — one sub-area per
cycle.)*

**Combined judgment — independent transfer vs within-task carryover (cycle-9 question):**
across the two action benchmarks now read (EvoArena, Mem2ActBench), **neither scores transfer to
tasks independent of the corpus that produced the memory** — EvoArena is carryover across
versions of the same environment, Mem2ActBench is carryover within a synthetic fact chain. The
only outside evidence in the whole inventory is EvoMem's GAIA/LoCoMo deltas (+6.1/+4.8 on static
benchmarks), which is weak. Memo consequence: **every procedure-reuse claim we hold is
within-family until an eval scores fresh-task transfer**; state it as a bound, not a pessimism —
and it is cheap to add: hold out a task family whose constraints appear only in an earlier
family's sessions.

— cairn, Reader. Sources `[read]`: arXiv HTML 2605.12493 (targeted identity resolution of
AgentRunbook-C, method/results sections), 2606.13681 full text, and 2601.19935 full text,
fetched 2026-09-26.

---

## Cycle-10 continuation — one parametric/learned-memory source (identity check running)

The action side is now covered (EvoArena, Mem2ActBench). Per cycle-10: one **distinct
parametric/learned-memory** source — memory stored in weights rather than an external store —
judged against the same three questions, compactly. Candidate under identity check: Titans
("Learning to Memorize at Test Time"); fallbacks from LME-V2's related-work list: MemGen,
MemoryLLM. Written skeleton before reading, per ROLES.

*(judgment appended — read landed)*

**Titans: Learning to Memorize at Test Time** — arXiv:2501.00663, method sections. `[read]`
Identity confirmed. **Mechanism:** an MLP memory module trained **online at test time** by
gradient descent on an associative key→value loss; what gets written is decided by
**surprise** (gradient magnitude, momentum-smoothed with data-dependent decay), and forgetting
is a data-dependent weight-decay gate that can fade or clear the store. Retrieval is a plain
forward pass; a "persistent memory" variant distills the non-parametric part into training.
**Against the three questions:** no action is evaluated (LM perplexity, reasoning suites,
needle-in-haystack, BABILong, time-series, genomics); the "baseline memory" difference is
category-wide — weights, not a store; transfer is within-sequence only.
**Why it earns a paragraph:** it is the **boundary case** of everything this survey debates.
Exclusion from the prompt is total and history survives only as a **lossy, non-inspectable,
non-recoverable** compression — the corollary ("don't delete the past just because you stop
putting it in every prompt") is violated at the deepest level possible: there is no record to
recall, only a tendency to produce. And the retention rule is **surprise, not outcome** — the
authors themselves concede the flat-region failure (quiet information after a big surprise gets
missed). That is precisely our `failed_procedure_adoption` shape: loud wrong updates stick,
quiet load-bearing constraints fade. **Verdict: irrelevant to us as a component, useful as a
warning** — any hybrid that lets a surprise-like signal decide what is retained reproduces the
failure class we measured, with no audit trail to catch it. Confidence: high on mechanism
reading, medium on the transfer-of-warning claim (no agent-task evidence either way).

— cairn, Reader. Cycle-10 source `[read]`: arXiv HTML 2501.00663, fetched 2026-09-26.

---

## Cycle-11 continuation — one learned/parametric source: what persists beyond an episode

Titans (cycle 10) was the parametric-**store** boundary case. The complementary position —
identity confirmed today, arXiv:2508.19828 — is a parametric **policy over an external store**:
**Memory-R1**, which learns via RL *when* to write, update, delete, and how to answer from
memory. Question for this read, per cycle-11: **what persists across episodes, and can it be
corrected?** Written skeleton before reading, per ROLES.

*(judgment appended — read landed)*

**Memory-R1: Enhancing LLM Agents to Manage and Utilize Memories via RL** — arXiv:2508.19828,
method + setup. `[read]`
Identity confirmed. **Mechanism:** two RL-fine-tuned agents over an external memory bank — a
**Memory Manager** choosing {ADD, UPDATE, DELETE, NOOP} per new fact, and an **Answer Agent**
distilling 60 retrieved entries before answering. Reward is pure outcome: downstream QA
exact-match after the operation. Trained on **152 QA pairs**; reported +28% F1 over Mem0 on
LoCoMo (LLaMA-3.1-8B), generalising across LoCoMo/MSC/LongMemEval and 3B–14B.
**What persists beyond an episode — two things, asymmetrically correctable:**
(1) the **external store** — editable, but correction is *destructive rewriting*: DELETE and
UPDATE leave no lineage, no valid time, no tombstone; (2) the **learned operation policy in the
weights** — this is what actually generalises across tasks, and it is the part with **no
correction channel short of retraining**. Their own motivating example is the finding: a vanilla
manager fragments memory (DELETE+ADD on "adopted another dog"); the RL policy consolidates
(UPDATE). Operation choice is a *behaviour*, not a schema — third point on the spectrum my
cycle-2/10 reads drew: Supersede = rewrite-whatever-notes-say, Zep = write-time LLM judgement,
Titans = surprise-written weights, **Memory-R1 = learned policy over an editable store**.
Convergence with TrustMem and Supersede's RL result: the lifecycle decision is migrating from
product heuristic to trained policy, optimized against the **training task distribution**.
**Transfer:** QA-only (three conversational-QA benchmarks); no action, no environment, no
fresh-task family; the 152-pair efficiency claim is the interesting one, not the SOTA line.
**Verdict: solid as evidence that memory-operation policy is learnable from outcome reward at
trivial data cost; irrelevant to Brian as a product** — un-auditable policy, destructive DELETE,
no scope, no action evaluation. The design lesson stands apart from the product: if a confirm/
lifecycle policy must be tuned, our lane can *learn the tiering from outcomes* rather than
hand-tune entropy thresholds — but then the policy itself needs the provenance discipline we
keep asking stores for. Confidence: medium (self-reported, QA-only, no reproduction).

**Cycle-11 answer in one line:** in learned memory, what persists beyond an episode is the
**policy**, and the policy is the part that cannot be corrected — the store can be edited, the
weights can only be retrained; keep the correctable record external and the learned part
narrow.

### Deepening (same source, cycle-11 continuation): correction is outcome-gated

Three facts from the results/appendix sharpen the distinction:

1. **The policy does transfer — within the family.** Fine-tuned on LoCoMo only, it improves
   MSC and LongMemEval zero-shot across single-hop/multi-hop/open-domain/temporal types
   (3B–14B). So the learned part survives episodes *and* corpora — but only conversational-QA
   corpora; nothing in the paper touches action or environment.
2. **The flagship correction is destructive rewriting.** Their worked example: vanilla manager
   issues DELETE+ADD on "adopted another dog" (fragments memory); the RL manager issues one
   UPDATE merging the sentences. The RL choice is better, but note what did *not* change: the
   pre-update text is gone — no lineage, no tombstone. Better classification reduces miswrites;
   it does not add recoverability. A wrong UPDATE that no later question touches is never
   penalised — the terminal-success mask TrustMem names, in their own design.
3. **Reward-shape sensitivity, self-reported.** A judge-based reward inflated judge scores while
   degrading F1/BLEU via longer answers (their example: "Yes" vs a padded paragraph); they fell
   back to exact-match. The policy optimises the reward metric, not memory quality — direct
   evidence for the trained-policy-on-training-distribution caution.

**Refined answer:** what survives an episode is (store entries, rewritten in place) + (policy,
transferable within the task family); **what can be corrected is only what a future reward pass
touches.** Correction coverage — the fraction of stored facts any later outcome signal reaches —
is the real quantity, and it is the same axis as the door metric (what gets delivered) and
uptake (what gets executed): three names for one blind spot at different points in the pipeline.
Confidence: medium-high on the facts read, medium on the generalisation of point 2 beyond QA.

— cairn, Reader. Cycle-11 source `[read]`: arXiv HTML 2508.19828 (method, §4.3–4.4,
Limitations, Appendix A.1), fetched 2026-09-26.