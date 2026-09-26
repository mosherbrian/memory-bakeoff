# PersonalWAB: a correct function is not necessarily a useful result

Tern · cycle48 ·26 September2026 · focused primary read complete; all panel pieces synthesized. [PersonalWAB/PUMA,2410.17236v2](https://arxiv.org/html/2410.17236v2), §§3,5,6 and AppendixA.

**Source findings.** Amazon behavioral records underpin generated profiles/instructions; per-user chronology is 80/10/10 history/train/test, not disjoint users. Profile generation's “entire history” wording leaves its precise temporal boundary unclear. Search/recommendation execute functions; review posting is assumed. Outcomes use target-item rank or review similarity. Multi-turn users are simulated with target information. InteRecAgent updates profiles after tasks. Full trained PUMA is not evaluated multi-turn; task-specific memory is.

Single-turn Table5:

| Variant | Overall function accuracy | Overall result score |
|---|---:|---:|
| PUMA | .994 | .406 |
| Without task-specific memory | .994 | .373 |
| Without SFT | .994 | .054 |
| Without DPO | .994 | .399 |

These are component ablations, not per-entry causal effects; the precise removal/retraining boundary is not fully described. AppendixA.4.5 separately credits relevant results regardless of search/recommendation route. Training hardware and inference timing are reported; full cost is not. Real-user correction burden remains unmeasured.

**Judgment.** Function correctness is diagnostic, not automatically the user objective. Prefer a permitted route that delivers the useful result; this never overrides actual constraints. No-memory versus memory should be judged on the result, not merely valid calls.

Corvid's synthetic-history characterization misses the distinction between behavioral records and generated profiles. Coupling does not imply no component evidence. Kiln's “no correction loop anywhere” conflates missing durable supersession with simulated feedback and an updating-profile comparator. Function-conditioned field selection is a useful candidate, not a universal retrieval requirement. Existing histories may already provide behavioral evidence without another store.

Confidence high on inspected endpoints, medium on transfer; profile chronology and ablation implementation remain limited. No experiment, installation or host change.


**Final control qualification:** the trained actor changes in SFT/DPO ablations. Single-turn near-flat generic retrieval does not extend to multi-turn results. The GPT-based task-specific-memory row also improves the overall result. Model naming differs between table headings and implementation text; reported latency cannot become a Brian-local comparison. [Final panel decision](../panel-response-c48.md).
