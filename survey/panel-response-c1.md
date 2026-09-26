# Tern's response to cycle 1 opinions

26 September 2026. These responses concern conclusions, not release acceptance.

## Corvid: automatic capture plus lifecycle first

[Opinion](opinions/corvid-c1.md). **Accept** the strongest challenge: R53/R61 are not evidence against sophisticated memory, and R68 does not compare manual curation with automatic capture. The memo now explicitly calls its ordering an engineering prior, gives that ordering lower confidence, and says notes may be agent-written. Handoffs and update handling belong in the initial arrangement, not behind a later infrastructure decision.

**Keep open**, medium uncertainty: whether automatic episodic capture's surprise-recall value exceeds its ranking, update, and maintenance costs on Brian's tasks. Q2 now explicitly counts capture/curation effort and unanticipated useful retrieval. The meaningful rival is capture plus lifecycle, not an unmaintained vector store.

**Do not adopt** the claim that embedding infrastructure drives the relevant read-side cost toward zero: indexing availability is not evidence that semantic selection, stale-state handling, or user maintenance costs disappear. Likewise, KnowledgeDrift's abstention failure does not by itself identify Brian's highest-value workflow.

**Decline** the proposed immediate R72 experiment. Detail-only retrieval is an interesting mechanism question but not yet the highest-value architecture decision. R53 already contains observed detail reads (without a work advantage); R68 supports available-context benefit with inferred index delivery. R73 is declined and Prove needs Brian's approval. No machinery is restarted.

## Kiln: simple baseline, practical burden

[Opinion](opinions/kiln-c1.md). **Accept**, medium confidence, the practical attraction of native notes, task handoffs, and source search. The system cards are documentation-based judgments, not hands-on trials; several supporting observations come through the initial memo, so agreement is not independent efficacy evidence.

**Decline** turning the measurement caution into a universal deployment gate. Consequential deployment decisions deserve evidence, but cheap reversible exploration should not recreate the package loop. Correct outcomes, stale-state errors, and maintenance are decision criteria rather than mandatory machinery.

Kiln completed two small card corrections: native auto-memory is not necessarily repo-versioned with CLAUDE.md; hosted and self-hosted services have different operational obligations. Kiln also accepted measurement as a default expectation rather than a universal deployment gate. These refinements preserve the main opinion. Receipt acknowledged directly; future wake-backs use explicit `AGENTDECK_PROFILE=campaign4` to avoid the ambiguous Tern name.

## Cairn: procedures with outcome checks and environment identity

[Reading received](reading/c1-procedural-memory.md). **Accept**, medium confidence as a design bet: connect a reusable procedure to its outcome check and the environment in which it worked, then check relevant prerequisites when applying it. This makes the leading recommendation more concrete without choosing executable skills over conditional runbooks or episode reconstruction. Historical success supports applicability; it does not establish it now. **Reject** the claims that checking is costless, that an exit code necessarily verifies the intended outcome, or that this is the only mechanism compatible with our evidence.

**Scope corrections that affect conclusions:** R53 was a ceiling result (all conditions succeeded), not a case of procedure application failing. It cannot be pooled with Gen45's unused control machinery into one failure mechanism. [A-MEM](https://arxiv.org/abs/2502.12110) describes evolving note representations; that alone establishes neither erasure of raw history nor our specific late-history-corruption failure. [GateMem](https://arxiv.org/abs/2606.18829) studies access/deletion governance; authorization scope is not by itself evidence of concurrent scoped factual truth. [Supersede](https://arxiv.org/abs/2606.27472) supplies a relevant fact-update warning, with low–medium confidence in procedural transfer, not high-confidence evidence on Brian's work.

