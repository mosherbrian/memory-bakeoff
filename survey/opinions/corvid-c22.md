# Contrarian, cycle 22 — delete the selection step before you improve it

**corvid · 2026-09-26 · cycle 22.** Signed opinion; ROLES.md “best rival idea.” Evidence already
read; no new source. Confidence **medium**.

**Is selective invocation the bottleneck? Plausibly, but unmeasured for Brian.** Separate capture /
selection / loading / following / correct execution. Local evidence is indirect: R53 was a ceiling
null (reads with no advantage), R68 had index delivery with no s2 read — neither isolates
selection. The real signals are Gen45 (model largely ignored provided control tools: 6 patches,
0 transitions), SkillForge’s ablation (removing explicit skill calling 87.9→77.9 ALFWorld), and
BASM (retrieving *more* skills raised the wrong-tool margin +47%). So selection/application can
fail and can hurt — but calling it “our most likely bottleneck” would be a hypothesis, not a
finding. `[read]`

**Strongest rival that removes an operation, not stores more: always-loaded core, no selection.**
Make the small reusable core part of the **always-present instruction surface** (a few lines, or a
single short cheatsheet entry), so there is no invoke decision to get wrong. DC-Cu has no retrieval;
DC always puts memory in the prompt. SkillForge *requires* the agent to call skills; the rival
deletes that step. Cost is prompt budget and attention, not correctness by selection. The
capture→select→load chain’s weakest link is selection, and the cheapest fix is to delete it.

**What action changes.** Prefer **always-loaded** over retrievable skills for the smallest core;
build selection/retrieval only when the always-loaded set outgrows its budget. This also means an
applicability predicate can live beside the core, so “stored” and “applied” coincide.

**Reconciling c21 (not manufacturing a fight).** There is no contradiction: procedures stay
**native/always-loaded** (where applicability is checkable), while the **preference layer** is the
candidate for integrated freshness/correction. Different layers, different failure modes.
**Territory check:** if the always-loaded core grows past budget, selection returns and this rival
weakens.

— corvid. Based on cycles 15–21 readings; no experiment.
