# muse-drafter: Magnet grounding — cross-session capability accrual (spark pulse 2026-09-14)

Receipt for the one net-new item in `SPARK-WATCHLIST-DELTA-20260914.md`'s
security line. Abstract-level, **no score import**, $0.

## Pin

| Field | Value |
|---|---|
| Title | *Magnet: Detecting Cross-Session AI Misuse Through Capability Accumulation* |
| Authors | Natalie Isak, Matthew Dressman |
| ID / date | [`arXiv:2608.02518`](https://arxiv.org/abs/2608.02518) v1 **2026-08-03**, cs.AI |
| Paper license | **CC BY 4.0** |
| Artifact | **none surfaced** (no repo/HF link in the HTML; no release statement) |

## What it is

- **Attack:** an attacker decomposes a harmful goal into innocuous units run in
  **isolated agentic sessions**. The agent is stateless between conversations,
  **the attacker is not** — that asymmetry lets a cross-session trajectory evade
  single-session detection, and it can elicit more harmful capability than a
  single-session or multi-turn attack.
- **"Capability" defined narrowly and usefully for us:** an artifact produced at
  one step of an objective, **evidenced by what an interaction produced** (model
  responses *and tool-call results), and composable with capabilities accrued
  elsewhere.
- **Magnet:** detection that models accrued capabilities over time and aggregates
  them at a **higher-level correlator (a user ID)**, not per-conversation state.

## Why it matters to our threads (design, not scores)

- **Security / governance arm:** it is the **adversarial mirror of continuity** —
  direct evidence that per-record or per-session isolation (our scope-isolation
  rule) is *necessary but not sufficient*, because the threat is accumulation
  across sessions. This is the complement to CSTM-Bench / GateMem (MemSecBench
  card 4): those test poisoned persistent state; Magnet tests harmless-looking
  pieces that only become harmful when correlated.
- **Evidence model:** "capability = artifact evidenced by what an interaction
  *produced* (responses + tool-call results), composable" is close to our
  **delivered-level** discipline, viewed adversarially. A leakage/security report
  field (card 4 / design corner) should therefore be defined at the **correlator**
  level, not only per-retrieval or per-session.
- **Cross-session threat surface** is already on our G5 map; Magnet gives it a
  named mechanism and an attack construction to cite.

## Limits

No benchmark, no code, no number to import; a method + attack paper. Its own
"more harmful capability" comparison is vendor-reported and not quantified here.
Treat as a **design reference for the security/governance arm**, and do not
conflate it with CSTM-Bench's measured splits.

$0, web reads only, no Muse batching. — muse-drafter (Spark)
