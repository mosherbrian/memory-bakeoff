# Claude deterministic instruction loading — requirements4–5

Tern ·26 September2026 ·cycle74. Current official [memory docs](https://code.claude.com/docs/en/memory) and [subagent docs](https://code.claude.com/docs/en/sub-agents); no runtime test.

**Narrow component: enabled project-root CLAUDE.md, main conversation.** Documented startup loading and post-compaction re-injection remove a separate actor fetch decision. Requirement4 **yes within this explicit scope**: selected instruction source enabled, readable supported file below the 4MiB skip boundary, actual instruction text rather than stripped comments. This is delivery, not compliance. It does not promise delivery to every subagent or another host, protect edits, or repair an oversized auto-memory index.

**Rules component:** unscoped rules load at launch; path rules load on matching file reads, not every tool call. Requirement5 **partial**: automatic conditional loading exists, but relevant work can proceed without that read. Valid patterns and enabled project sources matter. The 1,000-pattern/4MiB bound concerns brace expansion; overflowing patterns remain unexpanded, while other patterns can work. Invalid YAML removes the scope, risking over-delivery.

**Subagent correction:** most load the instruction hierarchy. Explore/Plan skip it; omitClaudeMd supplies another exception. Main auto-memory has a separate non-fork exclusion. Do not combine these into a blanket project-instruction exclusion.

**Cells:** new narrow root-loader row4=yes; new rules row4/5=partial. Broad native-memory row stays partial4/5. Installed-version behavior remains unverified.
