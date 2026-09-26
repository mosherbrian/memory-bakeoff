# Availability, invocation and application

**Tern ·26 September2026 · current official documentation, not an installed test.**

[Claude Code skills](https://code.claude.com/docs/en/skills) distinguishes description-based discovery, body loading on invocation and instruction persistence. Compaction can truncate or omit older invoked skills within its reattachment budgets; “stays forever” overstates this. Runtime invocation controls and tool permissions are real, so “nothing enforced” is false. `allowed-tools` pre-approves rather than restricts the tool pool; `disallowed-tools` removes tools while active. Neither proves the procedure is followed correctly. Hooks can implement particular checks, not universal semantic success. This narrows Kiln's card without turning documentation into an installed result.

[Pi skills documentation](https://raw.githubusercontent.com/badlogic/pi-mono/main/packages/coding-agent/docs/skills.md) also describes names/descriptions advertised before full instruction loading. Thus a skill-discovery surface is documented; parity in all host behavior is not established.

**Judgment:** a tiny always-present core avoids explicit retrieval but still requires interpretation and applicability decisions. Longer or occasional procedures favor selective loading; do not make Brian narrate every selection or rerun every check by default. Selection is a plausible failure point, not yet his measured dominant bottleneck. Policy-training ablations alter more than invocation alone; they cannot prove the local bottleneck.
