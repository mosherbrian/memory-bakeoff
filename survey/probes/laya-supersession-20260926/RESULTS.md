# Laya supersession probe — result

Tern ·26 September2026 · **Do not use this served configuration/question as a supersession gate.** It was fast, but missed every genuine update and introduced six false supersessions. This is a result about one supplied-pair question on a reused synthetic set, not all Laya checkpoints, Jev, or memory classifiers.

Brian authorized one small read-only LAN probe after fair panel design. [Pre-call plan](PLAN.md), [panel release](PANEL-REVIEW.md), [hash manifest](manifest.json), [exact cases](cases.jsonl). All46 requests completed over one persistent connection at `Brians-MacBook-Air.local:8799`, 16:41:31–16:41:39 UTC. No install, retry, fitting, prompt search, production write or second run. Only each case’s request object was transmitted; labels and baseline predictions were withheld.

| Method | Correct | Accuracy | False supersessions (FP) | Missed updates (FN) |
|---|---:|---:|---:|---:|
| Laya, fixed Noul p≥0.5 | 27/46 | 58.7% | 6/33 | 13/13 |
| Always no | 33/46 | 71.7% | 0/33 | 13/13 |
| Whole-token query rule | 46/46 | 100% | 0/33 | 0/13 |

| Fixture family | Cases | Laya correct | Always no correct | Rule correct |
|---|---:|---:|---:|---:|
| Genuine update | 13 | 0 | 0 | 13 |
| Different property (ledger-amend) | 11 | 5 | 11 | 11 |
| Different entity (mailbox-rename) | 11 | 11 | 11 | 11 |
| Different entity (roster-drift) | 11 | 11 | 11 | 11 |

The rule was informed by this fixture’s construction and already scored perfectly before inference; it is not a blind generalization result. Classifier accuracy could never show improvement here. Labels predate the probe but cases share templates, so46 is not46 independent field scenarios. Historical pi-lcm retrieval-displacement scores are a different endpoint and are not a baseline in this table.

One genuine update changes delta’s Redis migration from version7 to10: p(yes)=0.3710, so it was missed. One distractor describes delta’s **Postgres** migration instead of Redis: p=0.5033, so it was falsely accepted. These illustrate the supplied same-entity/same-property question, not observed production harm. All19 wrong cases are retained in [scores.json](scores.json), and all probabilities in [scored-cases.jsonl](scored-cases.jsonl).

**Probability and latency:** the fixed p≤0.1 or p≥0.9 band accepted **0/46** cases; selective accuracy is undefined, not100%. Brier0.22465 and five-bin event-probability ECE0.11420 are descriptive only, not evidence of calibration on future traffic. The ECE bins compare mean p(yes) with the observed yes rate; this is not necessarily the author benchmark’s confidence-ECE definition. Round-trip median159ms, p95 approximately189ms, first request378ms, subsequent median158ms; full run7.829s. The already-running server was not cold-started. Labeling, fixture preparation and integration costs are excluded.

**Identity and protocol limits:** replies include Noul, a confidence field, an action.act_probability field and server milliseconds, but no checkpoint/version/temperature identity. All action.act_probability values were1.0; they were ignored by the frozen scorer. Do not interpret them as verified correctness or permission to change memory. The installed reply shape is not identical to official Jev’s Noul documentation. Unknown serving configuration and one fixed prompt prevent attributing failures to a particular checkpoint, primitive implementation or training cause. No post-result tuning was attempted.

**Decision:** keep deterministic identity/property handling for these fixtures. Narrow semantic relevance or candidate-capture screening remains a separate hypothesis, not a demonstrated fallback win or an automatically commissioned second probe. Scope, authority and deletion remain outside this classifier’s decision rights. The small run was worth doing because it rejected this proposed gate cheaply; it did not justify a service or memory automation.

[Raw replies](responses.jsonl), [run metadata](run.json), [runner](run_probe.py), [scorer](score_probe.py). Original fixture and all pre-call frozen artifacts were hash-checked unchanged after scoring.
