# CORVID-S6-2G-VERIFY — gate verification for row S6-2G

Verifier: corvid-dsh, 2026-09-17 09:57 PDT. I authored neither the gate
(plumb-fable) nor the artifact it gates (kiln-flash). Prior measurement cited:
kiln-flash's S6-2 close note ("declared check → clean, rc 0 ... 25 mutants +
honest-STOP fixture rejected/accepted by name") — re-executed independently
below, plus mutants of my own construction on copies of the REAL artifact.

## Verdict: VERIFIED PASS

## What was checked

1. **Declared check** (`python3 /home/bmosher/memory-bake-off/team/S6-SELECTIVITY/check.py --selftest`):
   exit 0. Conforming continue AND honest-STOP fixtures accepted; 25
   single-defect mutants, 6 missing-file roots, dirty and hostile CLI roots
   rejected by name, no traceback.
2. **Clean run on the real artifact**: exit 0, and the gate's RECOMPUTED
   summary — `verdict continue; bm25 0.500 vs return-everything 0.200, gap
   0.300, declared margin 0.25` — matches kiln's close note number for number.
   The gate derives this from manifest helpful-sets and result rows itself
   (`_f1` set-F1, abstain case scores 1 only on empty retrieval); it does not
   trust a score field.
3. **Independence is structural**: gate mtime 2026-09-17 07:36:48 PDT vs
   earliest artifact mtime design.md 08:25:51 (corpus 08:26:56, manifest and
   results 08:29:16, decision 08:29:16, review 08:30:56, run_selectivity.py
   08:29:14). The gate predates every artifact file by ~49 minutes.
4. **Content enforces what row S6-2 demands** (source read): all six declared
   files; manifest `declared_at` strictly before every result timestamp
   (`DECLARED-AFTER-RESULTS`); manifest must not reference results
   (`MANIFEST-DERIVED`); every result row carries the sha256 of the manifest
   bytes (`RESULTS-NOT-BOUND`) and the manifest pins the corpus sha
   (`CORPUS-NOT-FROZEN`) — the corpus→manifest→results chain the row turns on;
   abstain cases must exist and be labelled and agree with the manifest's
   empty helpful-set (`NO-ABSTAIN-CASES`/`CASE-UNLABELLED`/`ABSTAIN-MISMATCH`);
   stores need ≥3 records (`SINGLE-RECORD-STORE`) with at least one distractor
   (`NO-DISTRACTORS`); all four control arms present, covering every case, and
   each delivering what its name says (`CONTROL-ARM-MISSING`/
   `CONTROL-INCOMPLETE`/`CONTROL-ARM-WRONG` — return-everything must return the
   whole store, oracle exactly the helpful set, return-nothing nothing);
   controls before engines by file order and timestamp (`CONTROLS-NOT-FIRST`);
   the separation recomputed by the gate with the pre-declared margin, verdict
   continue without separation rejected (`CONTINUED-ANYWAY`), stop accepted as
   a pass but only with a real finding (`STOP-WITHOUT-FINDING`) and no engine
   rows (`STOP-BUT-ENGINES-RAN`); engine rows must label every adaptation
   (`ADAPTATION-UNLABELLED`); design.md must cite
   `team/EXTERNAL-KNOWLEDGEDRIFT-20260916.md` and name exactly one of the
   three choices, with a reason required for build-own
   (`CITATION-MISSING`/`CHOICE-UNNAMED`/`CHOICE-UNREASONED`); reviewer ≠
   author (`REVIEW-NOT-INDEPENDENT`).
5. **Exit contract**: 0 clean / 1 with named `[MARKER]` lines and
   `S6-2 gate findings: N` / no traceback, held on the gate's own clean,
   honest-stop, dirty and hostile CLI roots.
6. **Adversarial mutants on copies of the real artifact** (one defect each):
   - declared_at moved after the results → REJECTED
     (`DECLARED-AFTER-RESULTS`, `RESULTS-NOT-BOUND`).
   - one result row's manifest sha stripped → REJECTED (`RESULTS-NOT-BOUND`).
   - an abstain case's expect flipped to retrieve → REJECTED
     (`ABSTAIN-MISMATCH`, `CORPUS-NOT-FROZEN`).
   - separation_margin inflated to 0.5 (above the achieved 0.300 gap) with
     verdict left at continue → REJECTED (`CONTINUED-ANYWAY`) — this is the
     row's core protection against choosing the margin after seeing the runs.
   - engine rows moved before the control rows → REJECTED
     (`CONTROLS-NOT-FIRST`).
   - KnowledgeDrift citation + choice line stripped from design.md → REJECTED
     (`CITATION-MISSING`, `CHOICE-UNNAMED`).
   - reviewer set equal to author → REJECTED (`REVIEW-NOT-INDEPENDENT`).
   - honest-STOP shape built from the real control rows (engines stripped,
     verdict stop with a finding) → ACCEPTED rc 0, summary line still prints
     the recomputed gap.
   (Co-firing markers above are the chain working: editing the manifest
   changes its sha, so unbound rows fire too.)

## Observation (not a defect, recorded for the sprint note)

The gate accepts a stop verdict whenever the controls are complete, the
finding exists, and no engines ran — it does not require that the gap failed
the margin. A stop despite separation is over-modest rather than deceptive,
the row text asks exactly for this acceptance, and the clean line prints the
recomputed gap either way, so a stop/separation mismatch is visible on the
gate's own output. On the real artifact the declared verdict is `continue`,
which the recomputed gap (0.300 > 0.25) supports.

## Stated limit

Timestamps are self-reported and a hash chain can be rebuilt deliberately;
the gate stops accident or convenience, not a determined forger. Whether the
distractors are plausible and whether the design's choice is right stay with
the S6-2 artifact verification. Gate sha256 not repeated here; file unchanged
since the mtime evidence above.
