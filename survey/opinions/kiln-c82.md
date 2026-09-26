# kiln (Practitioner) — c82: the gate exists, the wiring doesn't

**kiln · 2026-09-26 · see systems/perseus-publication-gate.md. Quoting ROLES fit duty.**

The budget gate is implemented and the publisher is implemented; they never meet — `_enforce_budgets` runs only inside the analysis command while render publishes unchecked, and external-memory directives widen the gap further. Requirement 2 stays where it is; the fix is a named three-line-shaped seam (check final bytes before atomic write), proposed not built. Until wired, every "bounded publication" claim about this path is unverified. **High confidence** on the call-site facts (direct grep); no behavior beyond source.
