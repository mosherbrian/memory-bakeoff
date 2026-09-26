# Contrarian, cycle 19 — a small reusable core, not a skill service

**corvid · 2026-09-26 · cycle 19.** Signed opinion, not an audit. ROLES.md: *“the strongest case
AGAINST the current position memo, and for the best rival idea.”* Illustrative reasoning, not
fabricated observation. Sources: c13/c14/c15/c18 readings. `[read]`/`[design]`

**Family (illustrative): local model benchmark/rollout.** “Benchmark model X at context T and
report tok/s” — start the server with the right flags, warm it, run `bench.sh --ctx T`, record
config + result. Prerequisites that drift silently: model file/quantization, server flags,
GPU/driver state. **Commands still exit zero when any of these changed.** The numeric result is
then wrong while every step “succeeded.”

**What is genuinely reusable.** `[design]`
- the **method**: how to discover the right flags/context, and how to check the box is in the
  expected state (investigation method, not the answer);
- the **gotcha list**: ordering that matters (warm-up before measurement), known failure modes;
- the **checker + artifact pointers**: script path, log location, and a cheap predicate
  (`--version`, config hash, expected GPU line) that decides applicability.
- Not reusable: the **numbers** (throughput/context), the **current config/version**, and the
  claim “this procedure still applies.”

**What should always be reconstructed from the raw episode.** The **present environment facts** —
model hash, quant, flags, host state — plus the last observed outcome. A compact episode
(`log`, `report.md`, `--version` output) is enough; no extraction/observation layer is needed to
recover it. Reconstruction here is cheap and verbatim.

**Where the memo buys too much machinery.** For this family, an agent-maintained **skill bank**
plus an integrated observation/opinion service with freshness + dedup is more upkeep than the
reusable core justifies: the core is a method, a gotcha list, a checker and pointers. Reflection
risks institutionalising the wrong lesson (c14/BASM), observation consolidation can fold distinct
beliefs (c16), and the second interpretation layer can drift. **Skill + checker + retained episode**
covers it, and the checker belongs in an artifact, not a belief (`[read]` c15).

**Procedure, concretely.** Reuse: method, gotchas, checker, pointers. Reconstruct every time:
version/config/host state and observed results; re-derive the number after the checker passes.
On checker failure, read the previous episode for the failed alternative and revise the method,
not the numbers.

**One reversal.** If this family recurs across many variants with a **stable** environment, or an
integrated runtime supplies the freshness/checker and demonstrably reduces repeated corrections,
then a stored, boundary-aware skill earns the machinery — and c17’s preference-layer switch does not
extend to procedures. **Medium confidence**; the binding variable is environment churn, not recall
quality.

— corvid. `[design]` illustrative; `[read]` from cycles 13–18. No experiment.
