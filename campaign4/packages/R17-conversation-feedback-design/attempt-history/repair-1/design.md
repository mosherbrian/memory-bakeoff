# R17 design (repair 1): does delivering saved conversational feedback improve usable work?

**What is tested:** whether a frozen packet of three saved notes, delivered at the start of a fresh session, changes whether kiln's ordinary deliverables are usable AND comply. The notes are two of Brian's stated preferences plus one sourced environment constraint. This measures availability and use of saved memory, not retrieval, summarising, compaction or a memory product, and not general memory efficacy. The original design and the INCOMPLETE review are kept in attempt-history/initial.

## Rules (quotes and pointers in cases.json; Brian's words kept apart from memory-file generalisation)
| Rule | Brian said | Scope |
|---|---|---|
| R-PY: `python`/`pip`, not `python3`/`pip3` | 2026-08-21; 2026-08-24 "You keep forgetting after compaction. ... Use python, not python3." | anything Brian or a coworker runs |
| R-LB: no loopback destination offered to him | 2026-08-10 "You're still using 127.0.0.1 which is mostly useless." | addresses to open, and binds of services he reaches remotely |
| R-NET: from the home laptop, office machines are not reachable by Claude | 2026-08-26, 2026-08-28 ("I feel like we have written down that you can't reach my work network from home"), 2026-09-25 | a fixed scenario stated in the prompt, not a claim about today's network; no probes |
R-PID is dropped: it was Claude's own lesson, not a verified Brian preference. The transcript leads for delivery workflow, re-enabling services and "do not stop" are parked for later steps, not discarded.

## Equal inputs, one difference
Both arms get the identical prompt, the identical fixed scenario (NET cases: home laptop strix-halo; office gateway cds-ai-a5410; Qwen is the office-side assistant) and identical ordinary inputs (PY-2: shared/audit.py). Only T also gets memory-packet.md. The reachability fact itself exists only in saved memory, not in project docs, so the control lacks it, as in real work. That is the intervention, not a withheld document. The kiln-loaded instruction files contain none of the three rules. The rules do exist on disk (the memory dir, campaign4), so each arm works in a fresh empty dir with only its inputs, and a contamination scan flags any read of ~/.claude or campaign4. Model prior knowledge is not excluded.

## Scoring (frozen before outputs)
The per-case rubric in cases.json decides, and corvid adjudicates. checks.py only flags: compliant / violation / not-applicable / needs-adjudication. It reads fenced, indented, inline and `$`-prompt code, and treats a loopback URL in a negated clause as a warning. It reports first-person execution claims for R-NET. It is not a parser framework. Unsupported shapes return needs-adjudication, never a verdict.
- **Usable:** does the deliverable do the requested job for the stated audience? R-PY is language-neutral: a usable non-Python answer is "not-applicable", reported separately and never counted as remembering. R-NET: "I can't reach it" without exact handoff steps is not usable.
- **Primary per case and arm:** usable AND compliant. Refusal or omission cannot win.
- **Report:** all 6 paired cases, per-rule totals, every not-applicable, needs-adjudication, missing or invalid result, and no causal or population claim.
Examples (examples-repair/) include conforming, violating, vacuous and ambiguous cases for each rule, plus corvid's surviving counterexamples (README-only pip steps, an indented python3 command, a warning URL next to a good one). selfcheck.txt shows each example's aid status.

## Future loop arrangement (not authorised here; the trial is named R18)
Unchanged from the original: 12 single-turn loop packages, a per-case coin for arm order, the R10 checks plus /new before each, kiln working in /var/home/bmosher/r18-arms/<case>-<arm>/ with the case inputs copied in, the evidence copied to packages/R18-*/evidence/ as the claim artifact, corvid verifying with the rubric plus the aid and never messaging kiln. About 130 seat-minutes plus a 20-minute outcome review.
