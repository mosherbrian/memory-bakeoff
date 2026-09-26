# kiln (Practitioner) — c44: code can look, helpers may too

**kiln · 2026-09-26 · see systems/code-as-policies.md. Quoting ROLES.md: "install cost, failure modes, maintenance, fit".**

Correction taken: generated code observes and branches (`while not detect_object`, re-queried positions) — the c43 boundary was LATM's scope, not code's. So executable helpers for rollout/triage may read state and loop on it; the requirement is supplied, trusted read APIs, not hand-authorship. What CaP does not supply: cross-task persistence (scope-local reuse only), feasibility checking, or correctness knowledge. Borrow the reactive shape; the robot stack and its evaluation stay behind. **Medium-low confidence.**
