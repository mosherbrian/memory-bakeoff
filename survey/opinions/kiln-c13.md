# kiln (Practitioner) — c13: who does the upkeep

**kiln · 2026-09-26 · ~350w · responsibility map only, nothing implemented. Sources: current Claude Code docs (memory + skills, read c2/c5/c9), pi-lcm workspace reads (c2-cont/c3), roadmap inputs, BRIAN-PRINCIPLES. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". No invented thresholds — repeated preferences are already established as costly.**

## The map: facilities vs glue, per step

- **Automatic capture:** EXISTS on Claude Code (auto-memory topic files; `/verify` self-recording). NOT OBSERVED on Pi or local agents — capture there is operator action today.
- **Canonical update:** half-exists. Git commit is the mechanism but nothing invokes it; `/memory` edits and skill files change without review unless committed. The update step has storage but no trigger.
- **Host refresh:** EXISTS on Claude Code (imports and rules resolve live at session start; synced skills refresh ~10min). NOT OBSERVED on Pi (checkout/symlink freshness is manual) or local agents (slices re-cut by hand).
- **Selective loading:** EXISTS (three tiers + path-scoped rules + `disable-model-invocation`).
- **Correction after changed prerequisites:** EXISTS NOWHERE as a facility. The only documented detectors are reactive: a run failing through a stale skill, a `/doctor` trim pass someone triggers, a usage glance. Nothing watches prerequisites.

## Most consequential gap and concrete alternative

The gap is host refresh + correction detection on Pi/local with Brian as the implied operator — the c12 arrangement works only if someone who is not Brian carries updates across. Alternative: **symlink views, agent-owned closeout.** Where the platform supports it, views should be links, not copies — Claude Code `@imports` already are; Pi's agent dir already symlinks auth/models, so canonical preference/skill files can be symlinked the same way (read-only workspace check, c3); only local-agent slices stay manual. And upkeep gets an owner: a closeout skill the agent runs at session end (capture corrections → propose canonical diff → Brian reviews by commit, never by copying). Operation owner: the agent per session, Brian as reviewer — the same review posture as code, no new role.

## Residual risk, honestly

Symlinks do not fix correction *detection* — nothing notices a changed prerequisite until a run fails or a trim pass runs. That detector remains unbuilt glue (a watcher is a small service with its own ops cost, not recommended now). The map's claim is narrower: with linked views and agent closeout, staleness converges to "wrong until the next run" with a visible diff, instead of "wrong on two hosts until Brian notices." **Medium-low confidence** — facilities are docs-verified, the closeout skill is proposed design. Deepened read-only: `.pi-agent/` contains exactly two symlinks (`auth.json`, `models.json`, both into `~/.pi/agent`) — symlink *resolution* in the agent dir is proven, but both are same-machine config links, so symlinking *canonical content* remains extrapolated, not observed. Downgrade that half accordingly: mechanism plausible, content-linking unproven.
