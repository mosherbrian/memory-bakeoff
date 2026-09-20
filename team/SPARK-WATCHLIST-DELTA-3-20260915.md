# watchlist delta #3 — 2026-09-15 (event sourcing / replay / context-compression)

Third instance of the vocabulary §5 watchlist (`.md #1`, `#2`). Query families:
`"event sourcing" autonomous agent state reconstruction`, `"experience replay"
coding agent`, `"context compression" agent memory`. Deduped against the ledger
and deltas #1/#2. **Candidate discovery only — no score import; abstract-level.**

## Strongest net-new — conflict/premise + compaction (our pi-lcm arm)

- **The Compaction Cliff in Long-Running AI Agent Memory** — `arXiv:2608.22752`
  (CIKM 2026). Compaction **summarizes a safety rule and an episodic log at the
  same rate**, so constraints are paraphrased/dropped; hierarchical truncation
  preserves only **50% of safety constraints** across 50 configurations. Proposes
  **per-type fidelity lanes** (constraints/procedures = full, beliefs/preferences
  = compressed, episodic = placeholder). **Direct hit** on our compaction arm,
  premise-resistance, and the epistemic-type system.

## Event-sourced agent state / provenance / replay

- **ESAA: Event Sourcing for Autonomous Agents in LLM-Based SWE** —
  `arXiv:2602.23193` (2026-02-26, **CC BY 4.0**). Immutable log of
  intentions/decisions/effects is the source of truth; deterministic projection +
  **replay verification with hashing**, boundary contracts, a **"done"
  immutability rule**, blast-radius containment; code-agent case studies.
  Direct fit: E-8, G1/G2, lineage.
- **The Log is the Agent (ActiveGraph)** — `arXiv:2605.21997` (v1 2026-05-22,
  Apache-2.0 `yoheinakajima/activegraph`). Append-only log → deterministic graph
  projection; **fork a run at an arbitrary point** (shared-prefix replay is
  free), audit replay, strict-mode reproducibility, "why is this in context?"
  provenance. Strong replay/fork/provenance shape.

## Coding-agent longitudinal / correction-replay

- **SWE-EVO** — ACL ARR 2026 (OpenReview, **CC BY 4.0**). Long-horizon software
  **evolution**: 48 tasks, avg **21 files**, ~874 tests; GPT-5.4+OpenHands 25% vs
  72.8% on SWE-bench Verified; proposes a **Fix Rate** partial-progress metric.
  Closest net-new to our G4/G5 coding substrate.
- **SWE-Together** — `arXiv:2606.29957` (2026-06-29). Interactive coding sessions
  with **user-correction replay** and provenance from real recorded user-agent
  sessions. Directly our transcript-miner / correction-event concern.
- **SWE-Replay** — `arXiv:2601.22129` (nonexclusive). Recycles prior trajectories,
  **branching at critical intermediate steps**; cost vs resolve-rate trade-off.

## Context compression (GEM/DIGEST adjacency)

- **ACON** (ICML 2026, Microsoft) — compresses observations + history via
  **natural-language guideline optimization**, −26–54% peak tokens; distills the
  compressor. · **ACM** `arXiv:2607.23809` — agent decides when to compress,
  offloads to external memory. · **AgentMemBench** `arXiv:2608.00009` — five
  strategies under one harness; only dense retrieval scales to long horizons.

## Already known / deduped

AMA-Bench `2602.22769`, SWE-bench/Terminal-Bench, MemoryAgentBench, LoCoMo/LME —
prior ledger.

## Method / next

Re-run families weekly, dedupe, append. All entries need a provenance + license +
artifact pass before carding; **Compaction Cliff** (`2608.22752`) and **ESAA**
(`2602.23193`) are the top two candidates. Owner: this seat (frontier librarian).

## Grounding pass (same day)

Paper-level, abs reads; artifact lanes marked honestly:

| ID | v1 | paper license | artifact |
|---|---|---|---|
| `2608.22752` Compaction Cliff | 2026-08-24 | **CC BY 4.0** | **released**: HF `searchsim/AgentArtifactCorpus` **CC-BY-4.0, gated+DUA**; code `searchsim-org/cikm26-knowledge-triage` **Apache-2.0**; + classifier → card candidate |
| `2602.23193` ESAA | 2026-02-26 | **CC BY 4.0** | candidate repo `elzobrito/conversation-esaa` **MIT** — author-name match, **not confirmed** as the paper impl |
| `2605.21997` ActiveGraph | 2026-05-21 | nonexclusive | repo `yoheinakajima/activegraph` **Apache-2.0** |
| `2606.29957` SWE-Together | 2026-06-29 | **CC BY 4.0** | not located this pass |
| `2607.23809` ACM | 2026-07-26 | **CC BY 4.0** | not located this pass |

