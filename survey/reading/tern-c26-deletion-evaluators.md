# The retirement evaluator can help or harm

**Tern · 26 September 2026 · primary §4–5.1 read; rest not yet read.**

[Xiong et al., 2505.16067v2](https://arxiv.org/html/2505.16067v2), cited by ReMe for deletion thresholds, compares periodic, history-based and combined deletion across four agents. History-based deletion uses downstream execution evaluations after retrieval; it is not per-entry counterfactual attribution. Table2 shows evaluator-dependent results: on AgentDriver, coarse-evaluator history deletion reduces success from36.92 to34.00, whereas the strict-evaluator comparison rises51.00→51.81. These are within-setting comparisons, not an isolated estimate of the value of changing evaluator alone.

The study also tests reordered task distributions for EHRAgent and AgentDriver. This is stronger shift evidence than merely invoking non-stationarity; it is not a changed-software-version or rare-procedure-return test. History deletion is not always the best deletion strategy under that shift. Source confidence high; transfer to Brian medium-low.

**My judgment:** operational counters deserve serious consideration; lack of causal attribution does not disqualify them. But outcome quality is part of the policy, not free supervision. An unreliable evaluator can turn automatic upkeep into automatic removal of useful guidance. Compare a proportionate, recoverable policy with retaining everything; do not promote the paper's thresholds or strict-evaluation privilege to defaults. Current-source recovery and exclusion from recommendations remain separate design responsibilities. No new counter, hook or experiment.
