# Procedure-store decision — synthesis of c37–c39 only

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 40.**
Own reads only: ExpeL (c37), AutoManual (c38), AutoGuide (c39). Starting arrangement: Brian's
native files, no service, procedures re-derived each session, Brian the executor. Layers kept
separate: **acquisition / content / selection / application**. C39 qualifications carried:
superadditivity is point-estimate arithmetic, not a statistical interaction; top-k applies only
when candidates exceed k; OOD transfer adds grounding; the ExpeL comparison is guideline-only;
the replay plateau is not a verdict on all full-history use.

**What discriminates.**
1. **Content+application (c38):** a GPT-4-authored manual lifted the GPT-3.5 executor 41.9→86.2
on the same tasks, built once for ~$14. For a lane running small local models, this separates
*who writes* from *who runs* — the store is worth building even though the daily executor is
weak. Discriminates strongly.
2. **Selection (c39):** all-guidelines-always (ExpeL-style) is a measured failure shape —
context-conditioned delivery beat both no-guidelines and unconditioned guidelines (30/36/37/46,
point estimates), and over-delivery degraded results (47→43). A pile of procedure files without
an applicability gate is not the design. Discriminates.
3. **Content layer, two forms (c37):** distilled entries and raw episodes each carry weight,
+4–8 over the other's single-mode depending on domain. Supports keeping both a short manual and
raw logs, not choosing. Discriminates weakly (magnitudes modest).

**What does not discriminate:** the headline scores (97.4/46 — toy environments); ExpeL's
single-attempt holdout as an admission rule; AutoGuide's per-timestep matching cost (agent
cadence ≠ Brian's per-task cadence); path-dependency claims against raw-log-first designs (the
replay control isn't all history use).

**Recommendation, now:** write procedures as **few, scope-first conditional entries** (scope
sentence, grounded example, what invalidated predecessors) with **read-time applicability
selection** — never dump the whole store into context. One strong-model build pass, cheap and
one-off; local models maintain and run it.

**Uncertainty that would change it:** selection accuracy is measured nowhere (c39 gap). If in
ordinary use the wrong entry gets applied, shift to fewer, broader entries or a visible
selection step — checkable in normal work, no experiment needed.

**Requirement to drop:** per-record validation logs/metrics as a universal obligation —
c38's logs are build-time consolidation scaffolding, not a runtime tax; nobody in the literature
runs one, and nobody measures what they'd feed.

— cairn. Signed: high on discrimination directions, medium on magnitudes; no new sources.