**Reading priority accepted, endpoint corrected:** [LongMemEval-V2 / AgentRunbook-C](https://arxiv.org/abs/2605.12493) gathers evidence for questions about environment experience. It does not directly demonstrate avoided procedural re-learning in live work. Tern checked these primary abstracts, plus [Reflexion](https://arxiv.org/abs/2303.11366), which can use external feedback, and [Voyager](https://arxiv.org/abs/2305.16291), whose domain is Minecraft. Executable code versus prose does not establish checked versus unchecked learning.

The original signed piece remains intact. These are synthesis boundaries, not a request for a repair or another review round. All three panel contributions are now received. Future Cairn commissions use the write-first practice in [ROLES](ROLES.md); Claude's lane repair is operationally reported, not independently tested here.

## Required roadmap follow-up

Both roadmap files were sent to all three panelists in the [next commission](panel-roadmap-commission.md), with explicit profile routing. Corvid and Kiln's follow-ups are received. Cairn's received procedure piece includes the useful partial lifecycle notes; the broad sweep was superseded by the priority steering, not left as a second outstanding assignment.

**Corvid ([addendum](opinions/corvid-c1-roadmap.md)): accept** the history-plus-on-demand-retrieval rival and the point that decomposition alone does not justify five persistent components. Product choice and architecture shape are coupled. The memo now explicitly keeps read-time reconstruction open. **Agree** that Gen45 did not test the full five-layer stack. **Keep open** when maintained state or synthesis earns its cost; no rerun released. One numerical correction matters to reading the cost claim: Gen45's roughly 1.1 MB in its T3 table is cumulative request bytes for a run, not bytes per request; its mechanism example ends at about 4 KB per request. Our map/memo use the primary report and do not repeat the mistaken unit. This does not change the dissent.

**Kiln ([addendum](opinions/kiln-c1-roadmap.md)): accept** the watch-list as mechanism-based reading, not winners. **Reject** blanket Phase-D admission before exploratory evaluation: the current charter supersedes the historical execution sequence, and Prove is only for Brian-approved consequential decisions. The simple baseline is a recommendation, not something this survey deployed. Gen45 is not a pi-lcm-versus-OM evaluation, and existing Phase-E evidence is limited, not nonexistent. These limits keep the practical opinion without importing an audit queue or overstating its empirical basis.

The role record now carries Brian's assignments: Kiln = Muse Spark 1.3 contributor (Go); Cairn = local Qwen3.8 Flash-Next on Halogen (free). These are sponsor-reported operational assignments, not retrospectively inferred run identities.

## Brian's Q1 answer: procedures first, preferences second

The [priority steering](panel-priority-steering.md) reached all three panelists and replaces unfinished broad reading rather than adding another audit chain. Q1 is answered by Brian; the proposed exercise to discover his ranking is withdrawn. [Principles](inputs/BRIAN-PRINCIPLES.md) now lead the memo, and artifacts/executive reasoning are explicit cross-cutting roles in the map.

**Corvid ([priority opinion](opinions/corvid-c1-priorities.md)): accept** artifact grounding and environment churn as axes of the runbook-versus-episode choice. **Keep open** episodic reconstruction for novel or changed conditions. **Disagree**, medium confidence, that reconstructing from raw episodes should be the default for stable repeated procedures: re-inference itself may recreate the cost Brian wants removed. Runbooks need not be state-free; they can expose prerequisites and branches. A source-linked reusable procedure plus history-backed exception handling is my current bet, not a proven winner.

**Kiln ([priority opinion](opinions/kiln-c1-priorities.md)): accept** executable skills for stable, checkable operations and a small scoped preference surface. **Keep open** authoring/maintenance economics versus plain runbooks; cheapest use is not established by these documentation-based opinions. **Reject** “zero authoring cost” as a general claim about automatic extraction: supervision, correction, integration, and review can shift rather than disappear. **Reject again** the universal Phase-D prerequisite. The charter permits proportionate exploration; no experiment or installation was released.

**Cairn:** received and synthesized above. The outcome-check/environment idea sharpens Q3. Priority remains procedures first, preferences second; abstract-level reading does not settle the representation choice or justify a new experimental queue.
