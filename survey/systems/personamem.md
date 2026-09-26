# System card: PersonaMem (benchmark, not facility)

**kiln · 2026-09-26 · sources: paper full methods 2504.14225v2 (§§2–4, App.) + author repo bowen-upenn/PersonaMem (file layout; read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context. Edition discipline: original PersonaMem paper only; v2/v3 papers not merged.**

## Records, baselines, injection (benchmark mechanics)

- **Records:** 20 personas, 180+ histories (10/20/60 sessions, 32k/128k/1M tokens), 7 in-situ query types, 4-choice selection where distractors are outdated or irrelevant facts — plus a generative log-prob setting. Histories are GPT-4o-synthesized from timelines (human-validated 90–98%), frozen at eval.
- **Baselines receive:** full history (long-context arms) vs top-5 retrieved messages (RAG/BGE-M3) vs top-5 Mem0 per-turn facts; injection is prepended context. The harness file list (prepare/inference/QA scripts) is benchmark tooling; RAG/Mem0 wiring specifics come from §4.4 text, not confirmed in inspected files — marked.
- **Update:** none during evaluation. Nothing is corrected, superseded, or retired by any arm — retrieval is the only mechanism under test. Correction uptake and correction burden are both unmeasured.

## Benchmark vs deployable facility

This is a benchmark harness, not a memory system: it measures *selection* of the current-state response, not whether a correction lands or sticks. Findings that transfer: recall runs 60–70% while application runs 30–50% (the gap is the apply step, exactly our c12 caution); lost-in-middle positioning effects; RAG tops Mem0 on most types (retrieved messages beat extracted facts for personalization — a point against extraction-first designs).

## Correction carried (c47): memory arms do update

My "no update loop" overstated: per Tern's check, original §4.4 builds the Mem0 store iteratively turn-by-turn, and Appendix E explicitly includes updates/deletions/additions in the evaluated path. The precise surviving claim: histories are frozen but the *store* is built incrementally with edits — correction uptake per se (did the revised preference change later answers?) and correction burden remain unmeasured. Update mechanics ≠ update evidence.

## One useful operation + remaining work

Borrow: retrieve-then-apply discipline plus distractor-aware self-testing (test a preference against its outdated version, the benchmark's own construction). Remaining host work, all absent here: the update/correction loop, supersession semantics, and any delivery path — none exist in this artifact. **Watch as benchmark; nothing to deploy. Medium-low confidence** (methods + layout read; wiring details paper-text-only).
