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
