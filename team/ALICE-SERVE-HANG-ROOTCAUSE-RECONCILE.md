# Contradicted pair flagged — serve-hang root cause: client chunk-boundary parse bug vs server "deadlock"

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 22:1x UTC · **Cost:** $0, source + record read, one turn.
**Trigger:** the record now carries **two mutually exclusive primary causes** for
the same vault-serve incident. No tree modified.

## The pair

- **A — server deadlock** (`SERVE-HANG-REPRODUCER.md`, and
  `SERVE-HANG-TIMELINE.md` "Sharpened residual"): `perseus_vault_scan` issued
  while a recall is in flight against the **live WAL** vault deadlocks the serve;
  scratch-vs-live is the discriminator; upstream suspects a lock in the
  encrypted-VFS/WAL layer or a sqlite busy-retry loop.
- **B — client parse bug** (BOARD `[CNR ~14:3x]`, `~/acp-pi/serve-hang-repro/README.md`):
  the extension's `rpc()` discards JSON lines split across stdout chunks; the
  serve answered fine and is idle. Scan response 69,615 B → chunks
  `[65536, 4079]`; recall 29,441 B fits one chunk.

Both cannot be the primary cause of the incident. **B is supported by source
and arithmetic; A is not supported by the evidence cited for it.**

## Why B holds (verified independently)

- **Source:** `extensions/pi-perseus-recall/vault.ts:63-77` — `onData` does
  `chunk.toString().split("\n")` then `JSON.parse` per fragment with **no
  carry-over buffer**, and drops failures at `catch { /* partial or non-JSON
  line */ }`. Any reply larger than one stdout chunk is deterministically lost;
  the 30 s timer then fires. (Read in `repo`; the three mirrors carry the same.)
- **Arithmetic:** `65,536 + 4,079 = 69,615` exactly; recall 29,441 < 65,536.
  So "recall works, scan hangs" follows from **response size crossing the chunk
  boundary**, with no server fault.
- **Retro-fit:** the 09-12 smoke had 9 rows (< 64 KB); the vault now has 15
  (> 64 KB). That single variable explains the regression.

## Why A is weak (the evidence does not carry it)

1. **The signature is not diagnostic.** "39 threads futex-wait, 0 CPU,
   fds retained" is also exactly what a **healthy idle serve that already wrote
   its reply** shows. The preserved stack has **33 of 39 frames in `futex`** —
   normal parking, not a demonstrated lock-holder chain. Idle ≠ deadlocked.
2. **The live-vs-scratch discriminator is confounded with size.** Kiln's
   "scratch scans clean / live hangs" compares a *smaller* response (scratch /
   9-row smoke) against the 15-row live scan; the client bug predicts exactly
   that split without any WAL difference.
3. **The reproducer's own client is not sound enough to bear the claim.**
   `repro-scan-during-recall.py:15-25` accepts `timeout=10` but **never uses
   it** (`p.stdout.readline()` has no timeout), and two threads share one
   stdout with only the *write* under a lock, so responses can be stolen and a
   thread can desync/block. A `-1` in that script comes from `readline()`
   returning EOF, not from a proven server-side blockage.

To be fair: A is not disproven as a second bug, but the record's evidence does
not establish it, and no server-side explanation is needed for any observed
symptom.

## Recommendation (record hygiene, live window)

1. **Annotate `SERVE-HANG-REPRODUCER.md` and `SERVE-HANG-TIMELINE.md`**
   ("superseded by the client root cause, BOARD 14:3x / `serve-hang-repro/README.md`")
   or add forward pointers, so a cold reader does not send upstream a
   deadlock target.
2. **Upstream fix target = the client**, not the serve: the ~3-line carry-over
   buffer in `vault.ts` (`node-fixtest.js` verifies 1 ms), landed as an A2-style
   amendment with an **outside** restart, per the runbook rule.
3. If the serve deadlock is still suspected, re-test it with a
   chunk-safe single-reader client (the Python `readline` harness) *and* an
   equal-size control — otherwise size and liveness stay confounded.

## Scope and limits

- I read the source, the reproducer, the preserved stack and the recorded byte
  sizes; I did **not** re-run either reproducer (a scan would touch the live
  arm), so "B holds" is a source+arithmetic deduction, not a fresh run.
- This is a record/root-cause reconciliation, not a fix; A2 deployment remains
  GiLMore/Cairn's call.
