# Reading note — Dynamic Cheatsheet: one writer, one executor, and what the sheet may contain

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 20.**
One source (Tern): **Dynamic Cheatsheet, arXiv:2504.07952** (Suzgun et al.; repo
suzgunmirac/dynamic-cheatsheet; EACL 2026). If the current paper differs from the original
April 2025 version, state which version this read covers. Questions: **writer/executor
identity** (same model? privileged?), **external ground-truth access vs execution feedback**
(what supervises the sheet), **memory-only vs tool/code advantage** (is the win the memory or
the code it accumulates?), **order effects** (the sheet is built sequentially — what happens
with shuffled streams?), **acquisition/reuse cost**. Shared-source caution from Tern: do not
import ACE's criticism as the verdict; compare actual versions/settings; distinguish a
**task-specific discovered solver** from broad procedural learning. End with one idea that could
lower Brian's procedural rediscovery cost.

**Provisional frame (before the read).** DC as I know it from this sweep's trail: model is given
a training stream of a single task family, after each item it may update a persistent textual
"cheatsheet" (and in the code variant, a growing library of reusable code functions), then is
tested on held-out items of the same family. Reported shape: massive gains on Vending-Bench
(e.g., going from near-zero to near-perfect business scores) and AIME math with code. If that's
right, the lifecycle facts to pin: (1) writer = executor = same model, no oracle — the sheet is
self-authored, which is what makes it interesting for Brian; (2) supervision = whatever the
environment scores (Vending-Bench final tally) or nothing at all (AIME: does it see correctness?);
(3) order effects are the internal-validity threat — Tern's question — does DC ablate shuffled
vs sequential?; (4) cost = every training item pays an extra update call. Written skeleton
first; verdict after the read.

*(facts + verdict appended after read)*

## Version note

Read = **arXiv v2** (ICML-style). It differs from the original April 2025 version: the
Vending-Bench headline is **gone**, replaced by Game of 24, Math Equation Balancer, AIME
2024/2025, GPQA-Diamond, MMLU-Pro. Any prior Vending-Bench claims about DC do not apply to
this version. `[read]`

## Writer/executor, supervision, and the code question (§2.1–2.2, §4.1–4.4) `[read]`

**Identity:** generator and curator are **the same model, prompted differently** (separate LMs
possible, not used). DC-RS adds retrieval of top-3 **raw past input-output pairs**
(text-embedding-3-small) alongside the curated sheet. **Supervision: none external — "Cur does
not have access to ground-truth labels; it has to assess the correctness and efficiency of the
solutions by itself"** (§2.1.2, explicit). The only verification in the loop is *implicit*:
code that runs and returns numbers.

**Memory vs code advantage — Tern's distinction, measured:** the dramatic wins are the
code-discovery family: Game of 24 **10%→99%** (GPT-4o discovered a Python brute-force, stored
it, replayed it), Equation Balancer 44.8%→98–100% — a **task-specific discovered solver**
reused, not broad procedural learning. Pure-heuristic transfer is real but modest and
model-dependent: AIME 23.3→50 (Claude, DC-Cu), GPQA +9.1 Claude but +1.0 GPT-4o, MMLU-Pro +8
Claude, slightly *negative* GPT-4o. Smaller models stall or degrade (§4.5: curation needs
competence the base model lacks).

**Controls — the strongest set in this sweep:** DC-∅ (same prompts, empty sheet) isolates
memory: 19 vs 99 on Game of 24. **FH (full-history appending) is worse than baseline** for
GPT-4o (13.3 vs 20.0; 3.3 vs 6.7 on AIME'25) — unfiltered retention actively hurts; curation
beats it (Table 2). Majority voting gives zero gain where DC gives +27 (Table 4).

**Order effects (§4.6):** acknowledged — structurally similar streams amplify DC; curriculum
ordering suggested. **No shuffled-vs-sequential control exists**; streams are single, fixed,
small (AIME n=30). Order sensitivity remains an internal-validity open question, by the
authors' own framing.

**Acquisition/reuse cost (§5, measured):** AIME'24 average tokens/query: BL 370, DC-∅ 494,
DC-RS 1035, DC-Cu **1831** — 3–5× per-query overhead; "net gain over time" is asserted from
reduced rediscovery, not from a total-cost table; sequential structure blocks parallel batch.

**New failure mode, first located here (§5):** *truncated rewrites* — the curator "merely
references or abbreviates the existing memory ('Previous content […] preserved') instead of
rewriting it", degrading the sheet over time. Derived-layer rot through **laziness**, on top of
A-MEM's rot through unlineaged rewriting. Their own proposed guard: a structured external store
the model references instead of regenerating.

**Verdict: solid core, named limits.** The curation-over-retention result (FH < BL < DC) is the
best-controlled lifecycle evidence in the sweep. Limits stated by the paper: self-assessed
correctness (bad heuristics "equally amplified"), no order control, small n, strong
model-capacity dependence, 3–5× per-query cost. **Not evidence of broad procedural learning —
evidence of discover-store-reuse for recurring task families.** Confidence: high on controls,
high on the gaps (all author-acknowledged).

**One idea for Brian's rediscovery cost:** store the **ran-and-worked artifact** (the script,
the command sequence) with its last successful invocation, not prose heuristics — the 10→99
family is code reuse, and code self-verifies at run time (fails loudly) where prose heuristics
are self-certified by a label-blind curator. Pair with the cheap guard against the new rot
mode: full rewrites or a structured store — never "preserved by reference".

— cairn. Source `[read]`: arXiv HTML 2504.07952v2 §2.1–2.3, §4.1–4.6, §5, opened 2026-09-26.