# kiln (Practitioner) — priorities: procedures first, preferences second

**kiln · 2026-09-26 · ≤200 words · reuse of existing reading, no installs/probes. Quoting ROLES.md: install cost, failure modes, maintenance, fit for Brian's stack.**

1. **Executable skill — rank first. Would recommend.** Authoring costs most (schema, checks, upkeep) but use is cheapest: it runs the procedure instead of redescribing it. Failure mode: bit-rot when the task changes and the skill doesn't; mitigate by versioning skills beside the runbooks they came from. **Medium confidence** (roadmap Phase-G logic + memo §4 direction; no hands-on claim).
2. **Plain runbook — rank second. Would recommend.** Cheapest to author and review; costs recur at every use (agent must re-read and reinterpret). Keep as the source every skill is distilled from, and keep **failed** runbook attempts with outcomes — a past successful trace is not automatically a presently applicable procedure. **Medium confidence.**
3. **Automatic procedural extraction — rank last. Would watch.** Zero authoring cost, highest failure cost: learned procedures preserve mistakes (roadmap failed_procedure_adoption ×3) and need admission machinery we haven't built. Revisit only behind a Phase-D-style gate. **Low confidence.**
4. **Minimal scoped preferences — the second cost.** One short notes surface (repo CLAUDE.md for shared, user project-memory for personal — not the same store), each entry sourced + dated, pruned on change. Treats Brian's #2 cost without building a second procedures system. **Medium confidence.**

Per Brian's principle: skills/runbooks are what the agent has learned; keep the full history and the artifacts that establish what is true; let executive reasoning — not the store — decide what applies now.
