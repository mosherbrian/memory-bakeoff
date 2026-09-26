# Reading note — INMS: when does shared memory beat passing the evidence?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 29.**
One new primary source (Tern): **INMS — Gao & Zhang, arXiv:2404.09982v3 (4 Mar 2026), identity
confirmed.** Cycle question: **when does sharing memory beat passing relevant evidence?** Read
the methods/control design: what agents share (raw episodes? filtered memories? summaries?),
the **filtering/retrieval mediation**, whether scenarios use common vs different users/tasks,
and whether the gains reflect an **independently learned value** or merely more context / more
model calls. Decisive question: **does the comparison isolate *sharing* from *retrieval* and
*training*?** No broad sweep.

C28 limits carried for synthesis: MINJA does not prove provenance-at-write is the only effective
control, does not show every single-principal assistant has its conditions, no web-content attack
is empirically demonstrated here, and a source tag is not a guaranteed defense; attribution
aids interpretation but is not authorization.

**Provisional frame (before the read).** The alternative to a shared memory is what Brian's lane
already does — an orchestrator passes the relevant artifacts/messages to each agent (evidence
passing). Sharing should *beat* passing when (a) the useful units are **distilled** (cheaper to
carry than originals), (b) retrieval is **selective** (each agent gets a few relevant items, not
the full packet), and (c) memory **accumulates across sessions** so the second task pays less
than the first. The control design to look for: shared-memory vs per-agent memory vs
full-history-passing baselines, ideally with a retrieval-only arm (shared store, no learning)
and a cost column. If those arms exist and sharing wins with equal tokens/calls, that is the
strongest positive evidence in this area; if not, "sharing beats passing" is unproven and the
paper is a demo. Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## What is shared, who filters, what the controls actually compare (INMS 2404.09982v3, §3.1–3.2, §4.1–4.6, §6) `[read]`

**Shared unit:** raw **Prompt-Answer pairs** — not distilled procedures — in a **per-domain
pool**; admission = an LLM scorer (gpt-4o) grading each new PA pair against an LLM-generated,
once-human-reviewed domain rubric, threshold **81/100** (set at the dataset mean). Retrieval =
dense cosine top-3, retriever continuously retrained as the pool grows.
**Setting:** 9 agents × 3 domains (poetry forms; puzzles/riddles/puns; study/travel/fitness
plans), each agent a *different task in the same domain*; 1,000 instances, 20/40/40 split;
metrics BERTScore/F1/LLM-judge — open-ended, no ground truth, no execution.

**The decisive control is absent.** Baselines are **retriever comparisons over the same shared
pool** (Random, BM25, Contriever, SBERT, TAS-B, SimCSE) and "Zero" = retrieving nothing. So the
Zero→Three gains conflate *retrieving good examples* (ICL) with *cross-agent sharing*: there is
**no private-pool arm** (same memories, same retrieval, each agent reads only its own). The
paper therefore shows "rubric-filtered, similarity-retrieved in-domain examples help every
agent", **not** "sharing beats passing evidence". Cost is also unpriced (a scorer call per
candidate memory; retriever retraining).

**Strongest positive evidence that does survive its design:**
(1) **cross-task, same-domain transfer** — each agent improves from *other tasks'* memories
(sonnet from limerick), consistent across 9 agents and 3 backbones, growing with pool
accumulation; (2) **domain boundaries matter** — per-domain pools beat one integrated all-domain
pool for every backbone (§4.4); (3) **echo-chamber recovery** (§4.6) — a deliberately biased
initial pool (75% biased pairs) is diluted by the scorer-gated influx and performance rebounds.
Limits: cross-LLM sharing is mixed ("rising or falling", net positive, varying degree); the
biased pool was constructed by fiat and already scored below threshold — recovery is largely
dilution + retrieval, a synthetic stress-test, not an observed drift.

**Answer to the cycle question, bounded to this source:** INMS does **not** establish when
sharing beats passing — that comparison was never run. What it supports: sharing is worth
trying **within a domain boundary**, with **quality-gated admission**, when agents' tasks are
*sibling tasks* — and the mechanism is selectivity (top-3), not volume.

**Transfer limit to Brian's hosts:** memory = few-shot PA pairs for open-ended generation;
Brian's pains are procedures and preferences — different unit, different success notion. The
transferable residue: **keep domain boundaries in any shared store** (his files already have
them), and don't expect cross-domain pooling to help. The sharing-vs-passing question for his
lane (worker A's session helping worker B vs the orchestrator pasting the relevant excerpt)
remains **open in the literature I have read** — labelled, not universal.

**Verdict: oversold for the sharing question (no private-pool control; retriever isolated,
sharing not); solid as a quality-gated ICL demo.** Confidence: high on the control gap
(baseline list explicit), medium on the echo-chamber reading.

— cairn. Source `[read]`: arXiv HTML 2404.09982v3, opened 2026-09-26; c28 limits carried
(provenance-at-write not claimed as only control; no web-content attack inferred; attribution
≠ authorization).