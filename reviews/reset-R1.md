# Reset R1 review — verbatim transcript, as relayed

Provenance: written into this tree by the implementer per the one-writer-per-tree
rule, from the conductor relay `dispatch/review-R1-relay.md` (worker-glm-3,
GLM-5.3-Flash, review pass 1 of 1, reply 2026-09-09 19:34 PDT). Verbatim below,
including the relay transport line wraps. Reviewed commit: a6fb38f53d1edbe5c
5920cb4f4934e69b19c63ec on reset/practical-pi-20260907. Verdict: R1 passes,
no blockers, four non-blocking notes (Note 1 folded into the repair pass).

---

# Reset R1 review — worker-glm-3 (GLM-5.3-Flash)

**Reviewed:** implementation commit `a6fb38f53d1edbe5c5920cb4f4934e69b19c63ec` on `reset/practical-pi-20260907` (pushed; matches `origin/reset/practical-pi-20260907`), base `9dfea2c` (= `origin/main`,
 ref `baseline/pre-reset-9dfea2c`), 11-file scoped diff `9dfea2c..a6fb38f`, `RESET_STATUS.md`, `RESET_PLAN.md` as installed, and the evidence sources cited by the recommendation. Review pass 1 of 1; o
ne targeted recheck will follow only if a repair pass touches the reviewed files. Committing this transcript does not restart review of unchanged implementation files.

## Verdict

**R1 passes. No blockers. Four non-blocking notes, of which Note 1 should be folded into the repair pass or carried explicitly into R2.** The recommendation is ready for Brian's single pilot-scope dec
ision.

## (a) Does the question serve Brian's workflow? — Yes

The selected gap — a new session in the same project cannot read any prior session despite lossless per-project storage — is a real structural gap for a solo developer resuming coding work, and I veri
fied it in code, not just prose: every search path in pi-lcm is conversation-scoped (`src/db/store.ts:227-233` `searchFts5` joins `m.conversation_id = ?`; `:300-304` `searchSummaries` filters `convers
ation_id = ? AND text LIKE ?`; `src/tools/lcm-grep.ts:56-96` passes `getConversationId()` to every search — its "all past messages" wording means all messages *within this conversation*). The four pla
n §5 example cases all require crossing exactly this boundary. The response is proportionate: one read-only tool over an existing store, no new model, no cloud, retain-Pi-LCM is the pre-registered acc
eptable outcome.

## (b) Are the evidence and inventory accurately represented? — Yes

Every load-bearing figure I checked matches its source:

- Co-return of superseded records, mechanism divergence, and Hit@3 perseus 0.434 / mem0 0.419 / bm25 0.226 (both engines below 44% absolute on dynamic conflict): `DECISION_MEMO.md` rows 1–3 and `resea
rch/MEMCONFLICT_GEN38_FULL_RELEASE.md` agree exactly.
- agentmemory 92.9% false supersession (418/450): `STATUS_AND_FINDINGS.md` lines 43/164/178.
- No runnable StateMem/MemStrata: `research/PHASE2_CANDIDATE_INTAKE.md` lines 192/195 ("CANNOT ADMIT" / "NOT LOCATED").
- Gen45 negative result, Gen49 null, and Gen50's "no case required anything that had aged out of the window": `RESULTS.md` lines 298–329/366–379 and `research/PI_FAILURE_AUDIT_GEN50.md` line 90. The G
en124 stale-recall risk is correctly cited as exploratory-permanent (`research/EVIDENCE_LANES.md` line 49) and the pilot measures it as a harm column rather than assuming it away.
- "No pinned seed" for qwen sampling: `RESULTS.md` line 279.
- Known-failure reconciliation in AGENTS.md matches `tests/KNOWN_FAILURES.json` totals (1557/26/3/5; clusters 8+16+5+2).
- The two Gen125 supersessions in `handoff/CODEX_TO_CHATGPT.md` quote the original lines verbatim (lines 83–84), keep the original account below, and the corrections themselves are source-backed (Gen3
8 release; `results/BASELINE_FINDINGS.md` anchors bm25/dense_lsa/hybrid_rrf).

Caveat discipline is preserved throughout: Gen38 stays a retrieval-lane result, configuration-scoped findings stay configuration-scoped, and no universal ranking is claimed.

## (c) Can the named implementation fit the R2 budget? — Yes, with one spec correction

