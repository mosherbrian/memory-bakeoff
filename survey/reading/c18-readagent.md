# Reading note — ReadAgent: interactive lookup vs gist, full-text, and retrieval

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 18.**
One source (Tern): **ReadAgent, arXiv:2402.09727** (Lee et al., ICML 2024). Questions:
gist-only vs full-text vs retrieval vs **interactive lookup** controls; **preparation + query
costs**; pagination and context constraints. Commission's question: *does this give a simpler
recoverable working view than a graph index for Brian's task families?* Constraints: distinguish
QA from enacted procedure; no universal architecture winner. Tern's carry-forward correction
accepted: **drop the "structural opposite" framing from c17** — A-MEM retains original content
too (my own c16 finding); the honest distinction is only *which layer the answer is drawn from*,
not whether source survives. Not repeated here.

**Provisional frame (before the read).** ReadAgent = "gist-first, look up pages on demand"
(LLMList-style: episode segmentation → LLM writes gists → model decides when to decompress a
page back into context). Expected shape for my inventory: a **two-tier working view** — cheap
derived summaries for navigation, verbatim source one tool-call away, no embedding index at all.
That is closer to Brian's lane (files + grep) than any graph: lookup is *interactive and
agentic*, not ranked retrieval. Cost questions to pin: how many LLM calls to prepare (gist every
page), how often the lookup policy actually fires, accuracy/cost vs full-context and vs
RAG-baselines, and whether the paper's setting is read-only QA (likely) — which bounds transfer
to enacted procedure. Written skeleton first; verdict after the read.

*(facts + verdict appended after read)*

## Mechanism and controls (ReadAgent 2402.09727, §3.1–3.3, §4.3–4.4) `[read]`

**Pipeline:** *episode pagination* — the LLM picks natural pause points between paragraphs
(min/max word bounds) → *memory gisting* — the LLM "shortens" each page ("shorten", not
"summarize": preserves narrative flow), page-tagged and concatenated into a **gist memory**
that fits context → **interactive look-up**: prompted with "what you remember" + the task, the
model requests pages by number ("look up Page [7,12]"); **selected raw pages replace the gists
in place**, preserving order. ReadAgent-P requests a batch; ReadAgent-S one page at a time,
seeing prior expansions — up to 6× retrieval-phase requests, worth it only on QMSum.

**Controls present:** gist-only; gist + **neural retrieval** top-1 vs prompt-based look-up
(82.65 vs 84.13 — interactive look-up slightly better); LLM pagination vs uniform-length
(85.71 → 86.83 — small gain); full text; truncated text; RAG baselines; a compression trade-off
sweep (bigger pages → higher compression → gist-only helps, look-up accuracy suffers past a
point). Outperforms all baselines on QuALITY/NarrativeQA/QMSum, including full-text where the
article fits 8K.

**Costs (§3.3, measured):** preparation is bounded-linear — pagination ≤ (max/min) passes plus
one gisting pass; look-ups run on gists, so they're short. On QuALITY dev (2,086 questions):
direct answering 8.71M words vs 6.50M with 1-page look-up (**−25.4%**), 2-page −20.4%, 5-page
−13.8%; savings grow with compression rate and tasks-per-document (gisting is one-time).

## Does this beat a graph index for Brian? — cue analysis, no universal winner

The two solve **different retrieval cues**: ReadAgent = *narrative position* ("what happened
after I said X") with zero embedding/graph infrastructure; HippoRAG 2 = *association across
documents* (synonym edges) with per-passage LLM indexing. For a session log — one linear,
immutable, append-only stream — gist-memory + page look-up is the simpler recoverable working
view by construction: cheap skim, verbatim expansion one call away, source never rewritten.
Limits for Brian's families: (1) **read-only QA only** — no enacted procedure, and gists carry
no when-to-apply, so procedure applicability is unrepresented (c15's field again absent);
(2) preparation amortises only over many queries **of the same document** — Brian's stack is
many small files, where per-file gisting is the wrong shape except for logs;
(3) look-up can only find what narrative position suggests — cross-file association is absent;
(4) the sharp one: **look-up fires only when the model notices a gap** — over-compressed gists
hurt exactly there (their own trade-off table). That is the same uncertainty-detection
dependency as Capture's ask channel and PAHF's confidence-silencing — but ReadAgent's framing
(*"what you remember"*, explicitly lossy) *invites* the lookup, while a memory written as
confident fact suppresses it. Cheap design lesson: label the skim layer as lossy.

**Verdict: solid in scope** (2024, PaLM-2-L, self-reported, QA-only) — **the right pattern for
session-log review, not a procedure store, not a cross-file index; composable with a graph, not
a rival.** Confidence: high on mechanism/costs (explicit numbers), medium on transfer (no
agentic-workload evidence).

— cairn. Source `[read]`: arXiv HTML 2402.09727v3 §3.1–3.4, §4.2–4.4, opened 2026-09-26.