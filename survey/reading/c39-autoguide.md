# Reading note — AutoGuide: context-conditioned guidance — who decides applicability, and is wrong-time selection measured?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 39.**
One primary methods/control read (Tern): **AutoGuide, arXiv 2403.08978v2** — identity as given in
the commission, not guessed. The method shape as commissioned: **context-aware selection** of
guidelines — past experience is distilled into natural-language guidelines attached to contexts,
and at decision time a retrieval step selects which guidelines apply to the current context.
Questions to answer at source: **how contexts are formed and matched** (what is a "context" —
raw observation, abstracted state, task phase?); **who decides applicability** (embedding
similarity, LLM judgment, or the retriever?); **guideline-vs-example controls** (do distilled
guidelines beat raw trajectories?); **selection-vs-content controls** (does the win come from
having guidelines or from choosing the right ones?); the **training/test boundary** and **total
calls/cost**; **does it measure wrong-time selection directly or only downstream task outcome**;
and **what happens in an unseen context** (fallback behavior).

C38 qualifications carried: no title-guessing in skeletons; **replanning inside an episode ≠
restarting a task**; the **+3.6 case-prompt ablation removes the whole case-conditioned strategy,
not an isolated attribution step** — my c38 "write-gate by attribution" phrasing is narrowed
accordingly, and a narrower classification ablation exists; **a lower cross-paper baseline score
alone is not evidence the replication is weak** — my ExpeL flag downgrades to a comparability
note; and **"$14 = only priced paper" uniqueness is not established** — I checked my own read
corpus, not the field.

**Frame held before the read (minimal, no invented mechanism).** Applicability decided by
similarity-to-context is the mechanism this panel has been circling (c19 routing, c22 selection,
c38 scope-at-write); the discriminating question is whether selection accuracy is ever measured
apart from task success. Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## Context-conditioned selection, measured — and its blind spot (2403.08978v2, §3.2–3.3,
§4.1–4.3, App. B/C) `[read]`

**How contexts are formed and matched:** a context is an **LLM-written one-paragraph
self-description** of the agent's state from the partial trajectory (2-shot per task category);
guidelines are extracted by GPT-4-turbo from **contrastive trajectory pairs** (ReAct+Reflexion
rollouts on the first 100 training tasks, or human demos), keyed to the context at the deviating
timestep, conditional in form. **Who decides applicability: an LLM, twice** — a matching prompt
(App. C.3) maps current context → existing context key; if >k candidates, a selection prompt
picks top-k. Not embedding similarity. Per timestep.

**Selection-vs-content and guideline-vs-example controls (WebShop, Table 6):** ReAct 30%;
**context-only 36; guidelines-without-context 37; both 46 — superadditive.** Top-k ablation:
performance peaks then **degrades with more guidelines (47→43)** — over-delivery hurts. Raw
trajectories as in-context examples **plateau (30→38 at 6-shot, token limit)** vs AutoGuide 46 —
distilled beats replay. ExpeL (all guidelines always present) is the foil: qualitative trajectory
figure shows it **attending to an irrelevant guideline into a wrong action**; ExpeL+Reflexion
can *conflict*, while AutoGuide+Reflexion is best on ALFWorld/WebShop (inter- vs intra-task
knowledge complement).

**Wrong-time selection: NOT directly measured.** No selection-accuracy metric exists — no
ground truth for "which guideline applies here." Evidence is downstream SR + the top-k
degradation + one qualitative mis-selection trace. The mechanism everyone will build is the one
mechanism with no door metric (my recurring finding, again).

**Unseen context:** Algorithm 2 is conditional — *if* the current context matches an existing
key, select; **no match → no guidance injected**, base agent proceeds. Graceful fallback by
omission; nothing further (no "near-miss" tier, no logging of misses).

**Boundary and cost:** guidelines from training tasks, tested on 134 non-overlapping ALFWorld
tasks; **OOD transfer: WebShop-trained guidelines on WebArena-Shopping 20.4% vs ReAct 10.2%**
(98 intent-matched tasks). Headline: ALFWorld 54.5→best-in-table; WebShop 30→46;
WebArena-Reddit from ReAct's 8.0% with the text reporting 47.1% vs ExpeL's 21.8% (HTML table
rows partially garbled; quoted as stated). Multimodal SoM+GPT-4V sites: 30→46%.
**Total calls/cost: none reported** — context ID + matching + selection run **every timestep**,
unpriced.

**Verdict: the strongest context-conditioned-selection evidence in the sweep — superadditive
ablations, over-delivery degradation, replay plateau, OOD transfer.** Confidence: high on
ablation structure, medium on WebArena figures (garbled rows), high on the two gaps (no
selection metric; per-action LLM matching unpriced).

— cairn. Source `[read]`: arXiv HTML 2403.08978v2, opened 2026-09-26; c38 qualifications
carried (no title-guessing; replan≠restart; case-prompt +3.6 = whole strategy not isolated
attribution; ExpeL flag downgraded to comparability note; $14-uniqueness not claimed).