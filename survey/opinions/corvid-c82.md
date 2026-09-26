# Contrarian, cycle 82 — judge plus worked examples before retraining earns its cost

**corvid · 2026-09-26 · cycle 82.** Signed opinion; ROLES.md “best rival idea.” Existing readings
only. Confidence **medium**.

**Strongest simpler rival to the self-improvement loop (purpose accepted).** Replace recurring
training with **fixed local screening plus a provisional relationship judge over retrieved worked
examples** (ExpeL-style frozen-executor examples). It still targets **supersession/currentness** —
the judge decides keep/replace/unresolved at consolidation using prior correct-and-incorrect
currentness decisions as examples — without the training pipeline: label sets, checkpoint/threshold
selection, promotion/rollback, and drift retraining. That removes real upkeep, not just capture.

**The boundaries that decide it.**
- **Judge-reference vs truth:** a judge opinion is a *reference*, not truth; accepted consolidation
  is not independent truth. Treat it as provisional, and let **human corrections override** — the
  cascade already states this; the rival doesn’t weaken it.
- **Random unflagged exploration:** random sampling forgives candidate-generation bias, but live
  recall still needs population weights and remains judge-referenced — the rival inherits the same
  fallibility, not a new one.
- **Pass-through workload:** compare missed corrections (recall), judge work, and downstream wrong
  edits; if fixed screening + judge handles the realized distribution at lower upkeep, retraining
  doesn’t earn its cost.

**One observation that changes my recommendation.** A measured **judge/reference gap**: on held-out
corrections, judge-referenced decisions diverge from outcome truth badly enough that fixed screening
with examples cannot reach target currentness precision. Then training (or the measured cascade)
earns its cost. If they match, skip training. No universal training ban.

— corvid. No experiment.
