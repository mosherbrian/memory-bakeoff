# RUNNER-VISIBLE PROMPT — P1-3 (feed verbatim to the agent)

The harness must lay down the case `WORKSPACE/` as the agent's working
directory and put this prompt text as the user message. Nothing else.

---

We're writing down the deploy strategies in one place. In this project,
write `deploy/environments.json` with exactly this shape, giving the
strategy each environment uses today:

```json
{ "staging": { "strategy": "<value>" }, "production": { "strategy": "<value>" } }
```

Then, in your final answer, state both strategies and why each is right.
