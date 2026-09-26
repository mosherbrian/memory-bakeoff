# Reading note c68 — STALE: does the system remember that a memory died, or just notice a new fact?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 68.**
Skeleton first; single queue; reading only. Lead located in c66: **STALE, arXiv 2605.06527** —
identity and actual edition to be verified **before** methods claims. Charge: explicit vs implicit
drift, label origin, same-executor controls, abstention/error asymmetry, changed-environment
versus static QA, cost, any correction-burden endpoint; and the isolating question — **which
comparison isolates remembering invalidity rather than noticing a new fact?** C67 carried: one
authorized probe complete (27/46 vs 33/46 majority vs 46/46 rule, all 13 updates missed); no
repeat, no new experiment; general classifier failure not established.

*(facts + verdict appended below)*

## Identity: STALE, arXiv 2605.06527v1 (7 May 2026) — benchmark + prototype CUPMem `[read]`

**Construct: implicit conflict, axiomatized.** Axiom 1 — a new observation renders a prior belief
incompatible under world knowledge; Axiom 2 — **no utterance anywhere explicitly negates,
corrects, or marks obsolescence**. Type I: same attribute, incompatible value implied (Seattle →
Portland utilities). Type II: change **propagates** through a causal dependency to a different
attribute (dry-heat scorpion → residence no longer Portland).

**Construction and labels:** 400 scenarios, LLM-generated then **human-expert reviewed**;
exactly one conflict pair per instance; ~152K-token histories, 50 sessions, distractors sampled
from **LongMemEval** and filtered so nothing else touches the attribute. 1,200 queries across
three probes: **SR** (ask directly), **PR** (query *presupposes* the stale state), **IPA**
(mentions neither; safe execution needs the updated belief). LLM judge against state logic, 95.8%
human agreement, conservative bias.

**What the comparisons isolate — the commission's question:** §4.4 decomposes retrieval from
adjudication on the **same frameworks**: new evidence appears in retrieval for **77.5%** of SR/PR
cases, yet of old entries recalled at write time only **3.3%** are judged to need update —
**noticing the new fact is demonstrably present; remembering its invalidating authority is
absent** ("visibility does not imply authority"). The SR↔IPA dissociation (Qwen 76.0→39.0) and
the premise-collapse (SR 92→PR 30; 76→**4**) separate recognition, authority, and application.
Same-backbone control: among GPT-4o-mini memory frameworks only LightMem (17.8%) beats the plain
model (8.7%) — memory modules mostly add nothing. Best overall: 55.2% (Gemini-3.1-pro); most
frameworks <10%.

**CUPMem (method half):** write-side adjudication (active / STALE / replaced / unresolved),
topology-triggered stale search across dependent slots, constrained readout (stale = history only;
unresolved blocks unsafe defaults; presupposed-invalid premises blocked). **Schema-dependent
prototype**; schema fixed before evaluation.

**Unmeasured:** repeated updates and gradual drift (one-shot conflicts only, authors state),
correction burden/cost, organic dialogue distribution.

**Verdict: the benchmark closest to this panel's central construct, and its headline is my c55
advice's blind spot quantified — implicit conflicts generate no failure signal; the failure is
authority transfer at 3.3%, not retrieval.**

**One idea:** premise-resistance is a testable, currently near-zero (4–30%) behavior — worth one
line in any acceptance list. **One reversal:** if conflicts are mostly *implicit*, read-time
resolution (my c33-backed default) may be structurally too late — write-side adjudication becomes
the candidate; reverse if CUPMem's schema dependence fails to cover real attributes.

**Confidence: high on the 77.5/3.3 decomposition and dimension dissociations (explicit tables),
high on one-shot scope (authors' limitation), medium that Type II propagation difficulty transfers
beyond this constructed ontology.**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, COVERAGE.md.