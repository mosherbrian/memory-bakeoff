# Reading note — StateFuse: preserving two incompatible lessons without pretending one is false

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 30.**
One new primary source (Tern): **StateFuse — Volkov/Li/Luo, arXiv:2607.05844v1, identity
confirmed.** Cycle question: *a shared correction must survive disagreement* — two hosts report
incompatible lessons about the same procedure. Read methods and **matched controls**. Specifics:
what is **preserved**, who **detects** conflict and who **resolves** it; which **predicates and
identities are supplied vs inferred**; separate four things the paper may be conflating —
**replicated-state convergence**, **correction handles**, **answer accuracy**, **operational
safety**; inspect the **reported accuracy tie** as carefully as positive results; and does the
controlled loop supply an **oracle unavailable to ordinary procedure work**? One transferable
idea, no new service recommendation.

C29 corrections carried: INMS §4.2's LLM-judge uses reference ground truth — I retract "no
ground truth" as an evaluation claim about it; top-3 does not isolate selectivity as the sole
mechanism; the useful-positive-retrieval reading stands despite the absent sharing-vs-handoff
control.

**Provisional frame (before the read).** A "conflict-preserving" memory system should differ from
every lifecycle design read so far (supersede/evolve/delete) by **not collapsing** contradictory
records into one winner. The loadable distinctions: (a) if the environment's true state is
injectable/observable in their setup, conflict *detection* is exact — an oracle ordinary lanes
lack; (b) if predicates/identities (which entity, which scope, which time) are **supplied** by
the benchmark rather than inferred from prose, the hard NLU part is done for them; (c) an
accuracy **tie** against a collapse-to-latest baseline would mean preservation buys safety
(auditability, reversibility), not accuracy — worth stating exactly that way if the data show
it. Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## What is preserved, who detects, who resolves (StateFuse 2607.05844v1, §3.2–3.6, §4.2–4.3, §5.2–5.4) `[read]`

**Preserved:** an immutable op-set (Evidence/Claim/Retraction/Decision adds); merge is plain
set union — the paper says so (*"the novelty … lies in deterministic interpretation rather than
in the merge algebra"*). Contradictions materialize as explicit **ConflictSet** objects.
**Detection is deterministic, not learned** — a ConflictSet exists when a *functional*
predicate has multiple distinct active values — but it consumes a **supplied predicate
registry**: per-predicate functional/multi-valued flags plus deterministic `normalize` and
`equal` functions, gated by a contract checker. **Predicates and identities are supplied, not
inferred** — this is the oracle point below.
**Resolution at projection only:** resolvers choose a candidate, abstain, or fail closed and
**cannot mutate base memory**; the primary resolver *abstains on close or symmetric conflicts*;
an optional LLM resolver is JSON-schema-bound, failures stay unresolved and logged.

**The four separations, scored separately.**
- *Replicated-state convergence:* standard OpSet union + deterministic interpretation — solid.
- *Correction handles:* the real novelty. Every claim carries **claim_id** (exact) and
  **claim_ref** (semantic handle = key + predicate-governed value). Ablation (§4.3,
  deterministic, **n=13**): semantic-target recoverability **100% vs 0%** for id-only, and
  no-resurrection 100% vs 76.9% — a retraction by handle suppresses later copies of the wrong
  lesson, even arriving *before* its targets.
- *Answer accuracy:* **the tie is real and the paper leads with it** (§5.2): on the
  MemoryAgentBench conflict slice (282 tasks) StateFuse = MV-register = provenance surface
  (64.9% acc, 100% conflict recall, 2.1% false certainty); raw log ties on accuracy but 0%
  conflict recall. And note what the paper doesn't headline: **Collapsed scores 97.5%** on that
  slice — where gold is latest-value, conflict-preservation *loses* pure accuracy by design
  (abstentions count against it).
- *Operational safety:* agent loop (Panel B, uniform verification budget): all
  conflict-preserving surfaces 80%→100% post-verify, 0% false certainty; Collapsed 40%→60%,
  **40% false certainty**, 2.20 extra action cost. Small deterministic loop — directional.

**Does the loop supply an ordinary lane's missing oracle? Yes, twice:** the predicate registry
hands it deterministic "same thing, different value" — exactly the semantic judgment ordinary
procedure work must itself make — and the uniform verifier lifts every honest surface to 100%.
The demonstrated advantages are therefore **contract properties** (surfaced contradiction,
safe abstention, cross-replica correction), not accuracy — which §5.3 concedes verbatim.

**Verdict: methodologically solid and unusually honest** (the authors report the tie and refuse
the broad claim themselves); **transfer limited by the supplied-predicate oracle**; handle
evidence thin at n=13. Confidence: high on the tie and oracle-dependence (explicit), medium on
the safety loop.

**One transferable idea, no service:** **two-handle corrections** — record each lesson with
both its instance and its *claim* ("deploy-X → use-flag-Y"), and let corrections target the
claim so future copies of the wrong lesson are suppressed without any merge machinery; pair it
with the abstention contract — when two claims survive, the surface says *conflict* and Brian
judges, rather than a silent winner. That is disagreement surviving to the principal, which is
the cycle's question, achieved by record shape rather than workflow.

— cairn. Source `[read]`: arXiv HTML 2607.05844v1, opened 2026-09-26; c29 corrections carried
(INMS LLM-J uses reference ground truth — retraction made in that file's spirit here; top-3 ≠
selectivity isolated).