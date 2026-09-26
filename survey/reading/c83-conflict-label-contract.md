# Reading note c83 — what the conflict benchmarks actually label, and the screening positive that keeps unresolved cases honest

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 83.**
Skeleton first; **existing survey notes only**, at most three reads (MemConflict intake row,
StateMem/StateMemBench card, tern-c3 identity row); no dataset re-reads or downloads, no new
paper, no gold relations inferred from names. Training candidates only — not authorized training
data, not an automatic pool. Deliver: which sources actually label binary candidate-conflict or
replaces/narrows/coexists/unrelated; label granularity, scope/time/authority coverage, unknowns;
and the minimum screening-positive definition that retains an unresolved case without laundering
it into a negative.

*(answer + proposal appended below)*

## What the three existing reads actually label

**MemConflict** (intake row, Gen38 accounting): labels **conflict class** — conditional /
DYNAMIC / static — over **true user updates injected by construction**. The relation is
*replaces*, fixed by the generator; the scored quantity is **retrieval of the current item**
(Hit@3 on a held-out 27-persona slice). It does not label candidate relatedness and never asks
whether an update was a replacement. Time/dynamics covered (the DYNAMIC class is this project's
question); authority = user-update-wins by construction.

**StateMemBench** (card): supersessions **supplied explicitly** — symbolic event programs, gold
by deterministic replay; five trap modes; drift rates judge-labeled with ceilings (binary
κ=0.67, cross-family 0.37). Again: relation fixed by construction, **answers scored** against a
closed pool. No valid-time axis; transfer to conflicts that must first be *detected* is
explicitly untested by the paper.

**Supersede**: existing notes confirm only its **identity distinction from Memora/FAMA**; its
label granularity is **not recorded** in my notes — named unknown, not inferred here.

**Answer: none of the three labels the four-way relation, and neither readable one even labels
binary candidate-conflict.** Both bake in *replaces* and score downstream retrieval/answers.
KnowledgeDrift, per FIELD-MAP, scores answers/abstention — same shape, not read again.

## Minimum screening-positive definition

**Positive = a candidate pair where the new record targets the same subject as an active record
and cannot be jointly satisfied under at least one plausible reading.** Binary, recall-first.
Two clauses do the work: **(1) uncertain → positive**, routed to adjudication, never to negative
— c68's asymmetry: a missed replacement is silent authority transfer, a false positive costs one
adjudication. **(2) The four-way relation (replaces/narrows/coexists/unrelated) is the
adjudicator's output, not the screeners gold** — narrows/coexists cases are screening *positives*
that later label as non-replacements. That is what keeps an unresolved case from being laundered
into a negative: the screeners positive class is *candidate relatedness*, not *replacement*.

**Label consequence:** benchmark pairs (injected updates) can seed **positives only**
(replacement ⊂ candidate-related); negatives must be **matched non-update continuations**, not
arbitrary pairs — otherwise the screener learns topic similarity, not conflict. No existing
source supplies those matched negatives; naming that gap is the finding, not a framework.

**Cell delta: none.** These are training candidates; no product row changes rating.

**Confidence: high on what the two construction-based sources label (direct card/intake text),
high that none labels the four-way relation (vocabulary absent from all three reads), medium on
the proposed positive definition (design judgment; its cost asymmetry rests on c68, one-shot
evidence).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, panel-response-c82.md,
OPTION-B-LEARNING-LOOP.md.