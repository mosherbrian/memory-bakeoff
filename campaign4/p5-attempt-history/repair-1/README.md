# P5 trusted timestamp ingress (SIMULATED — not live adoption)

The trusted write boundary owns receipt time and deadline derivation.
Baseline copied from pinned P4-r2 `4c07bd83` (driver cleaned `8f7c61ce`;
old bytes preserved); only `src/ingress.py` is new plus the authorized
clock-boundary adaptation of `src/driver.py` (all writes routed through
ingress; FakeClock gains coherent wall+monotonic). No host clock change,
no live adoption, no prior-package edits.

- `TrustedIngress.append / record_terminal` is the single accepted external
  write route. `store.append / record_terminal` are explicitly internal.
- `recorded_at` comes from the injected clock (`HostClock` in production,
  injected fakes in tests). Caller `recorded_at`/`receipt`/`_trusted`,
  caller start `deadline`, bad durations, over-allocation, unknown/expired/
  mismatched grants are rejected with deterministic owned codes.
- Source `occurred_at` + `provenance` kept separately; future skew beyond
  120 s (justified in interface.md) or malformed/naive claims are
  quarantined before touching lifecycle; backdated receipts keep both times
  and cannot retro-authorize (ledger validation stays authoritative after
  ingress).
- Wall-vs-monotonic divergence beyond 60 s quarantines the write
  (E_DISCONTINUITY) for bounded `reconcile_clock` without touching
  deadlines. Restart persists UTC/grants and opens a new monotonic epoch;
  historical receipts replay unchanged, never re-stamped.
- A far-future deadline inside a real pinned grant is valid (not skew).

Run: `PYTHONPATH=src python3 -m pytest tests/ -q` (54 tests, fake clocks
only; no sleeps/network/dispatch). Accepted core suite: 59 passed.
Duty cairn / escalation tern; no Brian notification. Simulated evidence
never certifies live behavior; host UTC proves receipt time, never
occurrence.

## Sole repair (D1 + D2 + D3)

- D1: `Driver._submit` binds the trusted actor context at the boundary;
  event claims (including `record_terminal` and atomic subevents) carrying
  their own `actor` are rejected (`E_FORGED_ATTRIBUTION`, owner tern);
  adapter contexts outside the trusted seat/role set are rejected.
- D2: starts need explicit `duration_s`/`grant_ref` (no fallback default);
  nested verify/handoff/hold deadlines must sit inside a 24 h cap or a
  phase-bound covering grant (2099-without-grant rejected; pinned distant
  deadlines accepted); actual phase is read from ledger state and caller
  `phase_hint`s are rejected; idempotent replays of seen event ids bypass
  re-validation without re-stamp.
- D3: each ingress lifetime mints a unique epoch (boot counter + token);
  backward UTC at reopen quarantines writes (`E_AMBIGUOUS_RESTART`) until
  bounded `reconcile_clock`; cross-process monotonic values are never
  compared; deadlines are never extended or reset.
