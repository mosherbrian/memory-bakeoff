# System card: MemOS (memory OS with local plugin)

**kiln · 2026-09-26 · ~500w · advice only, no installs/probes. Sources: primary repo github.com/MemTensor/MemOS README (read this session: v2.0 "Stardust", Apache-2.0, papers arXiv:2507.03724 / 2505.22101) + Phase-2 candidate intake ("strongest of the eight"). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Identity (documented, not installed)

MemOS treats memory as an OS-level resource: a MemCube abstraction over parametric, activation, and plaintext memory, behind one Unified Memory API (add/retrieve/edit/delete), with multi-cube isolation/sharing across users, projects, and agents. Four delivery paths: hosted Cloud API, self-hosted REST service, Cloud plugin, and local plugin. All benchmark numbers on the page (LoCoMo 88.83, LongMemEval 89.20, "35.24% token savings", OpenClaw 36.63%→50.87%) are vendor-reported — noted, not imported.

## Concrete update-to-delivery path (local plugin — the Brian-relevant variant)

The local plugin (npm install into DeepSeek Harness/Hermes/OpenClaw; local-first SQLite, hybrid FTS5+vector retrieval) runs a tight loop: **recall relevant context before the first model step of each request → save the new user/assistant messages after a successful turn**. Correction arrives via "Memory Feedback & Correction" — natural-language feedback refining stored memories — plus smart dedup and tiered skill evolution (L1 traces → L2 policies → L3 world model → crystallized skills), with a Memory Viewer dashboard for inspection. The cloud plugin variant documents fail-open behavior (an outage does not interrupt the task). Self-host instead means `docker compose up` for MemOS API + Neo4j + Qdrant plus your own LLM keys in `.env`.

## Does it simplify the stack or relocate the work?

It relocates. Against native files the local plugin adds: a Node dependency chain, an SQLite store beside every other store, an extraction/embedding pipeline behind dedup and skill evolution, and a dashboard to check. What it genuinely adds in return: cross-task skill reuse machinery and feedback-driven correction with an inspection surface — the two mechanisms native files lack. But note the tiering risk: L1/L2/L3/world-model/skill is *five* representations of the same past that can disagree, and nothing on the page describes what happens when they do. The extraction dependency is the familiar one (an LLM decides what a turn meant), and skill evolution is exactly where our failed_procedure_adoption family lives.

## Cost / fit

- **Local plugin:** install ~npm + agent setup, 100% on-device, no cloud dependency — the cheapest serious trial shape, and DeepSeek-Harness-native (relevant to this fleet's own tooling). Maintenance: config, embedding/LLM pins, dedup/skill-evolution behavior, viewer checks.
- **Self-host:** Neo4j + Qdrant + API service + LLM keys — a second infrastructure to operate for one user. **Cloud:** data off-box + subscription.
- Fit: no Claude Code-native path documented (plugins target DSH/Hermes/OpenClaw); Pi and local-model coverage would go through the generic API, not a tailored integration.

## Gap deepened: what MemCube actually promises (paper abstract, arXiv:2507.03724v4)

The card worried that five tiered representations (L1/L2/L3/world-model/skills) can disagree silently. The paper's abstract gives the designed answer: a MemCube encapsulates content *plus* provenance and versioning metadata, and cubes can be "composed, migrated, and fused over time, enabling flexible transitions between memory types." So cross-tier disagreement is supposed to be managed by versioned metadata and explicit transitions — a stronger claim than the README's feature list. Still abstract-level (I read the abs page, not the 36-page methods), and the hard question survives one level down: who adjudicates when a migrated cube contradicts its source — the scheduler, the LLM, or the user via feedback? Unresolved; named, not filled.

## Advice: **watch, medium-low confidence**

Strongest integrated candidate on the roster by mechanism (unified API + cubes + feedback correction + local-first option), and the local plugin deserves first look *if* a trial ever opens — but it is documented integration, not installed proof, and its numbers are vendor claims through its own OmniMemEval harness. Trial bar stays: a named cross-task or feedback-correction need, lifecycle-gated, never benchmark-admitted.
