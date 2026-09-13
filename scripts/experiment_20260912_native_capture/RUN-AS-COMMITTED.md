# RUN-AS-COMMITTED

- Command: `bash scripts/experiment_20260912_native_capture/probe.sh` (repo root).
- State coupling: **SCRATCH** — writes only its own `receipts/` and
  `/tmp/native-capture-probe`; needs the pinned local binary
  `/var/home/bmosher/perseus-build/src/target/release/perseus-vault`.
- Frozen receipt: `receipts/` + `FINDINGS.md` (commit 84cc6b9).
- Volatile fields on re-run (see FINDINGS.md §Receipt determinism):
  `created_at_unix_ms`, `auth-*`, `mem-*` ids — everything else is
  byte-identical; classified 2026-09-12 in
  `team/KILN-RD-RECEIPT-HYGIENE-20260912.md`.
