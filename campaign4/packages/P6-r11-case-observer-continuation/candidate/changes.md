# P6r11 candidate changes (kiln)
- Copied r9 baseline src/tests (manifest-bound, provenance preserved).
- case_entry.py only: shared NORMAL observer continuation (grant-bounded reattach, zero new sends) extended to failed-verification and quiet-rest setup, mirroring positive-handoff.
- harness/host_adapter/core byte-identical (not touched).
- Failed-verification COMPLETE-forbid retained; quiet-rest duplicate-end/no-resend retained.

## Amendment-2 (P6r11-rejection-1)
- candidate/src/r3harness/turn_handoff.py: authenticated verified-rejection (verify-run only, outcome failed, declared==committed worker hash, bytes differ; expected/observed persisted, durable+idempotent; negatives return None). R3_REVISION.json copy hash refreshed mechanically.
- candidate/src/case_entry.py: consume verified-rejection (reattach accept + sends 1+1 + hash evidence; FINAL COMPLETE-forbid retained); R3 parent path absolutized (layout adaptation).
- candidate/tests/test_r11_rejection_newpass.py: 4 executable tests (genuine + 3 negatives).
- candidate/stagec-plan.json supplied (r9-identical inputs); manifest has no self-entry, bound externally from claim.

## Routing repair (P6r11-routing-repair-1, base entry 2326e6b8)
- candidate/src/case_entry.py only: _raise_for_harness_error propagates structured harness error dicts (no "decision" key) with original code/reason before provenance/timing/case gates; wired into run-fixture, reattach and rerun paths with deliverer stop. Decision results (verified-rejection/committed/rest/owned) and raw output pass through untouched. Genuine timing absence without harness failure still fails honestly (E_NO_LATENCY path preserved).
- candidate/tests/test_r11_routing_repair.py: 4 focused tests (forged-route, claim-mismatch, unrelated-code, passthrough).
