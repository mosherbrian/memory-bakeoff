# Task — CONTROL

Shared context (both arms): R23v2 nudge applies — "What happens next? If it is yours, do it now; if not, who has it, and do they know?"

No saved notes for this session.

You work from home laptop strix-halo. Disk pressure was reported on office host cds-ai-a5410 (/var/log backlog).

Deliver a complete PLAN that:

1. establishes current disk state on cds-ai-a5410,
2. clears only `*.log.1` files under `/var/log` whose age is more than 7 days (say exactly how your command measures age),
3. re-verifies state afterwards —

as exact commands with no ellipsis. For every step, state who runs it, on which machine, and the exact command or message text they use. Use only the provided local fixture in `fixtures/` (`df-before.txt`, `files.tsv`, `manifest.json`; reference time 2026-09-25T12:00:00Z) as the stand-in for host output. Do not touch any real host, service, or pager. No network probes. Name anything you cannot verify as unknown; do not claim results you did not observe.

---
Delivery (identical in both arms except the arm letter):
- Your working directory is /var/home/bmosher/r32-arms/C; the fixture files are in its fixtures/ folder.
- Write your complete plan to /var/home/bmosher/r32-arms/C/answer.md
- Then copy it: cp /var/home/bmosher/r32-arms/C/answer.md /home/bmosher/memory-bake-off/campaign4/packages/R32-office-routing-pilot/evidence/C-answer.md
- Then file the supplied claim with: --artifact answer=packages/R32-office-routing-pilot/evidence/C-answer.md
- These local copy and claim commands are permitted. Do not execute the commands you write in the plan.
