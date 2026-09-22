# P6-r7 — H1–H4 pre-worker acceptance checklist (pinned)

- **Author:** corvid (independent reader; pinned BEFORE worker dispatch)
- **Date:** 2026-09-22; bound to contract `515deb16a0d038538a639b1c9ffc1e893b86ba3b0d18327e0878f1b94a468318` @ `fd497e7`
- **Parent:** P6-r6 `1b8a166d…`; verified only for its injected CLI scope — **not**
  live readiness. Binding manifests are historical evidence, not permission to
  restart/reuse expired incarnations.
- **Rule:** every check is blocking. Candidate work is read-only host discovery,
  private `/tmp`, injected effects **only**; no real seats/messages/restarts/
  timers/Signal, no shared-wrapper changes, no shadow/retirement/research run.
  Live invocation may not silently fall back to overlay.

## H1 — actual host branch (no synthetic producer)

- **H1.1 fixed:** the live (`_live_dirs`) path no longer raises `KeyError`
  `wake_shim`. A missing host path (e.g. real `wake`/`systemd-run`/`systemctl`
  absent) fails **owned** with a named error, never an uncaught `KeyError`.
- **H1.2 branch:** an actual host branch selects the **real authorized**
  wake/systemd commands and the **signed actual** runtime stream/socket paths;
  no `_drive_producers`, no substitute stream files, no shim trace assumption,
  no synthetic producer, no invented onset.
- **H1.3 same branch:** injected tests execute this **same** no-`--overlay-dir`
  branch, intercepting only external effects (PATH/producer boundaries). Overlay
  remains an explicitly simulated test path only.
- **H1.4 roles:** real worker/verifier tasks receive the complete
  contract-selected brief/claim/schema; the actual model turn + runtime event
  drive the handoff. No direct-script worker substitutes for a declared live seat.
- **H1.5 core:** same pinned core; if internals must change, a bounded reproducer
  returns to Tern first. H1 no-side-effect reproducer: calling parent
  `_candidate_plan(config, plan, _live_dirs(plan))` raises `KeyError: 'wake_shim'`
  (reproduced read-only).

## H2 — live gate (current-state, not two stale copies)

- **H2.1** immediately before any real send, verify current registry/profile/lane/
  workdir and **both live sockets/incarnations** against the signed binding;
  reject expired/stopped/rebound/mismatched runtime before any send — returning
  PASS on expired sockets is failure.
- **H2.2** signature binds plan + execution config + **executable code and
  candidate hashes**; changing tools invalidates the release. Preparation-only
  signatures cannot authorize task sends.
- **H2.3** no hardcoded old fixture IDs; identity never guessed from name.
  Independent worker/verifier; **exactly one send per action** across
  restart/ambiguous receipt.
- **Negative (pinned):** *expired host* — a stopped/expired recorded binding must
  make the gate reject before effect; a *missing host path* must fail owned.

## H3 — correlated timing and authority

- **H3.1** witness join is exact **action + execution + case**; an
  old-execution witness cannot certify a new execution.
- **H3.2** acceptance requires actual recorded positive ack/recovery evidence,
  never absence of `ack:false`.
- **H3.3** provenance and finite nonnegative uncertainty are validated and their
  bound incorporated conservatively into 30/60/90 (or 180/60/240); unknown/
  unbounded interval → **INCOMPLETE**.
- **H3.4** wrong/duplicate witness, missing ack, all-failure sample, late
  recovery, negative interval and contradictory clock evidence never accept.
- **H3.5** controlled fault onset capture is **executable** (not a shim-conjured
  sidecar); its observation limitations are documented; normal execution duration
  is reported separately; candidate detection time is never copied into an
  "independent source" label.
- **Negatives (pinned):** *wrong-execution witness* must reject/INCOMPLETE;
  *omitted ack* must never accept.

## H4 — exact commands and outcomes

- **H4.1** setup/derive/gate/run-case/timecheck/rollback run via actual
  subprocess CLI with the production branch selected and external boundaries
  intercepted — **no direct-import substitute**.
- **H4.2** require artifacts **and** exit/output; prove one worker/one verifier,
  failed verification cannot close, known missing wake/failure recovery,
  queued/ambiguous transport + restart, quiet rest, and cleanup.
- **H4.3** mandatory inherited cases stay **five** (normal handoff, lost
  completion, failure recovery, queued/ambiguous+restart, quiet rest); they may
  not silently shrink to three. Injected and pending-real evidence are separated.
- **H4.4** auth and error paths reject **before** effects; rollback archives
  **then** disables owned effects.
- **H4.5** the future live plan fully enumerates commands/cases/limits/
  preconditions with **no placeholders** (`<…>`, `MANIFEST_STREAM`, `ITEM`,
  `ACT`, `EX`).
- **Negative (pinned):** *no-overlay positive trace* — a positive injected run
  through the same entrypoint must emit a one-worker/one-verifier send trace with
  no shim-only artifacts; a trace that only exists under overlay is failure.

## Allocation / boundary

Worker initial ≤40m, one independent candidate pass ≤25m; ceilings
465/350 → **505/375**. Admission/checklist ≤15m. Live witness 10m and cairn
fixture 15m remain held, not re-added; preparation 30m spent, no renewal. No
fresh preparation grant. If candidate PASS, Tern separately decides preparation,
independent binding witness and live signature/grants. These checks cannot add
scope without a Tern amendment.
