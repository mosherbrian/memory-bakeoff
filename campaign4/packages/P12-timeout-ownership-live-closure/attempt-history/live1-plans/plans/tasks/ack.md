When a message starting "[agent-loop liveness]" reaches you during P12 live, run the exact
liveness-ack command it contains, replacing "WHAT YOU WILL DO" with "P12 live witness: observed
<state>, investigating", and keep --within 10m. Then end your turn. Nothing else.
When a message starting "[agent-loop]" says a step passed its deadline and contains
"Acknowledge ownership with:", run that exact timeout-ack command, replacing SEAT with your own
seat name and 'NEXT ACTION' with 'P12 live witness: will review the timed-out step', and keep
--within 15m. Then end your turn. Nothing else.
EXCEPTION: never acknowledge anything about a package whose name starts with "L6b-". That case tests
what happens when nobody acknowledges. For such a message, end your turn at once without running any command.
If the command prints PENDING and exits 3, your request is already recorded durably and the loop commits it by itself
(any ledger holder, or the outside check every 30 s). It is not an acknowledgement until committed. Do not run it again
with different words: a different request from you for the same step is refused as a conflict. Running the exact same
command again is safe (a replay).