**Top two (posture corrected after the artifact checks):**
- **Compaction Cliff = card candidate** (not design-ref): code
  `searchsim-org/cikm26-knowledge-triage` **Apache-2.0** (raw LICENSE; the API's
  NOASSERTION is stale), data `searchsim/AgentArtifactCorpus` **CC-BY-4.0 but
  gated + Data Use Agreement** (human sign-off to download), released
  classifier/harness. See `SPARK-COMPACTION-CLIFF-ARTIFACT-20260915.md` +
  `SPARK-COMPACTION-CLIFF-BODY-PASS-20260915.md`.
- **ESAA = design reference + optional author tool** (repo linkage unconfirmed —
  see the resolution section below). No score import.

$0, web reads only. — muse-drafter (Spark)

## ESAA artifact check — resolved (2026-09-15, second pulse)

Follow-up to the open question above ("candidate repo ... author-name match, not
confirmed as the paper impl"):

- **Paper author:** Elzo Brito dos Santos Filho (single author, `2602.23193`).
- **Repo `elzobrito/conversation-esaa`:** MIT, 3★, pushed 2026-08-27, described
  as "an event-sourced memory layer for continuity, handoff, and curation across
  agents" — an **author-owned tool** (npm CLI installer + hooks/watchers,
  append-only local log + compact read models for handoff), README in Portuguese.
- **Linkage: not proven.** The README does **not** cite the arXiv ID, title, or
  the ESAA paper; the abs page does not link the repo. Author-handle ↔ author-name
  match is strong (`elzobrito` = Elzo Brito), and the concept aligns, but the repo
  is a product-style tool, **not** the paper's evaluation harness.

**Verdict:** probable author-side implementation, **unconfirmed as the paper's
artifact**. Use as a *design reference* (event-sourced log + read models for
continuity is directly our pi-lcm/E-8 shape); do **not** cite the repo as "ESAA's
code" without the author confirming. Card posture for ESAA: design ref + optional
author tool, not a reproduction target.

$0, web/API reads. — muse-drafter (Spark)

## Artifact follow-ups — remaining "not located" rows (2026-09-15, third pulse)

- **ACM (`2607.23809`): LOCATED.** Paper CC BY 4.0; official repo
  `lixiaochuan2020/agentic-context-management` (**MIT**, GitHub API +
  root LICENSE 200; "official repository for the paper"). Reuse-green.
- **SWE-Together (`2606.29957`): still unlocated.** Paper CC BY 4.0; no repo
  link on abs page. Design ref only until an artifact surfaces.
- **AgentMemBench (`2608.00009`): still unlocated.** Paper arXiv-nonexclusive;
  no repo link on abs page. Design ref only.

$0, abs/API reads. — muse-drafter (Spark)

## Remaining delta-#3 items — provenance/license pass completed (2026-09-15, second pulse)

| item | pin | paper | artifact | verdict |
|---|---|---|---|---|
| **SWE-Together** | `2606.29957` v1 2026-06-29, cs.SE | **CC BY 4.0** | official `Togetherbench/SWE-Together` — **Apache-2.0**, 66★, active (2026-09-14); + HF session datasets | **card candidate (reuse-green code)**; interactive coding sessions + user-correction replay = our transcript-miner concern |
| **ACM** | `2607.23809` v1 2026-07-26, cs.AI | **CC BY 4.0** | official `lixiaochuan2020/agentic-context-management` — **MIT**, 36★ | **card candidate (reuse-green)**; agent decides when to compress + offloads to external memory |
| **ActiveGraph** | `2605.21997` v1 2026-05-21 | nonexclusive | `yoheinakajima/activegraph` **Apache-2.0** | design ref (append-only log → graph projection; fork/replay) |
| **SWE-Replay** | `2601.22129` v2 2026-02-05, cs.SE | arXiv non-exclusive | **no own artifact** (links only third-party moatless-tools / SWE-bench-mini) | design ref (branch at critical steps) |
| **AgentMemBench** | `2608.00009` v1 2026-06-16, cs.CL | arXiv non-exclusive | **no own artifact** (links only langchain) | design ref (five strategies; only dense retrieval scales) |
| **ACON** (ICML 2026, MS) | no arXiv ID given | — | not located this pass | design ref pending a pin |
| **SWE-EVO** (ACL ARR 2026) | OpenReview, no arXiv ID | CC BY 4.0 | not located this pass | design ref pending a pin |

**Delta #3 net:** reuse-green candidates = **Compaction Cliff** (D3, Apache/DUA),
**SWE-Together** (Apache), **ACM** (MIT); design refs = ActiveGraph, ESAA,
SWE-Replay, AgentMemBench, ACON, SWE-EVO. No score import.

$0, web/API reads. — muse-drafter (Spark)
