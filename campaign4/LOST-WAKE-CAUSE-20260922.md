# Why completions were lost: backtest of all 18, from kiln's own history

**Filed by** Claude (observer), 2026-09-22, at Brian's request. Reads only.
Tool: `~/projects/agent-loop/tools/backtest_wakes.py` (reproducible:
`python3 backtest_wakes.py control-events.tsv ~/.config/agent-deck/acp-history/a79067ca-1790000758.jsonl`).

**Method.** A loss is a COMPLETED row whose note says the completion was lost
("lost completion", "lost wake", "found in history not inbox", "no wake
sent"): 18 rows, 2026-09-21 23:26Z to 2026-09-22 21:33Z. For each, kiln's
history (every command with its output) was searched between the dispatch
and the recorded completion for a command that sends to cairn. Checked by hand
against kiln's full command list: no other send method appears in any window.

## Result

| case | count | meaning |
|---|---|---|
| a | 17 | kiln sent no wake at all (2 of these: turn killed by the 120 s stall watchdog before it could) |
| b | 1 | sent and failed: P6r13-initial-1, "matches no session" (missing profile; fixed in `wake` today) |
| c | 0 | delivered but not acted on |

**The controller was not at fault.** Neither "inbox missed" nor "wake-exe no
cairn match" (P6r5-recovery-1) was right: that turn was killed at 03:18:36Z by
`[stall] no response for 120s`, and no wake was ever attempted.

## Why kiln stopped sending

1. **Every dispatch says "Claim+wake cairn on completion" (17 of 18 prompts,
   all receipts) but never gives the command.** `wake` is not on PATH; the
   working form is `AGENTDECK_PROFILE=campaign4 ~/.config/agent-deck/wake cairn "..."`.
2. **Kiln knows that form only while its own conversation holds a working
   example.** 2026-09-21 14:53-19:43Z it woke cairn 12 times with the full path
   and lost nothing.
3. **Every context reset erased it.** The seat move on the evening of 09-21,
   then five stall-watchdog kills that rebuild the session (09-22 03:18, 07:06,
   09:35, 10:23, 14:48Z). After a reset kiln sent nothing, or guessed: at 17:30Z
   it ran `cairn-wake` and `wake-cairn` ("command not found"), and at 18:40Z
   and 19:58Z it wrote "No wake binary on host - claim filed at pinned
   claim_path for cairn pickup". At 21:29Z it read `wake --help` and used it
   (no profile: case b); at 22:06Z it worked.

The same lesson as the ledger edits: a model recovering from files copies
what it can see. An instruction without the exact command fails after every
reset.

## What would stop it (the dispatch text is the director's)

- Put the exact command in every dispatch and receipt:
  `AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake cairn "<qid> COMPLETE claim=<claim_path>"`.
- The stall watchdog is now 1800 s (was 120 s), so resets are rarer.
- Coax (live since ~22:35Z) catches any remaining case within ~3 minutes and
  now names the case (a/b/c) in its message; `wake` now logs failures, tells
  Claude, and records a 120-char excerpt so a wake can be tied to its dispatch.

## Per-loss output
    a  P5-repair-1              done 23:26  tries=0  turn ended without a wake; last words at 23:23:50: tor-repair-decision.md all addressed; accepted packages untouched; verification.md preserved; no live effects.
    a  P5-repair-2              done 23:33  tries=0  turn ended without a wake; last words at 23:32:47: subevents; invalid pairs rejected pre-write with both rows absent; replay idempotent; no new duplicate bodies.
    a  P5r2-initial-1           done 23:43  tries=0  turn ended without a wake; last words at 23:41:29: c76c0f49962951c603705a4848d7ba0d8a45a27d213 tests/test_repair.py Test counts: 83 passed here + 59 core passed.
    a  P6-stageA-1              done 23:54  tries=0  turn ended without a wake; last words at 23:51:51: no state.json, no ledger adoption, no wrapper changes, no clock change, no live effects, no research workload.
    a  P6-repair-1              done 00:04  tries=0  turn ended without a wake; last words at 00:01:43: D4: durable one-shot timers with restart-proof repeat/stale/early/cancelled rejection, ledger-deadline arming.
    a  P6r2-stageA-1            done 00:19  tries=0  turn ended without a wake; last words at 00:16:12: n; (5) executable placeholder-free fixture plan (not executed); (6) 107+59 + D2/D3/D4 retained, no dup bodies.
    a  P6r21-stageA-1           done 00:29  tries=0  turn ended without a wake; last words at 00:26:29: al/pause effects, no historical edits, no research, no script retirement, four seats never repurposed/stopped.
    a  P6r21-repair-1           done 00:46  tries=0  turn ended without a wake; last words at 00:44:40: rotation lossless, notified vs replay-fallback labeled. Broken-behavior tests changed with explicit rationale.
    a  P6r3-stageA-1            done 01:16  tries=0  turn ended without a wake; last words at 01:14:32: with no duplicate effects; cleanup verifies before reporting. No retroactive PASS claimed on prior provenance.
    a  P6r3-recovery-1          done 01:41  tries=0  turn ended without a wake; last words at 01:38:25: D2 runner-backed host timers, D3 honest check-latency gates, D4 reconciling rollback — all retained and green.
    a  P6r4-stageA-1            done 02:02  tries=0  turn ended without a wake; last words at 02:00:30: t-delivered + ledger proof, ambiguous stays pending with rollback BLOCKED, same-identity crash reconciliation.
    a  P6r5-recovery-1          done 03:24  tries=0  turn KILLED by the stall watchdog at 03:18:36: [stall] no response for 120s (ACP_STALL_SECS) - ending the turn; the next prompt
    a  P6r8-recovery-2          done 07:52  tries=0  turn ended without a wake; last words at 07:48:59: al full run green. Claim at `completion-claims/ex-p6r8-recovery-2.json`, verdict COMPLETE, no residual faults.
    a  P6r9-repair-2            done 14:13  tries=0  turn ended without a wake; last words at 14:11:32: treating this completion message + claim file as the wake. Verdict returns to Tern; no live authority claimed.
    a  P6r9-repair-3            done 15:14  tries=0  turn KILLED by the stall watchdog at 14:48:08: [stall] no response for 120s (ACP_STALL_SECS) - ending the turn; the next prompt
    a  P6r11-rejection-1        done 18:42  tries=0  turn ended without a wake; last words at 18:40:36: rvid 30m verify pending). No wake binary on host — claim filed at pinned `claim_path` for cairn/corvid pickup.
    a  P6r11-routing-repair-1   done 20:01  tries=0  turn ended without a wake; last words at 19:58:37: ved: corvid 25m verify pending). No wake binary on host — claim filed at pinned `claim_path` for cairn pickup.
    b  P6r13-initial-1          done 21:33  tries=2   | wrote claim wake: 'cairn' matches no session, or more than one 
    
    total: 18 lost  a=17 (never sent; 2 of them: turn killed by the stall watchdog)  b=1 (sent, failed)  c=0 (arrived, not acted on)
