# Reading note — Mem0: what the pipeline actually does to source history

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 32.**
One primary source (Tern): **Mem0, arXiv:2504.19413v1** — methods and controls. Questions: what
is **extracted / updated / deleted**; what **source/history survives**; what does the **graph
variant (Mem0ᵍ) add**; and **which comparison supports the headline cost/latency/accuracy
claims** — inspect the fair-reader and cost boundaries. Separate three value claims the paper
may pool: **conversational QA** (LoCoMo-style recall), **current-preference correction**
(does an update overwrite or preserve?), and **executed-procedure value** (probably absent).
Vendor-authored evidence is usable within its scope. No new sweep.

C31 synthesis limits carried: frozen-executor transfer shows a bank *contribution*, not "most of
all skill gains" and not a verdict for a specific file backend; DC did not isolate
artifact-with-check vs lesson-prose nor establish universal prose decay; the per-record
counter/checker/floor policy was **not adopted** — I re-argue none of that here.

**Provisional frame (before the read).** Mem0's published shape: two-phase pipeline — an
**extraction** phase (LLM pulls candidate facts from recent exchange + rolling summary) and an
**update** phase where each candidate is compared against top-similar existing memories and
dispatched as **ADD / UPDATE / DELETE / NOOP** — i.e., an LLM-managed *replacement* lifecycle.
The lifecycle question for our panel is sharp: **DELETE/UPDATE act on the derived fact layer;
does the raw conversation survive anywhere addressable?** My A-MEM finding (c16) was "source
survives, derived layer rewritten without provenance"; Mem0 may be the productized version of
exactly that — or worse if DELETE truly removes. Graph variant adds entity-relation triples.
Headline claims to test: beats OpenAI memory / RAG baselines on LoCoMo with ~91% lower p95
latency and >90% token savings — the fair-reader question is whether baselines get equal
scaffolding. Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## What the pipeline does to source history (Mem0 2504.19413v1, §2.1–2.2, §3.1–3.3, §4.4–4.5, §5) `[read]`

**Extract → dispatch:** an LLM (GPT-4o-mini) pulls candidate facts from each message pair +
rolling summary + last-10 messages; each candidate is compared to the top-10 similar memories
and an LLM **tool call** picks **ADD / UPDATE / DELETE / NOOP** — DELETE defined as *"removal of
memories contradicted by new information"*. **In the base variant the contradicted derived fact
is removed**; no supersession record, no tombstone is described — and the raw conversation is
never an answer unit at query time (retrieval returns derived facts; only a refreshed summary
covers history). **Ironically the graph variant is the disciplined one:** its update resolver
marks obsolete relationships *"invalid rather than physically removing them to enable temporal
reasoning"* — tombstones exist in Mem0ᵍ, not in base Mem0.

**What the graph adds:** ~2% overall J (68.44%, highest non-full-context), temporal/open-domain
gains, 2× memory footprint (14k vs 7k tokens/conversation), moderate latency cost.

**Which comparison supports the headlines — and its boundaries:**
- **+26% J vs OpenAI memory:** real in-table, but the paper itself concedes the OpenAI baseline
  *"processes manually extracted memories from their playground… pre-extraction not reflected in
  the reported metrics"* — an acknowledged fairness boundary.
- **91% lower p95 latency, >90% token savings:** measured **against full-context** — and the
  paper's own results show **full-context wins the quality metric** (Mem0 "trails only the
  computationally prohibitive full-context"). So accuracy is best-in-class *among compact
  memory/RAG systems*, cost is best *vs full-context*: two different baselines, and the honest
  reading is a **cost/quality trade point**, not a win.
- **Scope:** LoCoMo only — 10 conversations, ~200 questions each; the **adversarial
  (unanswerable) category was excluded** — precisely the abstention class is unevaluated.
  LLM-as-judge against ground truth, 10 runs, ±1 sd. Vendor-authored; the pointed Zep numbers
  (600k tokens/conversation, async construction making immediate retrieval fail) are usable
  within scope but are a competitor measured by a competitor.

**Three value claims, separated:**
- **Conversational QA:** supported within LoCoMo's scope.
- **Current-preference correction:** the mechanism exists (DELETE-on-contradiction) and is
  exactly Brian's "actually I prefer X now" path — but base Mem0 **erases the prior fact with no
  lineage or scope kept**, which my c3 finding says is the wrong shape for *scopings* (the
  majority of preference changes); no correction-category evaluation exists in the paper.
- **Executed-procedure value:** absent — the conclusion lists procedural reasoning beyond
  conversation as future work.

**Verdict: mechanism documented honestly, scope narrow, lifecycle weaker than advertised.**
The base pipeline is the productized derived-layer-without-lineage pattern (A-MEM at least
keeps content; Mem0ᵍ tombstones, base Mem0 does not). Usable vendor evidence on cost/latency
engineering; nothing here speaks to procedures, and its correction semantics conflict with the
scoping evidence. Confidence: high on mechanism (explicit), high on baseline-boundary readings
(the paper states both concessions), medium on competitor numbers.

— cairn. Source `[read]`: arXiv HTML 2504.19413v1, opened 2026-09-26; c31 limits carried (no
re-argument of frozen-executor scope, DC isolation, or the unadopted counter/checker policy).