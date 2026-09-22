
## Test-harness conventions (simulated branch only, never live)

- `FAULT_ROOT`/`FAULT_CASE` env passthrough lets signed TEST executables
  honor the armed intervention file for the current case (queued-first /
  ambiguous-once). The tool never sets `FAULT_CASE` and live commands
  ignore both variables. Send counting always uses durable kv msg records,
  never shim trace output.
- Prior completed cases' turn bindings are restored into each new case db
  through the production `bind_turn` API (`_carry_bindings`), so foreign
  ends in the shared runtime streams are recognized and skipped, never
  adopted. Only recorded completed-case evidence contributes.
- Rollback archives first; open recoveries and induced ambiguous sends
  keep un-acked intents by candidate design and are retained explicitly
  (never forged); settleable-but-unsettled intents still fail hard.

## R1 repair: the executing consumer (fixture_control + deposit path)

- Dispatch is two-stage in EVERY branch: the candidate transport calls the
  signed fixture `wake-deposit` wrapper (deposits `{seat,text,received_at}`,
  returns a truthful deposit receipt; never invents queued/ambiguous), and
  `run_case`'s deliver loop (`src/fixture_control.py`) moves texts to seats
  per the armed intervention file — hold, bounded induced delay, or
  immediate — emitting applied receipts (`faults/<case>.applied.json`) with
  before/after evidence. Live delivery invokes the real authorized wake;
  injected delivery copies to the seat inbox. The loop also tampers the
  artifact post-worker-commit for `corrupt-after-worker` (before/after
  hashes recorded).
- Every resolved end must trace to a delivery record (`E_UNDELIVERED`
  fail-closed): pre-planted ends the candidate alone would accept are
  rejected at this layer.
- Test-harness conventions: `FAULT_ROOT`/`FAULT_CASE` env lets signed TEST
  deposit executables honor the armed intervention for induced transport
  states (labeled induced; the tool verifies receipts, never invents them).
  The tool reads the intervention file itself and never sets these vars;
  live commands ignore them.
