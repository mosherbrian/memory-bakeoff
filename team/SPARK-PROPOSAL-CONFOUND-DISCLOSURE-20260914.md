# muse-drafter proposal: comparison-confound disclosure for the citation rule (2026-09-14)

**Proposal only — no policy change, no ledger edit, no implementation.** Owner of
the rule: Verity (rule check) / Corvid (Rev 2 drafter). For GiLMore's nod if
adopted. $0, synthesis.

## The gap

`CITATION-RULE-DRAFT.md` field 4 already captures **metric + reader + judge** and
the aggregation choice. It does **not** require the controls that decide a
*comparative* claim (memory method vs long-context/RAG baseline). External
evidence that this is the live failure: **MemDelta `2606.29914`** shows reported
memory gains mix the method with the LM/embedding/retrieval — its worked example
is Mem0 "beating" verbatim-RAG on LongMemEval-S **only because the baseline used
MiniLM embeddings** (72.7 vs 61.4), and it adds that **write-path cost is
systematically unreported** (can exceed 80% of agent exec time). Our own record
already has the same shape: Alice's **14 pp full-context swing** across
frameworks with no retrieval change (RD-THREADS 743) and Assay's cost study
("no system wins both axes", 2514).

## Proposed clause (extends field 4; applies only to comparative claims)

A memory-vs-baseline comparison may appear in a Brian-facing artifact only if the
citation names, in addition to field 4 (mapped to MemDelta's six recommended
rules — see `SPARK-MEMDELTA-BODY-PASS-20260914.md`):

1. **Comparison class + what was held fixed** — memory-only, representation-only,
   or *system-level* (state it). If system-level, say so; do not read it as a
   mechanism result.
2. **Embedding model + retrieval pipeline** (top-k, budget) for **every** arm,
   or `undisclosed` marked as a confound.
3. **Baseline context size / protocol tier** (e.g. LME-V2 Small vs Medium; the
   framework swing) — the baseline's own strength is protocol-dependent.
4. **Write-path cost** reported alongside accuracy, or `not reported`.
5. **Random-retrieval control** — separates "having text" from "relevant text"
   (MemDelta rule 2).
6. **Model-family rank stability** — ≥2 answer models, or `single-model` flagged
   (MemDelta rule 3: the ranking swings 45 pp across models).
7. **Matched-instance rule** — for costly arms, name the subset and its size
   (MemDelta compares Mem0 on 88 of 500).

## What it would have caught

Mem0-vs-RAG embedding artifact (MemDelta); the 14 pp baseline swing (Alice);
cost-axis omission (Assay); CSTM-Bench's **one correlator family** and
LME-V2's **pinned Qwen3.5-9B reader** / EvoMemBench's **single DeepSeek-V3.2
backbone** — all facts that belong in the citation, not the prose.

## Non-goals

Does not replace fields 1–8, does not change any Class, adds no grade, and does
not touch Corners 7b/8 (scorer design) or Alice's transparency table. It is a
disclosure requirement, not a scoring rule.

## Handoff

- **Verity:** is a comparative-only field-4 extension operational, or does it
  belong in Alice's per-system table instead?
- **Corvid:** if adopted, fold as field 4a in the next Rev; the MemDelta pin is
  `arXiv:2606.29914` (in `SPARK-CONTRADICTION-SCAN-20260914.md`).
- **GiLMore:** nod if wanted; else file as a design reference.

— muse-drafter (Spark). Proposal, $0; no score import.
