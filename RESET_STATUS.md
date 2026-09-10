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

## R2 result (recorded 2026-09-09 ≈23:00 PDT / 2026-09-10 UTC)

**Recommendation per RESET_PLAN.md §6: retain the baseline (Pi-LCM alone).**
No predeclared practical failure was fixed by arm B in any repetition, which
fails the "limited personal trial" rule at its first condition. The extension
itself is sound and reversible and stays in the repository at
`extensions/pi-project-recall/` — installing it remains a one-line `packages`
entry if Brian ever wants it, and removing it undoes everything.

**What happened.** All 16 evaluation runs (4 cases × 2 arms × 2 repetitions,
8-minute ceiling, none timed out — median 31 s) completed, except c2-B-rep1,
which I interrupted myself during a containment check that proved negative
(details below). Outcome by case: c1 — the strong recall opportunity — failed
its hidden requirement (telemetry display stability) in **all four runs, both
arms**: the model set the shared `STEPS_PER_MM` constant to 8 everywhere,
exactly the predeclared practical failure, even though the prior session in
its store contained the split-constant decision verbatim. c2, c3, c4 passed
in every completed run; c4's stale-harm probe never fired (upper bound stayed
100 everywhere). The decisive fact: **`project_recall` was invoked in 0 of 8
treatment runs.** The coding model (qwen3.6-35b-vulkan-nothink) treats a
natural "returning to this project after a break" prompt as self-contained;
it never searches prior sessions, so arm B's information state equalled arm
A's in every run. The tool was verifiably present and active (registration on
the real Pi runtime, node:sqlite driver; ≈ +1 k input tokens of tool schema),
cost ~3 % median wall overhead, wrote nothing, and misled no one.

