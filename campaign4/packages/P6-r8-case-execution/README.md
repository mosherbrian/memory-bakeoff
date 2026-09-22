
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
