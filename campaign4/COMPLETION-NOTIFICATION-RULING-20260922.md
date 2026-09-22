# Completion notification must survive a fresh session

Tern; 2026-09-22T22:57:35.364545+00:00. Effective immediately, all manual worker AND
reviewer dispatches and durable receipts contain the exact executable completion
notification command, with bound profile, destination session ID, action ID, and
absolute claim/verdict path substituted before send. A prose instruction, PATH
lookup, prior conversation example, or pointer alone is insufficient. This extends
31447c3; it does not replace exact-ID identity with title inference.

Cairn generates the command from the dispatch's validated destination binding and
shell-quotes every argument. Each dispatch text includes the command inline even
when the rest of the task is a path+hash reference; correctness outranks the short
wake target. Receipt records the same command/argv. Rebind when sessions change;
never copy an old ID without checking profile/role. Tern follows this too.

Sequence: write the truthful final claim/verdict first, execute the provided command,
preserve host send time/rc/stdout/stderr in a separate notification receipt. Report
INCOMPLETE/FAIL as such, not COMPLETE by habit. Notification failure does not alter
artifact completion or justify rerunning work. Started/queued are transport states,
not proof of controller action. Preserve ambiguous delivery for reconciliation, no
blind resend. A final conversational answer alone is not a delivered notification.
Dead-turn recovery still requires independent supervision: a killed process cannot
execute even a correct command. Coax/openwork remain Brian-authorized and unchanged.

Cause attribution: read LOST-WAKE-CAUSE-20260922.md @197be51. Its kiln-history
backtest of 18 tagged losses reports 17 never sent (including two watchdog kills),
one failed send, zero delivered-and-ignored. This director has read the report,
not independently rerun all 18 windows. Accept this as current incident evidence:
these losses do not support blaming cairn for ignoring delivered notifications.
Do not generalize the sample to every historical anomaly. Missing self-contained
commands are a dispatch-contract defect I own. Earlier conflicting descriptions
are superseded by this linked finding, not edited out of historical ledger rows.

Active R13 completion-3: add the exact command below as an additive receipt/dispatch
supplement; no overwrite of original receipt, no restart, new allocation or deadline
reset. Cairn forwards once only if kiln remains active and lacks it; if completion
already arrived, do not prod a finished task. Include a freshly instantiated command
in the subsequent corvid40m dispatch as well. No implementation/live scope change.

```sh
AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake 56513e0e-1790000758 'P6r13-completion-3 COMPLETE claim=/home/bmosher/memory-bake-off/campaign4/packages/P6-r13-core-record-integrity/completion-claims/ex-p6r13-completion-3.json'
```
For an incomplete result substitute INCOMPLETE for COMPLETE; the claim remains the
authoritative result. For corvid substitute its actual action ID and absolute
verdict path, fixed in that dispatch. The controller's eventual director notification
similarly includes the validated Tern destination, not an assumed cached command.
