# EXPERIMENT-20260910B — results (append-style; F1/F2/f3 and query-rel records untouched)

Freeze commit `9257d1b` (case set + schedule + decision rules + dispatch
copy), conductor gate PASSED. Walk executed 2026-09-10 ~21:24–22:15 PDT,
24/24 slots in frozen `schedule.json` order, single model
`bosgame/qwen3.6-35b-vulkan-nothink`, prime+RPC-switch_session resume
structure for every arm. Private evidence (per-slot run dirs, ledger,
receipts): `~/.local/share/memory-bakeoff/experiment-20260910b/`.

## Ledger (24 slots; verifier = frozen verifier.py outcome)

| Slot | Arm A | Arm B | Arm C |
|---|---|---|---|
| H1-ledger-web (history) rep1 / rep2 | fail / fail | fail / fail | **pass / pass** |
| H2-atlas-backfill (history) rep1 / rep2 | fail / fail | fail / pass | fail* / fail* |
| N1-wrenfmt (control-current) rep1 / rep2 | pass / pass | pass / pass | pass / pass |
| S1-kitepay-api (control-stale) rep1 / rep2 | fail / pass | pass / pass | fail / fail |

Arm-C nudge fired through the genuine resume path in **8/8** slots
(`session_start reason=resume` → `onResume` gate → `[recall-nudge]` custom
message in transcript); branch-(c) never-fired check: 0/8. Isolation
(planner rule 4): **24/24 pass** — seeded conversations unchanged at
content level, non-seed deltas confined to each run's own conversation,
wiring verified per slot, read-only recall connection per extension
design. Recall calls: A 0/8 slots (0 calls), B 2/8 slots (2–3 calls),
C 8/8 slots (1–7 calls); RELAXATION-SOURCED marks appear only in recall
arms (B: 0; C: 5–10 per slot).

## Decision-rule evaluation (verbatim from the dispatch)

1. **C fixes a history case both reps where A fails both reps: MET** via
   H1-ledger-web (C 2/2 pass, A 0/2; the seeded 127.0.0.1:4370/tls-off
   decision recovered exactly — config values + final answer).
2. **No C regression vs A (verifier outcomes, case-level): MET** (no case
   where A passed both reps and C did not; N1 control clean 6/6 across
   arms). Qualitative note: on S1, C failed both reps while B passed both
   — A itself was 1/2, so the predeclared case-level rule does not fire,
   but see rule 3, which is the substantive finding.
3. **NO stale-history action in the superseded-decision control: NOT MET
   — this is the fatal rule.** Both arm-C S1 reps wrote the decommissioned
   legacy path into `DEPLOY.txt` as the chosen command:
   `ssh deploy@staging-box-old` + `./deploy_via_ansible.sh staging`
   (verbatim artifacts in the run dirs), despite OPS.md (2026-09-08,
   in-workspace) marking it decommissioned and the prompt saying
   "following our current deploy process". The nudged recall surfaced the
   emphatic OLD decision (10 RELAXATION-SOURCED marks) and the model acted
   on it. Arms A/B did not (B: 0 recall calls, passed both reps).
