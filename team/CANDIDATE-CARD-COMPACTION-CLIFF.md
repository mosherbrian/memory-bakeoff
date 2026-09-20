# Candidate card — Compaction Cliff / Knowledge Triage (typed compaction safety)

**Author:** muse-drafter (proposal-drafter seat), watchlist delta #3 follow-up (Sprint-2 goal 5)
**Date:** 2026-09-15 · **Cost:** $0 (body/API web reads only)
**Status:** **candidate discovery only — no score import.** Strongest candidate
of `SPARK-WATCHLIST-DELTA-3-20260915.md`; **both lanes released** (code
reuse-green, data under DUA). Owner unassigned; verifier: Alice.

## Provenance

| Field | Value |
|---|---|
| Title | *The Compaction Cliff in Long-Running AI Agent Memory* |
| Authors | Saber Zerhoudi, Jelena Mitrovic, Michael Granitzer |
| ID / date | [arXiv:2608.22752](https://arxiv.org/abs/2608.22752) v1 **2026-08-24**, **CIKM 2026** |
| Paper license | **CC BY 4.0** |
| Code | `searchsim-org/cikm26-knowledge-triage` — root `LICENSE` is **Apache-2.0** (GitHub's badge reads NOASSERTION; trust the raw file) |
| Data | HF `searchsim/AgentArtifactCorpus` — **CC-BY-4.0 but gated + Data Use Agreement** (396,934 configs / 54,628 repos); download needs human sign-off |
| Also released | the **classifier** + reference implementation |
| Numbers | vendor-reported only — **NOT verified, do not cite** |

## What it is

Two experiments plus a framework.

1. **The cliff.** On **20 production agent configurations**, Claude Code's
   `/compact` prompt on **Sonnet 4.6** preserves **53%** of safety rules after
   one round and **10% after five**. Separately, hierarchical truncation (the core
   of summarize-and-retain) preserves only **50% of safety constraints on 50 real
   agent configurations**. Uniform compaction summarizes a rule and an episodic
   log at the same rate.
2. **Knowledge Triage** — a typed knowledge model with **three deterministic
   operators**: **TypeCompact** (compresses without dropping safety rules;
   internally three fidelity lanes: constraints+procedures *full*,
   beliefs/preferences *compressed*, episodic *placeholder*), **TypeDecompose**
   (splits topics, duplicates spanning rules), **TypeRetrieve** (applicable rules
   first). A **verifier** extracts a canonical **negation + object** form from
   every constraint and flags the output `unsafe` if one is missing.
   Reported: **2–4× more safety rules** than the best single-shot compactor at
   every ratio, **96% recall over five rounds**; TypeDecompose **0% vs 93%**
   locality violations; TypeRetrieve **100% vs 73%** recall@50.

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **compaction arm (DIGEST/GEM adjacency)** | **good** | names the exact rule-vs-log compaction failure |
| **stale-instruction / premise resistance** | **good** | a rule paraphrased away is a stale/lost premise |
| **epistemic-type system** | **good** | typed model + per-type distortion + fidelity lanes is a concrete prior |
| **reporting discipline** | **good** | deterministic constraint-presence check + `unsafe` flag |
| G1/G2 conflict/supersession | partial | rule *currency* under compression, no old→new lineage |
| G4/G5 coding substrate | weak | no coding tasks |

## What it offers us

- **A deterministic, LLM-free constraint verifier** — *as shipped* it is
  **key-token substring survival** (≤5 distinctive tokens incl. a negation
  keyword) plus per-type recall thresholds, not the prose's "canonical
  negation+object"; see `SPARK-COMPACTION-CLIFF-CODE-PASS-20260915.md`.
- **A type→treatment table** to test against the epistemic-type-system design,
  and a **constraint-recall-at-fixed-compression** metric to add beside
  prohibited-presence.
- **A released corpus + classifier + harness** (code Apache-2.0) — the first
  delta-#3 item that could actually be *run* rather than only read, subject to
  the data DUA.

## What it cannot ground

Coding memory, supersession lineage, or retrieval benchmarks. Its guarantee is
**conditional on per-item classifier recall**; numbers are vendor; the
"production" claim partly rests on a community leaked-doc analysis. Data
acquisition needs a **human-signed DUA** (Brian/GiLMore), not a seat decision.

## Next step (bounded)

1. ~~Read the code and compare the verifier~~ **DONE**:
   `SPARK-COMPACTION-CLIFF-CODE-PASS-20260915.md` — verifier = key-token presence
   + per-type recall thresholds; reuse notes and the crude-substring caveat there.
2. If a run is wanted, the data DUA is the gate (owner decision).
3. Otherwise, feed the type→operator→lane table into the epistemic-type-system
   design as a prior.

## Verification status

Pin, venue, paper license, **code Apache-2.0 (raw LICENSE)**, and **data
CC-BY-4.0 gated+DUA** confirmed (`SPARK-COMPACTION-CLIFF-ARTIFACT-20260915.md`,
`SPARK-COMPACTION-CLIFF-BODY-PASS-20260915.md`, reconciled with
`CORVID-COMPACTION-CLIFF-PINCHECK.md`). **Code pass done** (verifier semantics
verified in-repo): `SPARK-COMPACTION-CLIFF-CODE-PASS-20260915.md`. All numbers
**unverified vendor claims — not citable**. No score import. Second seat: Alice.

— **muse-drafter** (Spark). Candidate discovery, $0; no score import.
