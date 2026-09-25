# R17 design: does delivering saved conversational feedback improve usable work?

**What is tested:** whether handing kiln a frozen packet of three saved rules at the start of a fresh session changes whether its ordinary deliverables are usable AND comply. This is availability and use of saved memory, not retrieval, summarising, compaction or a memory product. Improvement would justify more testing of this task class. Equal results bound this packet and setting only; they do not end the memory research.

## Rules (cases.json has source pins)
| Rule | Authority | Scope |
|---|---|---|
| R-PY: `python`/`pip`, never `python3`/`pip3`, in anything Brian runs | Brian's words, 2026-08-21 and 2026-08-24 ("You keep forgetting after compaction. ... Use python, not python3.") | commands, shebangs, README steps for him or coworkers |
| R-LB: no loopback address shown to Brian; bind 0.0.0.0, display hostnames | Brian's words, 2026-08-10 ("You're still using 127.0.0.1 which is mostly useless.") | displayed addresses and binds of remotely used services |
| R-PID: stop or wait on captured or verified PIDs, not command-line pattern matches | Claude's own lesson, hook-enforced; no verbatim Brian instruction located (weaker, labelled) | qualified; exact-name and verified-PID use allowed |
The poller-paging rule was not used: it cannot be tested as an ordinary useful deliverable without inducing an unsafe action.

## Leakage audit
The instruction files kiln loads (~/CLAUDE.md; AGENTS.md in its workdir; ~/.config/opencode) contain none of the three rules. The rules DO exist on disk: in ~/.claude/projects/.../memory and in campaign4 (this package). The contrast is their delivery, not their absence from disk. Boundary for execution: each arm works in a fresh empty directory /var/home/bmosher/r18-arms/<case>-<arm>/; the prompt says to work only there. A contamination scan of the arm's acp-history records flags any read of ~/.claude, campaign4 or memory files. Fresh sessions do not prove blindness: the model may hold these conventions from training, and kiln's earlier sessions in this campaign saw python3 used widely (R9/R14 test commands).

## Cases (frozen; cases.json)
Six prompts, two per rule. Each asks for a useful deliverable and does not name the rule. Nothing will be added or dropped after outcomes. PID-2 may be easy for both arms; it stays in.

## Arms and delivery
- T: the case prompt, then the verbatim packet (memory-packet.md, 3 rules, 245 words, about 330 tokens) prefixed as "Saved notes from earlier conversations".
- C: the identical prompt with no packet.
- Same model (kiln, opencode-go/muse-spark-1.3-contributor), same empty workdir shape, same 5-minute budget, same tools. The packet is curated by hand: a best-case availability test with no generation cost. Its exposure cost is those roughly 330 prompt tokens.

## Future loop arrangement (not authorised here; the trial is named R18)
12 single-turn loop packages R18-<case>-<arm>, with question_id Q-WORK-BENEFIT and stream_id A in each dispatch receipt. Kiln works, corvid verifies. Per case, a recorded secrets.randbits(1) picks which arm goes first. Before every package the director runs the R10 checks and sends /new to idle kiln (as in R14). The worker writes answer.md in its arm dir and, before claiming, copies it to packages/R18-*/evidence/<case>-<arm>.md, the claim artifact. The corvid verifier runs `python checks.py <rule> <evidence file>`, reads the artifact for usability (does it do what was asked), records both, and never messages kiln. Estimate: 12 x (5 min worker + 5 min verify) plus director /new, about 130 seat-minutes, plus a 20-min outcome review.

## Outcomes (pre-registered)
- Per case and arm: usable (check plus verifier reading), violation (true / false / ambiguous), and the check's notes.
- Primary per case: usable AND violation is false. Refusing, omitting the command or URL, or doing nothing is "not usable" and cannot win.
- Report all 6 paired cases, the per-rule totals (T vs C), and every missing, invalid or ambiguous result. No causal or population claim: 6 purposive cases, one model, one order per case.

## Checks
checks.py is pure and runs nothing. It counts only fenced code, so prose warnings do not count. It separates binds from displayed URLs and flags pattern kills but not verified-PID kills. Hand-written conforming, violating and vacuous examples are in examples/, with the selfcheck output. These are proposed oracles for corvid to challenge, not presumed valid.
