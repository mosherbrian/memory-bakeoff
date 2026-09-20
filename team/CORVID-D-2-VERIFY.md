# CORVID-D-2-VERIFY — artifact verification of row D-2

Verifier: corvid-dsh, 2026-09-17 11:19 PDT. Author: kiln-flash (claimed 09:47,
closed 10:00), with a post-close harness repair by cairn (10:50, disclosed in
the row). Artifacts: the installed `/home/bmosher/.config/agent-deck/
acp-worker` and `/home/bmosher/conductor-chat/workers/test-acp-worker.sh`.
Declared check: `bash workers/test-acp-worker.sh`. I am the named verifier;
kiln and cairn authored.

**Verdict: VERIFIED PASS — the row's two-part contract (harness gets a socket,
then the fix installs) verifies end to end, including under cairn's
re-failure condition.**

## What was run

1. **Declared check, three times, under both shells:**
   - plain non-interactive shell → **4 passed / 0 failed, rc 0**
   - `bash test-acp-worker.sh < /dev/null` — the exact condition of cairn's
     re-failure (background worker got /dev/null stdin, exited on EOF before
     the socket bound, 2/4) → **4/4, rc 0**
   - repeat under /dev/null → **4/4, rc 0** (stability, per the D-4 transient
     lesson: one green run is not a gate).
2. **The installed worker carries the fixes** (mtime 09:13:29, before the
   10:00 close):
   - reader keeps the worker alive on engine EOF — the old `os._exit(1)`
     behavior is documented at the site it was removed from (line 753), so
     the socket no longer goes stale behind a dead process;
   - `prompt()`'s dead-engine path names the exit immediately:
     `engine process has EXITED (code N) - no reply was produced for this
     prompt` (lines 1052–53). The body carries the poller's mute-marker
     substring, so `seat_mute` escalates on it by itself instead of the old
     600-second stall;
   - the EXITED body is excluded from the proven-save (lines 1070–71) — the
     unproven session id is still not persisted.
3. **The harness repairs are in** (test-acp-worker.sh, mtime 10:50:39):
   - `WORKER` default is absolute (line 23) — the S4 no-$HOME rule;
   - `run_case` feeds the worker a stdin that stays open (`sleep 60 |`,
     line 73) — the fix for cairn's non-interactive re-failure, simulating
     the live pane;
   - connect retries past the file-before-listen beat (line 83), the row's
     original socket-appears-within-the-wait premise.
4. **Timeline honestly disclosed:** the harness changed at 10:50 — after
   kiln's 10:00 stamp — and the row says so in cairn's RE-FAILURE + FIX note
   ("verify the fix, not just the suite"). Verified the fix: the suite is
   green precisely where it failed before, from the seat-independence
   condition that broke it. acp-worker 09:13 < claimed 09:47 < done 10:00;
   the one post-close mtime is disclosed, not silent.

## Limits

- The dead-engine EXITED path is unit-exercised by the suite's cases; I did
  not kill a live engine in a production worker to see the message in a real
  pane — the poller's next real dead-engine incident is the field test.
- "Live workers pick the fix up on their next managed restart" remains
  kiln's stated deployment bound; as with D-1, harmless until then because
  the old behavior is degraded-late rather than wrong-by-default.
