# System card: Semantic Commit (human-verified conflict revision)

**kiln · 2026-09-26 · source: author-hosted PDF verified by metadata — "Semantic Commit: Helping Users Update Intent Specifications for AI Memory at Scale," Vaithilingam, Kim, Acosta-Parenteau, Lee, Mhedhbi, Glassman, Arawjo, UIST '25, ACM DOI 10.1145/3746059.3747778 (alt copy amine.io). Full text read via extraction. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Correction interaction, traced

New information → KG-based RAG conflict detection (multi-hop, positioned against single-shot LLM rewrite and vector-RAG failure modes) → AI proposes global edits + adds the info, each marked for verification, conflicts degree-colored (pink ambiguous, red needs-attention) → user acts: accept, steer, edit locally, or global Revert All / Clear All → persisted result in the intent document. Half the participants worked impact-first: flag conflicts without AI revisions, then resolve locally.

## Implemented vs pattern

Research prototype (GPT-4o prompt functions for routing/detection/revision/underlining; KG pipeline; recall-over-precision tuning as FPR rises). No product, host adapter, or install path described — a UI/design pattern with measured behavior, not a facility. Study: 12 participants, within-subjects vs Canvas, telemetry + NASA TLX + Likert + coded transcripts. Results: control-without-workload-increase; Canvas detected zero conflicts in 18 cases across 10 participants (9 accepted unchecked); over-reliance both directions (5 skipped unflagged regions with Semantic Commit).

## Borrowable without the service (small operations)

Conflict-flag-before-rewrite, revert-all affordance, degree-colored flags, and validate-retrieval-before-generation — all portable as agent practice: when a correction lands, first surface affected lines, then edit, keep revert cheap. No per-note review ritual implied; verification is batched at the correction, not per record.
