# P6-r3-cli-recovery — CLI acceptance cases (pinned before worker dispatch)

- **Author:** corvid (independent reader; test design under the existing
  contract, not contract authorship)
- **Date:** 2026-09-22; bounded admission pass
- **Contract:** `467c3f4d77a5…` @ `a35eace`; base parent
  `campaign4/packages/P6-r21-event-handoff` @ `f809fcddb68f5e28cf9d98537abb8694e32befcc`
- **Rule:** these are **black-box expectations on the exact CLI** (`harness.py`
  `setup` → `run-fixture` → assertions → cleanup), checked at OS boundaries with
  injected runners. No production/live calls are made during admission.

## How these are graded

A case passes only if the **candidate CLI itself** produces the observable —
call trace at the injected OS boundary, ledger rows, artifact files and
`latency.jsonl` — with no manual/helper calls substituting for missing CLI work.
The verifier independently re-runs the exact CLI with instrumented boundaries and
checks files/ledger/traces across reopen; mock self-assertion is not evidence.
On the pinned parent each positive case must **fail for the concrete reason**
listed.

## Cases

### C1 — live composition uses host time, not a fake clock
- **Sequence:** exact `setup`; then `run-fixture --live` with a valid plan hash,
  allowlist and injected OS runner.
- **Expected:** the live `Driver` is constructed with host UTC/monotonic (a real
  `HostClock`, no `FakeClock` default); `run-fixture` never substitutes a fake
  clock or fake executor on the live path; a missing required collaborator fails
  closed.
- **Parent failure:** `harness.py` builds `Driver(db_path, clock or FakeClock())`
  and the live branch constructs `Driver(args.db)` with no clock → **fake
  clock**. FAILS.

### C2 — the CLI performs the authorized worker send
- **Sequence:** same as C1 with a staged bound end + claim file + real artifact.
- **Expected:** injected transport call trace records a send to the
  contract-bound **worker** seat for the launch action/execution; no fake
  `start_dispatch`-only path.
- **Parent failure:** `run_fixture` calls `driver.start_dispatch(...)` (fake
  driver) and never `transport.send` for the worker → **no worker send**. FAILS.

### C3 — runtime subscription, not a one-time isolated read
- **Sequence:** C1; the stream is appended after the CLI starts.
- **Expected:** the CLI subscribes to / consumes the producer stream (persisted
  cursor, notification-driven), and a turn-end appended after start is observed;
  loss/truncation/restart reconcile without loss.
- **Parent failure:** a single `watcher.poll` over an isolated `/tmp` stream with
  no subscription/producer → appended-after-start end is missed. FAILS.

### C4 — runtime session/stream/item bound from evidence, not the plan hash
- **Sequence:** C1 with a runtime-created session/stream/item.
- **Expected:** the bound session/stream/item comes from launcher/runtime
  evidence and matches the emitted end event; a plan-hash-derived session does not
  satisfy the binding.
- **Parent failure:** `setup_manifest` derives `session`/`stream_key` from the
  plan hash. FAILS.

### C5 — no-end at the bound is an owned failure with nonzero exit
- **Sequence:** `run-fixture` with no source / no end.
- **Expected:** owned failure/BLOCKED and a **nonzero** exit; `latency.jsonl`
  records the no-end sample as a failure.
- **Parent failure:** `no-end-observed` is in the accepted-decision list and
  `main` returns **0**. FAILS.

### C6 — `latency.jsonl` is actually written with real fields
- **Sequence:** exact `run-fixture`, then the plan's latency assertion.
- **Expected:** `run-fixture` appends `{action, dispatch_at, detected_at,
  committed_at, outcome}` per observed action, with source-clock vs receipt
  uncertainty distinguished; the assertion that rows exist and gates
  30 s/180 s/60 s (totals 90 s/240 s) hold passes; **zero samples cannot pass**.
- **Parent failure:** the harness has **no latency writer**, so the plan's
  assertion (`assert rows`) fails. FAILS.

### C7 — deadlines derive from trusted start/grant, not a literal example
- **Sequence:** C1.
- **Expected:** the verifier/handoff deadlines are computed from the trusted
  start plus the authorized duration/grant; the literal
  `2026-09-22T01:00:00Z` is not baked in as the deadline.
- **Parent failure:** the plan and manifest carry the fixed `01:00Z` example
  deadline. FAILS.

### C8 — full closed graph through the CLI
- **Sequence:** C1.
- **Expected:** CLI records worker send → actual-format runtime start/end →
  route-free worker claim + recomputed artifact → contract-selected **verifier**
  send → verifier/director receipts → terminal or bounded recovery; the next
  dispatch is committed in-ledger, and the outbox acknowledges after delivery.
- **Parent failure:** none of the verifier/director steps occur (no worker send,
  no subscription, no claim file from the CLI). FAILS.

### C9 — fault matrix through the exact CLI
- **Sequence:** exact `run-fixture` with each injected fault: no source, slow
  start, missing claim, explicit failed turn, duplicate/stale end, truncated
  stream, restart.
- **Expected:** each yields the specific owned outcome/exit (recovery or bounded
  escalation), no invented verifier PASS/director decision, no arbitrary worker
  routing; duplicate/stale/restart produce no duplicate effect.
- **Parent failure:** the parent only polls an isolated file and cannot
  distinguish these; several return success/no-end. FAILS.

### C10 — cleanup/rollback verifies before reporting
- **Sequence:** exact plan cleanup after C1/C9.
- **Expected:** timer cancellation verifies actual unit state
  (`ActiveState=inactive`) and current action/execution identities before the
  rollback report; evidence is archived before deleting disposable state; no
  unconditional `reconciled` report and no swallowed command failure.
- **Parent failure:** cleanup writes
  `{'timers':'none-armed-verified','ids':'reconciled','owner':'restored-one'}`
  **unconditionally**, with no identity or unit-state check. FAILS.

### C11 — plan hash binds resources and commands
- **Sequence:** `--live` with a mismatched/absent plan hash, and with a
  non-allowlisted seat/resource.
- **Expected:** the CLI refuses (fail-closed) unless the plan file hash matches
  **and** the seat/unit resources are allowlisted by that plan; a merely nonempty
  `--plan-hash` cannot authorize arbitrary seats/resources.
- **Parent failure:** the live check compares the plan hash but does not bind the
  allowlisted resources to the plan's declared set. PARTIAL/FAILS.

### C12 — retained semantics and reopen reconciliation
- **Sequence:** C1 then reopen; crash before/after send and before/after ack.
- **Expected:** 135+59 regressions and D1–D4 corrections retained; intent/ledger
  and receipt reconciliation preserve no duplicate effects; a same local ID is
  not treated as transport exactly-once; no blind replay.
- **Parent:** helper tests exist, but the **CLI** path does not exercise them.
  FAILS as a CLI case.

## Pin

These expectations are fixed **before** worker dispatch. Any change to the
contract's requirements that these cases imply must be reviewed by Tern
separately; the verifier will not silently expand the contract.
