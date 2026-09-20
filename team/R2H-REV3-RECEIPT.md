# R2H REV-3 receipt — `check --pi-cmd` + unrunnable-binary guard

**Seat:** worker-glm-2 · **Date:** 2026-09-14 · **Spec:** `dispatch/R2H-REV3.md` (Brian-approved, day-0 blocker) · **Verifier:** Corvid
**Budget:** ≤30 min · **Rules:** no vault writes, no transcript content — honored.

## Change (deploy script only)

`implementer/repo/deploy/r2-habit-20260912/r2h_deploy.py`:
1. `check` accepts `--pi-cmd` (default `"pi"`, mirrors `smoke`); probe uses it.
2. Probe wrapped in try/except: missing binary AND unrunnable binary (shim,
   directory, non-executable) both become a clean FAIL row printing the
   resolved path. Crash class unreproducible by construction.

## Verification (Linux, this lane)

| case | result |
|---|---|
| `check` default path | PASS row byte-identical format (`/home/bmosher/.local/bin/pi (...)`); all other rows unchanged |
| `--pi-cmd /home/bmosher/.local/bin/pi` (dev-binary-style explicit path) | PASS, same row |
| `--pi-cmd /nonexistent` | `FAIL pi binary: /nonexistent: not found (resolved /nonexistent)`, no traceback |
| `--pi-cmd <non-executable file>` | `FAIL ... probe failed (PermissionError ...)`, no traceback |
| `--pi-cmd <directory>` | `FAIL ... probe failed (PermissionError ...)`, no traceback |

## Freeze / re-ship

- `FREEZE.md` untouched (still byte-frozen); this note lives here, not there.
- `r2h_deploy.py` REV-3 sha256 `005211d4…4377c`
- Commits (path-limited, `deploy/` only, branch `reset/practical-pi-20260907`):
  `b510112` (fix) + `822be32` (stamp).
- Re-shipped: full `r2-habit-20260912/` pack + `PACK-SHA256.txt` (script hash +
  commit) so Brian can check staleness himself.

## For Corvid (verification)

Diff is 11+/6- in one file; suggested check: `git show b510112 -- deploy/`
+ re-run the four probe cases above. Day-0 unblocked on Brian's work machine
via `check --pi-cmd ~/pi-dev/pi-dev`.
