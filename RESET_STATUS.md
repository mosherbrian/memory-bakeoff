# Reset status — the one current decision page

**Reset branch:** `reset/practical-pi-20260907` · **Base:** `9dfea2c` ·
**Governing instruction:** [RESET_PLAN.md](RESET_PLAN.md)
**Page owner:** replacement implementer (GLM-5.3 under ZCode, this reset's recorded substitution).
**Reviewer:** GLM-5.3-Flash in `worker-glm-3` (plan §1 fallback, recorded substitution).

Older status documents ([STATUS_AND_FINDINGS.md](STATUS_AND_FINDINGS.md),
[CODEX_HANDOFF.md](CODEX_HANDOFF.md), [handoff/CODEX_TO_CHATGPT.md](handoff/CODEX_TO_CHATGPT.md),
[RESULTS.md](RESULTS.md)) are historical from the reset's start. This page owns
current next actions and resource use.

---

## Recommendation (for Brian's one pilot-scope decision)

**Retain Pi-LCM as the substrate and test exactly one addition: a read-only
cross-session recall tool over the project's existing pi-lcm store.** If the
pilot does not show a practical gain, retaining Pi-LCM alone is the expected
good outcome.

**What Pi-LCM already provides.** Brian's live setup runs Pi 0.84.4 with
pi-lcm 0.1.3 (`/var/home/bmosher/projects/pi-lcm-bun`, `work-main` @ `1c582c4`).
Every message is persisted losslessly to a per-project SQLite database
(`~/.pi/agent/lcm/<sha256(cwd)[:16]>.db`) with an FTS5 index; compaction builds
DAG summaries on a small local model (`fast`/`npu-summarise`) with pre-warming;
and three tools (`lcm_grep`, `lcm_expand`, `lcm_describe`) recover compacted
detail — **within the current conversation only**.

**The gap is structural, not a quality defect.** Every search in the store is
filtered to the current `conversation_id` (`src/db/store.ts` in pi-lcm:
`searchFts5`, `searchSummaries`). A new session in the same project starts
blind to every prior session's messages and summaries, even though they sit in
the same database file. The four workflow cases the reset plan names — resuming
after a session boundary, obeying a revised decision made in an earlier
session, avoiding a documented failed approach, recovering why an alternative
was rejected — all require reading prior sessions in a new one. None is
possible today without manually re-feeding transcripts.

**Why not the other candidate.** A supersession-aware current-state projection
layer (roadmap layer 2) is the other candidate considered. The project's own
evidence argues against building it now: every measured engine co-returns the
superseded record ([DECISION_MEMO.md](DECISION_MEMO.md) row 1), mechanisms
diverge completely (row 2), both measured engines sit below 44% absolute on
dynamic conflict ([research/MEMCONFLICT_GEN38_FULL_RELEASE.md](research/MEMCONFLICT_GEN38_FULL_RELEASE.md)),
agentmemory's write-time supersession falsely retired 92.9% of distinct stress
memories ([STATUS_AND_FINDINGS.md](STATUS_AND_FINDINGS.md)), and the intake
located no runnable StateMem/MemStrata
([research/PHASE2_CANDIDATE_INTAKE.md](research/PHASE2_CANDIDATE_INTAKE.md)).
No locally runnable, evidence-supported implementation exists; it cannot fit
the one-adapter R2 boundary.

**Why recall could change a coding outcome, and what could go wrong.** The
prior Pi pilots measured bounded context composition and a verbatim
instruction floor on short single-session tasks and found no gain
([RESULTS.md](RESULTS.md): Gen45, Gen49); the Gen50 failure audit found no
failure needed aged-out history *within* a session. The session boundary is
the unmeasured family. The known risk is stale recall: raw history contains
superseded values, and the reader may use what it last read (Gen124,
exploratory, [research/EVIDENCE_LANES.md](research/EVIDENCE_LANES.md)). The
pilot therefore returns timestamps and source-session identifiers with every
hit, and scores stale or wrong-scope use as a harm column — the risk is
measured, not assumed away.

**Cost.** One small TypeScript extension, no new model, no cloud calls, fully
local, reversible by removing one line from Pi's `packages` setting. R2
budget: 4.5 aggregate agent-hours, ≤16 eight-minute runs, ≤6h machine
occupancy. Detailed specification below.

---

## Component map

| | |
|---|---|
| **Pi-LCM provides today** | Lossless per-project SQLite store (messages, summaries, FTS5); DAG summarisation on `fast`/`npu-summarise`; pre-warm; within-conversation recovery tools; compaction relief for Pi's native window |
| **The candidate adds** | One read-only tool (`project_recall`) searching `messages` + `summaries` across **all** conversations in the current project's store, each hit annotated with timestamp, session id and session start; env-gated for A/B |
| **Still unmeasured** | Whether real workflow sessions hit the boundary (the pilot's question); stale/wrong-scope harm from recalled history (scored per run); token/latency overhead of recall calls |
| **Why it could change a coding outcome** | A fresh session can retrieve a rejected-approach rationale or a revised decision before re-walking dead ground; today it cannot, structurally |

## Candidates considered (2)

1. **Cross-session project recall adapter — RECOMMENDED.** Smallest reversible
   addition; uses the store that already exists; no new model or service;
   directly targets the selected gap.
2. **Current/scoped-state projection layer — deferred.** No evidence-supported
   locally runnable implementation exists; known false-supersession hazards;
   exceeds the one-adapter boundary. Belongs to a later decision if recall
   shows the boundary matters and stale returns prove costly.

## Selected practical gap

**Targeted historical recall across session boundaries** — one of the plan's
four gap options, not equated with the others. Current/scoped state handling,
procedural reuse and bounded-working-context continuity remain distinct and
are not claimed by this pilot.

---

## R2 pilot specification (exact)

| Item | Value |
|---|---|
| Implementation | New extension `extensions/pi-project-recall/` in this repository (TypeScript Pi package) |
| Entry point | Pi `packages` mechanism — absolute path added to `packages` in `~/.pi/agent/settings.json` (same mechanism that loads pi-lcm); tool `project_recall(query, scope: messages\|summaries\|all, limit?, after?, before?)` |
| Store access | Opens `~/.pi/agent/lcm/<sha256(cwd)[:16]>.db` **read-only** using pi-lcm's driver-selection pattern (`node:sqlite` preferred — Pi 0.84.4 runs under node, Node ≥ 22.19; `bun:sqlite` fallback; pi-lcm `src/db/driver.ts`), separate connection; WAL permits a concurrent reader alongside pi-lcm's writer; zero writes |
| Query | `messages_fts MATCH ?` joined to `messages` **without** the `conversation_id` filter, `ORDER BY m.timestamp DESC LIMIT ?`; summaries via `summaries.text LIKE` as pi-lcm does; every hit carries `conversation_id`, session start, `timestamp` |
| Local dependencies | None beyond the Pi runtime (`node:sqlite` built-in under node; `@sinclair/typebox` already present via pi-lcm peers). No network, no model calls |
| A/B gating | Arm A: `packages` without the extension (bit-identical to today). Arm B: with it. Alternation A,B / B,A across repetitions; `PI_PROJECT_RECALL=0` env override as a second kill switch |
| Rollback | Remove the path from `packages` (or set env override); no store changes to undo — the tool never writes |
| Host | Strix Linux host (this machine, Fedora, linux 7.0.14-101.fc43.x86_64) |
| Coding model | `bosgame/qwen3.6-35b-vulkan-nothink` (Pi `defaultProvider` `bosgame`), local inference only — private-corpus-safe per plan §5 |
| Pi / pi-lcm config | Pi 0.84.4 (`/var/home/bmosher/.bun/bin/pi`, bun runtime); pi-lcm 0.1.3 @ `/var/home/bmosher/projects/pi-lcm-bun` (`work-main` @ `1c582c4`); compaction model `fast`/`npu-summarise`; `prewarm: true`, `prewarmContinuous: false`, `prewarmStableBlock: false`; `minMessagesForCompaction: 15`; Pi native compaction enabled, `reserveTokens: 65536`, `keepRecentTokens: 19660`, `debugMode: true` (verified in `~/.pi/agent/settings.json`; identical in both arms); `defaultThinkingLevel: high`. Nothing else varies between arms |
| Case selection | 4 session-boundary coding-workflow cases selected from existing public repo tasks / recorded material **before** any treatment outcome is observed; ≥2 must present a real recall opportunity. Each case's project store is seeded with a prepared prior-session transcript (one-time preparation, checksummed, recorded separately from run rows) |
| Repetitions / seeds | 2 repetitions per case per arm = **16 runs max**; qwen sampling has no pinned seed (recorded Gen44) — if seeding is unavailable it is recorded, not forced |
| Run ceiling | 8 minutes per run including ordinary memory operations; a timeout is recorded, never retried unbudgeted; partial results preserved |
| Validation commands | `bun test extensions/pi-project-recall/` (unit tests incl. negative control: a query matching nothing returns empty without fabricating; positive control: a known message from a *prior* conversation is found); first smoke expectation per review Note 1: the sqlite driver loads under the actual Pi runtime (node / `node:sqlite`, not bun); one unrelated smoke task before evaluation exposure; feature-active-when-enabled / original-path-works-when-disabled checks per plan §5 |
| Outcome checks | Existing project tests / concrete task artifacts; for memory behaviour, the actual recalled source and trace; model self-report is never the score; ambiguous stays ambiguous |
| Result columns | task ID, arm, repetition, configuration reference, success/failure/ambiguous/timeout, stale or wrong-scope action, supporting receipt/source, human corrections, tool calls, token/usage totals (report unavailable when unavailable), preparation time, run time |
| Resource limits | R2 ceiling 4.5 aggregate agent-hours incl. review; ≤6h experiment machine occupancy; stop rules per RESET_PLAN.md §2 — hard stops |
| Reporting limitation | Recall opportunities come from prepared, checksummed transcripts, not Brian's real saved sessions (plan-compliant; review Note 4) — the R2 results page restates this whenever the pilot is interpreted |

---

## Status

| | |
|---|---|
| **Completed** | R0: legacy launchers verified inactive (no project units/timers/processes; `PENDING.json` was `answered`, now truthfully `paused`); incumbent workspace preserved untouched; isolated clone, origin repointed to GitHub, base reconciled `5d1d6a0` → `9dfea2c`; reset branch + baseline ref created. R1: entry-point repairs on this branch (this page, RESET_PLAN.md, AGENTS.md, control-plane and handoff pointers). R1 review: **PASS, no blockers**, four non-blocking notes (verbatim transcript in [reviews/reset-R1.md](reviews/reset-R1.md)); consolidated repair pass applied — Note 1 driver spec corrected to `node:sqlite`, Note 2 config values stated, Note 3 cluster phrasing split, Note 4 carried as a reporting limitation |
| **Remaining uncertainty** | Whether real sessions hit the recall boundary (pilot's question); one targeted recheck of the repair diff pending |
| **Next action** | Targeted recheck by worker-glm-3 on the repair commit, then Brian's single pilot-scope decision on the recommendation above. R2 does not start without it |
| **Implementer time (cumulative)** | R0 ≈ 0.3 h (session 1, 18:10–18:21: discovery, clone, branch; session 2 re-verification to 18:29). R1 ≈ 0.2 h (18:29–18:38: reading, edits, focused tests, commit). Session 3 ≈ 0.1 h (closeout reconstruction after bridge reset). Repair pass ≈ 0.1 h (review transcript + this diff). Total ≈ 0.7 h against the 2.5 h R0+R1 ceiling |
| **Reviewer time** | ≤ 0.9 h (review pass 1, reply 19:34 PDT, own accounting in [reviews/reset-R1.md](reviews/reset-R1.md)). Targeted recheck pending |
| **Experiment machine time** | 0 h — no experiments run |
| **Token/cost figures** | Unavailable in this harness; logged as unavailable, not zero |
| **Brian attention used** | ≈ 5 min launch (conductor dispatch, estimated); decision minutes not yet spent |

**Substitutions recorded (plan §1):** implementer GLM-5.3 under ZCode
(conductor routing; the plan's Codex default was not used, 2026-09-09);
reviewer GLM-5.3-Flash in `worker-glm-3` (plan §1 fallback, because GLM-5.3
is the implementer).
