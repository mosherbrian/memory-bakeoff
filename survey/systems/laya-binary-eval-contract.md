# System card: Laya binary-eval contract (source-read)

**kiln · 2026-09-26 · source: NandhaKishorM/laya @ 4066d5d (`laya/evals.py`, `laya/evals_cli.py`, `laya/onnx_agent.py`; read-only clone, no run/model call). Quoting ROLES fit duty. Roadmap inputs, principles, c67 probe as context.**

## Positive-class contract (exact)

- Served answer carries raw `noul` P(yes) **and** `answer_confidence` = calibrated max(p) — for noul, max(p, 1−p), i.e. confidence in the predicted class either way. These are different fields: probability vs class-confidence. Do not read one as the other.
- Returned prediction vs thresholded flag: the model returns the probability; the **0.5 threshold lives in eval code** (`_correct`: `noul >= 0.5`), not as a served flag. Any operating threshold is caller-chosen; the artifact supplies p, not a decision.
- Custom Evaluator metrics **do** reach CLI gates: `--min METRIC=VALUE` / `--max METRIC=VALUE` (plus `--min-accuracy`/`--max-ece` shortcuts) compare against `report.overall` keys — custom metric names included — with failures exiting 1; `--baseline` compares saved reports with tolerances. So a screening gate (recall floor, ECE ceiling) is expressible in the existing CLI, no scorer to build.

## Mismatch check: none found on this path

No binary score-to-probability conflation in code (fields distinct, docstring explicit); no test-data/training leakage in the eval path inspected (eval runs a fixture file against the served model). Checkpoint-swap speculation out of scope — pinned revision above; served-checkpoint identity remains a deployment observation, not a code property.

## Opinion: small supplied extension point, confirmed

The eval CLI already implements threshold gates + baseline comparison over custom metrics — the desired screening needs a different *invocation* (fixture + thresholds), not different code. No scorer built, no model called. **Medium confidence** (direct functions read; served-model behavior unmeasured).
