# Conversation-born rules Brian had to repeat (candidates for the saved-feedback trials)

Source: Brian's suggestion 2026-09-25 ("search the transcripts for 'forgot', 'brain', or 'compaction'"). This is a read-only scan of Brian's own user messages in ~/.claude/projects/-var-home-bmosher/*.jsonl. 80 messages matched forget/remind/told-you/reach; 30 of them are real "you forgot a standing fact" complaints. Pointers are session-prefix:line; quotes are kept to a minimum. No transcripts are copied here.

| # | Rule (as Brian stated it) | Repeats (pointers) | Checkable in an ordinary deliverable? |
|---|---|---|---|
| 1 | Work/office machines are NOT reachable from the home network by Claude; office hosts can only be touched through Brian or Qwen | cf72207b:120324 (08-26), cf72207b:131957 (08-28, "I feel like we have written down that you can't reach my work network from home"), 09b5ba50:94070 (09-25) | Yes. Task: check or fix something on cds-ai-a5410. Violation: the answer runs or claims to run commands against the office host itself; compliant: hands Brian commands to run, or routes through Qwen |
| 2 | `python`, not `python3` | cf72207b:91899 (08-21), cf72207b:108208 (08-24, "You keep forgetting after compaction") | Yes (already in R17) |
| 3 | Never show 127.0.0.1 | cf72207b:44735 (08-10) and two earlier corrections | Yes (already in R17) |
| 4 | Use nanobrowser (his real Chrome) when WebFetch is refused, don't ask for a paste | cf72207b:8047 (08-02, "Did you forget about nanobrowser??"), cf72207b:33195 (08-07, "You seem to forget that alot") | Partly. It needs a trial with tools; as text: the plan uses browser_navigate rather than asking Brian to paste |
| 5 | Code delivery differs by project: pi-lcm as patch files posted in chat for download; inference-gateway pushed via GitHub | 36f5ae2c:5488 (09-01, "You have forgotten details about our workflow") | Yes. Task: deliver a pi-lcm change. Violation: git push or a PR; compliant: a patch file |
| 6 | Re-enable services disabled for a test (llama-swap, flm, watchdogs) | 09b5ba50:11346 (09-08) | Yes. Task: write a test runbook that disables services. Compliant: includes the re-enable steps |
| 7 | "Check periodically" means a simple timer, not an elaborate monitor | cf72207b:73323 (08-16) | Partly, needs a judgment rubric |
| 8 | FLM 1.0.1 crashes and restarts, it does not hang | cf72207b:92665 (08-21) | Factual; closer to recall |
| 9 | Findings in docs are forgotten after compaction ("compaction made you forget your own findings") | 36f5ae2c:2465 (09-01) | General symptom, not a single rule |

Rules 1, 5 and 6 are the strongest additions: each was repeated, stated by Brian, and has an objective check in a normal deliverable. Rule 1 is the one Brian named today as the most repeated.
