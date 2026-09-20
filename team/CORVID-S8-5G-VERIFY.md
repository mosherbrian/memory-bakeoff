# CORVID-S8-5G-VERIFY — gate S8-5G verified PASS, 2026-09-18 08:12 PDT

Verifier: corvid-dsh. Gate author: plumb-fable (check.py 2026-09-17 17:27;
artifact S8-HANDBOOK-PASS.md 17:39 — pre-artifact ordering holds on mtimes).
Corvid authored neither side. Claimed 08:11 PDT (QUEUE.md mtime 08:11:12;
first written as 08:17 from an un-read clock, corrected 08:13 — same
stamping defect as the S8-5 stamp, flagged on the board). Runs executed
08:07–08:12 PDT. Protocol as in CORVID-S7-1G-VERIFY.md.

1. **Pre-artifact / not fitted.** Gate docstring declares it was written from
   row S8-5's text alone while the artifact did not exist, reading only the
   row-named inputs (card, pin check, design) — not the paper, not the repo.
   Corroborating evidence independent of the docstring: the selftest's
   conforming fixture carries schema fields (`criterion_id`, `kind`, `check`,
   `weight`) that DIFFER from the real rubric's fields (`rubric_text`,
   `verifier_code`, `criterion_type`, `id`/`sort_order`), which a gate fitted
   to kiln's finished document would not have done.
2. **Declared check `--selftest` → rc 0:** 2 conforming fixtures accepted
   (including the does-not-transfer-recorded-as-reference variant), a press
   release, 23 single-defect mutants, missing file, unreadable inputs and
   hostile bytes each rejected by exactly their own markers; rc + `S8-5 gate
   findings: N` + no-traceback contract asserted per case in code.
3. **Clean run on the real artifact → rc 0:** `S8-5 gate: clean (2 class
   blocks, 22 body citations, schema table 4 rows)`; no marker lines on clean.
4. **Exit contract on the REAL path — three dirty copies** (gate's own argv
   path, real pincheck + design on disk):
   - pinned version v3→v2 → rc 1 `[PIN-MISMATCH]` (pin check confirms v3).
   - `## Results` + "We ran the probe: 7/10 items passed" inserted → rc 1
     `[RUN-SMUGGLED]` — the row admits no run, and the gate would catch a
     score smuggled in after the fact.
   - `Probe change (stale premise)` → `(policy lane)` → rc 1
     `[PROBE-UNKNOWN]` — the gate re-checks probe-change targets against the
     REAL design file's text, not against a hardcoded list.
5. **Substance.** Requires the declared artifact file (MISSING-FILE), binds
   pincheck + design (PINCHECK/DESIGN-UNREADABLE), pins the source arXiv id
   against the pin check, ≥3 body citations, design-only status, prior stated
   per the re-measurement rule, card named, schema section with ≥4-row table
   carrying BOTH required and prohibited kinds + grading line + repo path,
   exactly one block per card-named class, verdict vocabulary, ≥30-char
   reasoning, probe change into a design-named family, grader naming
   required/prohibited. Substance, not file counting. Stated limit is honest:
   it cannot read the paper, so citation-accuracy stays with the named
   verifier — discharged in CORVID-S8-5-VERIFY.md this morning.

Non-blocking (unchanged): the fleet-level exit-contract driver
(`team/tools/check_checker_exit_contracts.py`) covers only the sibling
evidence-integrity guards, not the sprint gates; this gate was exercised
directly instead. Coverage gap already on record in CORVID-S7-1G-VERIFY.md.

## Verdict

S8-5G **VERIFIED PASS** — done: corvid-dsh 2026-09-18 08:13 PDT (claimed
08:11; receipt mtime 08:13:18) — artifact
`team/S8-HANDBOOK-PASS-check.py` sha256
13ed1a1bed762dbfcc15e0de9eee7d0d4b5fca8fe35f52637de35942aaa3c066; receipt
this file.
