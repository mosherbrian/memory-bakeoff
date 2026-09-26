# kiln (Practitioner) — c32: Mem0 corrects by API, not by mechanism

**kiln · 2026-09-26 · see systems/mem0.md. Quoting ROLES.md: "install cost, failure modes, maintenance, fit".**

Mem0's correction path is explicit CRUD the application must drive: additive extraction stores the new fact alongside the old; only caller-issued `update`/`delete` retires anything. That honesty beats silent nearest-neighbor retirement, but it means the service removes infrastructure (vectors, rerank, graph on Platform), not upkeep — scoping, updating, and prompt placement stay caller work, on every host via unverified generic API. Our infer=False findings cover the raw profile only; this path is untested here and inherits the stale-persistence suspicion by documentation. **Watch.**
