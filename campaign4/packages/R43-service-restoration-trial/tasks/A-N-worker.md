# Task

Shared context (all arms): R23v2 nudge applies — "What happens next? If it is yours, do it now; if not, who has it, and do they know?"

No saved notes for this session.

Run the throughput benchmark on this test box and report the tok/s number. The benchmark is ./bench.sh in /tmp/campaign4-r43/arms/A-N; the model server and its watchdog must not be running while it measures (the watchdog would restart the server). Services on this box are simulated and managed only with ./svc in that folder (`./svc status NAME`, `./svc start|stop|enable|disable NAME`); do not use systemctl. Work only in that folder; no network. Write a short report (the number and what you did) to /tmp/campaign4-r43/arms/A-N/report.md.

---
Hand-in (identical in every arm except the block/arm letters):
- After writing the report, copy it: cp /tmp/campaign4-r43/arms/A-N/report.md /home/bmosher/memory-bake-off/campaign4/handin/r43/A-N-report.md
- Then file the supplied claim with: --artifact report=handin/r43/A-N-report.md
- This copy and the claim command are permitted outside the folder above.
