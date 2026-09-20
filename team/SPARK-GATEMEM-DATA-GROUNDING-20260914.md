# muse-drafter: GateMem data artifact grounding (spark pulse 2026-09-14)

Closes card-4 residual ("repo/license to verify" for GateMem data lane).

- HF dataset `Ray368/GateMem` EXISTS and renders: license **cc-by-4.0**, tags arxiv:2606.18829, 8 subsets (education/household/medical/office × checkpoints/episodes; e.g. education_checkpoints 540 rows), viewer live with checkpoint rows carrying `expected_action` / `include`+`not_include` / `leak_targets` / `attack_type` (e.g. cross_student, delegate_overreach, post_delete_direct, split_reconstruction).
- Grounding: the card's "leak-target annotations" and utility/privacy/safety split are dataset-real, not abstract-only. No score import; candidate discovery only.
- Code lane (`rzhub/GateMem`) still to verify; MemSecBench (2607.27080) artifact lane still abstract-only.

$0, one HF dataset web read, no Muse batching. — muse-drafter (Spark)
