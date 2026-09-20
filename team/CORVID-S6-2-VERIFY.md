# CORVID-S6-2-VERIFY — artifact verification for row S6-2

Verifier: corvid-dsh, 2026-09-17 10:36 PDT (clock-read; this is the ARTIFACT
verification — the gate S6-2G was verified separately at 09:57,
`team/CORVID-S6-2G-VERIFY.md`). Author: kiln-flash. I authored neither.
Prior measurements cited: the S4-12 zeros and the S4-14 corrected re-run
(cited in design.md as the row requires), and Astra's Sprint-6 specification
plus the KnowledgeDrift card (cited in design.md before the corpus was built).

## Verdict: VERIFIED PASS

## Independent recomputation (my own code, not the gate's — 12/12 PASS)

corpus sha256 matches the manifest pin; manifest `declared_at`
(15:29:16.475403Z) is strictly earlier than all 60 result timestamps; all 60
result rows carry the sha256 of the manifest bytes; controls precede engines
in BOTH file order and timestamp; six arms × ten cases complete; oracle
perfect on every case; return-everything returns the whole 4-record store;
return-nothing returns nothing; recomputed gap 0.300 matches decision.json;
verdict `continue` justified (0.300 > declared margin 0.250); all 20 engine
rows carry non-empty adaptation labels.

## Reproduction (the provenance test)

`run_selectivity.py` re-executed in a path-faithful sandbox (sibling modules
symlinked; the live artifact untouched): **all 60 rows reproduced identical
`retrieved_ids` per (arm, case), decision identical modulo timestamps.** The
runner imports the real pinned providers — in-tree `BM25Provider`
(canonical `be2bfa9`), `ClaudeMemChromaLSANoRecencyProvider`,
`PiLcmToolLevelProvider` (the S4-14 verbatim relaxedVariants port) — so the
rows demonstrably came from running the engines, not from hand-writing them.

## Corpus inspection (the part a gate cannot judge)

- Distractor plausibility: every retrieve case holds the three declared
  classes, present in the bytes — same-entity different-fact (sel-001-r1
  artifact path beside the port answer), stale/superseded value
  (sel-001-r3 "port was 8080 … superseded"; sel-005-r4 lifted 256 KiB limit),
  different-entity same-fact-type (sel-001-r4 client-101 port;
  sel-005-r3 internal 16 MiB).
- Abstention constructions match KnowledgeDrift's two forms as declared:
  unwritten subject (sel-006 fax, sel-007 conference room, sel-010 espresso —
  the asked subject appears nowhere in the store); written subject, no note
  on the asked aspect (sel-008 postgres documented, upgrade-to-16 date not;
  sel-009 search service documented, replica count not).
- Manifest helpful sets agree with my independent reading of each query.

## Profiles confirmed (mean set-F1, recomputed)

bm25 0.500 (5/5 retrieve fully recalled, 0/5 abstain held — it fired on ALL
five abstain cases including the unwritten subjects; the no-stopword-prefilter
deviation is declared in review.json, not tuned post-run);
pi_lcm_toollevel_sel 0.600 (5/5 abstain held, 1/5 retrieve rescued);
claude_mem_chroma_lsa_no_recency_sel 0.250 = the firehose level (0.200) plus
0.05, quantifying Astra's "coverage, not skill" reading of its 30/30;
return-nothing 0.500 — see observation below.

## Verdict legitimacy and observations

1. The STOP/CONTINUE rule was applied as frozen: gap 0.300 > margin 0.250 →
   continue, engines after controls. The margin itself is justified by
   arithmetic in design.md (the firehose's ceiling on this corpus shape is
   exactly 0.2), declared before the runs.
2. **The instrument separates selective retrieval from the firehose — and
   nothing else yet.** bm25 (0.500) ties return-nothing (0.500) on the mean
   with exactly complementary profiles (perfect recall / zero abstention vs
   zero recall / perfect abstention); pi-lcm shows the mean is not capped at
   0.5 by trading the other way (0.600). Kiln disclosed this in review.json.
   This is the measured basis for the compose candidate in
   team/BACKLOG-NEXT.md rank 2 — the arms are complementary, not ranked.
3. Tightness of the declaration chain, recorded honestly: the manifest's
   declared_at precedes the first result timestamp by ~0.3 ms — machine-honest
   but produced in the same process invocation. The substantive pre-declaration
   is design.md (frozen 08:25:51, five minutes before the manifest) including
   the margin rationale and the STOP rule. Chain holds; the margin of proof is
   minutes, not hours.
4. Verification environment note: my lane's redirected HOME (agent-deck
   sandbox) hides `/home/bmosher/.local/lib/python3.14/site-packages`, so a
   naive re-run fails on `import numpy` — the exact worker-HOME hazard behind
   the 2026-09-16 "a check must not depend on who runs it" standing rule. The
   declared check for this row (the gate) is stdlib-only and unaffected; the
   reproduction above needed an explicit PYTHONPATH.

## Stated limits

Descriptive, small-n, synthetic pattern-level corpus; per-arm means are
comparable only through the declared gap rule (kiln's note 4); nothing here is
an engine ranking — the three profiles trade abstention against recall in
different directions; no claim about the 90-day window is supported (fixed
stamps; no-recency arm used precisely so the window is out of play, per the
S6-1 correction).

## Result

Row S6-2: artifact complete, chain intact, numbers re-derived independently
and reproduced by re-execution, corpus design sound, verdict legitimate.
VERIFIED PASS.

## Addendum — second independent pass, 2026-09-17 12:23 PDT

The row cell never received this verdict (found while working cairn's re-sent
verification batch — the dispatch predates this receipt). Re-ran the full
recomputation from scratch the same hour: corpus sha `5a8668f7…` match, 60/60
rows bound to the live manifest hash, controls rows 0–39 before engines from
row 40, helpful sets valid, per-arm means identical to the morning pass
(return-nothing 0.500, return-everything 0.200, bm25 0.500 with 0/5
abstain-empty, oracle 1.000, pi-lcm 0.600 with 5/5, claude-mem 0.250 with
0/5), gap 0.300 > margin 0.25, verdict continue legitimate. Gate rc 0 +
selftest rc 0 re-run. Conclusions unchanged; VERIFIED PASS stands twice over.
