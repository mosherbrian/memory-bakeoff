# EXPERIMENT-20260910B — implementer prep record (pre-freeze)

Status of the harness work required by `dispatch/EXPERIMENT-20260910B.md`
before any evaluation slot runs. Cases are NOT yet delivered by the reviewer
(worker-glm-3); nothing here freezes the case set. Evaluation does not start
until the reviewer-authored cases + the generated `schedule.json` + this
harness are committed together (the freeze commit), per the dispatch's
freezing-discipline section.

## What exists after this prep

| Piece | Where | Notes |
|---|---|---|
| Harness | `run_b.py` | 3 arms (A pi-lcm only; B +recall; C +recall+nudge), 24 slots = 4 cases x 2 reps x 3 arms, prime+resume session structure for genuine `session_start reason=resume`, per-slot ledger under the private dir. Reuses `scripts/run_pi_pilot_r2.py` machinery read-only (frozen F1/F2 code). |
| RPC resume driver | `rpc_task.mjs` | The task invocation for ALL arms. **Finding:** plain `pi --print --session <file>` opens the session but reports `session_start reason "startup"` (pi 0.84.2 CLI initial-runtime default), which cannot arm the nudge gate — verified by the failed prep smoke of 2026-09-11T04:03Z. The RPC protocol's `switch_session` command goes through `AgentSessionRuntime.switchSession` and emits a REAL `reason "resume"` (pi `dist/core/agent-session-runtime.js:141`) — the same runtime path the deck uses on reconnect. The driver spawns `pi --mode rpc --session <file>`, switches session (genuine resume), sends the task prompt, and records the full event stream. |
| Case contract | `cases/README.md` | The reviewer authors `case.json` / `seed_transcript.json` / `repo/` / `verifier.py` per case; hidden requirements live only in seeded history + verifier. |
| Randomization | `build_schedule` in `run_b.py` | Deterministic `random.Random(20260910)`, shuffles [A,B,C] within each case/rep block (8 blocks). Determinism + coverage unit-checked at prep time. `schedule --write` persists `schedule.json` for the freeze commit once case ids exist. |
| Smoke seed | `smoke_seed.json` | Seeded prior-session note carrying marker `SMOKE-B-7f3b` (seed conversation id `seed-smoke-prior`) for the pair-smoke reachability check. |
| Pair smoke | `smoke --out DIR` | ONE pre-evaluation run of the full extension PAIR under daily-like settings: arm C packages (pi-lcm + pi-project-recall + pi-recall-nudge) via the isolated agent dir, pi-lcm ACTIVE (normal writes), genuine prime(fresh)+task(RPC `switch_session` resume) path. Writes `SMOKE_RECEIPT.txt` plus a deterministic reachability probe (the task run's own recall results are recorded as model-dependent observables, not gates). Receipt for this prep: `EXPERIMENT_B_PRIVATE` default `~/.local/share/memory-bakeoff/experiment-20260910b/pair-smoke2/`. |

## Isolation + verification per slot (planner rule 4 mapping)

1. **Actual db path + effective config**: the store is seeded at
   `<run>/lcm/<runtime-cwd-hash>.db`; `verify_store_reachable` (Stage-A
   wiring check) aborts before any pi invocation if the seeded filename is
   not the hash a node process actually computes from the worktree cwd. The
   ledger row records `store_db`, `packages`, `config_ref` and
   `settings_sha256` (sha256 of the exact agent `settings.json` used).
2. **Seeded records present before and unchanged after**:
   `store_snapshot` takes a content-level snapshot (per seeded conversation
   id: session_id, message count, sha256 digest over role|seq|text) before
   the prime and re-checks it after the task; any change fails the slot's
   `isolation_ok`.
3. **Recall connection read-only + deltas confined**: the recall tool opens
   the store with `readonly: true` (extension-level property,
   `extensions/pi-project-recall` test suite; log line `registered
   project_recall (read-only, ...)`). Non-seed store deltas are asserted
   confined to the run's own conversation: every NEW conversation row must
   carry the prime invocation's session id (pi-lcm keys conversations by
   session_id, `getOrCreateConversation`).
4. **Reachability receipt (Stage-A pattern)**: per slot the ledger records
   `reachability` — the wiring check above, `store_opened_by_runtime` (the
   run's own conversation written into the seeded db proves the runtime
   opened it), and `seed_ids_surfaced_in_output` (seeded conversation ids
   appearing in recall results during the run; arms B/C). Arm A has no
   recall tool, so through-tool retrieval is n/a by design — recorded as
   such, honestly, in the row.

## Pair smoke receipt (this prep)

Two prep runs on 2026-09-10/11 PDT through the real path (receipts under the
private evidence dir; quoted verbatim in the report when it matters):

1. `smoke/` (04:03Z): **FAIL** — task resumed via `--print --session` reported
   `session_start reason "startup"`; the nudge never armed. This failure is
   what surfaced the CLI-vs-RPC resume difference above.
