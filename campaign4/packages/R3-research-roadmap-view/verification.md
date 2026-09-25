# R3-view-1 — independent reader verification

- **Reader:** corvid-dsh (worker kiln; not the author).
- **Worker claim:** `ex-R3-view-1-w1.json`; hash verified equal —
  `research-roadmap.md` `42dac504…`. Word count **521 ≤ 1000**.
- **Verdict: INCOMPLETE (outcome failed).** Content is faithful and the
  proposal/accepted/rejected distinctions, unknowns, pending list and staleness
  notice are correct, but **one primary evidence link does not resolve** and is
  asserted as known, contrary to the package's broken-link rule.

## Source fidelity — passes

Every factual claim matches its linked/recorded source:

- Real-work benefit unestablished — matches R1 `acceptance.json` /
  `synthesis.md` (`098bdc1c…`).
- S11 rule survives declaration+holdout at 0.25/0.5, zero useful loss; priors
  failed — matches R1 evidence table (`ef70fc51…`).
- External transfer fails: **0/40 at 0.5 with 10/80 lost; best 6/40 at 20/80**
  — matches `team/S13-KD-COVERAGE-TRANSFER/verdict.json` (I re-read the
  verdict: `by_threshold` grid, 0.75→6/40 at 20/80).
- False replacement 22/33 → 33/33; abstention 0/40 across five; both S13 gates
  as process evidence — all match R1/R2 accepted records.
- R2 **not accepted**, "does not adopt it"; `terminal-disposition.json`
  (`ac9c210c…`) says `EXHAUSTED_NOT_ACCEPTED`, exact-match recall does not
  satisfy the actual-work-task contrast, exclusion pins and top-k missing —
  faithfully rendered.

## Distinctions and scope — passes

Proposal vs rejected vs accepted is explicit (R2 design = not accepted and not
adopted; S11 = local survival only; gate episodes = process, not efficacy).
As-of host UTC, historical source dates, and a staleness/refresh notice are
present. No new synthesis, effect estimate, badge, or verdict; "No experiment is
released by this page." Python frozen reference and the dry retention audit are
correctly separated as future work, not research prerequisites. Pending list
names owner + status.

## Defect — broken primary evidence link

In "Established evidence", the S13 verdict link
`../../team/S13-KD-COVERAGE-TRANSFER/verdict.json` resolves from this file's
directory to `campaign4/team/...`, which **does not exist**; the real path is
`../../../team/S13-KD-COVERAGE-TRANSFER/verdict.json` (three levels up:
view → packages → campaign4 → repo root). It is asserted as the source for the
transfer finding rather than labelled unavailable, which the package forbids
("A broken/missing evidence link must be labelled unavailable, not asserted
known"). The other four links resolve (`../R1-evidence-synthesis/synthesis.md`,
`../R1-evidence-synthesis/evidence-table-normalized.tsv`,
`../R2-task-comparison-design/terminal-disposition.json`,
`../../pending-decisions.md`).

## Required fix (one line, no new research)

Change that link to `../../../team/S13-KD-COVERAGE-TRANSFER/verdict.json`, or
label it unavailable. No other change needed.

*Reviewed: `package.md`, `inputs.json`, `research-roadmap.md` (`42dac504…`),
R1 `synthesis.md`/`acceptance.json`/`evidence-table-normalized.tsv`,
R2 `terminal-disposition.json`, `SPONSOR-RESEARCH-RESUMPTION-20260924.json`,
`team/S13-KD-COVERAGE-TRANSFER/verdict.json`, `campaign4/pending-decisions.md`,
and link resolution from the view's directory.*
