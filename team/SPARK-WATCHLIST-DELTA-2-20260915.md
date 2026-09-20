# watchlist delta #2 — 2026-09-15 (fresh query families)

Second instance of the vocabulary §5 watchlist (`.md` #1: `SPARK-WATCHLIST-DELTA-20260914.md`).
Queries deliberately avoided "memory" (`"valid time" "transaction time"` agent,
`"process mining" tool-use agent traces`, `"case-based reasoning" tool-using
agent`). Deduped against the ledger; only net-new items below. **Candidate
discovery only — no score import.**

## Conflict / supersession + transactions (G1/G2, axis C)

- **Transactional Belief Commit for Stateful Agent Memory** — `arXiv:2607.23929`,
  2026-07-27. Frames persistent shared memory as a **commit/rollback** problem:
  "one agent's write becomes another agent's premise." Closest net-new match to
  our supersession-as-transaction theory and to multi-agent shared state.
- **State-Aware Runtime for Long-Horizon LLM Agents** — Cambridge Open Engage
  working paper, 2026-07-11 (v2). Explicit **transaction-governance layer**:
  separate model generation from canonical state, memory ops, validation,
  commit/rollback, audit. Non-arXiv → lower confidence; design reference.

## Process mining / procedural memory (G4/G5)

- **TraceCompiler** — `arXiv:2608.02680`, 2026-08-03 (EPFL/Binome), CC BY 4.0.
  Mines noisy tool traces into **mostly-deterministic workflows** with typed
  bindings and **auditable evidence tuples** per dependency edge; borrows
  process-mining's fitness/precision/generalization quartet. Directly our
  process-mining blind spot + provenance.
- **AgentProcessBench** — `arXiv:2603.14465` (KDD 2026). **Step-level process
  quality**: each assistant step labelled correct/neutral/incorrect; a PRM
  benchmark. Sibling of CodeTracer's failure-onset localization.

## Provenance / trace reuse

- **AgentTrails** — `arXiv:2607.18816` (VLDB 2026 workshop). Multi-trace
  **provenance graphs** + joined quotient graphs, activity capsules; trust & reuse
  for agentic tasks. Net-new provenance shape.

## Policy governance / stale rules (stale-path, premise awareness)

- **HANDBOOK.md** — `arXiv:2607.25398`, 2026-08. Standing policy must constrain
  behavior across ~17 steps / 30 tool calls; documented failures:
  in-environment request **overrides the standing policy**, a required check is
  performed **then ignored**, rule details **lost over the horizon**. The closest
  net-new analogue to our stale-instruction / premise-awareness concern, with a
  deterministic two-sided grader.

## Long-horizon context (long-context null)

- **AgentLongBench** — `arXiv:2601.20730`. Environment-rollout long-context
  benchmark; "sharp drop as episodes grow and tool use grows; **failures not
  explained by context length alone**" — a long-context-null corroboration.
- **NetAgentBench** — `arXiv:2604.09678`, CC BY 4.0. State-centric network-config
  FSMs; **"coherence per turn" penalizes destructive commands that silently erode
  prior state** — a negative-transfer / state-preservation metric shape.

## Method + limits

Re-run the vocabulary query families with date terms, dedupe against #1, append a
dated section. All entries abstract/HTML-level; IDs need a provenance + license
pass before carding; none imported. Owner unassigned; this seat can carry it.

$0, web reads only. — muse-drafter (Spark)
