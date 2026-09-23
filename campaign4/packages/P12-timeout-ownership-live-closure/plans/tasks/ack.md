When a message starting "[agent-loop liveness]" reaches you during P12 live, run the exact
liveness-ack command it contains, replacing "WHAT YOU WILL DO" with "P12 live witness: observed
<state>, investigating", and keep --within 10m. Then end your turn. Nothing else.
When a message starting "[agent-loop]" says a step passed its deadline and contains
"Acknowledge ownership with:", run that exact timeout-ack command, replacing SEAT with your own
seat name and 'NEXT ACTION' with 'P12 live witness: will review the timed-out step', and keep
--within 15m. Then end your turn. Nothing else.
