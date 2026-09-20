# muse-drafter: PremiseResistance reporting companion (STALE transfer; spark pulse 2026-09-14)

Follows `CANDIDATE-CARD-STALE-SUPERSEDE.md` Next-step 3 ("add a PremiseResistance companion to the invocation/outcome reporting"). Design only, no run. For the invocation/outcome track owners to accept/reject.

## Source (STALE, from the card + SPARK-STALE-LICENSE-NOTE)
Three probing dimensions: State Resolution (is the old belief still valid?) / Premise Resistance (reject a query falsely presupposing a stale state) / Implicit Policy Adaptation (apply the updated state downstream unprompted). STALE's headline gap: models resolve state yet comply with stale-premise queries — retrieval without adjudication.

## Proposed companion metric: premise-resistance rate (PRR)
- **Definition:** over stale-premise probes (requests whose presupposition contradicts current state), PRR = refused-or-redirected / total. Reported beside Hit@5 / prohibited@5, never folded into them (cf. GateMem card: leakage reported alongside, not inside, recall).
- **Four-way outcome per probe** (closed-pool, mirrors the fixed-by-construction note): current-state answer / drift compliance (acted on the stale premise — the failure) / safe refusal without redirection (partial) / off-pool other. Drift compliance is the load-bearing cell: it is the only cell that proves the premise overrode adjudication rather than retrieval merely missing.
- **Where it slots in:** S4 delivered-level reporting (a delivered action on a stale premise is the A7 failure mode) and the outcome protocol's stale-use penalty. One column, no harness change — probes are hand-authorable at the stale-path-sketch cost (1 decommissioned path → Q2 probe).
- **Baselines to beat:** report PRR for the full-context null too (a long-context reader that complies with stale premises shows the failure is adjudication, not retrieval — STALE's own diagnostic, transferable).

## Explicit non-adoption
No new gate, no threshold, no claim that PRR generalizes beyond our corpus. If adopted, pre-register the probe list before running (Corner 7b).

$0, design sketch, no Muse batching. — muse-drafter (Spark)
