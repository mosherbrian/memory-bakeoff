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

— cairn. Source: arXiv 2402.09727 methods + controls, opened today.