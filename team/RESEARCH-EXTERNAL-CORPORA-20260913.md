# EXTERNAL TRANSCRIPT CORPORA FOR THE MEMORY BAKE-OFF
ChatGPT Deep Research report, commissioned by Brian 2026-09-13. Filed verbatim
by GiLMore. Verification status: UNVERIFIED — Alice to check key claims (deep
research reports can fabricate specifics); acquisition gated on Brian's call
for SWE-chat (HF gated access = his account).

## Executive summary

**Yes—there is now enough public material to expand a coding-memory corpus substantially, but the supply is extremely lopsided.** As of September 2026, there are **hundreds of thousands of downloadable, execution-grounded agent-only software-engineering trajectories**, including current releases such as NVIDIA Open-SWE-Traces, Nebius SWE-rebench/OpenHands, SWE-Hero, SWE-smith rollouts, MEnvData-SWE, and MindForge. In contrast, genuinely **real human↔coding-agent histories with corrections, changing requirements, interruptions, and persistent project context remain scarce**. The standout is **SWE-chat**, with 5,851 real coding sessions and raw transcripts; Wisp's Claude Code release is much smaller but unusually authentic and long-form.

For a **memory bake-off**, I would therefore not construct the corpus by simply taking the largest trajectory datasets. That would mostly measure whether a memory system can retain observations from an autonomous benchmark rollout. I would make the benchmark deliberately heterogeneous:

    M[Memory bake-off corpus] --> H[Human longitudinal]
    M --> A[Long-horizon autonomous]
    M --> C[Conversational / correction-heavy]
    M --> X[Cross-session continuity]

    H --> S[SWE-chat]
    H --> W[Wisp Claude Code]
    C --> D[DevGPT]
    A --> MF[MindForge]
    A --> N[Nebius SWE-rebench]
    A --> O[Open-SWE-Traces]
    A --> E[MEnvData-SWE]
    X --> G[Gap: collect opt-in sessions]

The **highest-value first ingestion is SWE-chat**. Raw session transcripts; user prompts; assistant responses and thinking; Read/Write/Edit/Bash and other tool activity; tool results; timestamps; summaries; file-history snapshots; continuations; user messages queued while the agent is busy; commit diffs; files touched; agent-versus-human code attribution; and explicit annotations for user **correction, rejection, failure report, takeover, and requirement change**. The release has 5,851 sessions, 2.69 million transcript rows, and 14,459 linked commits.

Ranked sources: 1. SWE-chat (EXCELLENT) 2. Wisp Claude Code Sessions (EXCELLENT) 3. MindForge-27B (EXCELLENT; mean 181.6 turns / 177K tokens) 4. Nebius SWE-rebench OpenHands (EXCELLENT; 67,074 traces) 5. NVIDIA Open-SWE-Traces (EXCELLENT; 511,668 rows, 42.6 GB) 6. MEnvData-SWE (EXCELLENT; 3,872 traces, 10 languages) 7. SWE-Hero (PROMISING; 34,269) 8. Kwai SWE-smith 66k (PROMISING) 9. DevGPT (PROMISING; 17,913 prompts, no tool traces) 10. SERA (PROMISING; >200K synthetic) 11-16. Nebius SWE-agent, SWE-bench/SWE-smith, SWE-Gym, R2E-Gym, MiMo, OpenSWE (PROMISING) 17. Programming by Chat (LIMITED - raw chats excluded for privacy) 18. SWE-ZERO (LIMITED - execution-free).

## Key findings for memory research

1. **Raw scale is no longer the bottleneck.** 2. **Counts must not be summed as independent** (heavy dataset-family overlap; dedupe by repo/issue/commit). 3. **D-class final-state-only data intentionally absent from high ranks** (patches without history contribute little to memory evaluation).

**SWE-chat fields most valuable for memory research:** user prompts annotated with **correction, rejection, failure report, pacing complaint, takeover and requirement change**; sessions marked as continuations; summaries and file-history snapshots; queued-message behavior — naturally occurring tests of "newer instruction supersedes older instruction," interruption handling, durable-vs-transient distinction. Project-state linkage: branch, files touched, tokens, human-vs-agent attribution; checkpoints connect sessions to commits with full diffs — a benchmark item can ask "what did the project actually become after the user said it?"

**Wisp:** mirrors ~/.claude/projects/ (one dir per project, one JSONL per session) — same format as Brian's own transcripts; good for testing whether a memory system stores an enduring config decision but lets an obsolete process state decay. **MindForge:** best long-context torture test — early black-box discovery must constrain the final implementation dozens/hundreds of turns later while superseded hypotheses must not (evidence accumulation + hypothesis revision). **Nebius SWE-rebench:** 64-turn runs create state dependencies — a memory system that preserves every observation indiscriminately can be HARMED by stale early hypotheses.

**Critical limitation (Programming by Chat):** 11,579 real IDE sessions/74,998 messages/899 developers exist but raw chats excluded for privacy — do not auto-recollect without legal/privacy review.

## Normalization schema (events, not chat turns)

session(session_id, project_id, user_id_pseudonym, source, real_vs_generated, started/ended, parent_session_id, task_or_issue_id)
events[](sequence_id, timestamp, actor[human/assistant/tool/system], event_type[prompt/response/reasoning/tool_call/tool_result/file_snapshot/summary/correction/checkpoint], content, tool_name/input/output, file_path, command, supersedes_event_ids[], state_scope[transient/session/project/user], provenance)
state_changes[](commit/diff, files_touched, test_result, package/config changes)

**Do NOT precompute memory solely as extracted facts** — keep the event stream and derive benchmark annotations separately, or the extraction determines what the memory system is allowed to notice. Preserve **temporal and supersession relations**: a requirement_change should point to the earlier request it supersedes; a package version learned from pyproject.toml should be invalidated if a later edit changes it.

## Corpus gaps (= exactly our design's features)

Cross-session continuity for same human+repo; preference persistence; architecture decisions made once and relied on later; revised requirements; stale facts needing supersession; resumptions after days/weeks; tool/model migrations. Recommendation: **opt-in longitudinal collection** — one developer × one repo × 2-6 weeks, native transcripts, explicit consent, post-collection questionnaire. A few hundred such histories cover dimensions another million SWE-bench rollouts do not.

Also: create **"do not remember" targets** (PIDs, transient test failures, temp paths, intermediate hypotheses) — a bake-off rewarding only successful recall incentivizes over-retention. And **preserve failed/corrected trajectories**, not just successes.

Score separately on **retention, update/supersession, scope, temporal validity, provenance** — never one aggregate score.

## Acquisition plan (A-H): SWE-chat anchor (1-3 days, up to 5,851 real sessions, gated HF+ODC-BY, repseudonymize identities) -> Wisp (0.5-1 day, MIT, second PII pass) -> MindForge (<1 day, MIT, 1,001 traces) -> Nebius SWE-rebench (2 days, CC BY, keep failures, sample 5-15K) -> MEnvData (<1 day, Apache-2.0, polyglot) -> Open-SWE-Traces reservoir (2-4 days incl. dedup) -> DevGPT (1-2 days, human-dialogue items) -> scale corpora last. Target: all scarce real-human sources, all 1,001 MindForge traces, several thousand MEnv traces, stratified samples from the big execution corpora.
