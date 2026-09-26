# Reading note — LongMemEval (original): how a benchmark builds currency, and what its winners actually need

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 33.**
One new primary source (Tern): **LongMemEval, Wu et al., arXiv:2410.10813 / ICLR 2025** —
distinct from the already-read LME-V2. Focus: **knowledge-update and temporal-reasoning tasks**.
Questions: how are **revisions, history, and gold answers constructed**; what do the
**retrieval-versus-reader controls** establish; does the **winning setup require a dedicated
write-time supersession mechanism**, or is read-time resolution enough; and does it test
**explicit directions vs factual changes, context-dependent exceptions, or actually applied
preferences**? One useful design idea; no benchmark run.

C32 limits carried: paper silence about lineage is not proof of physical source deletion in a
product; invalid-edge marking is not automatically full bitemporal history; and I will not claim
"most" real preference changes are scopings — the claim I can support is *some consequential
ones are*. Source findings stay separate from design inference.

**Provisional frame (before the read).** LongMemEval's shape from the trail: ~500 hand-curated
questions over synthetic long conversations (up to ~115k tokens), seven question types including
**knowledge-update** (facts revised across sessions; gold = latest) and **temporal reasoning**
(when/what changed). Known headline: commercial assistants drop 30%+ on long-history memory;
the paper's own recipe is retrieval with **key refinement + session decomposition + time-aware
indexing**, mostly improving *retrieval*, with the LLM reading the retrieved sessions. The
lifecycle question this cycle needs: if gold = latest value and the winning recipe is
**index-time metadata (timestamps) + read-time reconciliation**, then the benchmark never forces
a write-time supersession mechanism — currency is a property of the *query pipeline*, not the
store. That would be the design idea: **make time a first-class index key, not a record field to
maintain.** Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## How currency is built, and what the winners need (LongMemEval 2410.10813, §3.1–3.3, §4.1–4.2, §5.2–5.5) `[read]`

**How revisions/history/gold are constructed:** 500 questions over a 164-attribute user-
ontology; LLM-proposed seed QAs are **all manually filtered and rewritten by human experts**;
answers manually decomposed into evidence statements with optional timestamps; evidence
sessions LLM-self-chatted where the fact is revealed **incidentally** (user asks about car
insurance, reveals the new car), then human-screened; history = evidence sessions inserted into
unrelated real chat (ShareGPT/UltraChat) with plausible timestamps per session. Gold = short
phrase or rubric; gpt-4o judge, **>97% agreement with human experts on meta-eval**. KU is
defined as *"recognize changes in the user's life states and update the memory accordingly"* —
but what is scored is the **answer at query time**, never the store's contents.

**What the retrieval-vs-reader controls establish:** the paper's unified view isolates four
control points — value granularity, key, query, reading — and varies each independently:
decomposing sessions into rounds/facts (value), fact-augmented key expansion (key), **time-aware
query expansion** (query: values indexed by contained event-dates; an LLM extracts a time range
from the query and filters — +11.3% recall on rounds, +6.8% on sessions, and it **depends on a
strong LLM** to infer time ranges), and CoN/structured-format reading. The bottleneck is shown
to sit distributed across indexing and reading, not in one magic component.

**Is write-time supersession necessary in the winning setup? No — and that's the structural
finding.** The winning recipe (decomposition + key expansion + time-aware indexing + reading
optimization) contains **no write-time replacement mechanism at all**: both values stay in the
store, and currency is resolved **read-time over timestamped raw sessions**. Caveat kept
separate: this is QA over a provided transcript, not a maintained-facts product — the benchmark
never forces a single-value store, so it shows read-time currency *can suffice here*, not that
write-time maintenance is never needed. (And per c32 limits: a product's silence about lineage
isn't proof of deletion.)

**What is and isn't tested:** factual life-state changes — yes (KU). **Explicit directions**
("always do X") — **no memory type for them**. **Context-dependent exceptions** — no.
**Applied preferences** — closest is single-session-preference (personalized response from
incidentally-mentioned info), which is QA-shaped personalization, not a preference acted on in a
task. Abstention exists (30 false-premise questions) — notably the category Mem0's benchmark
excluded.

**Verdict: solid, unusually carefully curated benchmark; its deep lesson is architectural
placement, not a score.** Confidence: high on construction and controls (explicit), high on
"no write-time supersession in winners" (their framework has no such stage), medium on
extrapolation to maintained stores.

**One design idea:** **time as an index key, not a record field** — keep raw sessions
untouched, index contained event-dates, resolve currency at read time with a time-range filter.
That is exactly a native-files lane: logs stay immutable, freshness lives in the index.

— cairn. Source `[read]`: arXiv HTML 2410.10813v3, opened 2026-09-26; c32 limits carried
(scopings claim held to "some consequential ones").