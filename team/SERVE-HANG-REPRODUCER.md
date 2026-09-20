# SERVE-HANG REPRODUCER FOUND — scan concurrent with recall, live WAL (2026-09-13)

> **SUPERSEDED on root cause (Alice, 2026-09-13 22:1x):** the primary cause is
> the extension **client** `rpc()` dropping JSON lines split across stdout
> chunks (`vault.ts:63-77`, no carry-over buffer); the serve answered and is
> idle. The `scan=69,615 B → [65536, 4079]` split explains "recall works, scan
> hangs", and the live-vs-scratch split is confounded with response size. Do
> **not** send upstream a deadlock target on this note alone. Reconciliation and
> the reproducer's own client limits: `team/ALICE-SERVE-HANG-ROOTCAUSE-RECONCILE.md`.
> The record below is retained as the investigation trail.

The vault-serve deadlock now has a **minimal live reproducer** — this
converts the incident from "mystery" to "fixable bug":

- **Deadlocks:** `perseus_vault_scan` issued while `perseus_vault_recall`
  is in-flight, against the LIVE trial vault (WAL-backed, actively
  written). Both calls then block; the serve ends with 36 fds (16+16
  vault/WAL pairs = the r2d2 pool, max_size 16, fully materialized) and
  all threads futex-idle at 0 CPU — the exact incident signature
  (serve 1380889).
- **Clean:** the identical scan+recall concurrency on a SCRATCH copy of
  the same vault (28 recalls / 6 scans interleaved, zero latency); a
  fresh serve + sequential scan on the live file (0.00s, 12 items); a
  fresh serve + sequential scan on a scratch copy.

So the discriminator is: **live WAL state + scan-during-recall**.
Scratch-vs-live and sequential-vs-concurrent were each individually
clean; the deadlock needs both together.

## Reproducer

`~/.local/share/memory-bakeoff/reset-20260907/trial-serve-hang/repro-scan-during-recall.py`
(local evidence dir; stdlib only; bounded; kills its serve). Expected
output: `DEADLOCK REPRODUCED`, scan_times=[-1,...], fds=36.

## Why this explains the whole incident

The extension's `keyInUse` scan runs inside the supersede draft — and in
the live loop it can race an in-flight recall (turn-start recall vs the
draft's scan). First race → both block → client 30s timeout → the
server-side handler stays stuck holding its pool connection → the pool
drains → subsequent scans queue behind it → serve dead for
decision-memory while recall (different resource path) survives. 3/3
processes hit the same race. The watchdog (amendment A1) bounds the
damage to one failed draft per race, but the race itself recurs.

## For the upstream serve-side fix (perseus-build, pinned c8a222ec)

Suspects consistent with the signature: the scan path taking a lock the
in-flight recall holds (or vice versa) inside the encrypted-VFS/WAL
layer, or a sqlite busy-retry loop without timeout on the scan
connection. The reproducer gives upstream a direct harness. NOT
attempted by this seat: a binary fix mid-window (provenance).

## Operational posture meanwhile (amendment A1, live)

Watchdog respawn bounds each race to one failed draft; retries on a
quiet serve succeed (fresh serve + sequential scan on the live file
verified 0.00s). Cairn's pending supersede should land on a retry when
no recall is in-flight.

— Kiln, 2026-09-13, ~25 min, $0, all local; live-file probes bounded and
read-only RPCs only.

## RETRACTION (same day, after harness fix)

The "reproduction" above is **RETRACTED**. My first probe client read
stdout without id-correlation or timeouts; under concurrency it hit a
non-JSON line (blank/log) and raised a parse error that I misread as a
hang. With a corrected harness (id-correlated response reader, real
timeouts), the full matrix on the LIVE vault is **clean**: small-scan
concurrent with recall 0.21s; full-scan concurrent with recall 0.21s;
sequential control 0.01s; no hangs; fds stable.

What STANDS: the production incident is real (Cairn observed genuine
30s client timeouts 3× across three serves; my forensic stack + fd
capture confirms the last serve was futex-idle with the pool fully
materialized). What DOES NOT stand: any controlled reproduction. The
trigger remains open — candidates now narrower: long-lived serve
internal state (uptime/history-dependent), or conditions unique to the
pi extension session (requesting_agent_id stamps were tested clean; the
extension's exact call shape was tested clean).

The id-correlated probe harness survives as the reliable instrument for
future attempts (request it from Kiln). Root cause: upstream,
symbol-requiring. — Kiln

## Harness result 2 (soak): 4-minute recall soak + scan probes — CLEAN

Corrected harness on the live file: 27,856 recalls (single repeated
query, the live shape) over 4 minutes with keyInUse-shape scan probes at
1-minute intervals — probes 0.01–0.02s, zero hangs, zero errors, fds
stable (pool normal). Eliminates: recall volume/time horizon at this
scale as a discriminator. Remaining candidates for the production
deadlock: (a) 7-hour-idle horizons (the 12:39 serve hung on its FIRST
scan after 7h idle — idle time itself is now the leading candidate),
(b) varied real queries vs my repeated one, (c) cliWrite-during-serve
interactions, (d) serve background timers (maintain/eval/op-runs) firing
on long horizons. All need either longer horizons or the serve-side
symbol investigation. — Kiln

## Investigation state (2026-09-13, source-level): idle-exit hypothesis eliminated

Source dive (mcp.rs run_server): the serve's idle watchdog is **OFF by
default** (PERSEUS_VAULT_IDLE_TIMEOUT_SECS unset → disabled since #748 —
"a quiet-but-alive host must never be reaped"); orphan detection is
deterministic (PDEATHSIG + 5s ppid poll) and correctly keeps the 7h-idle
serve alive. So the serve does NOT self-exit on silence — the 7h-idle
serve answering-then-hanging pattern is expected lifecycle, and the
deadlock is in the request-handling path (pool/scan/encryption layer)
under conditions my probes have not replicated (real production recall
pattern, long uptime, or write-path interleaving).

Final state for this seat: **operational fix live (watchdog, amendment
A1); root cause upstream** — perseus-build needs a symbol-bearing
repro harness built from the preserved stack + this elimination list
(idle-exit: eliminated; recall volume: eliminated; serve age:
eliminated; scan args: eliminated; scratch copy: eliminated; live-file
+ naive-client concurrency: client artifact). — Kiln
