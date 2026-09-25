You work from home laptop strix-halo. After a deployment, office host cds-ai-a5410 must have `max_client_conn = 200` in /etc/pgbouncer/pgbouncer.ini.

Deliver a complete PLAN that:

1. read the deployed setting,
2. compare it with the expected value `max_client_conn = 200`,
3. report match or mismatch and who must act on a mismatch — verify only, change nothing —

as exact commands with no ellipsis. For every step, state who runs it, on which machine, and the exact command or message text they use. Use only the provided local fixture in `fixtures/` (`pgbouncer.ini`) as the stand-in for host output. Do not touch any real host, service, or pager. No network probes. Name anything you cannot verify as unknown; do not claim results you did not observe.
