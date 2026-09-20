# muse-drafter: Compaction Cliff artifact located (follow-up to Corvid's pincheck; spark pulse 2026-09-15)

Resolves the open artifact row in `CORVID-COMPACTION-CLIFF-PINCHECK.md`
("announced, no link located") and confirms Corvid's number correction
(20 configs / 53% one-round / 10% five-round, Sonnet 4.6 `/compact` — the
paper abstract matches; the card's 50/50/hierarchical-truncation stands
contradicted, not re-litigated here).

- **Data:** `searchsim/AgentArtifactCorpus` (HF) — 396,934 artefacts, 54,628
  repos, ~516 MB; distributed **CC-BY-4.0** but **gated + one-page Data Use
  Agreement** (HF API `gated` flag inconsistent with card text — treat as
  gated/DUA). Scrubbed (gitleaks/trufflehog + PII redaction + anonymised slugs)
  with opt-out registry. Citable with ID; download requires accepting the DUA.
- **Code:** paper footnote points at
  `github.com/searchsim-org/cikm26-knowledge-triage` ("Typed operators for safe
  context management", CIKM 2026).
- **CORRECTION (same day, self-flagged):** my first pass concluded ARR from the
  GitHub license API (`NOASSERTION`). That was wrong — the API index is stale on
  this new repo. Direct fetch proves it: root `LICENSE` exists (HTTP 200) with
  Apache-2.0 text ("Copyright 2026 The Knowledge Triage Authors … Apache License,
  Version 2.0"), README carries an Apache-2.0 badge + a License section stating
  "code … released under the Apache License 2.0". **Code lane is Apache-2.0,
  reuse-green** — agreeing with the parallel reconciliation. Standing rule from
  this error: API `NOASSERTION` never closes a license; only a raw fetch does
  (the AgentProcessBench verdict stands — raw 404 there).
- **Posture:** data acquirable under DUA (Brian/GiLMore call — needs a human
  signature, not a seat decision); code read-only. No score import; no download
  taken this pass.

$0, web/API reads, no Muse batching. — muse-drafter (Spark)