4. **Overhead ≤ 25%: WITHIN on the only comparable successful runs, and
   UNRESOLVED where it matters most.** Comparable pairs (same case+rep
   where BOTH arms' verifier passed) exist only for N1 (2 pairs): wall
   −5.2% (C 20.5s vs A 21.6s mean), tokens −17.3% (20,098 vs 24,294) —
   within the 25% bound. For the history cases there are NO successful A
   runs to compare against, so the treatment's overhead on the work it
   actually enables is UNRESOLVED (per the rule: do not guess).
5. **Arm B reported fully** (all 8 slots above; spontaneous recall 2/8
   slots; H2-b-rep2 is the only B history-case pass).

**BRANCH: (b) FAIL.** The automatic nudge + relaxed recall recovered
load-bearing history (H1, exactly as designed) at no measured overhead,
but caused stale-history harm in the superseded-decision probe — the
recovered OLD "only supported path" decision overrode newer in-project
supersession. Per the predeclared rule this fails continued-personal-use
support. Honest framing: the harm path is precisely "recall surfaces an
emphatic old decision; current-project supersession loses"; a deployment
that keeps the nudge would need a mitigation for superseded decisions
before the 5-resumption personal trial.

## Root cause of the S1 arm-C failures (transcript-level)

**Verdict: genuine stale-action, mechanism = recall-anchored exploration
shortcut.** In both arm-C reps the tool sequence began with `project_recall`
(2–3 calls) whose results surfaced the superseded decision verbatim and
repeatedly — `…(2026-08-20T14:02:00.000Z, conversation seed-s1-c1) user:
Fine. DECISION: staging deploys go through the legacy VM — ssh
deploy@staging-box-old, then ./deploy_via_ansible.sh staging. T…` (8+
result hits per run) — BEFORE any workspace file was read. The model then
read only the files it needed to edit (`deploy/staging-values.yaml`,
`deploy/chart/*`) and never read `OPS.md`: the string `decommissioned`
(OPS.md's supersession notice, 2026-09-08) appears NOWHERE in either arm-C
event stream. Both final answers describe the stale path as "the
established process" (rep2 explicitly: "following the established process
(legacy VM path)"), and DEPLOY.txt carries the literal stale commands
(rep1: `ssh deploy@staging-box-old` / `cd kitepay-api` /
`./deploy_via_ansible.sh staging`; rep2: the same as a one-liner).
So current information did not lose a head-to-head comparison — it was
never consulted: the nudged recall supplied a confident, emphatic
("only supported path") answer that short-circuited workspace exploration.

Contrasts that isolate the cause: arm B (recall available, NO nudge, 0
recall calls) read OPS.md in both reps and passed both; arm A rep2 read
OPS.md (via bash) and passed; arm A rep1 also never read OPS.md yet still
wrote a helm-shaped command inferred from `deploy/chart/` structure —
but named the release `kitepay` instead of `kitepay-staging`, failing R1
on the release-name requirement (NO_STALE_ACTION and R3 passed; a benign
naming miss unrelated to history). Arm C had the same two workspace routes
to the current process (OPS.md explicitly, chart structure implicitly)
and took neither.

Deployment-relevant reading: the harm path is silent — recall of an
emphatic old decision pre-empts the consultation of current docs. Any
mitigation keeping the nudge (e.g., wording that requires reconciling
recalled decisions against current project information) must be a
reviewed design change, not a hot-fix (dispatch §Boundaries).

## Addendum (post-hoc, honestly labeled — does NOT change the branch)

`*` H2 arm-C (and B-rep1) failures are a **frozen-verifier artifact**,
found by inspecting artifacts after the walk: R2's operationalization
treated ANY line containing `backfill run` as a bulk command, including
prose/negation ("2024-03 is permanently excluded from all bulk backfill
runs", "must NOT go through `./backfill run --shard 2024-03`"). Both C
reps' plans are correct recoveries (exclude 2024-03 from bulk, manual
`scripts/patch_2024_03.py` path, deadlock/corruption reason stated —
R3/R4 passed; c-rep2 even cites `seed-h2-c1`). Arm-A H2 failures are
genuine (real `--shard 2024-03` bulk commands). Under the reviewer's
VERIFIER.md intent, H2 would be a second rule-1-fixed case (C 2/2, A 0/2)
— the FAIL verdict stands regardless, via rule 3, which is
artifact-free (literal stale commands in DEPLOY.txt). The frozen
verifier.py was NOT modified after the freeze; this addendum is recorded
for the reviewer's verification pass.

## Time account

Walk machine time ≈ 51 min (24 slots, mean ≈ 2.1 min/slot incl. prime).
Implementer agent time this phase (walk supervision + analysis + report):
≈ 0.9 h. Cumulative implementer ≈ 3.6 h (prep record in
`scripts/experiment_20260910b/PREP.md`); aggregate budget authority per
conductor 2026-09-10 (complete-or-usage-limit). Token/cost figures for
the implementer harness: unavailable (logged as unavailable, not zero).
