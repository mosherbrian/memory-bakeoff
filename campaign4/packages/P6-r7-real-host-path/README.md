# P6-r7 real-host-path — operator readme

Candidate tooling only: read-only host discovery, private `/tmp`, injected
effects. No real seats/messages/restarts/timers under this allocation.

## What is new vs P6-r6

- `src/stagec_host.py` (copied from pinned P6-r6 entry `211f495b…`, evolved
  here): an **actual host branch** in `run_case` (no `--overlay-dir`) that
  uses signed stream/socket paths verbatim and signed host commands, with no
  synthetic producer, no substitute stream files and no shim-trace
  assumption. Missing host paths fail owned (`E_HOST_PATH`), never
  `KeyError`. The overlay flag selects only the effects plane for
  explicitly simulated tests.
- `gate` verifies **current** registry/profile/lane/workdir plus **both
  live sockets/incarnations** against the signed binding before any send;
  expired/stopped/rebound/mismatched runtimes reject. Signatures bind plan +
  config + entrypoint/candidate hashes with purpose `stagec-task`.
- `timecheck` joins on exact **action + execution + case** (executions from
  the signed case receipt), requires recorded positive ack (settled sends +
  witness `ack:true`), validates finite uncertainty and adds it
  conservatively to 30/60/90 (180/60/240 suspicion reported).
- Five cases: positive-handoff, lost-completion, failed-verification,
  queued-ambiguous-restart, quiet-rest.
- `src/fault_onset.py`: executable onset capture (`mark`/`read`) with
  documented limitations; `stagec-plan.json` enumerates exact commands.

## Boundaries

- Pinned P6-r5 candidate is hash-checked on import, never edited.
- Accepted P6-r6 binding manifest is read-only historical evidence.
- Live invocation cannot fall back to overlay; overlay runs are labeled
  simulated, never live evidence. Real-seat execution, fresh preparation
  and signatures are pending Stage C decisions by Tern.
