# CORVID-S6-3G-VERIFY — gate verification for row S6-3G

Verifier: corvid-dsh, 2026-09-17 09:59 PDT. [Corrected — stamp: this line and
the QUEUE cell first said 10:02, a future time I estimated instead of reading
the clock; `date` read 09:59 at completion. That is the D-7 defect class
committed by the verifier of the timestamp row — recorded here rather than
silently rewritten.] I authored neither the gate
(plumb-fable) nor the artifact it gates (kiln-flash). Prior measurement cited:
kiln-flash's S6-3 close note ("declared check → clean, rc 0 (selftest green)") —
re-executed independently below, plus mutants of my own construction on copies
of the REAL artifact.

## Verdict: VERIFIED PASS

## What was checked

1. **Declared check** (`python3 /home/bmosher/memory-bake-off/team/S6-ROADMAP/check.py --selftest`):
   exit 0. Conforming fixture accepted; 26 single-defect mutants, 4
   missing-file roots, the "four hollow files" control (right file names, none
   of the distinctions — exactly the file-counting failure the row names), and
   dirty/hostile CLI roots all rejected by name, no traceback.
2. **Clean run on the real artifact**: exit 0.
3. **Independence is structural**: gate mtime 2026-09-17 07:39:40 PDT vs
   earliest artifact mtime evidence.json 08:38:01 (map.md 08:38:41,
   next-experiment.json 08:39:06, review.json 08:39:07). The gate predates
   every artifact file by ~58 minutes.
4. **Content enforces the distinctions the row is FOR** (source read):
   - every commitment carries a map.md line whose id and status agree with
     evidence.json (`COMMITMENT-WITHOUT-LINE`/`MAP-STATUS-DISAGREES`), with
     promised and next_decision filled (`COMMITMENT-INCOMPLETE`) and a ≥4-word
     quote VERBATIM from the actual roadmap file, checked by normalized
     substring against the file's own bytes (`QUOTE-NOT-IN-ROADMAP`);
   - "not evidenced here" and "never done" are separate values; absent-ish
     values (missing/null/n/a) are rejected (`STATUS-COLLAPSED`); a status
     must agree with its artifact field (`STATUS-CONTRADICTS-ARTIFACT`); no
     map line may carry both absent states (`ABSENT-STATES-COLLAPSED`); map.md
     must define both (`LEGEND-MISSING`);
   - each superseded charter section is checked to be real text of
     PORTFOLIO-CHARTER-draft.md (`CHARTER-SECTION-UNKNOWN`) and must name WHAT
     supersedes it — a bare "stale/outdated/obsolete" answer is rejected
     (`SUPERSEDED-BY-WHAT`); at least one section must be reconciled
     (`NO-SUPERSEDED-SECTIONS`); map.md must address the live arrangement the
     row lists: three seats, one request in flight, the 2026-09-20 window,
     OpenCode Go (`LIVE-ARRANGEMENT-MISSING`);
   - next-experiment.json must be ONE experiment (`EXPERIMENT-NOT-ONE`),
     marked proposed-not-built (`EXPERIMENT-NOT-MARKED-PROPOSED`), carry NO
     results/outcome/measured fields (`EXPERIMENT-BUILT`), a real baseline
     (`EXPERIMENT-NO-BASELINE`), a stopping rule that states a condition
     (`EXPERIMENT-NO-STOPPING-RULE`), and a tie to G4 (`EXPERIMENT-NOT-G4`);
   - Phase F: all three options assessed with evidence lists that resolve
     (`PHASE-F-MATRIX`/`ARTIFACT-UNRESOLVED`), ONE deciding uncertainty as a
     sentence, not a list (`PHASE-F-UNCERTAINTY`), and a Phase F entry in
     map.md naming it (`PHASE-F-NOT-IN-MAP`).
5. **Exit contract**: 0 clean / 1 with named `[MARKER]` lines and
   `S6-3 gate findings: N` / no traceback (the gate also converts its own
   crashes to `[GATE-ERROR]` + findings line), held on the gate's clean,
   hollow, dirty and hostile CLI roots.
6. **Adversarial mutants on copies of the real artifact** (one defect each;
   first batch ran in /tmp where the repo-relative roadmap ref could not
   resolve, adding spurious `ROADMAP-UNRESOLVED`/`ARTIFACT-UNRESOLVED`
   co-firings — my harness's artifact, not the gate's; the two mutants whose
   target marker was obscured were re-run in a path-faithful sibling
   directory, then removed):
   - a commitment's status collapsed to "missing" → REJECTED
     (`STATUS-COLLAPSED`).
   - superseded_by set to "stale" → REJECTED (`SUPERSEDED-BY-WHAT`).
   - baseline stripped → REJECTED (`EXPERIMENT-NO-BASELINE`).
   - results attached to the "proposed-not-built" experiment → REJECTED
     (`EXPERIMENT-BUILT`).
   - deciding_uncertainty as a 3-item list → REJECTED (`PHASE-F-UNCERTAINTY`).
   - R-PA quote replaced with a fabricated sentence → REJECTED, cleanly
     (`QUOTE-NOT-IN-ROADMAP` only).
   - R-PA's map line status flipped to never-done, evidence.json untouched →
     REJECTED, cleanly (`MAP-STATUS-DISAGREES` only).
   - reviewer set equal to author → REJECTED (`REVIEW-NOT-INDEPENDENT`).

## Stated limit (the gate declares this itself; confirming it)

The gate proves every listed commitment is real (quote in the roadmap) and
every cited artifact exists. It cannot prove the commitment LIST is complete
(11 commitments mapped — is that all of them?) nor that an artifact SUPPORTS
its status claim. Both stay with the S6-3 artifact verification.

## Result

Row S6-3G: artifact exists, declared check exits 0, independence structural,
gate rejects distinction-less and falsified documents by name. VERIFIED PASS.
