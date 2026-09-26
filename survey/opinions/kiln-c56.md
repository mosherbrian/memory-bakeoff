# kiln (Practitioner) — c56: one rollout, stored once, reused once

**kiln · 2026-09-26 · ≤300w · illustrative model-test/rollout, not incidence. Existing reads only. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Worked sequence

1. **First success:** rollout passes; agent appends the exact command sequence + environment notes (versions, paths, flags) to a dated run log (facility: files; convention: writing it down).
2. **Distill (maybe):** if the shape looks repeatable, a short skill with scope line + worked example — *maybe*: most corrections stay log entries, never skills (c55 carried).
3. **Config change:** paths move; next run fails at step 2. Agent greps the log (facility: pi-lcm/file search), reads the old sequence, adjusts the path, reruns.
4. **Update:** the skill, if it existed, gets its path line edited with a dated note; if only the log existed, the new run appends. No closeout wait required, no reload demanded unless the host needs it, no Brian commit-review prescribed.

## Smallest stored object

The dated run log with exact commands — not the skill. Skills earn existence on second reuse; the log is the substrate everything else derives from.

## What requires judgment (never automated here)

Whether the failure is a path change (edit and proceed) or a procedure change (rethink); whether the old sequence misleads (archive with reason) or informs (adjust inline). pi-lcm history supplies evidence, not capture into guidance — the promotion decision is the agent's, at the moment, with the log open. **Medium-low confidence** (worked from inspected facilities; no deployment claimed).
