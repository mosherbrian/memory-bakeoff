# P6-r7-real-host-path — readiness review (R1–R3, independent)

- **Reviewer:** corvid; **Date:** 2026-09-22, root `/home/bmosher/memory-bake-off`
- **Receipt:** `readiness-review-receipt.json` (`P6r7-readiness-1`), start
  `2026-09-22T05:00Z`, deadline `2026-09-22T05:10Z`, budget 10m, worker 0
- **Authority:** `director-readiness-review.json` (`ACCEPT_REPAIR_EVIDENCE_WITHHOLD_STAGE_C`)
- **Bound evidence:** repair PASS `677dbeac…`; entry `46681fbb82cb…`; plan
  `cc5993ab…`; checklist `ce7401f1…`; contract `515deb16…` @ `fd497e7`
- **Effect limits:** read-only; no worker repair, preparation, live task,
  timer/service fixture effect or restart.

## Verdict

**FAIL** — the repaired CLI is sound for its injected scope, but the execution
path is **not ready** to run the five real host cases: fault induction is not in
the plan/host branch (R1), the sequential five-command composition shares one
state root and would replay/overwrite rather than execute distinct cases (R2),
and `wait_s=8` expires far before the 900/600-second real allocations with no
demonstrated resume (R3). Bounded, reproducible, not a rewrite.

## R1 — fault-induction provenance: FAIL

Traced all five exact `run-case` commands in `stagec-plan.json` (`3_positive`
… `7_quiet_rest`) plus `src/stagec_host.py`:

- In the host (no-overlay) branch `run_case` sets `bg = None` — it never starts
  `_drive_producers`, and there is no host-branch equivalent. `hold` (lost
  completion), `tamper` (failed verification) and `queued-first`
  (queued/ambiguous + restart) exist **only** in
  `tests/test_stagec_host.py::producers`, i.e. the test harness, not the tool or
  the plan.
- The plan's exact commands pass only `--case <name>`; nothing selects an
  induced fault, and no actor/provenance is named for a real onset. The
  plan documents `host_commands` (wake/systemd) but not fault injection.
- `src/fault_onset.py` exists (onset capture), but with no host-branch induction
  hook it is only reachable from the test producer boundary.

So the "independent controlled fault onset capture must be executable, not a
sidecar conjured by a shim" (H3) requirement is **not met for real execution**;
injected boundary behavior is being exercised instead of a real execution step.

**Minimum correction:** specify and implement host-branch, per-case fault
induction as an explicit executable step (operator/fixture actor) with its own
independently captured onset provenance, and register the exact command/actor
per case; or, if induction is intentionally external, add that as an explicit
plan phase with the acting party and onset source, and stop counting the
test-boundary `hold`/`tamper`/`queued-first` as a real execution step.

## R2 — same-root five-case composition: FAIL

- Every plan case uses the same root `/tmp/p6stagec` and the same
  `live_run_dirs` (`db`, `claims`, `art`, `onsets`, `msgs`, `latency`,
  `witness`), the same action IDs (`p6c-w1`/`p6c-v1`) and the same timer unit
  `p6-stagec-handoff-1.timer`.
- `run_case` reuses `dirs["root"]/manifest.json`, `candidate-plan.json`, the
  same `dirs["db"]`, `dirs["claims"]` and shared `latency`/`witness`/onset
  files for every case; it creates directories but never scopes them per case.
- The candidate's own restart/duplicate detection means a second `run-case` on
  the same db/stream will be treated as `duplicate-end-ignored`, not a fresh
  distinct case; `timecheck` reads a single shared `latency.jsonl` and
  `witness-rows.jsonl`. Evidence would be appended/overwritten across cases.
- The only place distinct cases are proven is `tests`, which calls `_make_env()`
  to create a **fresh** environment per case — so the actual five-command
  composition on one root is untested.

**Minimum correction:** give each case a deterministic case-scoped subroot
(db, claims, stream, onsets, msgs, artifact, latency, witness, receipt, manifest,
and action IDs/timer unit if needed) and run the five commands sequentially
against it, asserting five distinct results rather than replay/overwrite; add
one composition test that exercises the same root layout the plan prescribes.

## R3 — `wait_s` vs real allocations: FAIL

- `_candidate_plan` hardcodes `wait_s: 8` while real allocations are
  `duration_s: 900`, `verify_window_s: 600`.
- In the pinned candidate, `run_fixture` derives the **trusted decision deadline**
  as `trusted_now() + wait_s` and a wall backstop of `wait_s + 5.0` (≈13 s)
  (`harness.py:405–411`); the notifier timer is armed with `seconds=wait_s`
  (`:290`). With `wait_s=8` the owned decision is taken after ~8 s, long before a
  real model turn (600–900 s) could complete.
- There is no resume/re-attach path in the plan or host branch: nothing
  re-arms the wait or drains late completion after the case returns, and
  `timecheck` would see rows with no `committed_at` (INCOMPLETE), not a late
  recovery. So late completion does **not** demonstrably resume without another
  send.

**Minimum correction:** set bounds consistent with the real allocations (e.g.
`wait_s`/verify window aligned to `verify_window_s=600`, escalation within
`duration_s=900`) or implement and demonstrate a resume path: the observer wait
may expire, but a late completion re-attaches and is joined without a fresh
send, with the trusted deadline governing the owned decision.

## Scope note

The H2 repair PASS (`677dbeac…`, entry `46681fbb82cb…`) is preserved for its
injected CLI scope; this review makes no claim it is invalid. Package is not
accepted or terminal. In accordance with the boundary rationale, the three gaps
above are necessary before any further implementation or preparation allocation;
this is a bounded existing-composition fix, not new platform features.

## Effect

Bounded **FAIL**, reproducible from `stagec-plan.json`, `src/stagec_host.py`,
`tests/test_stagec_host.py`, and `harness.py:405–411`. No worker repair,
preparation, live task, timer/service fixture effect or restart occurred;
registry unchanged. Reported to Tern (and cairn).
