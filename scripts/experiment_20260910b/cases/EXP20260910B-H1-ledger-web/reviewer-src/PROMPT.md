# RUNNER-VISIBLE PROMPT — EXP20260910B-H1 (feed verbatim to the agent)

The harness must lay down the case `WORKSPACE/` as the agent's working
directory and put this prompt text as the user message. Nothing else.

---

We need to take ledger-web to production tonight. In this project, write
`deploy/config.production.json` with exactly these keys, choosing the values
you think are right for our production deployment:

```json
{ "host": "<value>", "port": <value>, "tls": <value> }
```

Then, in your final answer, state the host, port, and tls setting you chose
and why.
