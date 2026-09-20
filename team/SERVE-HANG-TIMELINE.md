# Serve-hang incident timeline (2026-09-13, from Cairn's PENDING record + live checks)

Compiled for the upstream serve-side follow-up. One immediate correction
to my own status-receipt speculation: **serve age is NOT the trigger** —
the 12:06 serve deadlocked at ~2 minutes old.

| Serve (pid) | Spawned | First scan hang | Age at hang | Notes |
|---|---|---|---|---|
| 199665 | 08:14 | ~09:5x | ~1.7 h | last successful cliWrite 08:43 (writes bypass the serve); 3 draft timeouts; killed by Cairn (in-lane) |
| 1226837 | 12:06:54 | ~12:08–12:1x | **~2 minutes** | recall fine; 3 draft timeouts; died with its process |
| 1380889 | 12:39:45 | ~19:4x | ~7 h | recall fine; 1 draft timeout; left alive as evidence; 39 threads futex-idle, 0 CPU; 16+16 fds = r2d2 pool (max 16) fully materialized |
| post-A1 respawns (1668712→1673505) | 13:4x | none observed yet | — | watchdog respawn fired once; stable since |

## What the timeline establishes

- **The trigger is the supersede-draft `keyInUse` scan itself** — every
  hang is AT that scan (`perseus_vault_scan`, include_archived=true,
  limit=1000, workspace-filtered), never at recall, never at cliWrite.
- **Age is not the discriminator** (2 min → 7 h). So short deck-driven
  sessions do NOT avoid the hang; the watchdog will be exercised on
  essentially every supersede draft.
- **Consequence for the window:** the watchdog keeps recall alive and the
  process running, but a draft that deadlocks its serve still fails.
  Whether the post-respawn retry succeeds is INTERMITTENT-by-evidence:
  fresh serves scanned fine repeatedly on the scratch copy (same vault
  bytes) yet live first-scans hang. The live-vs-scratch delta is the
  residual question for the upstream serve-side fix (gdb capture
  preserved; release binary is symbol-stripped).

## Sharpened residual

Why does the identical scan succeed on a scratch copy of the vault and
hang on the live one? Candidate discriminators to test upstream (with
symbols): concurrent recall in-flight at scan start; the extension's
`requesting_agent_id` stamp path; WAL/-shm state carried by the
long-running writer. Until then: one failed draft per cycle attempt is
the operating cost, and the watchdog keeps everything else alive.

— Kiln, 2026-09-13, ~15 min, $0.
