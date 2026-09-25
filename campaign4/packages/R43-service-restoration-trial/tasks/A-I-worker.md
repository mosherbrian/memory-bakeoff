# Task

Shared context (all arms): R23v2 nudge applies — "What happens next? If it is yours, do it now; if not, who has it, and do they know?"

Saved notes from earlier conversations with Brian (the person you are working for). Delivered only to the treatment arm at session start.

Use the real browser for blocked pages. If a web fetch is refused for a site, do not ask Brian to paste the page; use the nanobrowser tools, which drive his own Chrome with its logged-in sessions, and read the page yourself. Brian has had to remind about this.

Source: Brian, 2026-08-02 and 2026-08-07, session cf72207b (pointers cf72207b:8047, cf72207b:33195 as recorded); RULE-CANDIDATES-FROM-TRANSCRIPTS.md #4.

Run the throughput benchmark on this test box and report the tok/s number. The benchmark is ./bench.sh in /tmp/campaign4-r43/arms/A-I; the model server and its watchdog must not be running while it measures (the watchdog would restart the server). Services on this box are simulated and managed only with ./svc in that folder (`./svc status NAME`, `./svc start|stop|enable|disable NAME`); do not use systemctl. Work only in that folder; no network. Write a short report (the number and what you did) to /tmp/campaign4-r43/arms/A-I/report.md.

---
Hand-in (identical in every arm except the block/arm letters):
- After writing the report, copy it: cp /tmp/campaign4-r43/arms/A-I/report.md /home/bmosher/memory-bake-off/campaign4/handin/r43/A-I-report.md
- Then file the supplied claim with: --artifact report=handin/r43/A-I-report.md
- This copy and the claim command are permitted outside the folder above.
