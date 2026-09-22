# Rollback (demonstrated within fixture; PROPOSED for Stage C)

Order matters: disable candidate effects first, reconcile identity, then
restore one owner. Never restore-then-disable (that risks dual control).

1. Disable candidate effects: cancel all `p6-fixture-*` timers; confirm
   none armed (`timers` registry empty, `cancelled` set intact).
2. Reconcile action/execution IDs and timers: every fixture action must be
   terminal or explicitly owned-bounded; match each `exec-current:*`
   against its ledger/disposition; confirm zero campaign IDs touched.
3. Restore one owner: restart exactly one of (legacy watcher | candidate)
   per retirement-matrix `restore_command`; verify the other stays stopped.
4. Delete fixture artifacts: `/tmp/p6-fixture-ledger.db`,
   `/tmp/p6-fixture-msgs/`; report artifact hashes to Tern.
5. Record outcome: recovered terminal rest or acknowledged owned escalation;
   never claim rollback by deletion alone.

No indefinite dual controller at any step. Stage A performs no rollback
(live); the injected suite exercises reconcile paths against fakes.
