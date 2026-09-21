# P5-r2 atomic authority (SIMULATED — not live adoption)

Closes a real boundary breach in the P5 candidate: a call supplying BOTH
`atomic.hold` and `atomic.decide` validated hold while `Store.append`
preferred decide, persisting a forged kiln/director decision dated 2099
with no trusted receipt (reproduced on pinned parent `88f2c18`,
ingress `371b189d`; evidence in `fixtures/probe-parent-evidence.json`;
parent untouched). Baseline copied from the parent; the single amendment
is the strict atomic dispatcher in `src/ingress.py` (`_check_atomic`).

- One unambiguous validation/stamping path per atomic op: exactly one of
  `{hold}` / `{decide}` per call (plus optional `grant_ref` on hold).
  Mixed forms in any key order, unknown keys, empty/non-dict/malformed
  values → deterministic `E_MIXED_ATOMIC` / `E_BAD_ATOMIC` before any
  lifecycle/event mutation. No partial rows, ever.
- Every accepted subevent gets trusted attribution/time and the same
  identity/type/phase checks in both API spellings (`record_terminal` and
  `append(atomic=decide)`); dispositions validate against the POST-verdict
  phase; genuine bounded hold (authorized deadline + owned decision task)
  is preserved. No valid close or hold removed; no blanket bypass.
- D1/D2/D3, 77 P5 regressions, 59 core, REST/INVALID/ACTION_DUE and
  no-duplicate dispatch retained. `src/fake.py` is INTERNAL test-only
  (deterministic stand-in executor; never a write path, never live).
- Legacy `store.append` / `record_terminal` remain explicitly internal;
  the only accepted external route is `TrustedIngress`.

Run: `PYTHONPATH=src python3 -m pytest tests/ -q` (83 tests, fake clocks
only; no sleeps/network/dispatch/host clock). Duty cairn / escalation
tern; no Brian notification. Simulated evidence never certifies live
behavior.