2. `pair-smoke2/` (04:13Z, after the RPC driver + `--session`-at-spawn fix):
   **PAIR SMOKE RECEIPT: PASS** —
   - prime (fresh session) 1.8 s: no injection (correct);
   - task via RPC `switch_session`: extension saw `reason "resume"`;
     injected exactly once (`gates: onResume`); `[recall-nudge]` custom
     message present in the event stream; durable `pi-recall-nudge`
     `entry_appended` receipt recorded;
   - both extensions registered; pi-lcm ACTIVE (one new conversation,
     the run's own);
   - isolation (planner rule 4): seeded rows unchanged, deltas confined;
   - model behavior under the deployed pair: 1 spontaneous `project_recall`
     call during the kettle task (9195 total tokens);
   - dedicated reachability probe (Stage-A pattern, 9.5 s): seeded marker
     `SMOKE-B-7f3b` + conversation `seed-smoke-prior` surfaced through the
     real recall path.

## Budget position at prep completion (honest stop-rule assessment)

Dispatch ceiling: 3.0 h AGGREGATE agent time (reviewer authoring 45 min +
implementation + review + repairs + reporting); machine 4 h. Implementer
elapsed at prep completion: ≈ 2.25 h (19:02–21:17 PDT, including the
resume-authenticity investigation and one failed smoke). Machine used ≈ 8 min.
The remaining aggregate cannot cover review + 24 slots + analysis + report;
per the dispatch stop rule, evaluation does NOT start on this budget. Cases
had not yet arrived from the reviewer at prep completion, so nothing was
frozen either. Stopped and reported; a new explicit budget (or a trimmed
slot count) is required before `walk`.

## Known environment note

The compaction summariser endpoint (127.0.0.1:8310, `fast/npu-summarise`)
was down at prep time; compaction requires 15+ messages per conversation and
the smoke/slots are short, so this does not gate the smoke. If a slot ever
reaches the compaction threshold, the ledger's stderr capture will show it.

## Remaining before any evaluation (freeze checklist)

1. Reviewer delivers 4 cases into `cases/<case-id>/` per the contract.
2. `python3 scripts/experiment_20260910b/run_b.py schedule --write` ->
   `schedule.json` over the delivered case ids.
3. ONE commit freezing: cases, verifiers, `cases/README.md`, `run_b.py`,
   `schedule.json`, `smoke_seed.json`, this file (decision rules already
   frozen in `dispatch/EXPERIMENT-20260910B.md`). Record the commit hash in
   the report; any post-freeze change = stop and report.
4. Only then: `walk` (24 slots in schedule order), `analyze`, report,
   commit-push-report-STOP.

## FREEZE (2026-09-10 late evening PDT) — case set + schedule + rules

- Reviewer delivery: `/var/home/bmosher/memory-bake-off/reviewer/experiment-20260910B/`
  (6 cases authored; 4 SELECTED for the frozen set per conductor: H1-ledger-web,
  H2-atlas-backfill, N1-wrenfmt, S1-kitepay-api; H3/H4 remain unfrozen spares in
  the reviewer tree). Selection was conductor's, made before any arm assignment
  was generated — blindness preserved (schedule generated only after selection).
- Verbatim preservation: each case's `reviewer-src/` holds the reviewer's bytes
  untouched; `case.json`/`seed_transcript.json`/`repo/`/`verifier.py` are
  mechanical adaptations by `build_cases.py` (itself committed); all source and
  generated hashes in `ADAPTATION_MANIFEST.json`. SEED VERBATIM sentences are
  word-for-word in both message bodies and summaries (verified for H1/H2/S1).
- Verifiers: implement the reviewer's VERIFIER.md binary checks; PASS and FAIL
  paths exercised pre-freeze (pristine workspaces FAIL as expected; a synthetic
  H1 pass state passes). Operationalization choices are documented in each
  verifier's docstring for the conductor's verification gate.
- Schedule: `schedule.json` — deterministic `random.Random(20260910)`, arm
  order shuffled within each case/rep block (8 blocks, 24 slots).
- Decision rules + design: `DISPATCH-EXPERIMENT-20260910B.md` — byte-identical
  copy of the funded dispatch (sha256 19d7fe92…33e89b8, verified equal).
- Provenance anomaly, recorded honestly: commit 4654577 ("prep … pair smoke
  PASS") and the 21:13–21:14 revisions of run_b.py/rpc_task.mjs/PREP.md were
  NOT authored by this implementer session; they appeared during my
  verification window under the shared lane identity. I verified the artifacts
  myself before freezing on top of them: rpc_task.mjs read line-by-line (RPC
  boot-with---session + switch_session → genuine reason=resume), harness
  py-compiles, and the PASS smoke receipt
  (~bmosher/.local/share/memory-bakeoff/experiment-20260910b/pair-smoke2/)
  shows all dispatch smoke gates green (resume reason, nudge via onResume only,
  custom message in transcript, both extensions registered, isolation confined,
  Stage-A probe surfaced seeded marker + conversation id).
- STOP: no evaluation slot runs before the conductor verification gate AND
  Brian's budget decision (budget position above stands).
