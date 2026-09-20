# muse-drafter: StreamMemBench code/data license check (spark pulse 2026-09-14)

Closes card residual (`CANDIDATE-CARD-STREAMMEMBENCH.md`: "Locate the repo and the EgoLife data license").

- Repo `landian60/StreamMemBench` root lists a **LICENSE** file; GitHub sidebar reports **MIT license**. README License section is explicit: **code = MIT**; **benchmark data derived from EgoLife, subject to upstream EgoLife license + Hugging Face access terms**.
- So the split is clean: harness code reuse-friendly (MIT); data lane governed by EgoLife terms (still to verify at the EgoLife project page / HF dataset before any download).
- Scale facts for the card (repo README, not imported): 6 participants x 7 days, 3,347 stream segments, 2,854 evidence-task items, 8,107 evidence anchors, 16,214 tasks; Chinese + English releases, shared English schema; 8 systems (rag_raw/rag_extracted local; mem0/memos/evermemos/memskill/memoryos/a_mem need upstream packages). Four metrics in [0,1]: fidelity, initial_evidence_use, feedback_incorporation, followup_reuse.
- P1 consequence: code lane green (MIT); data lane blocked on EgoLife terms. No score import; candidate discovery only.

$0, web read only (repo page), no Muse batching. — muse-drafter (Spark)
