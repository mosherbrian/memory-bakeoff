# SUPERVISED PREVIEW / NOT QUALIFIED FOR UNATTENDED USE

This build of agent-loop is a supervised preview. Run it only while a person
watches it. It has not passed its unattended-use qualification.

## Why it is not qualified

Campaign 4 package P8 (qualification of this Go program) ended **NOT READY**,
terminal EXHAUSTED at its one repair, on 2026-09-23. Records in
`memory-bake-off/campaign4/packages/P8-go-unattended-qualification/`:
`terminal-disposition.json`, `qualification-final.md`, the amended
`repair-1-review.md`, and `liveness-blockers-addendum.md` (commit a3dc87a,
sha256 32963c79...).

Known blockers found in P8. In the P10 candidate (branch `p10-liveness`), 1 to 3
are fixed and tested with stubs and the real CLI (`evidence/candidate-cases.txt`
in the P10 package); none is observed live yet. The released c124d82 build still
has all of them:

1. **Damaged incident file.** A damaged or unreadable `<db>.liveness.json`
   makes `agent-loop liveness` exit 1 before it assesses anything. No one is
   notified, so a fault at that moment is missed.
2. **Pass time in the future.** If the last pass time is in the future (for
   example after the host clock steps back), the liveness check reads it as
   fresh and can report healthy rest until the clock catches up.
   (`agent-loop expose` shows such a pass as UNKNOWN, but the liveness check
   itself does not.)
3. **No process-incarnation binding.** A pass recorded by a previous `run`
   process can stand for the current one until the new process completes its
   first pass.
4. **Supervision never observed live.** The systemd behaviour (restart,
   watchdog, exit 64 on stop, the start limit, timer accuracy) has only been
   tested with stubs. The unit files in `examples/systemd-unqualified/` are
   unqualified examples: nothing installs or enables them.

Other limits:

- **Trusted host.** The CLI does not authenticate its caller. Any host user
  who can run `agent-loop` with the config acts for the roles recorded in it.
- **No continuation of old packages.** A package registered before principals
  were recorded (candidate 4a00d67 and earlier) is refused
  `E_AUTHORITY_MISSING` at every step. Nothing is backfilled.
- **Costs** are not in the binary. `agent-loop expose --json` gives each step's
  seat, session, `started_at` and `ended_at`, which an external tool can join
  with provider billing.

## Stop is not cancellation

`agent-loop stop` stops the `run` loop. It does not cancel anything already
granted. Every dispatched step has its own systemd one-shot timer
(`agent-loop-<project>-<qid>-w1.timer`, `...-v1.timer`) that still fires at the
step's deadline, interrupts the step, sends `/cancel` to the seat and wakes the
director, whether or not `run` is running.

Inventory of a project's timers:

    systemctl --user list-timers --all 'agent-loop-<project>-*'

Cleanup, only after the packages are decided or deliberately abandoned:

    systemctl --user stop 'agent-loop-<project>-*.timer'
    systemctl --user reset-failed 'agent-loop-<project>-*'

## After an uncertain send

The outbox never resends blindly. After a restart, `run` reconciles each
pending dispatch: delivered ones are acknowledged, sent or queued ones are held
awaiting receipt, ambiguous ones are held for a person, and only never-sent
ones are sent, under the same identity. `agent-loop status` counts dispatches
still open in the outbox. Resolve an ambiguous one by checking the seat, not by
re-dispatching the package.
