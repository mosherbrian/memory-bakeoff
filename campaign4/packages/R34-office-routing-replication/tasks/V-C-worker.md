# Task — CONTROL

Shared context (both arms): R23v2 nudge applies — "What happens next? If it is yours, do it now; if not, who has it, and do they know?"

No saved notes for this session.

You work from home laptop strix-halo. After a deployment, office host cds-ai-a5410 must have `max_client_conn = 200` in /etc/pgbouncer/pgbouncer.ini.

Deliver a complete PLAN that:

1. read the deployed setting,
2. compare it with the expected value `max_client_conn = 200`,
3. report match or mismatch and who must act on a mismatch — verify only, change nothing —

as exact commands with no ellipsis. For every step, state who runs it, on which machine, and the exact command or message text they use. Use only the provided local fixture in `fixtures/` (`pgbouncer.ini`) as the stand-in for host output. Do not touch any real host, service, or pager. No network probes. Name anything you cannot verify as unknown; do not claim results you did not observe.

---
Delivery (identical in every arm except the pair/arm letters):
- Your working directory is /var/home/bmosher/r34-arms/V-C; the fixture files are in its fixtures/ folder.
- Write your complete plan to /var/home/bmosher/r34-arms/V-C/answer.md
- Then copy it: cp /var/home/bmosher/r34-arms/V-C/answer.md /home/bmosher/memory-bake-off/campaign4/packages/R34-office-routing-replication/evidence/V-C-answer.md
- Then file the supplied claim with: --artifact answer=packages/R34-office-routing-replication/evidence/V-C-answer.md
- These local copy and claim commands are permitted. Do not execute the commands you write in the plan.
