# muse-drafter: contradiction-term fan-out against the 5 new candidates (spark pulse 2026-09-14)

Follow-up to `SPARK-VOCABULARY-FANOUT-20260914.md` ("next: contradiction-term
fan-out"). Directive §12.6: the highest-value half of discovery is the negative
evidence. Queries appended `limitations`, `criticism`, `replication`,
`false positive`, `no improvement`, `contamination` to each candidate. Primary
HTML read where it surfaced. Candidate discovery only — **no score import**.

## Per-candidate outcome

| Candidate | External critique / replication | Self-declared limits (primary) | Artifact |
|---|---|---|---|
| BeliefShift `2603.23848` | none found | trajectories simulated (human-authored + synthetic); CRR not auto-scored yet; English-only, single cultural frame | **no code/data link surfaced** |
| MemoryArena `2602.16313` | none found | repo is a **"preview version … actively maintaining"** (`ZexueHe/MemoryArena`); low completion attributed to representation/training mismatch, not memory absence | code repo + site `memoryarena.github.io`; license unverified |
| CSTM-Bench `2604.21131` | **follow-on critiques it**: *Magnet* `2608.02518` builds on/critiques CSTM-Bench's intent-tracking; measures cross-session decomposition ASR 18.7%→26.0%→37.4% by delivery mode | in-paper scope: 54 scenarios/shard, **one correlator family (Anthropic Claude)**, no prompt optimisation, append-only by design; released "to motivate larger, multi-provider datasets" | HF `intrinsec-ai/cstm-bench` **MIT** (prior pass) |
| CodeTracer `2604.11641` | none found | not searched this pass | MIT repo+HF (prior pass) |
| PrecisionMemBench `2605.11325` | none found | single independent author; 89 cases | unverified |

## Payoff: one net-new load-bearing find

**MemDelta — `arXiv:2606.29914`, "Controlled Baselines and Hidden Confounds in
Agent Memory Evaluation."** Not in `RD-THREADS`/`ECOSYSTEM-MAP`/`QUEUE`/`CLAIMS-LEDGER`.
Its thesis is a direct, independent statement of our comparability discipline:
reported agent-memory gains **mix the memory method with changes in the language
model, embedding model, or retrieval pipeline**. Worked example: Mem0 "beats" a
verbatim-RAG baseline on LongMemEval-S **only because the baseline used MiniLM
embeddings** (72.7 vs 61.4); swap the answer model and Sonnet refuses a
long-context question the full-history baseline should answer, so the baseline's
measured strength is itself model-dependent. Adds two audit rules we do not
enforce: **disclose the embedding model**, and **report write-path cost** (which
it says can exceed 80% of agent execution time).

This is the method paper behind three things already in our record:
Alice's 14 pp full-context swing across frameworks (`ALICE-SMARTSEARCH-CLUSTER`,
RD-THREADS 743) and Assay's cost study / Memora verification (RD-THREADS 2514).
**MemDelta is not a new score source — it is a controlled-baseline protocol we
should fold into the citation/evidence rule before the next arm**, so a future
memory-vs-long-context delta names every variable it left free.

## Already in record (do not treat as new)

- **Memora `2604.20006`** (ACL 2026 Findings) — Assay verified "frequent reuse of
  invalid memories … marginal improvements" exact and logged **FAMA** as an
  external formulation of the false-supersession gate (RD-THREADS 2514). The
  contradiction pass re-found it; it is **not** net-new, and still has no card.
- **Benchmark contamination** — systematic review (GEM 2026, 6–40% inflation
  estimates) and "Rethinking Temporal Signal of Benchmark Contamination" (ACL
  2026) are method references for our contamination discipline, not candidates.

## Scope caution surfaced for the cards

BeliefShift's own framing is that **"opinion drift is not a memory problem; it
is a reasoning problem"** — so if carded it must be labeled a *belief-dynamics /
reasoning* analogue to axis C, not an agent-**memory** benchmark; it would be
misread as a memory score otherwise.

## Limits

Abstract/HTML/README level; no numbers imported, no score import. External
critique searched for all five but exhausted only for CSTM (Magnet) and the
MemDelta cross-reference; CodeTracer/PrecisionMemBench contradiction search
still open. Licenses unchanged from the fan-out pass. Second seat: Alice.

$0, web reads only, no Muse batching. — muse-drafter (Spark)
