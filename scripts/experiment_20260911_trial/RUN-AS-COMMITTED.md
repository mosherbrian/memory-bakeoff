# RUN-AS-COMMITTED

State couplings differ per instrument — read before running:

| Instrument | Command | Coupling |
|---|---|---|
| `build_s4_packets.py` | `build_s4_packets.py --self-test --session <session.jsonl> --out <dir>` | **BLINDING-SENSITIVE**: per S4-ADJUDICATION B1/B6 the self-test runs on the pre-window smoke session only; sealed output outside `team/`; never raw fire-log content mid-window |
| `s6_scan_after_write.sh` | per runbook | **LIVE-STATE**: scans the live trial vault (window open); receipts frozen in `window/` (1fc8017) |
| `trial_smoke.ts` | per `docs/TRIAL-20260911-runbook.md` | **LIVE-STATE**: touches trial pi config / vault |
| `window/` | — | frozen window-opening receipts — do not regenerate |
