# System card: DynaMem (grounded refresh, borrowed pattern)

**kiln · 2026-09-26 · sources: paper full methods arXiv:2411.04999v1 (§§1–5) + dynamem.github.io (identity only). No install/probe. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Mechanism (source-read)

- **Refreshed from sensors:** posed RGB-D frames → sparse voxel grid; per voxel: location, observation count, source image ID, CLIP/SigLIP semantic feature, latest time. Add = cluster + merge (count/feature-average/time update). Remove = ray-casting: a voxel sitting in the frustum between camera and observed depth (<2m cap for noise) *must be empty* → deleted. Absence in a fresh observation is first-class evidence, not a missing value.
- **Retained/excluded/deleted:** all observations persist with provenance (image, time, count); outdated voxels deleted on frustum evidence; images with no voxels referencing them are dropped from query context. Query is two-stage: candidate via voxel/mLLM → confirm with OWL-v2 detector → act, else abstain ("not found" beats best-match — the anti-false-positive rule).
- **Invalidation assumptions:** trusted depth under 2m, stable poses from underlying SLAM, frustum geometry as absence proof. Break any of these and removal hallucinates.
- **Results (noted, not imported):** 70% vs 30% over the static full system (complete-system comparison, not a memory-only ablation); ablations: add-only 67.8 vs 70.6, no detector cross-check 59.2, hybrid 74.5.

## Transfer to software work (pattern, not product)

Brian buys no robot — skip as product outright (Stretch, RGB-D, SAM/CLIP/OWL/Gemini stack; install cost absurd, failure modes physical). Borrow four operations, all ~zero cost: (1) **re-observe before acting** — re-run the cheap check (test, endpoint probe, `git status`) rather than resolving old accounts; (2) **confirm-then-act retrieval** — candidate memory → verify against the world → act or abstain; (3) **absence as evidence** — a missing expected signal retires the belief (the frustum rule, generalized); (4) **re-verify prioritization** — least-recently-checked first (their temporal value map). Gen45's T3 loop (337 requests on a stale composed view, never re-grounded) is exactly the failure this pattern prevents.

## Advice: **skip product, borrow pattern, medium-low confidence**

The pattern slots into our closeout/verify discipline: every skill carrying a "re-check" line *is* grounded refresh at software scale. Mechanism verified on paper; transfer argued by analogy (marked) — software state rarely offers frustum-grade absence proof, so borrowed rule (3) needs a per-case "what counts as absence" definition.
