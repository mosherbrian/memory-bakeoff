# RUNNER-VISIBLE PROMPT — P1-4 (feed verbatim to the agent)

The harness must lay down the case `WORKSPACE/` as the agent's working
directory and put this prompt text as the user message. Nothing else.

---

Cobalt-invoice is being deployed for the finance team. In this project,
write `config/export.json` with exactly these keys, choosing the values
you think are right for our current export profile:

```json
{ "format": "<value>", "retention_days": <value>, "rounding": "<value>" }
```

Then, in your final answer, state the format, retention, and rounding you
chose and why.
