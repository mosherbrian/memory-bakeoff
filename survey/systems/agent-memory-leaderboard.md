# System card: Agent Memory Leaderboard (evaluation infrastructure)

**kiln · 2026-09-26 · source: official README at github.com/AML-memory/agent-memory-leaderboard (verified existent: 1.2k stars, launched 29 Jul 2026, continuous operation, cycle 2 expected 20 Sep 2026) + linked docs/API-guide pages by reference. Browser read only; no install/run/clone. Quoting ROLES signed opinion/write-first. Roadmap inputs, principles, response-c72 as context.**

## Protocol (as documented)

- **Participant supplies:** publicly reachable Add (write conversation/event/document/history) + Search (evidence for query+scope) endpoints; own API, storage, bandwidth, compute; smoke test, then full run, then review-to-publish.
- **Platform holds fixed:** answer generation, evaluation, aggregation, orchestration; versioned evaluation contract (benchmark bundle + pipeline revision + model config + scoring rules) per comparable result; 0–100 normalized scores.
- **Tracks:** textual (10+ datasets incl. PersonaMem, LoCoMo-Refined, LongMemEval; ~1,500 histories, ~5,000 questions) + coding (12 repos, 150 + 1,290 time-constrained tasks; unreleased track, private verifiers). Capability taxonomy incl. governance, temporal understanding, epistemic safety.
- **Scoring provenance:** contract-matched comparisons only; review before publish; per-benchmark contracts in-repo; corpora/golds/rubrics deliberately withheld.

## Facility vs infrastructure: infrastructure only

AML supplies no memory store, no retrieval, no host integration, no Brian-path adapter — the participant *is* the memory system under test. Executor/model/budget matching is contractual (recorded per result, fixed answer side), not a hosted runtime. Submission ownership and cost sit entirely with the submitter.

## Verdict: **read, use, build nothing**

Useful as discovery (which systems exist, versioned) and as the reason not to trust cross-study scores — its whole premise matches our no-leaderboard-import rule. Changes nothing on any host; no capability row moves; coverage gains one resolved infrastructure identity. **Medium confidence** (README-level read; docs-site details not exhaustively traced, executor specifics per submission).
