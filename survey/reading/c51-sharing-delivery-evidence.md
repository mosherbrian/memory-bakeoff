# Reading note — does any read evidence establish cross-host sharing beats relevant-context supply?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 51.**
Existing own reads only (c29, c46–c49); no new source. Question: for a project-scoped correction
("use pnpm here"), does any evidence show **benefit from making the same correction available to
several executors** versus **supplying only relevant context per task**? Separating: bytes stored
/ host loads / model applies / useful outcome.

**c29 INMS** `[read]` — the only sharing-design source in the corpus: it evaluated a shared
multi-agent memory **without a private-pool control**, so sharing-versus-passing was never
operated. Verdict: establishes absence, not benefit.

**c46 PersonaMem** `[read]` — RAG-over-raw-messages beat Mem0's derived facts, but that ranks
*what context to supply* to one executor at one length (32k, two models); nothing about hosts.
Verdict: relevant to supply choice, silent on sharing.

**c47 PersonaMem-v2** `[read]` — single model writes memory and answers; open-ended outputs
exist; no multi-executor condition anywhere. Verdict: silent.

**c48 PersonalWAB/PUMA** `[read]` — task-specific memory retrieval improves **programmatic**
single-turn outcomes at a fixed 7b executor: evidence that *selecting the relevant history*
carries the gain — which is the rival hypothesis to sharing, not its support. Verdict: mildly
counter to "just make everything available."

**c49 TidyBot** `[read]` — one rule summary, one executor (plus physical action); no second-host
condition. Verdict: silent.

**Answer: no direct comparison exists.** Sharing-vs-handoff remains the open gap flagged since
c29; the panel must not let a delivery architecture inherit authority from silence.

**Recommendable anyway (opinion):** a project-scoped correction belongs in **one durable
project-local source each host already loads natively at project open** (CLAUDE.md/AGENTS.md
class), because the burden of proof sits on adding machinery, and the handoff alternative needs
relevance-prediction accuracy that no source measures (the c50 unknown). Where a host cannot
load it, the correction rides in the task brief as fallback. Brian operates no synchronization;
no per-record measurement tax — the needed comparison is one-off, not standing.

**Missing comparison (one):** same tasks, same scoped correction — all-projects-load vs
dispatcher-includes-only-when-relevant — scored on application rate **and** out-of-scope
misapplication. Reversal condition: if handoff-only matches application while cutting
misapplication, sharing is the worse default.

**Confidence: high on absence of direct comparison (corpus searched), medium on the
recommendable-anyway call (argues from burden-of-proof, not measured benefit).**

— cairn. Built from c29, c46–c49; c50 qualifications carried (raw-vs-derived does not isolate
deletion; rules are guidance, not just indexes).