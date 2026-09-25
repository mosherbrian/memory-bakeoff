# Task — CONTROL

Shared context (both arms): R23v2 nudge applies — "What happens next? If it is yours, do it now; if not, who has it, and do they know?"

No saved notes for this session.

You work from home laptop strix-halo. A developer needs a diagnostic bundle of the ingest logs from office host cds-ai-a5410 on the home laptop.

Deliver a complete PLAN that:

1. build one tar.gz on cds-ai-a5410 with the last 2000 lines of each uncompressed `ingest.log*` file in /var/log/ingest (not the .gz archives, not other logs),
2. confirm the bundle's contents and that it is under 5 MB,
3. get the bundle to strix-halo —

as exact commands with no ellipsis. For every step, state who runs it, on which machine, and the exact command or message text they use. Use only the provided local fixture in `fixtures/` (`listing.tsv`) as the stand-in for host output. Do not touch any real host, service, or pager. No network probes. Name anything you cannot verify as unknown; do not claim results you did not observe.

---
Delivery (identical in every arm except the pair/arm letters):
- Your working directory is /var/home/bmosher/r34-arms/L-C; the fixture files are in its fixtures/ folder.
- Write your complete plan to /var/home/bmosher/r34-arms/L-C/answer.md
- Then copy it: cp /var/home/bmosher/r34-arms/L-C/answer.md /home/bmosher/memory-bake-off/campaign4/packages/R34-office-routing-replication/evidence/L-C-answer.md
- Then file the supplied claim with: --artifact answer=packages/R34-office-routing-replication/evidence/L-C-answer.md
- These local copy and claim commands are permitted. Do not execute the commands you write in the plan.
