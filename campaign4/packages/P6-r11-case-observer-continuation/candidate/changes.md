# P6r11 candidate changes (kiln)
- Copied r9 baseline src/tests (manifest-bound, provenance preserved).
- case_entry.py only: shared NORMAL observer continuation (grant-bounded reattach, zero new sends) extended to failed-verification and quiet-rest setup, mirroring positive-handoff.
- harness/host_adapter/core byte-identical (not touched).
- Failed-verification COMPLETE-forbid retained; quiet-rest duplicate-end/no-resend retained.
