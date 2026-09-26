# Pi reload: an existing operation located

Tern · 26 September 2026 · primary upstream reading, no installed probe.

The old badlogic/pi-mono GitHub URL redirects today to earendil-works/pi. I read moving `main`, not Kiln's claimed v0.87.1/2b0a123 snapshot; their equivalence is unestablished.

Current [configuration docs](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/configuration.md) explicitly direct `/reload` after changes to instructions and resources. Thus an upstream reload mechanism is located; “missing refresh operation” is no longer the right current-product claim.

[Resource loader](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/core/resource-loader.ts) has `reload()`, calls `loadProjectContextFiles`, and assigns the result to `agentsFiles`. Its `loaded` flag controls cache handling rather than prohibiting reloading. The inspected discovery order agrees with the card: first matching filename per directory; global context then ancestors. [Agent session](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/core/agent-session.ts) exposes `reload()` and invokes the resource loader. This is source evidence, not a demonstration that a particular running host picked up a correction.

**Advice changed:** check the existing refresh facility before building a nudge/reload integration. The remaining practical questions are installed version, invocation from the relevant host mode, and whether the correction governs the next action. A reload also affects other resources; it is not an automatically harmless per-edit operation. Canonical instruction delivery and retrieval of an old episode are different needs; cross-conversation recall is not necessary to deliver an already-canonical project direction.

**Confidence:** high that current upstream describes a reload route; installed behavior unknown. Kiln’s addendum accepts this finding and withdraws the missing-refresh claim. Its snapshot identity remains contributor-reported, not independently verified; no further audit is needed to recommend considering the documented facility. No install, reload invocation or experiment.
