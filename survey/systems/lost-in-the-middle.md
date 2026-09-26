# System card: Lost in the Middle (benchmark/method, not facility)

**kiln · 2026-09-26 · source: paper v3 full methods 2307.03172v3 (§§1–5 + App.). Pinned edition; no later replications merged. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Controlled findings (2023-era models only)

- U-shaped position curve on multi-doc QA and synthetic KV retrieval: best at context start/end, worst in the middle — mid-placement can score *below closed-book* (GPT-3.5-Turbo worst-case < 56.1%). Models: GPT-3.5/Turbo-16K, Claude-1.3/100K, MPT-30B, LongChat-13B, Llama-2 sizes, Flan encoder-decoders; GPT-4 subset similar trends.
- Extended-context versions perform nearly identically to base within shared lengths — longer windows ≠ better use.
- Reader saturates early: 20→50 retrieved docs buys ~1–1.5%; reranking/truncation beats dumping.
- Query-aware contextualization (query before+after data) fixes synthetic retrieval to near-perfect but barely moves QA trends.

## Minimal host composition convention (no new service)

Keep injected blocks short (~20 best docs, not 50); place the decision-relevant item first or last; repeat the query around the data; truncate by rank rather than filling windows. This is file/prompt discipline, not infrastructure — the effect argues for *less* context engineering, not a new component.

## Unknown / unfounded transfers

Current-host behavior unmeasured (2023 models ≠ today's hosts — no transfer claim); procedure/preference application untested (QA-only); latency/$ costs absent. An effect's existence mandates no service.
