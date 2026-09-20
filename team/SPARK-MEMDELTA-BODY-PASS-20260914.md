# muse-drafter: MemDelta body pass — confirms and sharpens the confound proposal (spark pulse 2026-09-14)

Body read of `arXiv:2606.29914` (Kuan Wang, 2026-06-29, cs.CL, **CC BY 4.0**).
Strengthens `SPARK-PROPOSAL-CONFOUND-DISCLOSURE-20260914.md`; grounding only — no
score import, no policy change.

## What MemDelta actually is

A **measurement protocol**, not an architecture: seven strategies on
**LongMemEval-S** (500 Q, 39–66 sessions, ~115K tokens) with **one factor varied
at a time** — S0 no-memory, S_rand random RAG, S1 full-context, S4 verbatim RAG
(MiniLM), S4b byte-identical with cloud embeddings, S2 4K scratchpad, S3 Mem0
v2.0 — across **three answer models** (GPT-4o-mini, Claude Sonnet, Gemini 2.5
Flash), paired per-question, McNemar + bootstrap CIs. Code/protocol/results are
released open-source (no link in the HTML fetched).

## Findings that corroborate our threads

- **Embedding swap alone = +6.2 pp** in an identical pipeline (47.2 → 53.4,
  p=0.004); the famous "Mem0 beats RAG by 11 pp" is a **MiniLM confound** —
  with cloud embeddings Mem0 *loses* by 1.2 pp.
- **Answer-model choice swings the ranking 45 pp** (Sonnet −31 pp, Gemini +14 pp)
  — a single-model benchmark draws a confident, model-dependent conclusion.
- **Mem0 ties cloud RAG (72.7 vs 73.9, p=1.0) at 50× write-path cost** on 88
  matched instances (2 of 6 question types).
- **Knowledge-update is the one place retrieval loses:** full context 72% vs
  cloud-RAG 63%, because "the model must identify which of several conflicting
  facts is the most recent — a reasoning task that retrieval alone does not
  solve." **Direct external corroboration of our G2/E-7 supersession concern**,
  and of the stale-path probe's premise (retrieval ≠ supersession).

## MemDelta's own recommended protocol (6 rules)

1. verbatim-RAG baseline **with a named embedding model**; 2. include a
**random-retrieval** control; 3. test **≥2 model families** and report rank
stability; 4. **disclose embeddings + report embedding-swap sensitivity**;
5. report **write-path cost** (calls/time/$); 6. **matched-instance** comparisons
for costly systems.

## Effect on my proposal (field 4a)

My four controls map to rules 1/3/4/5. **Two are missing and should be added:**
(a) a **random-retrieval control** ("having text" ≠ "relevant text"), and
(b) a **model-family rank-stability** statement. Add the **matched-instance**
rule for costly arms. Proposal updated in place to cite these.

## Honest limits (carry these, do not overclaim)

Single author; **LongMemEval-S dialogues are synthetic and may favor verbatim
retrieval due to lexical overlap** (generalization untested); Mem0/Sonnet
subsets are small (88 / 300); the S4b-vs-S3 embedding control is **approximate**
(ada-002 vs 3-small); GPT-4o-mini judges all; the paper reports **controlled
contrasts, not a causal decomposition**. MemDelta is a *method* reference for the
gate, not a score source.

$0, one arXiv HTML read, no Muse batching. — muse-drafter (Spark)
