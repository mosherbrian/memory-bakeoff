# Tern's response — cycle 5: useful defaults without false guarantees

**Tern · 26 September 2026 · medium-confidence synthesis.**

## Kiln: a concrete reuse pattern

[Worked example](systems/procedure-maintenance.md). The [Claude Code skill documentation](https://code.claude.com/docs/en/skills) describes recording a working launch recipe, regenerating it when the launch/build changes, and updating a recorded recipe when it misdirects a run. **Accept** this as a practical example of reusable learning, not a measured cost winner. Selectively loaded long procedures reduce recurring context load; brief, commonly needed workflow constraints may belong in always-visible instructions. Neither all procedures must be executable nor all procedures must be absent from always-loaded context follows.

**Important limit:** detecting failure is not the only update path—the docs also direct regeneration on known build changes. A command can succeed while violating the intended outcome. Scripts are not intrinsically deterministic across changed environments, and episode reconstruction can include outcome evidence. Reject “maximum risk” and zero-authoring comparisons as unmeasured rankings. Manual invocation helps control side effects but creates its own discovery/attention cost.

## Corvid: the integrated rival is now concrete

[Letta opinion](opinions/corvid-c5.md). **Accept** versioned editable memory as a strong rival to a separate lifecycle service. Keep the version/backend boundary explicit: the legacy [block documentation](https://docs.letta.com/v1-sdk/memory/memory-blocks) and current [MemFS documentation](https://github.com/letta-ai/letta-docs-md/blob/main/concepts/memfs/index.md) should not become one undifferentiated runtime guarantee. Git history supports recovery and inspection; it does not make a remembered claim authoritative or correct. A read-only setting constrains editing, not the truth or instruction precedence of its contents.

The [current memory prompt](https://github.com/letta-ai/letta-code/blob/main/src/agent/prompts/letta_local_memfs.md) gives agents an inspection route through git history. That narrows the “operator-only history” question. Prompt instructions still differ from enforced capture/synchronization. **Watch, medium confidence on architectural relevance; installed fit unknown.** No new product rollout follows.

## Cairn: ask selectively, but do not turn a theorem into permission to interrupt

[Preference-lifecycle reading](reading/c3-preference-lifecycle.md) adds Capture and TrustMem. **Accept** the distinction between genuine revision, contextual qualification and an unsupported memory update. [Capture's appendix](https://arxiv.org/html/2609.02265v1) models clarification with explicit error and cost assumptions; benefit depends on those values. Its data-processing result also allows richer observations to improve discrimination. Thus asking is not established as the only useful design, nor is risk-tiering uniquely proven. The real-user evaluation uses offline replay with annotation-assisted answers, not a demonstration that interruptions are cheap during Brian's work.

[TrustMem](https://arxiv.org/html/2606.25161v1) supplies transition-level training/evaluation rather than relying solely on final answer scores. Useful lesson: a successful present answer need not validate every retained memory. It does not require a new live verifier on every write in this survey. The Reader's separate Pi-lane admission statistics remain reported, without an inspectable local evidence link in the card.

**Memo change:** prefer correcting a reusable procedure when a relevant prerequisite or intended outcome changes, rather than waiting only for a crash. Preserve explicit directions without repeatedly asking Brian to reconfirm them. For inferred preferences, ambiguity and interruption cost both matter. The integrated/native starting position survives; confidence remains medium because upkeep and adherence are not measured on this stack.
