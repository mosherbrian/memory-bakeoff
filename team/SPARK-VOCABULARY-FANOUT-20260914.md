# muse-drafter: discovery-vocabulary fan-out scan (spark pulse 2026-09-14)

Executes the **vocabulary fan-out** thread-pool item from the intelligence
directive (`RESEARCH-INTELLIGENCE-DIRECTIVE.md` §7.2, §12.2; canonical query
list in `CORVID-DISCOVERY-VOCABULARY.md` §3). That note maintained the query
list; this pass *runs* it. The named 8-card harvest is closed (`RD-THREADS`
3012), so this is the first post-harvest scan. Candidate discovery only — **no
score import**.

**Decision frame (directive §12.1):** which benchmarks/mechanism papers testing
long-horizon agent *state*, *belief change*, or *trajectory provenance* already
carry public artifacts, exist outside the word "memory", and are not yet carded?

**Method.** Three queries deliberately avoiding "memory": `"cross-session state
tracking" agent benchmark`, `"belief revision" LLM agent benchmark`,
`"event sourcing" OR "state reconstruction" agent trajectory benchmark`. Grepped
`RD-THREADS.md` / `ECOSYSTEM-MAP.md` / `QUEUE.md` for every hit; discarded those
already carded. Contradiction terms not used this pass (next fan-out).

## Net-new candidates (none present in the ledger)

| # | Candidate | ID / date | Fit | Artifact status |
|---|---|---|---|---|
| 1 | **BeliefShift** — temporal belief consistency, contradiction detection, evidence-driven revision; 2,400 human-annotated multi-session trajectories; metrics BRA/DCS/CRR/ESI | `arXiv:2603.23848`, 2026-03-25 | **G1/G2, axis C** | abstract-level only; no code/data link surfaced; license to verify |
| 2 | **MemoryArena** — gym for multi-session Memory–Agent–Environment loops with interdependent subtasks | `arXiv:2602.16313` | **G4/G5** | abstract-level; ICML'26 review found; license to verify |
| 3 | **CSTM-Bench** — cross-session threat detection; stateless guardrails miss attacks whose aggregate is malicious; 26 taxonomies, kill-chain × cross-session-pattern; 54+54 splits | `arXiv:2604.21131`, 2026-04-22, cs.CR | **security arm**, G5 as threat surface | HF `intrinsec-ai/cstm-bench`, **MIT** (primary-read, 108 rows) |
| 4 | **CodeTracer / CodeTraceBench** — trajectory diagnosis with step-level annotations, failure-onset localization, cross-trajectory memory | `arXiv:2604.11641` | **coding substrate / provenance / failure trajectory**, G4/G5 | repo `NJU-LINK/CodeTracer` **MIT** + HF `NJU-LINK/CodeTraceBench` (primary-read; **3,316 distinct** full, of which **1,000 verified** — do not cite the 4,316 default split, it is their union) |
| 5 | **PrecisionMemBench** — precision / noise isolation / session latency / belief mutability over 89 cases; decouples retrieval precision from generation; frames memory as state-management *and* search | `arXiv:2605.11325`, May 2026 | E-3/E-4 + our leakage-not-recall discipline | abstract-level; independent researcher (lower confidence); license to verify |

## Excluded as already covered

StateMemBench (`2608.19652`, card 6), STALE (`2605.06527`, card 3),
LongMemEval/LME-V2 (cards), MemSecBench/GateMem (card 4), EvoMemBench
(card 8). `"cross-session state tracking"` mostly re-surfaced card 6 — evidence
the query list works and this class is partly harvested.

## Why these five, ranked

1. **BeliefShift** — the "belief revision" vocabulary hit, and the only one that
   scores **contradiction detection** and **evidence-driven revision** as
   separate tracks; direct external analogue to our axis-C / E-7 concern.
   Gap: no artifact link seen.
2. **MemoryArena** — an actual memory–agent–environment *execution* loop, closer
   to our G4/G5 shape than recall-only benchmarks.
3. **CSTM-Bench** — gives the security arm its second independent lens beside
   MemSecBench/GateMem, and it is **MIT with the dataset on HF (primary-read)** —
   cheapest to reuse.
4. **CodeTracer / CodeTraceBench** — coding-trajectory provenance and
   failure-onset localization; overlaps our transcript-mining substrate and the
   session-memory continuity thread; MIT.
5. **PrecisionMemBench** — conceptually aligned with our "leakage is not
   recall" rule and exact-context-size reporting, but single-author and
   unverified; keep as a framing reference.

## Limits

Abstract- or README-level only; **all quantitative claims unverified, none
imported**. Licenses primary-read only for CSTM-Bench (MIT) and CodeTracer
(MIT); BeliefShift/MemoryArena/PrecisionMemBench licenses unverified. Second
seat: Alice. Next pass: contradiction-term fan-out (`fails`, `no improvement`,
`replication`, `contamination`) against these five.

$0, web reads only, no Muse batching. — muse-drafter (Spark)
