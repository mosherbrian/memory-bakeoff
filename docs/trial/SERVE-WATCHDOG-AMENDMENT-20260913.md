# AMENDMENT: vault-serve watchdog (emergency, window-open) — 2026-09-13

**Authority:** GiLMore URGENT dispatch (fix the vault-serve hang blocking
Cairn's live-arm S1 cycles; window closes Tuesday EOD). This is a
mid-window amendment to the frozen extension lineage (060d842), filed
openly with before/after hashes for Verity review. Executed by Kiln.

## Incident (3/3 fresh processes, serves 08:14 / 12:06 / 12:39)

- Pattern: `recall` answers fine; the FIRST supersede-draft's `keyInUse`
  scan (`perseus_vault_scan`, include_archived=true, limit=1000) never
  returns → extension 30s client timeout → draft/supersede fails.
- The serve is internally deadlocked on the scan RPC: stdio socketpair
  alive, 39 threads futex-idle at 0.00s CPU, 16 vault + 16 WAL fds (the
  r2d2 pool, max_size 16, fully materialized). Transport probe: the
  stream is NOT dead, so a respawn-on-stream-death would never fire.
- Root cause is serve-internal (upstream perseus-build 2.23.2, pinned
  binary sha c8a222ec) and NOT yet identified: scratch-copy scans
  (sequential, concurrent, fresh serve on the live file) all succeed
  instantly — the deadlock lives in the long-lived serve's accumulated
  internal state. gdb thread capture preserved at
  ~/.local/share/memory-bakeoff/reset-20260907/trial-serve-hang/
  (release build is symbol-stripped; upstream reproduction with symbols
  is the follow-up).

## The fix (extension-side watchdog; minimal diff)

`vault.ts`: an RPC timeout now marks the server `suspect`; successful
RPC clears it; `restart()` kills the serve, resets the start promise,
and spawns a fresh one. `index.ts` `getServer()`: a suspect server is
respawned (with console receipt) before the next operation.

- Effects: the operation that hit the timeout still fails once (no blind
  retry of mutations); the NEXT call gets a FRESH serve, which is proven
  to answer instantly (diagnostic: fresh serve scanned the live vault in
  0.00s while the old serve was deadlocked).
- Recall is never dropped: respawn replaces the child; pi keeps its
  registered tools. (Contrast: killing the serve externally destroyed
  recall for the process — the old failure mode.)

## Provenance delta (window pin 060d842 → amendment A1)

| File | 060d842 | after A1 |
|---|---|---|
| index.ts | (pinned) | 24296ad6d4f9f4b2c866192d752f1e9c2b080e9c0abefab7283e5cad10ef89ff |
| vault.ts | (pinned) | 905f604cfa3c255e379b3467e0e32c295faa30f1cd3784659f1cb30899cc5f27 |
| other 5 code files | unchanged | unchanged |

No behavioral change on the happy path (no timeout → no respawn; same
queries, same prompts, same instruments S1–S6). S6 semantics unchanged:
the scan is the same MCP call on a fresh serve.

## Verification

- Extension suite: **47 pass / 0 fail** (46 pre-existing + 1 new watchdog
  lifecycle test: timeout→suspect→restart→NEW serve pid→recall answers).
- Deployment: worker-pi restart per the runbook resume procedure
  (state-only, 706090b) — the current process runs the old in-memory
  code and cannot self-heal; the fresh process gets the watchdog.

## Open items

1. Serve-side root cause: upstream perseus-build work with symbols
   (follow-up; NOT window-critical once the watchdog is live).
2. Verity review of this amendment (requested; GiLMore to route).
3. One failed draft per deadlock incident remains possible (cost noted).

— Kiln, 2026-09-13.
