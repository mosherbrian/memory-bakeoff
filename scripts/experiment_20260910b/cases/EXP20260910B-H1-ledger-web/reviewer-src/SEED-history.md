# SEED HISTORY — EXP20260910B-H1 (project label: `ledger-web`)

Seed BOTH conversations into the slot's isolated store as prior sessions of
this project, preserving message text VERBATIM (the verifier checks values
that appear word-for-word below). Timestamps are part of the seed.

## Conversation 1 — load-bearing

- title: "production deployment planning"
- date: 2026-08-28

```
[2026-08-28 10:12] USER: Ops walked me through the host today. We need to
lock the production serving setup for the dashboard before tonight.

[2026-08-28 10:14] ASSISTANT: Understood. The reverse proxy (nginx) on that
host fronts the app, so the app itself should never listen on a public
interface — it must bind to 127.0.0.1 only and let the proxy handle the
outside world.

[2026-08-28 10:15] USER: What about the port?

[2026-08-28 10:16] ASSISTANT: Not 8080 — the metrics sidecar already owns
8080 on that host, which is why the staging attempt failed to start last
week. Use port 4370 for the app.

[2026-08-28 10:18] USER: And certificates?

[2026-08-28 10:19] ASSISTANT: TLS terminates at the nginx proxy, so the app
must serve plain HTTP: keep tls OFF in the app config. If you enable tls in
the app too you get a double-termination loop and the health checks die.

[2026-08-28 10:20] USER: Agreed. DECISION: ledger-web production serves on
127.0.0.1:4370, plain HTTP, TLS off in the app — the proxy terminates TLS.
I'll put it in the deployment ticket too.
```

**SEED VERBATIM (load-bearing sentence):** "DECISION: ledger-web production
serves on 127.0.0.1:4370, plain HTTP, TLS off in the app — the proxy
terminates TLS."

## Conversation 2 — filler (irrelevant)

- title: "chart palette"
- date: 2026-08-30

```
[2026-08-30 15:02] USER: The usage charts are hard to read. Pick a palette.

[2026-08-30 15:04] ASSISTANT: Use indigo for the primary series and amber
for the comparison series; both clear on the dark theme.

[2026-08-30 15:05] USER: Fine, indigo + amber it is.
```
