# P3-core-validator — implementation report

Worker kiln, 2026-09-21. Pinned spec: P2 r2.1 at
`5bfbb071e6efdb6f15de1c582295363a94cd08c7` (hashes re-verified before
dispatch: contract `87435405…`, transitions `3afedd35…`, ownership
`cd198c0b…`, boundary-schema `ec6daf09…`, walkthrough `12348310…`,
verification `93263e9a…`). No semantic conflict required a Tern question;
no policy was silently picked — every behavior below cites its spec row.

## Commands and actual results

```bash
cd campaign4/packages/P3-core-validator
python3 -m pytest tests/ -q        # 26 passed in ~9s (fake clock, no sleeps)
python3 -m src.cli apply --store /tmp/ledger.db --event <event.json>
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

See `sha256sum` output recorded at completion (bound in the cairn wake):
6 `src/` files, 3 `tests/` files, 7 event fixtures, 10 snapshot fixtures,
`schema.json`, `README.md`, and this report.

## Limitations and known operational deviations

1. `worker_seat` binding is carried on the in-memory record for the
   self-verify check, not yet a persisted ledger field — a fresh prototype
   gap corvid may probe (reproducer must supply the same seat binding).
2. `dispatch_receipt` acknowledgement is persisted in the `meta` ack table,
   not as ledger events — delivery state is durable and restart-safe, but it
   is not itself an auditable event row.
3. Trigger exactly-once is caller-held (`triggers_fired` set passed to
   `validate`); the store does not yet persist fired trigger ids across
   restarts — same class as (2), flagged rather than hidden.
4. `publish_snapshot` `extra` allows test-only `in_flight` enrichment; the
   production path publishes ledger-derived content only.
5. SQLite WAL files accompany the store path; "one file" means one
   authority, not literally one inode.
6. Adapters, watchers, live dispatch, and any wake/stop/Signal path are
   absent by contract — readiness for live integration is NOT claimed.
