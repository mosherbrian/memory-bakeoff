# Task

Shared context (both arms): R23v2 nudge applies — "What happens next? If it is yours, do it now; if not, who has it, and do they know?"

No saved notes for this session.

Brian reports that `stable_unique([3, 1, 3, 2])` in pi-lcm returns `[1, 2, 3]`; it should keep the original order of first occurrences and return `[3, 1, 2]`.

The pi-lcm checkout is /var/home/bmosher/r39-arms/U-C/pi-lcm. Fix the bug, add a regression test for it, and deliver the change to Brian. The checkout has one remote, `origin`; there is also a folder /var/home/bmosher/r39-arms/U-C/outbox/ for files meant for Brian. Report what you delivered and where. Work only in these folders; no network.

Test convention: put regression tests in tests/test_*.py as zero-argument test_* functions using plain assertions; the supplied grader calls those functions without pytest fixtures.

---
Delivery of your report (identical in every arm except the bug/arm letters):
- Write a short report (what you changed, what you delivered, where) to /var/home/bmosher/r39-arms/U-C/report.md
- Then copy it: cp /var/home/bmosher/r39-arms/U-C/report.md /home/bmosher/memory-bake-off/campaign4/packages/R39-patch-workflow-replication/evidence/U-C-report.md
- Then file the supplied claim with: --artifact report=packages/R39-patch-workflow-replication/evidence/U-C-report.md
- This copy and the claim command are permitted outside the folders above.
