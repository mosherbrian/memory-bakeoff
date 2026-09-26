# kiln (Practitioner) — c36: retry buffer, not reusable lesson

**kiln · 2026-09-26 · see systems/reflexion.md. Quoting ROLES.md: "install cost, failure modes, maintenance, fit".**

Reflexion's buffer resets per task by design (Ω ≤ 3, thrown away after): it is current-task recovery, not long-lived memory — the 91% is pass-after-trials, and WebShop/weak-model failures bound it to checkable tasks with capable models. Borrowable: bounded retries with last-N reflections in context, consecutive-failure stop, self-tests distrusted at measured FP rates. Importance scoring and reflection cost real calls; evidence pointers are stored but never leave the task. Nothing here retires, persists, or transfers — and that honesty is the point. **Medium confidence.**
