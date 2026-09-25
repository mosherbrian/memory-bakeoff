# Limitations, missing sources, and check log

## Repair note (R1-synthesis-repair-1 scope)
- Corrected omission: the initial synthesis substituted S12-1G and the S13
  runner mismatch for the actual criterion (both S13 rejected/unsatisfiable
  gates). Added per-entry pins `team/CORVID-S13-1G-VERIFY.md` and
  `team/CORVID-S13-2G-VERIFY.md` at commit 22c995f (read in full, not
  replayed); original 124 bytes unchanged.
- Repaired malformed evidence-table rows: data rows carried 7 fields
  against an 8-column header (missing `commit`); all rows now carry
  per-entry commits (485d783d, or 22c995f for the two added reviews).
- Recommendation reconsidered against the new evidence: unchanged. Both
  S13 gate reviews are measurement-process evidence (unsatisfiable /
  fabrication-demanding checks, both unimplemented fixes), consistent with
  the existing framing; they move no efficacy conclusion and propose no
  new experiment.

## Method limits
- Retrospective synthesis at pinned commit 485d783d; prior exposure to
  summaries disclosed. No fresh runs; arithmetic checked by reading recorded
  artifacts only. No statistical significance claimed anywhere (samples are
  5–40 cases per cell; verdicts report raw counts).
- blind-baseline.md and admission rationale deliberately unread (verifier's).
- The five package checks map: (1) traceable evidence — every row above names
  source+commit+field; unknown recorded where absent; (2) no overgeneralization
  — operational defects (gates, runners) counted as process, never efficacy;
  (3) counterevidence retained with denominators; (4) exactly one next step
  with falsification; (5) verifier judgment left to the verifier.

## Missing / partially inspected sources (explicit unknown)
- S6-SELECTIVITY corpus/results: cited via sha-pinned priors inside verdicts,
  not independently inspected (not in the 124). Numbers using it are marked
  as verdict-reported.
- S7-COMPOSE numeric cells: rerun arms read from verdict.json; answer-page
  figures (0.60/1/5/5/5) cross-checked against those arms, consistent.
- S9-STALEPATH-PROBES, S9-RANK-DIAG, S9-SELECT-FIX, S9-EVAL-CANARY guards:
  read for instrument/repair character (evaluator-integrity and planner
  repairs, operational context per policy) — not efficacy evidence and not
  counted as such. No efficacy numbers taken from them.
- S11-ABSTAIN3 design.md bar text: taken via verdict.json's bar field and
  corvid's 33-check recomputation record, not re-read in full.
- REQUIREMENTS-NEXT-SYSTEM: read partially (sections A1–A4, B1); used only
  for process context (preregistration/admission/gate norms), not for
  efficacy claims.

## Counterevidence search log
- Sought verdicts contradicting each answer-page row: S12-1G rounds (process,
  resolved), S13 divergence cell (both fail — retained), S7-STATELAYER
  agentmemory comparison (cross-system context, retained as labeled),
  corvid self-corrected checker defect in S12-2 verify (method note, retained).
- Sought missed updates favoring the layer: all arms report 0 missed across
  S7/S10/S11 — retained as stated; zero-missed does not imply safety.
- Sought external transfer success: S13 is the only transfer test; it fails.
- Sought task-outcome measurements: none exist in the 124 files.

## What would change this synthesis
- A preregistered memory on/off task-outcome comparison (recommended).
- A positional-corpus S13 rerun changing more than the 0.5 cell — would
  revise the divergence note, not the outcome unless the bar is met.
- Any pinned record, missed here, showing measured task improvement or
  real-compaction continuity — none found; list above is the search scope.
