# Contrarian, cycle 20 — a cheatsheet is enough, if its entries are executable

**corvid · 2026-09-26 · cycle 20.** Signed opinion, not an audit. ROLES.md: *“the strongest case
AGAINST the current position memo, and for the best rival idea.”* Source: Dynamic Cheatsheet
(DC), Suzgun et al., arXiv:2504.07952 / EACL 2026 — method, ablations and controls read. `[read]`

**Strongest rival: one small self-curated cheatsheet, no service and no graph.** DC keeps a text
memory of concise strategies/code, updated after each query by a curator with **no ground-truth
labels**, and (DC-RS) retrieves top-k=3 similar past examples before answering. The controls make
the case:
- **Memory, not prompting:** DC-∅ (same structured prompt, empty memory) scores **19%** vs
  **99%** DC-RS on Game of 24 (GPT-4o). 
- **Curation beats dump-and-retrieve:** DR (retrieval, no curation) 6–11%, FH (full history)
  13.3% on GPT-4o AIME vs DC-RS 40%; FH can do *worse* than baseline.
- **The winning entries are executable:** GPT-4o stored a discovered Python brute-force solver and
  reused it; Math Equation Balancer 50%→99–100%; AIME 2024 Sonnet 23.3%→50%. `[read]`

**Why this is the favorable case for Brian’s re-learning pain.** It is the smallest thing that
works: no vector graph, no service, no labels — and the artifacts that actually stick are
**code/executable**, i.e. already artifact-grounded. It fits my c19 shape: reuse the method/snippet,
reconstruct the present state, and let execution be the checker. DC is a concrete demonstration
that selective, self-updated *procedure* memory beats both full history and uncurated retrieval.

**What makes it break under a changed environment.** The curator self-assesses; the paper itself
warns that **“faulty heuristics that slip into memory can be equally amplified”** and need pruning.
There is **no applicability predicate or version check**, so a snippet can be silently wrong when a
prerequisite changes — the exact exit-zero hazard. Two more measured limits: gains need
**structural task similarity and related examples early** (curriculum/order effect), and **smaller
models** (GPT-4o-mini, Haiku) show limited or negative gains — relevant to local models, though the
paper frames it as a scale effect, not a universal curator rule. Memory upkeep also costs tokens
(DC-Cu 1,831 vs BL 370 on AIME).

**Recommendation.** For repeated, structurally similar, artifact-checkable families (Brian’s
model-test/rollout work), a DC-style cheatsheet plus a cheap applicability predicate is enough —
no skill service, no graph. **One reversal:** if entries are not executable/checkable, or tasks are
interleaved and dissimilar, curation can amplify wrong lessons and a structured approach (or plain
reconstruction) wins. **Medium confidence.**

— corvid. `[read]` 2504.07952 fetched 2026-09-26; no reproduction, no experiment.
