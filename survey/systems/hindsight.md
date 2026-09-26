# System card: Hindsight (current product pipeline)

**kiln · 2026-09-26 · sources: paper abstract arXiv:2512.12818 (Latimer et al., Vectorize.io + Virginia Tech), product docs hindsight.vectorize.io (Claude Code integration page + concepts, read this session), repo github.com/vectorize-io/hindsight (MIT, ~13.3k stars per paper). No install/probe. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Pipeline distinction (load-bearing)

Our bake-off measured **Hindsight raw/no-LLM**: append-only mention-time history with current-state contamination. The current product pipeline is a different object and old numbers must not stand in for it: **retain** runs an LLM extraction (facts, entities, temporal data, relationships) plus normalization into canonical entities, time series, and indexes, routed into world-facts vs experiences pathways; retained facts auto-consolidate into **observations** (deduped, exact-quote evidence with proof counts, updated-not-overwritten, freshness-aware — unconsolidated regions are verified against raw facts before use); **recall** runs four strategies in parallel (semantic, BM25, graph, temporal) fused by RRF + cross-encoder rerank, token-trimmed; **reflect** does agentic reasoning with bank mission/directives, and user-curated knowledge pages re-synthesize on a `source_query`. Four logical networks (world, experience, observation, opinion-with-confidence) separate what the agent knows from what it believes — the evidence/interpretation boundary, built in.

## One concrete host path (Claude Code, documented)

Plugin = hooks + MCP + skill: `SessionStart` health check; `UserPromptSubmit` auto-recall injected as invisible `additionalContext` (default 1024-token cap, observation type default, low/mid/high budget); `Stop` auto-retain (full-session or every-N-turns chunked with overlap, tool calls included); `SessionEnd` cleanup. MCP `agent_knowledge_*` tools for explicit read/write/search; subagent skill with isolated banks; bank scoping static/dynamic (per agent/project/session/channel). Current direction is one bank per repo shared across agents (coding-agents plugin supersedes per-agent plugins).

## Service vs model calls vs host integration (separated)

- **Service:** local daemon (`hindsight-embed` via uvx, auto-managed) or external/self-hosted server (Docker Compose + Postgres; cloud exists). Storage is server-side, not files Brian can read.
- **Model calls (optional but load-bearing):** retain extraction LLM (openai/anthropic/gemini/groq/ollama/claude-code providers — note ollama is the local-inference path; claude-code bills to subscription, corrected c16-cont), cross-encoder rerank, reflect reasoning. No-LLM operation is not the product; raw mode is what we measured and rejected.
- **Host integration:** plugin install + `~/.hindsight/*.json` config + hooks. **No Pi integration is listed** among 60+ integrations — Pi consumption would need generic MCP wiring (unverified); local agents likewise via API/MCP. So cross-host application is unproven, not disproven.

## Cost / failure modes

Install: plugin + daemon + LLM key (or external server + token). Ongoing: extraction call per retain cycle, recall latency against a 12s hook timeout, 1024-token recall block per prompt, Postgres to operate self-hosted. Failure modes: extraction-LLM dependence (the familiar lifecycle risk, now with consolidation + freshness checks as mitigation, unmeasured by us); observation staleness between consolidation runs; bank-scope misconfiguration (one static bank sharing everything vs over-fragmented dynamic banks); vendor direction changes (per-agent plugins already superseded once).

## Source addendum 2026-09-26 (c16 continuation): Pi adapter + provider correction

- **CORRECTION:** the c16 card listed the `claude-code` LLM provider alongside ollama as local-first options. Wrong: per the model docs, `claude-code` routes extraction through the Claude Code **subscription**, not local inference. **Ollama alone is the local-inference path.** Lead note records this; card corrected here.
- **Pi support is real (changelog 0.5.0):** "first-class support for Pi, sharing the same extension adapter and installer as Prime Agent." Adapter source inspected (`src/pi.ts` + `src/harness/pi-extension.ts`): Pi has no hooks system, so the adapter is a persistent extension listed in `~/.pi/agent/settings.json`. **Retain path:** `agent_end` event → transcript converted at the boundary (`readPiMessages`) → shared RuntimeCore `onTranscript` (write-back). **Inject path:** `before_agent_start` → `onPrompt` recall → injection **appended to the system prompt** (not user context); 0.7.0 allows first-prompt injection to select reflection, knowledge pages, or recall. Native `hindsight_*` knowledge tools registered via `registerTool`. **Bank:** resolved from `process.cwd()` → per-repo bank shared by every agent on that repo; `{harness}` templating keeps Pi sessions attributable separately from Prime Agent.
- **What this changes:** Pi-side automatic capture and system-prompt injection now have an existing mechanism — two c13 glue items move from "unbuilt" to "implemented upstream, unverified locally." Cross-host refresh becomes *plausible* (server-side bank shared by any host with the API URL + per-repo bank identity), but is still unproven: no install, no run, no evidence on Brian's Pi. Prerequisite-change detection and mistaken-correction entrenchment are untouched by this adapter.

## Advice: **watch, medium-low confidence**

The observation layer (evidence-grounded, proof-counted, freshness-aware beliefs) is the most Brian-shaped mechanism in any product yet — it is essentially the "scoped notes with source + date" bet with automation attached — and the claude-code-provider option keeps extraction local. But it is a service with a Postgres, LLM-billed extraction, no Pi path, and benchmark numbers (LongMemEval 91.4% class) that are vendor-run. Trial bar unchanged: a named cross-host or consolidation need, lifecycle-gated on our corpora, never score-admitted.
