# Reading note — HippoRAG 2: discovery without discarding, and what "continual" actually means

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 17.**
One source (Tern): **HippoRAG 2, arXiv:2502.14802** (OSU-NLP-Group/HippoRAG). Questions:
1. How do passage nodes + graph links improve **discovery without discarding source passages**?
2. What does **continual learning** mean in its experiments — revisions/stale preferences tested,
   or mainly corpus growth?
3. Fair comparison vs dense retrieval: **indexing/query costs and reader setup** included?
End with the strongest useful idea for Brian, not universal graph superiority. ROLES frame:
*"a verdict per source: solid, oversold, or irrelevant for our goal."* Roadmap frame: layer-2
supersession *"conservative and evidence-backed rather than 'nearest neighbor means
replacement'"* — relevant because HippoRAG's linking is literally nearest-neighbour-ish
(PMI/synonym edges over an OpenIE graph).

**Provisional frame (before the read).** My inventory's shape: retrieval-side systems (A-MEM c16,
SkillRL c15) mutate a derived layer; nothing here has tested revision except Capture/PAHF's
persona-swap replays. My prior on HippoRAG2: passages stay stored verbatim (it is retrieval, not
memory revision); "continual" = incremental corpus addition; the interesting claim will be
*query-time* graph spreading improving multi-hop discovery over flat dense retrieval. The
transferable question for Brian: does a graph index over **immutable passages** get most of the
"connect related things" benefit **without** touching the derived-layer-with-no-lineage problem
at all? Written skeleton first; verdict after the methods/controls read.

*(facts + verdict appended after read)*

## Q1 — How discovery improves without discarding passages (§3.1–3.5) `[read]`

The graph is an **additive retrieval index, not a rewrite of the corpus**. Offline: LLM OpenIE
extracts triples → phrase nodes + relation edges; an encoder adds **synonym edges** between
phrase pairs above a similarity threshold; **each passage is itself a node**, joined by
"contains" edges to its phrases. Explicitly: *"our KG is used to aid the retrieval process
rather than to expand the retrieval corpus itself. This allows HippoRAG 2 to introduce less
LLM-generated noise"* (§2.2) — the stated contrast to GraphRAG/RAPTOR, which substitute LLM
summaries into the answerable corpus. Online: query→triple embedding match, LLM **recognition
memory** filter, then Personalized PageRank seeded by filtered-triple phrases **plus all passage
nodes**; the output is ranked **verbatim passages** for the reader. So the derived layer
(triples, synonyms) only *routes*; it never replaces the source in the answer. Structural
opposite of A-MEM (c16): there the derived layer is the record; here the source is the record
and the derived layer is disposable.

## Q2 — What "continual learning" means in the experiments

Three dimensions — factual memory (NQ, PopQA), sense-making (NarrativeQA, LV-Eval),
associativity (MuSiQue, 2Wiki, HotpotQA) — all static-corpus QA. **Revisions, contradictions and
stale preferences are never tested**: no conflict/update/stale experiment exists anywhere in the
paper (grep-verified; knowledge-conflict work appears only as related-work citation). "Continual"
= corpus growth + synonym edges *"link synonyms across different passages, facilitating the
integration of both old and new knowledge"* — i.e., addition. Nothing marks which of two linked,
co-existing claims is newer; no timestamps or validity on nodes/edges. **The title's "continual
learning" is framing, not an evaluated capability against revision.**

## Q3 — Fairness vs dense retrieval

Fair elements: identical reader (Llama-3.3-70B) across methods; strong dense baseline
(NV-Embed-v2 7B); retrieval (recall@5) reported separately from QA; structure baselines
reproduced with the same LLM; per-mechanism ablations (query-to-triple +≈7 Recall@5 over
NER-to-node; each of linking/contextualisation/filtering contributes); indexing cost stated
(App. F): 1.1 s/passage with the 70B, or MuSiQue's 11,656 passages in <24 h for <$2 via
gpt-4o-mini batch — and far fewer tokens than LightRAG/GraphRAG. Unfair-by-omission elements:
plain dense retrieval's indexing is embedding-only (no LLM calls), so the honest delta vs
*plain* RAG includes per-passage LLM indexing plus a **per-query LLM filtering call** (recognition
memory) whose latency is not headlined.

**Strongest useful idea for Brian — "discovery layer, verdict layer".** HippoRAG 2 shows you can
get multi-hop *discovery* ("the correction about the deploy script relates to that runbook")
from an additive graph while answers always come from immutable source passages — the derived
layer can be rebuilt or thrown away without touching history. What it lacks is exactly what a
correction-heavy lane needs: recency/validity marks, which are cheap to add precisely *because*
the source is immutable — decide discovery with the graph, decide *which passage wins* from
source metadata at read time. Inverse of Perseus/A-MEM, where the derived layer is the record.

**Verdict: solid for what it claims (discovery/retrieval), oversold on the title word
"continual" (revision untested), irrelevant as a memory-maintenance architecture.** Confidence:
high on mechanism and on the revision gap (explicit statements + absent experiment); medium on
cost transfer (their corpus ≠ Brian's session logs).

— cairn. Source `[read]`: arXiv HTML 2502.14802v1 §2.2, §3.1–3.5, §6.1–6.2, App. F, opened 2026-09-26.