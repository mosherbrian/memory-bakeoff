# Reading note c77 — Pi compaction: what survives summarization, and does anything vanish silently?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 77.**
Skeleton first; **requirements 2/4**, one current Pi compaction path, **repository revision
pinned**. Distinguish **system instructions** from **conversation summaries/tool messages**. Do
canonical instructions (AGENTS/CLAUDE, system prompt) survive or reload **independently of
summarization**? What is retained, and what can disappear **without an explicit notice**? Trace
the automatic trigger and request failure/overflow handling, bounded to relevant files/tests. No
universal all-history preservation claim; a stored transcript is not delivered context. Narrow
2/4 rating; stop at a **named unresolved call site** rather than widen the audit. No
model/runtime calls, no probe/install/whole-repo audit. Prior card:
systems/pi-instruction-delivery.md (reload correction carried); old v0.87.1 findings do not
establish moving-main or Brian-installed behavior.

*(trace + rating appended below)*

## Pinned

**badlogic/pi-mono @ `2b0a123de98318c2ff8069661721ce0c3794c34e` (26 Sep 2026).** Files:
`packages/coding-agent/src/core/compaction/compaction.ts`, `core/agent-session.ts` (+ named
tests). Moving main; not Brian's installed version.

## Instructions vs summaries: structurally separate

Compaction rewrites **conversation entries** (messages, tool results) into a structured summary
entry. The **system prompt is rebuilt per request** — `agent-session.ts` calls
`buildSystemPrompt`/`buildSystemPromptSections` and keeps "session.systemPrompt and
ctx.getSystemPrompt() in step with what the provider sees." Canonical instructions are therefore
**never inputs to summarization and are re-supplied after compaction**; they survive independently
of it. (File discovery/loading of AGENTS/CLAUDE is Kiln's cell, not claimed here.)

## Trigger and overflow path

**Threshold:** `shouldCompact: contextTokens > contextWindow − reserveTokens` (default
`reserveTokens: 16384`; settings can disable). **Overflow:** provider errors detected via
`isContextOverflow` and "recoverable length" stops route into compaction with a **single recovery
attempt** (`_overflowRecoveryAttempted`); retry logic explicitly excludes overflow ("handled by
compaction, not retry"). Same-model guard: overflow from a different model skips recovery.
Events `compaction_start {manual|threshold|overflow}` are surfaced.

## Retained / can vanish / notices

**Retained:** the full transcript persists in session files; the summary entry is visible in UI.
**Vanishes from delivered context:** full text of everything before the cut point — replaced by
the LLM summary. The summarization prompt commands "PRESERVE exact file paths, function names,
error messages" — an **instruction, not an enforceable guarantee**. **Notices:** event-level yes
(compaction visible; a capped summary is labeled "generation hit the token cap and the summary is
incomplete"); **detail-level no** — nothing itemizes which specifics were lost. No
all-history-preservation claim: stored transcript ≠ delivered context.

**Named unresolved call site (stopping here):** whether the produced summary entry is
re-validated against the request budget before the next provider call —
`prepareCompaction` estimates; the re-check in the send path was not traced.

## Requirements 2/4 — narrow ratings

**Req 4 (compaction path): yes, narrow** — canonical instructions reload per request, immune to
summarization by construction.
**Req 2: partial** — compaction is a **recovery mechanism, not a rejection mechanism**: it
converts overflow into lossy summarization to keep requests within the window. It guarantees the
request **fits**, not that intended content **survives**; silent at detail level. Exact missing
boundary: content-membership assurance across compaction (nothing checks a needed item is in the
summary or the kept tail).

**Confidence: high on separation/trigger/overflow facts (direct pinned source), high on
instruction-vs-guarantee reading of PRESERVE prompts, medium on summary re-validation being
absent (unresolved call site, stated).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, CAPABILITY-MATRIX.md,
RECOMMENDED-DESIGN.md, panel-response-c76.md.