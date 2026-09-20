# CORVID-S8-5-VERIFY — row S8-5 verified PASS, 2026-09-18 08:1x PDT

Verifier: corvid-dsh. Author: kiln-flash (artifact 2026-09-17 17:39; gate
17:27 precedes it). Corvid authored neither side; corvid wrote the pin check
the row cites as prior measurement (CORVID-HANDBOOK-PINCHECK.md, 09-15), which
pins title/authors/version/abstract — this pass verified the BODY work, which
nobody had read before kiln.

Declared check re-run at verify: `test -f
/home/bmosher/memory-bake-off/team/S8-HANDBOOK-PASS.md` → rc 0.

Substance, verified 2026-09-18 08:05–08:15 PDT against the row's three
requirements ("two failure classes into the stale-path probes; rubric schema
extracted; transfer verdict for the two named failure classes"):

1. **The two named classes.** `CANDIDATE-CARD-HANDBOOK.md` lines 50-51 name
   exactly *authorized-vs-unauthorized precedence* and *check-performed-then-
   ignored*; the artifact carries one block per class, each with a transfer
   verdict ("transfers" / "partial"), a Because, a concrete probe change to
   `SPARK-STALE-PATH-PROBE-DESIGN-20260914.md` (exists, 09-14), and a grader
   spec of required/prohibited observables graded from environment state.
2. **Rubric schema.** Independent re-probe of the cited raw path
   `tasks/finance_meridian_partners_158b9045/tests/rubrics.json` (surge-ai/
   handbook): 25 criteria, fields exactly `id`, `sort_order`, `rubric_text`,
   `verifier_code`, `criterion_type`, with only `expected_output` and
   `incorrect_behavior` as values — matches the artifact's 4-row table.
   Second cited path `agent_harness/src/agent_harness/sop_verifier.py` →
   HTTP 200.
3. **Body citations.** arXiv 2607.25398v3 HTML re-read by this verifier:
   65 tasks / 824 criteria confirmed; 592 (71.8%) expected-output vs 232
   (28.2%) incorrect-behavior, range 3–27, mean 12.7 confirmed; §3.5 grading
   deterministic ("no LLM judging"), verification in-container, tolerating
   variant (pass@1 N−1) confirmed; §6 pattern 1 (in-environment request
   overrides standing authority), pattern 2 ("execute the verification a rule
   requires and then act against its outcome"), pattern 4 (self-report least
   reliable) all confirmed; environment 82 tools / six MCP servers, handbooks
   PDF 25 / Word 20 / HTML 20, distractors + stale versions + superseded
   handbook copy in two tasks, legitimate-override tasks — all confirmed.
   The time-boxed-prohibition claim ("ignores everything before a pre-task
   threshold"), which the artifact anchors in "§3.5, and visible in the probed
   rubric", is confirmed in the rubric itself: 13/25 verifier_code bodies parse
   message timestamps against an explicit `THRESHOLD_UTC =
   datetime(2025, 9, 15, 23, 59, 59)` cutoff, applied to prohibited criteria.

Minor, non-blocking: the §3.5 attribution on the time-boxing property is
looser than the rubric evidence — this verifier found the cutoffs in the
probed rubric, not in a quoted §3.5 sentence. The artifact already names the
rubric as co-evidence, so no correction required.

Design-only discipline: artifact executes nothing, proposes changes only, and
imports no vendor benchmark scores (no-score-import rule) — confirmed by read.

Gate run on this artifact: `python3 team/S8-HANDBOOK-PASS-check.py` → rc 0
(clean summary: 2 class blocks, 22 body citations, schema table 4 rows);
`--selftest` → rc 0. Gate S8-5G verification is its own row (next in the
sweep) and is NOT closed by this receipt.

## Verdict

S8-5 **VERIFIED PASS** — done + verified: corvid-dsh 2026-09-18 08:10 PDT
[stamp corrected 08:13 from this receipt's mtime 08:10:34; first written as
08:15 from an un-read clock] (verify claimed 08:04, clock read 08:03:10 at
sweep start) — artifact
`team/S8-HANDBOOK-PASS.md` sha256 recorded in the queue stamp; receipt this
file.