One TypeScript extension, a separate read-only SQLite connection, and ≤16 eight-minute runs (≤128 min) fit comfortably in the 4.5-hour stage. The live configuration row is accurate against the host: P
i 0.84.4 (`pi --version`), `defaultProvider` bosgame / `qwen3.6-35b-vulkan-nothink`, pi-lcm 0.1.3 @ `work-main` `1c582c4`, compaction `fast`/`npu-summarise`, prewarm flags, `minMessagesForCompaction:
15`, `defaultThinkingLevel: high` — all confirmed in `~/.pi/agent/settings.json`; the store path (`src/utils.ts:25` sha256(cwd)[:16], `src/config.ts:47`) and WAL mode (`src/db/connection.ts:36`, suppo
rting the concurrent-reader claim) are confirmed in source; hostname `strix-halo` matches the "Strix host" identification; `@sinclair/typebox` is present.

**Note 1 (should-fix, non-blocking): the spec says the extension opens the store "via `bun:sqlite` (built-in)", but Pi runs under node** — `/var/home/bmosher/.bun/bin/pi` is `#!/usr/bin/env node`, and
 pi-lcm itself selects `node:sqlite or bun:sqlite, whichever the runtime has` (commit `d92bc66`). Written as specified, the extension fails to load its driver at the first smoke test. Consequence for
the decision: none — the fix is copying pi-lcm's existing driver-selection pattern, "no new dependencies" stays true, and the budget is unaffected. Correct the wording in RESET_STATUS.md during the re
pair pass, or carry it as the first R2 smoke-test expectation.

## (d) Could the proposed validation reveal failure? — Yes

The unit negative control (no fabrication on empty match) and positive control (hit from a *prior* conversation found), the feature-active/original-path-works checks, and the 16-run paired comparison
with a stale/wrong-scope harm column can each produce failure, ambiguity, or null results; ambiguous stays ambiguous; the null outcome is explicitly acceptable. Cases are selected before treatment out
comes are observed, and transcript seeding is one-time, checksummed, and recorded separately from run rows — compliant with plan §5.

## Process constraints verified

- **PENDING.json:** provenance fields preserved; `status: paused` with `paused_at`/`paused_reason`; the prior status was `answered`, so the plan's commit-the-pause-first conditional never triggered —
one commit is correct.
- **Hooks, no bypass:** `core.hooksPath` is wired to `.githooks` — the hook file's own documented install step — so the pre-commit hook was active for this commit. The hook blocks only on `status == "
awaiting"` (`.githooks/pre-commit` line 13), so `paused` passes by design. The test-vocabulary extension is the plan-mandated truthful state, and scheduler semantics (trigger on `awaiting` only) are u
nchanged.
- **Test claim reproduced:** I independently ran the three named files: **24 passed, 1 skipped** — exact match.
- **R0 containment reproduced:** plan §3's systemctl/ps filters return nothing on this host — no project units, unit files, timers, or processes.
- **Base reconciliation:** `origin/main` is exactly 4 commits past the plan's reviewed `5d1d6a0`, each correctly characterized in the RESET_PLAN.md header (memo; long-context null built-not-run; stale
-use penalty built-not-applied; MemConflict materialisation). RESET_PLAN.md is installed verbatim below a clearly marked header. The patch deliverable matches the commit's file set.

## Non-blocking notes (2–4)

2. **Configuration completeness (cosmetic):** the "complete evaluated configuration" row omits `debugMode: true` and the Pi native compaction token values (reserveTokens 65536 / keepRecentTokens 19660
 — "unchanged" is true but the values are unstated). Both arms are identical either way.
3. **AGENTS.md phrasing (cosmetic):** "16+5 absent MemConflict dataset" merges two distinct clusters (`memconflict_dataset_absent` 16 failures, `memconflict_collection_errors` 5 errors); both are data
set-absence-caused and the linked file is authoritative.
4. **Ecological validity (carry into R2 reporting):** recall opportunities come from prepared, checksummed transcripts rather than Brian's real saved sessions — plan-compliant, but the R2 results page
 should restate this as a limitation when interpreting the pilot.

## Resource accounting (for the status table)

Reviewer session: dispatch-to-reply 2026-09-09, ≤0.9 h (reply 19:34 PDT; dispatch postdates the implementer's 18:36 commit). Combined R0+R1 implementer (≈0.5 h) + reviewer (≤0.9 h) ≈ ≤1.4 h against th
e 2.5 h aggregate ceiling. No experiment machine time; token/cost figures unavailable in this harness.

**Recommendation to the conductor:** relay the pass verdict and Note 1 to the implementer; after any repair commit (or with notes carried, if the implementer elects no repair), I will run the one targ
eted recheck, and then this deliverable goes to Brian for the pilot-scope decision.