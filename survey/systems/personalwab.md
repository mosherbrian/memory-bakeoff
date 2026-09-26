# System card: PersonalWAB/PUMA (personalized actions, trained policy)

**kiln · 2026-09-26 · sources: paper full methods 2410.17236v2 (§§1–6) + author repo HongruCai/PersonalWAB (env functions, PUMA SFT/DPO scripts, deepspeed config; read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Executable functions, histories, feedback

- **Functions (5):** search_product_by_query (BM25/Pyserini), get_recommendations_by_history (SASRec, cold-start removed), add_product_review, respond, stop. Real executable code in-repo — the environment is functions, not a GUI.
- **Histories:** 1,000 users from Amazon reviews (real purchases/ratings) + LLM-generated profiles (price sensitivity, diversity, tone); 80/10/10 chronological split. Instructions synthesized from ground-truth liked items/reviews.
- **Feedback:** single-turn rank-based result accuracy + function accuracy; multi-turn LLM user simulator (profile + ground truth fed) with avg-steps efficiency metric; DPO pairs from result-ranked parameter candidates.

## Memory / training / host operations

- **Memory:** bank of raw behavior records; task-specific retrieval = cosine top-K then per-function feature extraction (search: title/category/price/store; recommend: title/category/ASIN; review: ratings/comments only).
- **Training:** function-ID SFT + heuristic pseudo-label SFT + DPO on LLaMA-2-7B (deepspeed). Reuse: small fine-tuned model at 2.8s vs 6.5–6.9s GPT baselines.
- **Host:** benchmark harness only — no plugin, adapter, or deployment facility. Training price unquantified in my read; inference cheap by design.

## Missing operation + fit

No preference-correction/update loop anywhere: behaviors accumulate, profiles are static post-generation, and no supersession/deletion/update semantics are described. Correction burden unmeasured. For Brian: the transferable pieces are task-specific retrieval (filter by function, not generic top-K) and function-accuracy-before-result-accuracy measurement — both portable to our skills discipline. The trained policy itself (SFT+DPO per workload) is watch-only: benchmark shopping tasks, unpriced training, no host path. **Watch; borrow retrieval discipline. Medium-low confidence** (methods + repo read; ablations/cost appendices skimmed, not deep).
