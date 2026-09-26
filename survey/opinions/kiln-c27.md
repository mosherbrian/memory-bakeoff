# kiln (Practitioner) — c27: memory for ambiguous outcomes

**kiln · 2026-09-26 · ≤250w · existing capabilities only. Quoting ROLES.md: "install cost, failure modes, maintenance, fit". Roadmap inputs + principles as context.**

## Illustrative procedure: flaky-failure triage

Success is ambiguous — the fix may have worked or the flake may have hidden. What saves rediscovery is not a verdict but the *trail*: which logs were checked, what was ruled out, what remains open.

## Smallest arrangement: a three-part note

One short file, three labeled sections: **Observations** (dated, sourced, no inference) / **Tentative explanation** (explicitly marked hypothesis with its disconfirmer — "drops if X recurs after fix Y") / **Current direction** (the next check, not a conclusion). This structure is the mechanism: it stops a guess from hardening into a "known fix" while keeping the legwork reusable.

- **Implementation (exists):** Claude Code user/project notes + Pi canonical file + pi-lcm recall; three headers cost nothing.
- **Proposed practice:** the agent updates it at closeout; revision triggers are new evidence or a contradictory outcome — not a schedule, not a move/prune ritual.
- **Honest limits (c26 carried):** archiving affects future discovery, not already-loaded context; the superseding note may lose retrieval to the older corpse; archived history stays useful as raw material. No ritual fixes that — the disconfirmer line is the closest thing: it tells the next run exactly what would retire the hypothesis.
