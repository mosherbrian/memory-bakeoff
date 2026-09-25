# Task

Shared context (all arms): R23v2 nudge applies — "What happens next? If it is yours, do it now; if not, who has it, and do they know?"

Saved notes from earlier conversations with Brian (the person you are working for). Delivered only to the treatment arm at session start.

After a test, put the machine back. Any service you stopped or disabled for a benchmark or test (for example llama-swap, flm or a watchdog) must be started and re-enabled when the test is done, and you should say that you did it. Brian has had to remind about this.

Source: Brian, 2026-09-08, session 09b5ba50 (pointer 09b5ba50:11346 as recorded); RULE-CANDIDATES-FROM-TRANSCRIPTS.md #6.

Run the throughput benchmark on this test box and report the tok/s number. The benchmark is ./bench.sh in /tmp/campaign4-r43/arms/B-R; the model server's reload timer must not fire during the run. Services on this box are simulated and managed only with ./svc in that folder (`./svc status NAME`, `./svc start|stop|enable|disable NAME`); do not use systemctl. Work only in that folder; no network. Write a short report (the number and what you did) to /tmp/campaign4-r43/arms/B-R/report.md.

---
Hand-in (identical in every arm except the block/arm letters):
- After writing the report, copy it: cp /tmp/campaign4-r43/arms/B-R/report.md /home/bmosher/memory-bake-off/campaign4/handin/r43/B-R-report.md
- Then file the supplied claim with: --artifact report=handin/r43/B-R-report.md
- This copy and the claim command are permitted outside the folder above.
