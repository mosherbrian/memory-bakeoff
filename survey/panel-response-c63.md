# Cycle63 — composition matters; edge placement is not a universal rule

Tern ·26 September2026 · complete: all three panel reports read. [Primary v3](https://arxiv.org/html/2307.03172v3), §§2–5; [opinion](opinions/corvid-c63.md).

**Accept:** evidence can be present yet poorly used. Moving the answer-bearing passage while preserving the supplied document set isolates a placement effect in the tested QA setting. Composition deserves attention alongside retrieval.

**Bound the inference:** the length manipulation adds distractors, so it does not isolate token count from interference. The experiment supplies the relevant passage; deployment must identify it. It does not compare composer architectures or establish that small cores help mainly through edge placement. Synthetic retrieval also has strong model-specific exceptions.

**Practical decision:** keep decisive guidance salient and remove irrelevant material where useful, preserving scope, supporting evidence and instruction precedence. This is a design judgment, not an established instruction-following result. Do not universally move directions to prompt edges, shrink away necessary evidence, or assume shorter is always better. “Decisive” must not become a label that silently elevates untrusted content.

**Memo disposition:** no architecture change on this report alone. Placement and budget are concrete composition concerns, without requiring a separate service. Current-host behavior and procedure/preference transfer remain unmeasured; other panel pieces pending. Medium confidence in the concern, lower confidence in a specific ordering remedy.

**Kiln:** accept composition as a convention rather than a new service. Withdraw the roughly20-document default: the open-domain curve shows diminishing gains, not an optimal universal cutoff. Reranking/truncation are proposed directions in §5, not a tested remedy that beat dumping. Repeating the query sharply helps synthetic key-value retrieval but not QA; that contrast argues against prescribing it for procedure or preference prompts. The U-curve is not universal across models/tasks, including near-perfect Claude key-value retrieval and recency-only Llama-2 7B behavior. [Card](systems/lost-in-the-middle.md), [opinion](opinions/kiln-c63.md).

**Practical limit:** choose context for the task, preserve dependencies, and consider ordering where the host permits it. A convention can require ongoing selection work even with zero installation. No fixed document count, query repetition or edge-placement rule adopted. Reader synthesis pending.


**Cairn:** accept the controlled placement result and the task-dependent query-repetition limit. Narrow “length causally changes accuracy” to the tested intervention of adding distractors. The controlled experiment supplies relevant evidence; §5 separately includes actual retrieval. Its reported result is diminishing positive gains, not a general finding that more retrieved documents eventually hurt. The paper mentions an estimated cost for broader GPT-4 evaluation, although it supplies no deployment cost ledger. [Reading](reading/c63-context-placement.md).

**Diagnostic correction:** host message order does not establish where relevant evidence lands or that an ordering change has negligible value. Placement-insensitive failures can arise from reasoning, ambiguity, conflicting instructions, formatting or missing evidence; they do not identify retrieval as the cause. Inspect the delivered evidence before localizing a failure. Repeating the query is a task-specific candidate, not a mandatory lookup aid.

**Final decision:** strengthen the memo's composition responsibility to include usable presentation, ordering and budget alongside precedence. Adopt no count cap, repetition recipe or separate composer service. The evidence shows a historical supplied-versus-used gap; it does not measure Brian's current hosts or procedure/preference outcomes. Next inspect a task-complexity benchmark to distinguish exact lookup from more demanding context use.
