# R&D provenance audit — retraction travel and bad evidence pointers (four-engine set)

**Author:** Corvid (worker-glm-dsh3), R&D staff
**Task:** GiLMore R&D dispatch 2026-09-12, follow-on to `team/RESEARCH-4-ENGINES-SURVEY.md` (the retracted-figure provenance thread).
**Status:** documentation audit only. No engine run, no experiment, read-only. One turn.

---

## Plain English (for Brian)

The portfolio campaign is about to cite numbers about these four memory engines. This audit checks two things: does the one retracted number stay retracted wherever it appears, and does each cited number point at an artifact that actually contains it?

The retraction is healthy — every document carries it. The **evidence pointers are not**: three rows in `RESULTS.md` (the reset branch's first-read results page) link artifacts whose contents contradict the row, and one Hindsight row links a run that was formally invalidated. The underlying numbers may well be fine (they exist in other runs); the links are wrong. Three one-line fixes, at P1, no engine spend.

**One correction.** The dispatch calls `32.9%` "Hindsight's." It is **MemBukkit's** scan fraction. Hindsight's open thread is different: it has never had a faithful product run. That mislabel is itself the defect class this note audits, so it is recorded rather than quietly fixed.

---

## A. Retraction travel — healthy

`~32.9%` (MemBukkit bank scan fraction) is retracted in `research/MEMBUKKIT_SCAN_FRACTION_AUDIT.md`. Every active entry point I checked states the retraction, not just the audit:

| Document | Carries "RETRACTED"? |
|---|---|
| `research/MEMBUKKIT_SCAN_FRACTION_AUDIT.md` (source) | yes |
| `AGENTS.md` | yes |
| `README.md` | yes |
| `RESULTS.md` (row 81) | yes |
| `STATUS_AND_FINDINGS.md` (3 places) | yes |
| `CODEX_HANDOFF.md` | yes |
| `research/ROUND1_FINAL_READOUT.md` | yes |
| `RESET_PLAN.md:41` (records the retraction as completed) | yes |
| `team/RESEARCH-4-ENGINES-SURVEY.md` | yes |

No document reintroduces `32.9%` as a live claim. The Gen40 intended-model note's "0.30 to 0.33" is a different, correctly-scoped measurement. **Nothing to do here.**

## B. Receipt-pointer defects — three rows in `RESULTS.md`

`RESULTS.md` is the reset branch's first-read results page, and `RESET_PLAN.md:117` explicitly tasks correcting "a remaining bad evidence pointer" there. These are those defects. Every "actual" value below was read from the linked artifact's `summary.md`/`summary.csv` this turn; every "matching artifact" exists in the same tree.

| Row | Stated claim | Linked artifact | What the artifact actually says | Matching artifact | Fix |
|---|---|---|---|---|---|
| 81 — MemBukkit shared-LSA routing | Hit/all-relevant **0.583 / 0.542** | `results/membukkit_stress_lsa` | **0.458 / 0.375** (the CI fake-reranker diagnostic) | `results/current_full_stress4505` | repoint stress link |
| | | `results/membukkit_core` | **0.333 / 0.250** | `results/current_full_core5` | repoint core link |
| 82 — MemBukkit documented fallback | Hit/all-relevant **0.875 / 0.750** | `results/membukkit_hybrid_1.0` | **0.500 / 0.417** | `results/membukkit_fallback_gen8_stress-r1` | repoint |
| | | `results/membukkit_stress` | **0.083 / 0.083** | `results/membukkit_fallback_gen8_core-r1` | repoint |
| 85 — Hindsight raw/no-LLM learned-reranker | Hit/all-relevant **0.833 / 0.708** | `results/hindsight_gen4_core_r1` | **INVALIDATED** (`INVALIDATED.md`; 0.833 / 0.792) | `results/hindsight_gen6_external_local_core_r1` (1.000 / 1.000) | drop the invalidated link |
| | | `results/hindsight_gen5_external_local_stress_r1` | 0.833 / 0.708 — **matches** | (keep) | keep |

Present identically in `pilot-gen45/RESULTS.md` (line 75) and the reset `implementer/repo-glm-dsh3/RESULTS.md` (line 81).

Two notes for whoever applies the fix:
- The invalidated Gen4 link is the worst of the three: `research/HINDSIGHT_GEN4_INVALIDATION.md` says *all* Gen4 Hindsight directories are "excluded from leaderboards, comparative analysis, and product claims." A first-read page currently points at one.
- The matching artifacts are old-schema `run.json` (no `provenance`/`publishability` fields). Repointing is necessary but not sufficient for publishability — the P1 provenance check still has to run (same caveat the survey recorded for Habitus).

## C. A collision, not a defect

`RESET_STATUS.md:209` has a cell reading `32.9` in the `c1-a-rep2` row. That is a different metric, not the retracted scan fraction. Flagged so a future grep for "32.9" does not re-conflate the two — the exact error class this audit is about.

## D. Load-bearing numbers → artifact map

| Engine | Number the campaign may cite | Local artifact | Status |
|---|---|---|---|
| Habitus | stress Hit@5 0.792 / prohibited 0.025 | `results/habitus_stress` | pointer consistent (row 80) |
| Habitus | core Hit@5 0.875 | `results/habitus_core` | consistent |
| Habitus | "1024-D dense concept vectors" | none (upstream README) | upstream claim; vendored code uses a deterministic hash |
| agentmemory | 418/450 false supersessions (92.9%) | `results/agentmemory_raw_product_gen13_stress-r1/lifecycle.json` | consistent; row 86 carries the caveat |
| agentmemory | LongMemEval-S R@5 95.2% | none | upstream; unverified locally |
| Hindsight | core Hit@5 1.000 | `results/hindsight_gen6_external_local_core_r1` | exists but **not linked** from row 85 |
| Hindsight | stress Hit@5 0.833 / all-relevant 0.708 | `results/hindsight_gen5_external_local_stress_r1` | consistent |
| Hindsight | "most accurate agent memory ever" | none | upstream; no faithful product run |
| MemBukkit | routing 0.583 / 0.542 | `results/current_full_stress4505` | correct artifact exists; **row 81 mislinks** |
| MemBukkit | fallback 0.875 / 0.750 | `results/membukkit_fallback_gen8_stress-r1` | correct artifact exists; **row 82 mislinks** |
| MemBukkit | product 92.6% / ~3.2k tokens | none | upstream; product path unrun |
| MemBukkit | scan fraction | retracted | see A |

Pattern: every local number has a real artifact; every *upstream* headline (95.2%, "most accurate ever," 92.6%) has none, which is the portfolio's job to produce, not a documentation defect.

## Handoff

- **Implementer (reset docs):** apply the three pointer fixes at P1; do not re-litigate the numbers themselves.
- **Stratum (caveat-travel):** the retraction needs no repair — it travels. Absorb this note into the P1 receipt set and verify the fix landed.
- **Kiln (portfolio build):** cite `current_full_stress4505`, `membukkit_fallback_gen8_*`, and `hindsight_gen6_external_local_core_r1`; never the invalidated Gen4 path.

## Method and limits

- Read-only. Every "actual" number was read from the artifact's `summary.md`/`summary.csv`, and the invalidation from `INVALIDATED.md`, this turn.
- Both trees checked; the pointers are identical in `pilot-gen45/` and `implementer/repo-glm-dsh3/`.
- This audits **pointers**, not the correctness of the underlying measurements. A corrected pointer still needs the P1 provenance/publishability check.
- I edited no owner's document; the fixes are for the implementer to apply.

— **Corvid** (worker-glm-dsh3). The number was retracted; the link that was supposed to prove it never was.
