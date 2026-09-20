# muse-drafter: HaluMem body pass — extract / update / QA metric split (spark pulse 2026-09-14)

Executes `CANDIDATE-CARD-HALUMEM.md` next-step 2 (borrow the
extraction/updating/QA metric split as a reporting shape — **design, not a
run**). Body read of `2511.03506v1`. Grounding only — vendor rates stay
**uncited, no score import.**

## The operation-level split (what to borrow)

Evaluation is **after each session**, not end-to-end after all sessions — this is
what localizes the stage a failure arises in.

| Stage | Metrics |
|---|---|
| **Extraction** | Memory Recall (`N_correct/N_should`) · **Weighted** Memory Recall (importance-weighted, per-item score ∈ {1, ½, 0}) · Memory Accuracy (`Σs/N_extract`) · Target Memory Precision · **False Memory Resistance (FMR) = `N_miss/N_distractors`** |
| **Updating** | Update Accuracy · Update **Hallucination** Rate · Update **Omission** Rate (against gold pairs `m_old→m_new`) |
| **QA** | QA Accuracy · QA **Hallucination** · QA **Omission** |

## Data schema and lineage

- A **memory point** carries content, **type (persona / event / relationship)**,
  and **importance**; gold update pairs are `m_old → m_new`, and **updated
  entries preserve the replaced information for traceability** — an explicit
  supersession/lineage record, the closest published analogue to our
  source-provenance shape (already noted on the card).
- Datasets: HaluMem-Medium (20 users, 30,073 rounds, ~160k tok avg, 14,948
  memory points, 3,467 QA) and HaluMem-Long (1M tok/user, 53,516 rounds); both
  ~15k memory points / ~3.4k questions. Six-stage construction (Persona-Hub
  seeds → GPT-4o; life-skeleton → event-flow → memory points → session
  generation with **adversarial distractor injection** → question generation);
  human annotation 700 sessions / 8 annotators, correctness 95.70%.

## Findings that matter to us

- **Extraction coverage is the bottleneck, and it breaks updating**: all systems
  extract <60% recall, update correctly <26% with **omission >50%** — because a
  pre-update memory that was never extracted cannot be updated. Upstream
  hallucination/omission **propagates** to QA. This is an independent, staged
  version of our formation→use→reuse chain and of "write-path is the
  bottleneck."
- **FMR** (ignoring distractor memories the assistant mentions but the user never
  confirms) is a net-new metric shape for us — maps to our distractor/near-miss
  discipline and false-supersession.

## Concrete borrowing (design)

For our own runs, report **three staged numbers + FMR** rather than one accuracy:
extraction coverage (weighted), update accuracy/omission, QA accuracy, and
distractor resistance — evaluated **per session**, so a stale-use failure is
attributed to extraction, update, or QA, not collapsed. Aligns with our
delivered-level rule and the provenance gate; no adapter planned.

## Limits

Dataset is **synthetic personae/GPT-4o dialogues** (grounds no human-behavior
goal); scoring is GPT-4o-as-judge; every rate above is vendor-reported and
**not citable**. The metric *shape* is what transfers.

$0, one arXiv HTML read, no Muse batching. — muse-drafter (Spark)
