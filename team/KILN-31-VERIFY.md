# kiln-flash second-seat verify — external-corpora verification + triage (QUEUE row 31)

**Verifier:** kiln-flash (sole doer seat) · **Date:** 2026-09-17 · **Cost:** $0, web reads only
**Subject:** the folded coverage on `team/RESEARCH-EXTERNAL-CORPORA-20260913.md`
(Brian's Deep Research report, filed UNVERIFIED): Corvid's
`CORVID-EXTERNAL-CORPORA-VERIFY-TRIAGE.md` (row artifact), Alice's
`ALICE-EXTERNAL-CORPORA-FULLPASS.md` + `ALICE-EXTERNAL-CORPORA-COSIGN.md`
(A1–A4), Assay's `ASSAY-EXTERNAL-CORPORA-SPOTCHECK.md` (incl. Rev 2).
Originally verifier Alice (furloughed, cannot file) — reassigned kiln-flash
2026-09-17.
**Independence:** I authored none of it — the report is Brian's external
Deep Research output; the triage, full pass, spot-check and co-sign are four
other seats' work. Blind holds.

## Declared check

`test -f /home/bmosher/memory-bake-off/team/CORVID-EXTERNAL-CORPORA-VERIFY-TRIAGE.md`
→ **exit 0**. ✓

## Cross-seat consistency (paper level)

The four documents reconcile with no outstanding contradiction: Corvid's Rev 2
folds Alice's A1 (vocabulary confirmed by card; "overstated" withdrawn) and A2
(labels LLM-annotated); A3's gating contradiction is resolved in Corvid's favor
with Assay's explicit Rev-2 withdrawal ("I conflated a public card with public
data"); A4's version pin is present. Assay's MindForge delta (abstract-only
UNVERIFIED) was closed by Corvid's Table-1 read exactly as both documents
record. The triage, full pass, spot-check and co-sign tell one story.

## Re-derived from primary sources this pass

| Claim | Source queried today | Result |
|---|---|---|
| SWE-chat `gated:"auto"`, card public, `odc-by` | HF API `SALT-NLP/SWE-chat` | exact ✓ (`private:false`, `gated:"auto"`, `license:"odc-by"`) |
| SWE-chat files gated (the L2 blocker) | datasets-server `first-rows` | **401** ✓ — blocker real; card README via `/resolve/` returns 200 ✓ |
| SWE-chat `prompt_pushback` includes `takeover`, `requirement_change`; labels **LLM-annotated** (A1/A2) | card README schema | verbatim ✓ (also `prompt_intent`, `user_persona`, `session_success` all "LLM-annotated") |
| Nebius SWE-rebench **67,074** / **64.3** / `cc-by-4.0` | HF API + card table | verbatim ✓ ("Total Count … 67,074", "Average Count … **64.3**") |
| Open-SWE-Traces: report's **511,668** wrong; v1.0 ≈207k, post-filter **151k**, `cc-by-4.0` | HF API + card | substance ✓ — card news: "Released 207k agent trajectories", "Now, v1.0 includes 151k"; `511,668` appears nowhere |
| Wisp MIT | HF API | `license:"mit"` ✓ |
| MEnvData-SWE-Trajectory apache-2.0 | HF API | `license:"apache-2.0"` ✓ (3,872 count not re-derived; license was the card-level gate) |
| Programming by Chat 11,579 / 74,998 / 899 (Alice fullpass) | arXiv API `2604.00436` | verbatim ✓ ("74,998 developer messages from 11,579 chat sessions across 1,300 repositories and 899 developers") |
| MindForge 1,001 / 181.6 / 177K (Corvid, paper Table 1) | arXiv API `2607.27146` | paper exists and is the right one (from-scratch program-development environments); counts are body/Table-level and stay Corvid's read — consistent with every seat's stated bound |

## Two new notes (non-blocking)

1. **Open-SWE-Traces card has drifted since 2026-09-13.** The exact figure
   "207,489" is no longer on the public card — today it says "207k" (v1.0
   release news) and leads with "151k" (post-filter) for v1.0. The seats' 09-13
   citations were accurate as of their read; the drift itself proves Alice's A4
   (pin the version) is load-bearing, not cosmetic. The report's 511,668 remains
   wrong under any version.
2. SWE-chat's card annotates **four** schema fields LLM-annotated
   (`prompt_intent`, `prompt_pushback`, `user_persona`, `session_success`) —
   wider than the two A2 names. A2's re-derive-before-scoring rule should cover
   all four.

## Discipline check

No score import anywhere in the folded coverage: the triage is lanes,
blockers and design rules; the frozen P2 leaderboard is untouched; the report
is treated as candidate discovery throughout. Blockers correctly assigned
(SWE-chat gate → Brian's account decision; MindForge license; Programming by
Chat privacy; dedupe prerequisite; OST count correction).

## Verdict

**PASS.** The row's done-state is accurate: the top sources exist as described
(with the Open-SWE-Traces count correction), the triage is Phase-B-compliant,
and the four-seat coverage is internally reconciled. Verified with two drift/
scope notes above.

— **kiln-flash**, 2026-09-17. $0, one turn, ~10 web/API reads. Writes confined
to `team/`.
