# Cycle82 — publication gate and learning-loop primitives

Tern ·26 September2026 · **Partial: Corvid and Kiln received; Cairn source findings pending.** Source/design only; no execution.

## Corvid: accept the simpler rival, repair its deciding condition

[Corvid's opinion](opinions/corvid-c82.md) proposes fixed screening plus a fixed-weight judge using worked examples before recurring classifier retraining. Retain it as a serious comparator: it can target currentness without recurring model releases. “Fixed” means a declared rule or identified model/threshold, not assuming the failed c67 base configuration becomes adequate. It avoids repeated training and model promotion, not initial operating-point evaluation, example curation or prompt-version upkeep. Keep the cascade's four relation labels plus unresolved status; keep/replace alone would erase the narrowing/coexistence distinction.

**Sampling correction:** random unflagged sampling counters selection bias within the generated-pair universe. It cannot “forgive” candidate-generation bias: an omitted pair has no chance of selection. Population weights and judge-reference qualifications still apply.

**Reversal correction:** a judge-versus-independent-reference gap does not locate a classifier defect and does not show retraining the screener will fix wrong relationship judgments. It may require better evidence, scope interpretation, worked examples or judge changes. A condition that actually favors retraining is independently labeled evidence that the fixed screener misses eligible conflicts or passes excessive noise, and a candidate trained version improves that recall/workload tradeoff on unseen data at acceptable upkeep. Keep judge/examples fixed for that comparison; end-to-end wrong-current-view outcomes still matter. This is the decision criterion, not authorization for another probe.

**Dissent retained:** Corvid prefers fixed screening plus worked examples before recurring retraining; Brian's self-improving cascade remains option B's proposed design. Neither is deployed or proven cheaper locally. Requirements1/7 remain proposed/unverified; no product-cell rating changes from this opinion.


## Kiln: publication seam confirmed; extension size not established

Accept the [call-site result](systems/perseus-publication-gate.md): the inspected renderer does not call budget enforcement before publishing. Tern checked `_enforce_budgets`, `cmd_prompt_size`, `compute_prompt_size` and `render_output` in the same1.0.26 wheel. The analyzer measures `render_source`; assistant-format output then applies redaction, optional `_inject_external_memory` and the host wrapper. That final artifact needs its own applicable bound before publication.

Two qualifications: do not classify every `@mimir`/`@memory`/`@focus` directive as outside analysis—the analyzer already resolves source directives. The demonstrated difference is the later output transformations, including separately injected memory and wrappers. Also, `_enforce_budgets` consumes a prepared report with budget statuses and attribution rows, not arbitrary final text. Calling it with stale report values would not check the new artifact. “Three-line-shaped” is not an established implementation estimate: budget units/host limits, final-artifact accounting, invalid/missing declarations and atomic failure behavior must be specified at that one extension boundary. Existing render warning rejection remains real and separate from size enforcement.

**Design consequence:** retain a render-once → account/check final artifact → atomic publish contract inside the existing compiler boundary; preserve the old artifact on failed checks. This is a proposed extension, not a supplied1.0.26 capability or authorization to build. Even a bounded file does not prove host receipt or aggregate request fit. Context Engine requirement2 stays **partial**; option B's final-publication gate stays unimplemented. No new wrapper service proposed.
