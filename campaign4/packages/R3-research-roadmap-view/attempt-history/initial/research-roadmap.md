# Research roadmap view (tier-4 static snapshot, not live state)

As-of (host UTC): 2026-09-25T01:57:38Z. This page derives from the accepted
records linked below and nothing else. It is a static snapshot: source files
may have changed since; re-render before relying on it. No new synthesis,
effect estimate, or experiment is contained here.

## Research question

What does the existing evidence establish about a small reversible memory aid
for Brian across compaction/restarts, what remains unsupported, and what
single smallest next discriminating experiment (or no experiment) follows?

## Established evidence

- **Real-work benefit: unestablished.** Nothing in the frozen record measures
  task outcomes with memory on vs off, continuity through actual compaction,
  or reduced errors ([synthesis](../R1-evidence-synthesis/synthesis.md),
  accepted 2026-09-25T01:36Z).
- **Local relevance rule survives locally only.** The S11 corpus-coverage rule
  meets its bar on declaration and holdout sets (thresholds 0.25/0.5, zero
  useful loss); priors failed the same bar ([evidence
  table](../R1-evidence-synthesis/evidence-table-normalized.tsv)).
- **External transfer fails.** Unchanged rule on 120 frozen KnowledgeDrift
  probes: 0/40 abstentions at threshold 0.5 with 10/80 useful lost; best case
  6/40 at 20/80 cost. Mechanism: recombined in-corpus vocabulary defeats
  per-term coverage ([S13 verdict](
  ../../team/S13-KD-COVERAGE-TRANSFER/verdict.json), 2026-09-20).
- **False replacement: native fails, tested layer worsens** (22/33 → 33/33;
  trivial key-equality class closed; compaction unmeasured).
- **Abstention gap spans implementations** (0/40 for all five tested); delivery
  fragility under load is unlinked to task harm.
- **Gate episodes are process evidence**, including both S13 rejected gates
  (impossible selector; fabrication-demanding inventory) — not efficacy
  evidence for or against memory.

## Limits and unknowns (never green)

- No task-outcome, compaction-continuity, or error-rate measurement exists.
- S13 pooled-vs-positional corpus semantics unresolved (both values fail the
  bar; pending decision S13-1 below).
- Samples are 5–40 cases per cell; no significance claimed.
- The R2 cued-recall design was **not accepted**: exact-match recall does not
  satisfy an actual-work-task contrast; exclusion pins and top-k remain
  missing ([terminal disposition](../R2-task-comparison-design/terminal-disposition.json),
  2026-09-25T01:56Z). This view does not adopt it.
- Corpus provenance: S11/S13 local files pinned by content hash; S6 priors
  cited via verdict pins, not independently inspected.

## Next action and owner

Tern owns the next research decision: select an actual work-task/rubric with
an observed boundary (per the R2 terminal finding), or explicitly scope a
smaller step. No experiment is released by this page. The machinery phase is
closed; Python stays a frozen historical reference (no deletion without a
separate explicit oracle-retirement decision). A dry retention
inventory/reference audit is separately authorized future work, not a
prerequisite.

## Pending decisions

| Question | Owner | Status |
|---|---|---|
| S13-1 pooled-vs-positional registered meaning ([row](../../pending-decisions.md)) | tern | open since 2026-09-20 |
| Next research package selection (actual work-task/rubric + boundary) | tern | open; R2 exhausted without acceptance |
| Python oracle-retirement (if ever) | Brian on Tern proposal | not opened; reference frozen meanwhile |
| Retention expiry quotas | separate approved action required | dry audit first; no deletion |

## Source dates and refresh notice

R1 frozen commit 2026-09-20; R1 accepted 2026-09-25T01:36Z; R2 terminal
2026-09-25T01:56Z; sponsor resumption 2026-09-24. This snapshot may be stale
the moment any linked record changes — staleness is expected, not a defect;
re-render from current bytes rather than trusting this page.
