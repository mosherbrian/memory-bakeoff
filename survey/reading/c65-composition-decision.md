# Decision note c65 — composing context without a maintenance job: two controls, one rejected inference

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 65.**
Skeleton first; own c61–c64 only; no new source. C64 corrections carried: no universal difficulty
ordering, no model-independent effective length, **no established incremental-editing advantage**;
word-frequency tasks are unvalidated summarization proxies; failures do not identify causes by
category; no per-record verification, automatic retirement, or sponsor-review ritual.

*(decision appended below)*

## Two genuinely discriminating controls

**1. The same composition move, two outcomes (Lost in the Middle §4.2, c63)** `[read]` — query
before **and** after the data: UUID lookup 45.6% worst-case → near-perfect; multi-doc QA unchanged
or slightly worse. Same models, same corpora, one intervention, opposite verdicts by task type.
This is the only control in c61–64 that discriminates **composition advice itself**: placement
interventions are task-specific, so neither "always repeat the query" nor "composition doesn't
matter" survives.

**2. Window extension changes nothing (c63)** `[read]` — the 16K variant is superimposed on its
base at shared lengths. Discriminates against the "more context capacity" remedy: what to put in
the window is a different decision from how big it is. (Scope: 2023 models, tested pairs.)

c61's LongMemEval/PersonaMem pair and c64's task-config variation **establish responsibilities**
(currency is a real failure surface; usable length varies with configuration) but, per the
carried corrections, cannot rank mechanisms or prescriptions.

## The tempting inference to reject

**"Aggregation is hard, so maintain the current view by incremental local edits."** My own c64
reach. The ordering isn't universal, the aggregation proxy is unvalidated for meaning-bearing
summaries, and RULER **compares no update strategies** — incremental edits can equally miss
distant contradictions or drift. No read in c61–64 picks an update policy.

## Advice (one sentence)

**Compose the next task's view from the task itself** — the handful of records its own name,
current direction, or named artifact point to, each carrying scope and date — and leave
everything else recoverable by search; no standing bundle, no audit, no pre-knowing which
preference will matter.

**Architecture change: none.** This is a judgment refinement on the existing arrangement, which
is the honest outcome — c61–64 supply two placement controls and a rejected prescription, not a
new component or a recurring duty. My maintained-view preference (c61 dissent) stays conditional
on it saving repeated interpretation, and composition-from-task is how it gets consulted, not a
reason to grow it.

**Confidence: high on control 1 (explicit within-paper contrast), high on control 2 as scoped,
medium that compose-from-task outperforms a curated bundle for Brian — no read runs that
comparison, and I am not pretending otherwise.**

— cairn. Built from reading/c61–c64.