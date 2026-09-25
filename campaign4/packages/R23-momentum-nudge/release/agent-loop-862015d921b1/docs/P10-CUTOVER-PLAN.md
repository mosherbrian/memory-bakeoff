# P10 cutover and rollback plan (stage D; only after live PASS and Tern's signature)

## Scope found on the host (read-only, 2026-09-23T14:11Z)

| Effect source | Unit / file | What it does | campaign4 only? | Cutover action |
|---|---|---|---|---|
| openwork | `openwork.timer` (2 min) → `openwork.service`, `Environment=AGENTDECK_PROFILE=campaign4`, `ExecStart=%h/.config/agent-deck/openwork` | nudges cairn about open dispatches in `campaign4/control-events.tsv` | yes: one ledger, profile campaign4 | disable --now |
| campaign4-watch | transient `campaign4-watch.timer` (45 min) → `campaign4-watch` script | backstop wake/pause for campaign4 silence | yes (named, profile campaign4) | stop (transient: no disable) |
| coax | `coax-dry.timer` (1 min) → `agent-loop coax --live --notify ...` | the Go coax: wakes cairn when a campaign4 turn ended with no result row; defaults: ledger `campaign4/control-events.tsv`, profile campaign4 | yes (defaults) | disable --now. It is the Go coax, not a legacy script; the file stays |
| shadow-watch | `shadow-watch.timer` (15 min) → `%h/.config/agent-deck/shadow-watch` | replays the campaign4 TSV through the core; reports to Claude | yes | disable --now |
| cairn's controller role | cairn seat instructions | manual dispatch, CONFIRMED rows, deadline timers, TSV writes | campaign4 | cairn is told in writing: duty and liveness owner only; no dispatch, no ledger rows |

Not in scope (checked: no campaign4 dependence): `escalation-watch` (fleet
escalation ledger), `fleet-*`, `igw-*`, `clawdbot-*`, `sprint-*`, `gate-batch`.
Kept: `~/.config/agent-deck/wake`, lane wrappers, `campaign4-pause`.
No script file is deleted.

## Before the switch (capture; all into `cutover/pre/`)

    for u in openwork coax-dry shadow-watch; do systemctl --user cat $u.timer $u.service; systemctl --user is-enabled $u.timer; systemctl --user is-active $u.timer; done > units.txt
    systemctl --user cat campaign4-watch.timer campaign4-watch.service > campaign4-watch.txt
    sha256sum ~/.config/agent-deck/{openwork,campaign4-watch,shadow-watch} ~/.local/bin/agent-loop > hashes.txt
    AGENTDECK_PROFILE=campaign4 agent-deck list --json > registry.json
    cp ~/memory-bake-off/campaign4/control-events.tsv control-events.pre.tsv
    tail -n 50 ~/.local/share/agent-deck/wake-send.log > wake-send.pre.txt

Drain: no DISPATCHED row may be open in `control-events.tsv` (every dispatch has
a result row or a Tern disposition). If one is open, stop and return it to Tern.
The TSV is archived as history; it is never imported as current authority.

## Switch (one owner at every moment)

1. Old effects off:

       systemctl --user disable --now openwork.timer coax-dry.timer shadow-watch.timer
       systemctl --user stop campaign4-watch.timer
       systemctl --user list-timers --all | grep -E 'openwork|coax-dry|shadow-watch|campaign4-watch'   # must show none active

   Tell cairn (wake, and a record in the package): its controller role ends now;
   it stays duty and liveness owner.
2. Install the qualified binary and units (the exact bytes live-qualified):

       install -m 755 ~/.local/bin/agent-loop ~/.local/bin/agent-loop.prev-c124d82   # kept for rollback
       install -m 755 <qualified candidate> ~/.local/bin/agent-loop
       install -D -m 644 <config> ~/.config/agent-loop/campaign4.json    # NEW ledger ~/.local/share/agent-loop/campaign4.db
       cp examples/systemd-unqualified/agent-loop@.service examples/systemd-unqualified/agent-loop-liveness@.{service,timer} ~/.config/systemd/user/
       systemctl --user daemon-reload
       agent-loop check --config ~/.config/agent-loop/campaign4.json     # kiln, corvid, tern, cairn confirmed in the registry
       systemctl --user enable --now agent-loop@campaign4.service agent-loop-liveness@campaign4.timer

   Config: seats `kiln`, `corvid`, `tern`, `cairn` with their registry ids,
   `director` tern, `duty` cairn, `unit` `agent-loop@campaign4.service`.
3. Verify servicing: within 60 s `agent-loop expose --config ~/.config/agent-loop/campaign4.json`
   shows a pass from the current InvocationID; the next liveness run says `rest`.

## First real package: P10-production-handoff-1

    agent-loop dispatch --config ~/.config/agent-loop/campaign4.json --qid P10-production-handoff-1 \
      --worker kiln --verifier corvid --duration 20m --verify-window 10m \
      --task @handoff-task.md --verify-task @handoff-verify.md

- `handoff-task.md` (signed in advance): write `campaign4/OPERATOR-HANDOFF-20260923.md`
  and `campaign4/packages/P10-go-requalification-cutover/operator-handoff-manifest.json`:
  source/binary/config/unit pins, install/run/status/stop/restore commands, the
  effect-ownership and rollback map, known limits. Then run the claim command
  the task carries, naming both files.
- `handoff-verify.md`: check every pin and command against read-only host facts
  (`sha256sum`, `systemctl --user show/cat`, `agent-loop check`, `expose`); claim
  `completed` only if all match, `failed` otherwise.
- The verifier is fixed by the dispatch (corvid); the worker cannot choose it.
- Tern closes it with `agent-loop decide --config ... --qid P10-production-handoff-1 --kind question_answered --ref <record> --reason ...`.
  No manual wake counts as the software's operation.

## Rollback (any failure, or Tern's call)

1. Archive: `agent-loop expose --config ... --json > cutover/rollback-expose.json`;
   copy the new ledger (db, wal, shm) and claims; list `agent-loop-campaign4-*` timers.
2. Candidate effects off:

       systemctl --user disable --now agent-loop@campaign4.service agent-loop-liveness@campaign4.timer
       systemctl --user stop 'agent-loop-campaign4-*.timer'      # a stop marker alone is not timer cancellation

3. Reconcile: for any action dispatched by the candidate, record its identity and
   whether the worker/verifier already received it (wake log); hand each to cairn
   as an open item in the TSV with its claim path, so nothing is sent twice and nothing is lost.
4. Restore: `install -m 755 ~/.local/bin/agent-loop.prev-c124d82 ~/.local/bin/agent-loop`
   (coax-dry needs it).
5. Old effects on:

       systemctl --user enable --now openwork.timer coax-dry.timer shadow-watch.timer
       systemd-run --user --unit=campaign4-watch --on-active=45min --on-unit-active=45min %h/.config/agent-deck/campaign4-watch   # as recorded in cutover/pre/campaign4-watch.txt

   Tell cairn its controller role is restored.
6. Verify one owner: `systemctl --user list-timers --all` shows the old four and no
   `agent-loop@campaign4`/`agent-loop-liveness@campaign4`.