**Overhead.** Over the 7 pairs where both runs completed (any verdict):
median wall A 31.2 s → B 32.2 s (+2.9 %); median total tokens A 38 070 →
B 34 148 (−10 %). On the plan's threshold basis — the 5 pairs where both
runs **passed** (c1 excluded) — median wall 29.2 s → 32.2 s (+10.3 %) and
median tokens 31 529 → 33 301 (+5.6 %). Both bases sit far inside the
accepted 25 % threshold; the differences are labelled noise (no seed, small
samples, and B's tool never executed), not savings. The cost comparison
passes but is moot given the null outcome.

**Run table** (verifier requirement labels: A/B; c1 requirement A passed in
all runs — the assertion order proves it — requirement B is the failure).
Full per-run rows with tool calls, usage, receipts and the recall traces:
`~/.local/share/memory-bakeoff/reset-20260907/r2/ANALYSIS.json` (private);
harness: `scripts/run_pi_pilot_r2.py`, analysis: `scripts/r2_pilot/analyze.py`.

| Run | Arm | Verdict | Wall s | Tokens | recall calls |
|---|---|---|---:|---:|---:|
| c1-a-rep1 | A | fail (req B) | 31.2 | 38 786 | – |
| c1-b-rep1 | B | fail (req B) | 29.9 | 39 832 | 0 |
| c1-a-rep2 | A | fail (req B) | 32.9 | 42 663 | – |
| c1-b-rep2 | B | fail (req B) | 34.7 | 70 988 | 0 |
| c2-a-rep1 | A | pass | 25.2 | 27 789 | – |
| c2-b-rep1 | B | **interrupted** (experimenter stop; partial preserved, not restarted — cap slot spent) | – | – | – |
| c2-b-rep2 | B | pass | 32.4 | 34 148 | 0 |
| c2-a-rep2 | A | pass | 27.8 | 28 778 | – |
| c3-a-rep1 | A | pass | 33.6 | 38 070 | – |
| c3-b-rep1 | B | pass | 32.2 | 33 301 | 0 |
| c3-a-rep2 | A | pass | 34.4 | 38 169 | – |
| c3-b-rep2 | B | pass | 35.8 | 40 155 | 0 |
| c4-a-rep1 | A | pass | 29.2 | 31 529 | – |
| c4-b-rep1 | B | pass | 27.5 | 26 350 | 0 |
| c4-b-rep2 | B | pass | 25.5 | 25 821 | 0 |
| c4-a-rep2 | A | pass | 12.9 | 11 053 | – |

**Limitations, recorded plainly.**

1. **c2-B-rep1 hole.** I stopped the walk mid-run on a suspected
   cross-run-contamination signal that the audit disproved (0 out-of-worktree
   accesses in every run; the alarming-looking `find` started at the run's own
   worktree). The slot was spent and not restarted, so c2's rep-1 pair is
   missing and the overhead medians rest on 6 pairs.
2. **pi-lcm config fidelity.** pi-lcm resolves its settings from
   `homedir()/.pi/agent/settings.json` and ignores `PI_CODING_AGENT_DIR`, so
   under the isolated harness both arms ran pi-lcm with **defaults**, not
   Brian's tuned values; persistence changed shape rather than going inert —
   each run wrote its own conversation to a UUID-named database inside
   `LCM_DB_DIR` instead of the cwd-hash-named file of the daily setup
   (verified post-hoc: every run dir holds the seeded cwd-hash file,
   untouched, plus one UUID file carrying that run's messages). `lcm_grep`
   therefore saw only the live conversation — the c4-b-rep1 trace shows
   exactly that — and the seeded prior sessions were reachable only through
   `project_recall`. Both arms were affected identically, so the A/B
   comparison is internally valid, but arm A was "pi-lcm present, persistence
   reshaped", not the full daily interactive behaviour; compaction never
   became reachable in either arm.
3. **Synthetic recall opportunities** (prepared, checksummed transcripts —
   `PREP_MANIFEST.json`, private), not Brian's real saved sessions; carried
   review Note 4 restated here.
4. **One coding model, no seeds** (qwen sampling seed unavailable, recorded),
   8 treatment runs; the null is about *unprompted spontaneous* tool use with
   natural resume prompts. An explicit "check past sessions first" habit is a
   different usage pattern — plausible, unmeasured, and the natural next
   thing for Brian to try by hand before any further budget.

---

## Status

| | |
|---|---|
| **Completed** | R0: legacy launchers verified inactive (no project units/timers/processes; `PENDING.json` was `answered`, now truthfully `paused`); incumbent workspace preserved untouched; isolated clone, origin repointed to GitHub, base reconciled `5d1d6a0` → `9dfea2c`; reset branch + baseline ref created. R1: entry-point repairs on this branch (this page, RESET_PLAN.md, AGENTS.md, control-plane and handoff pointers). R1 review: **PASS, no blockers**, four non-blocking notes (verbatim transcript in [reviews/reset-R1.md](reviews/reset-R1.md)); consolidated repair pass applied — Note 1 driver spec corrected to `node:sqlite`, Note 2 config values stated, Note 3 cluster phrasing split, Note 4 carried as a reporting limitation. **R2: implemented, validated and run** — `extensions/pi-project-recall/` (12/12 bun unit tests, 7/7 node-runtime driver smoke, registration verified on the real Pi 0.84.4 runtime under node:sqlite, feature-active/disabled smoke checks passed) plus the 16-slot paired pilot above |
| **Remaining uncertainty** | Whether an explicitly prompted "check past sessions" usage pattern (unmeasured) would change the model's behaviour; whether a different coding model would use the tool spontaneously |
| **Decision recorded** | **Brian approved the R2 pilot as specified on 2026-09-09 ~20:55 PDT** (relayed by conductor-glm), with the **default 25% overhead threshold** for the R3 trial decision per RESET_PLAN.md §6: 25% for median run time and available token usage over paired successful runs; unavailable or insufficient cost comparisons are labelled unresolved, not passed |
| **Next action** | R3: conductor dispatches the result review to worker-glm-3 (GLM-5.3-Flash) against the R2 commits and result table; then Brian's final adopt / retain / unresolved decision per §6 |
| **Implementer time (cumulative)** | R0 ≈ 0.3 h · R1 ≈ 0.2 h · session 3 closeout ≈ 0.1 h · repair pass ≈ 0.1 h. R2 ≈ 0.8 h (reflog-dated commits 22:26–23:01 PDT ≈ 0.6 h: extension, harness, cases, smokes, 16-run walk, containment audit, analysis, result page; plus ≈ 0.2 h post-result verification and accuracy repairs). Total ≈ 1.5 h. R2 ceiling 4.5 h aggregate (incl. review) — not reached |
| **Reviewer time** | ≤ 0.9 h R1 (review + recheck, [reviews/reset-R1.md](reviews/reset-R1.md)). R3 review pending within its own 1.0 h stage ceiling |
| **Experiment machine time** | ≈ 0.2 h (2 smoke runs + 16 evaluation walk slots, sum of wall times ≈ 8 min 20 s; local llama-swap server was already running and is not counted) |
| **Token/cost figures** | Per-run usage totals available and recorded in the private ledger (`r2/ledger.jsonl`, `ANALYSIS.json`); model inference cost $0 (local server); implementer-harness token/cost figures unavailable in this harness, logged as unavailable, not zero |
| **Brian attention used** | ≈ 5 min launch (conductor dispatch, estimated); R1 pilot-scope decision spent 2026-09-09 ~20:55 PDT (approval + default threshold); final-decision minutes remain |

**Substitutions recorded (plan §1):** implementer GLM-5.3 under ZCode
(conductor routing; the plan's Codex default was not used, 2026-09-09);
reviewer GLM-5.3-Flash in `worker-glm-3` (plan §1 fallback, because GLM-5.3
is the implementer).
