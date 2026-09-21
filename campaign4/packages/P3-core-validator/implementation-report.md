# P3-core-validator — implementation report (repair v3)

Worker kiln, 2026-09-21. Authority: Tern's prospective allocation extension
1 (repair 2, attempt 3). Corvid's v2 verdict confirmed D1–D4 fixed and
identified one introduced regression: completed worker flight survived
publication into CHECKING, falsely alarming `E_OVERDUE_ACTION`.

## Repair-2 correction (narrow)

- `lifecycle.apply`: `START` records worker flight in the pure core;
  `PUBLISH` ends it and records either the verifier's own bounded action
  (`verify: {action_id, owner, deadline}`) or an explicitly owned bounded
  handoff (`handoff_deadline`, owner duty/director; neither present →
  `E_BAD_ALLOCATION`). Flight and handoff survive `BLOCKED`/resume and
  replay untouched (interrupt/resolve move phase only).
- `store`/`validator`: verifier-flight acks recorded distinctly; snapshots
  project verifier flight or the bounded handoff entry (never null
  owner/deadline); liveness/overdue rules apply to the verifier action.
- Required evidence, all tested: (1) 17:10/17:05/17:25/17:15 reproducer is
  ACTIVE on the repair, while the stale worker-flight projection still
  alarms `E_OVERDUE_ACTION`; (2) validation at 17:35 faults overdue;
  (3) store reopen reproduces both; (4) BLOCKED/resume keeps action `vf1`;
  (5) handoff is ACTIVE-bounded (owner duty, deadline 17:20) and overdue
  past it, never unbounded silence; (6) all D1–D4, REST, omission, atomic
  publication, no-duplicate, no-live-effects, stdlib, fake-clock
  regressions hold — 40 tests green.


## What changed per defect

- **D1 (allocation enforcement):** `apply()` now enforces verifier spend
  (`elapsed_s` required, capped by pass budget ≤ per-pass ceiling), validates
  `new_allocation` as `{"grant_s", "granted_by": "tern"}` within the ceiling
  (free-form `"10m"` rejected), and adds the duty-only `recover` event from
  BLOCKED with the hard 600 s per-pass ceiling — the recorded 20-minute
  archive-recheck shape is rejected (`E_ALLOC_EXCEEDED`) even under an
  inflated cumulative budget. New tests: spend/missing/cap rejections,
  grant-shape rejections + valid grant, deviation rejection + valid 8-min
  recovery + overspend rejection.
- **D2 (in-flight projection):** `publish_snapshot` emits full action
  identity (`action_id`, `owner`, `deadline`, `dispatch_receipt`); missing
  keys validate `E_MALFORMED`. New fixture `overdue-flight.jsonl` reproduces
  corvid script B: ledger-derived overdue work → `E_OVERDUE_ACTION`.
- **D3 (successor liveness):** liveness requires `dispatch_receipt ==
  acknowledged` AND a finite deadline. New fixture `no-receipt.json`
  reproduces script A → `INVALID` (malformed/dangling, never ACTIVE).
- **D4 (atomic terminal rule):** `Store.append` rejects bare terminal
  verdicts (`E_MISSING_DISPOSITION`); `close` / `apply --decide` /
  `apply --hold` commit verdict+disposition or verdict+bounded-hold in one
  transaction (`record_terminal` wired and tested). `verify_pass` alone no
  longer closes: held verdicts validate ACTIVE (pending), legacy bare
  terminals (raw pre-core rows, as in the omission fixture) validate
  `INVALID`. New tests: bare rejection with stable row count, hold→ACTIVE,
  atomic close→REST, legacy omission→INVALID preserved.
- `fixtures/schema.json` now defines projection field types, the allocation
  model, liveness, and the two new codes (`E_ALLOC_EXCEEDED`,
  `E_BAD_ALLOCATION`).

## Commands and actual results

```bash
cd campaign4/packages/P3-core-validator
python3 -m pytest tests/ -q        # 32 passed in ~5s (fake clock, no sleeps)
python3 -m src.cli apply --store /tmp/ledger.db --event <event.json>
  [--decide <decide.json> | --hold <RFC3339>]
python3 -m src.cli close --store /tmp/ledger.db --verdict <v.json> \
  --decide <d.json>
python3 -m src.cli snapshot --store /tmp/ledger.db --out /tmp/snap.json
python3 -m src.cli validate --store /tmp/ledger.db \
  --snapshot /tmp/snap.json --now <RFC3339>
```

- Group 1 (boundary validator, `test_validator.py::TestValidator`, 8 tests):
  omission→INVALID `E_MISSING_DISPOSITION`; three rest kinds→REST with no
  action; trigger-due→`ACTION_DUE` once then REST; chain-live→ACTIVE;
  two-successors→REST; 8 adversarial snapshots + malformed + absent →
  correct codes; unrelated-busy→`E_DANGLING_SUCCESSOR`; stale snapshot
  cannot hide the ledger.
- Group 2 (lifecycle, `test_lifecycle.py`, 13 tests): happy path, valid
  negative completes, repair→exhaustion (9a), direct exhaustion on withheld
  acceptance, self-verify refusal, unauthorized/late/missing-deadline
  rejections, CHECKING resume same attempt, expired verification needs a
  grant, amend/supersede, terminal closure, enumerable-kind enforcement.
- Group 3 (idempotency, `TestIdempotency`, 5 tests): duplicate delivery
  ignored with row count stable; crash-after-start redelivers the same
  action with executor run count == 1 across a store reopen; interrupted
  snapshot rebuilds to REST; forged post-terminal publish rejected; stale
  interrupt after completion rejected.

## Source/fixture/test hashes

Tree manifest (sorted per-file sha256 over `src/`, `tests/`, `fixtures/`,
`README.md`, this report) recomputed at completion and bound in the cairn
wake.

## Limitations and known operational deviations

1. `worker_seat` binding is carried on the in-memory record for the
   self-verify check, not yet a persisted ledger field.
2. Delivery acks live in the durable `meta` ack table, not as event rows.
3. Trigger exactly-once is caller-held; the store does not persist fired
   trigger ids across restarts.
4. `publish_snapshot` `extra` allows test-only enrichment; the production
   path publishes ledger-derived content only.
5. SQLite WAL files accompany the store path; "one file" means one
   authority, not one inode.
6. `DECISION_TASK` hold actors are recorded as duty/cairn; director-opened
   holds arrive as the same task shape with no separate author field.
7. Adapters, watchers, live dispatch, and any wake/stop/Signal path are
   absent by contract — readiness for live integration is NOT claimed.
