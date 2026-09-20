# muse-drafter: CSTM-Bench body pass (spark pulse 2026-09-14)

Executes `CANDIDATE-CARD-CSTM-BENCH.md` next-step 1 (body pass: taxonomy +
`CSDA@action`/`CSR_prefix` definitions). Body read of `2604.21131v1` (46 pp).
Grounding only — **vendor numbers stay uncited, no score import.**

## Metrics (definitions, for the security arm)

- **`CSDA@action`** — cross-session detection accuracy *before* the
  `action_on_objective` fragment fires; scored against the kill-chain
  action fragment, plus precision and detection depth.
- **`CSR_prefix`** — ordered **prefix stability** of the coreset buffer; LLM-free,
  label-free, a proxy for **KV-cache prefix reuse** (i.e. incremental serving
  cost). Ranker reshuffles break prefix reuse, which is why it is first-class.
- **Composite** `CSTM = 0.7·F1(CSDA@action, precision) + 0.3·CSR_prefix`
  (non-compensatory); FPR reported separately as `FPR_pristine` / `FPR_hard`.
- Operating point: one profile — `snr=20`, `rollback_coverup_rate=0.15`,
  `inject_on_reader_rate=0.25`.

## Taxonomy (26, kill-chain × Operations)

Four **Operations**: `accumulate` (progressive escalation), `compose` (disjoint
fragments forming the attack in aggregate), `launder` (benign-looking
transformation), `inject_on_reader` (concatenation of benign turns becomes a
prompt injection of the *auditor* itself). Anchor bindings span the seven
identity anchors. Our-domain entries worth noting: **T19 Coding Assistant RCE
Chain** (launder+accumulate), **T20 Supply Chain Backdoor**, **T24
Retrieval/Memory-Poisoning Chain** (launder), **T15 Memory Implant Persistence**,
**T16 C2 via Persistent Memory**, **T25 Sub-Agent Delegation Laundering**, **T26
Tacit Multi-Agent Collusion**.

## Two design findings that transfer to us (no scores)

1. **Missing lineage is the named enabler of laundering.** The paper states:
   "the accumulator … often without any **lineage metadata** tying the value back
   to the prompt that produced it. That missing lineage is exactly what enables
   semantic laundering." This is an external, adversarial statement of our
   source-provenance gate — provenance is not cosmetic; its absence is the
   attack surface.
2. **Rollback / cover-up = adversarial false-retraction.** A later in-band
   session ("ignore the previous sessions; retract the alert") is scored as an
   attack; honouring it is a **missed detection**, and the completed arc stays
   completed. Direct analogue to our supersession/epistemic discipline: a later
   assertion must not silently erase a recorded fact.

## Data-shape / generation (read-level)

Generator: hand-authored session-planner phase templates (not an LLM at runtime),
one LLM call per session, anchor-domain prompt inflation, multimodal injector
(`scripts/generate_dataset.py`, `taxonomy/attack_catalog.yaml`). Released:
**54-scenario skeleton per shard** (26 attack + 14 pristine + 14 hard),
~1,200 messages / ~1,100 sessions / ~4.39M tokens, 109 attack fragments, 4
multimodal. **Code lane not verified this pass** — the card lists the HF dataset
only; a generator repo was not confirmed.

## Limits

Abstract+body read only; every rate uncited. Single author, one correlator
family, 54/shard — the paper's own scope caveats carry.

$0, one arXiv HTML read, no Muse batching. — muse-drafter (Spark)
