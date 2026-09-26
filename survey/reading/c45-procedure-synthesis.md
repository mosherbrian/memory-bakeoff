# Procedure synthesis II — what c41–c44 actually decide for Brian's lane

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 45.**
Own reads only: CLIN (c41), AWM (c42), LATM (c43), CaP (c44). No new paper. C44 correction
carried: my "zero accumulation" for CaP was **wrong** — session history (§III-A) and functions
added to scope (§III-C) do accumulate within a session; the defensible statement is **long-term
learning unmeasured**. Also carried: hierarchy gains are aggregate, not per-subtype; sim, real,
and code-benchmark metrics stay separate; no per-record tax; no experiment.

**Two findings that discriminate** (against the starting arrangement: local model re-derives
everything each session, no store, no authoring pass):

1. **LATM's maker ablation (c43):** GPT-3.5 as tool-maker fails 0/5 on hard tasks while the same
capacity class **runs GPT-4-made tools at parity** — authoring and executing are different
capacity problems. For a small-local-model lane this decides the division of labor: occasional
strong-model authoring, routine local execution. "All-local, every session" is the shape the
evidence rules out. Confidence: high (direct ablation).
2. **AWM's rule-vs-LM near-null (c42):** deduplicated action-sequence mining matched LM-induced
workflows on executed WebArena (35.6 vs 35.5). Once a store exists, **how content is mined
barely matters** — which rules out induction machinery as a prerequisite. A plain pass over
repeated sequences into files is enough to start. Confidence: high on the null's scope
(sophistication claims), per c42 qualification it does not prove "store vs no store."

**Two that do not discriminate:**

- **CLIN's generalization magnitudes (c41):** earned under simulator reward plumbing (subgoal
rewards NL-converted, valid-action lists) our lane lacks; the revision trace is qualitative.
Direction (structure beats free-form, −6) informs content style, not the arrangement.
- **CaP's code-benchmark gains and absolute SRs (c44):** unit-test pass rates are not task
outcomes; hierarchy gain is aggregate; sim ≠ real. Nothing here chooses between store designs.

**Practical recommendation (signed, now):** one strong-model authoring pass per recurring task
family produces **parameterized, perceptually-conditional procedure files** (CaP's shape, not a
fixed action sequence); local models run and lightly maintain them; mining can be dumb
(dedup-and-save). No induction service, no reward-engine dependency, no per-record metric. The
open question remains **long-term accumulation value** — unmeasured across all four sources —
so keep the store small and inspect it when a run fails that used a stored procedure.

— cairn. Signed: high on both discriminating readings, medium on transfer to coding-workflow
cadence; no new sources.