# Laya: trained local correction prefilter — design option B

Tern · cycle80 sponsor correction ·26September2026. **Design candidate only; no training, dataset extraction, labeling calls, Jev calls, installation or second Laya run.** Owner proposed: Claude for dataset/model deployment and reporting; Brian is not assigned routine labeling or memory upkeep.

## Evidence and corrected scope

The [author README](https://github.com/NandhaKishorM/laya#fine-tune-for-better-accuracy), read today, reports typed-decisions accuracy0.362 for base English versus0.766 after task-specific fine-tuning. It links a Kaggle2×T4 notebook covering dataset creation, training, temperature fitting and evaluation. It also warns that shipped probabilities are overconfident. These are author results on that benchmark, not measured correction-detection performance on Brian's messages. The earlier ECE checkpoint/population distinction remains; no pooled calibration claim is adopted.

**c67 verdict:** zero-shot base configuration rejected for the supplied supersession question, not Laya as a trainable method. Claude now identifies the served checkpoint as the shipped base; the run itself recorded no checkpoint hash/version/temperature. Keep both facts: later operational identification and incomplete contemporaneous identity. Counts unchanged:27/46, majority33/46, keyword46/46. The rule wins on these surface-derivable fixtures; that is not general supersession validation. [Corrected result](../probes/laya-supersession-20260926/RESULTS.md).

## Proposed role in option B

Pi/Claude Code + existing skills + Perseus Context Engine remain the host/delivery arrangement. A **local reflector prefilter** would flag a user message as a correction, repeated instruction or stated preference; it nominates material for the reflector, never decides authority, supersession or deletion. Labels must distinguish quoted/hypothetical/third-party text from the principal's own directions. Repetition needs prior conversational context; an isolated-message classifier cannot establish it. Source transcripts remain recoverable even when the filter misses a candidate.

Proposed training: a frontier teacher labels a few thousand representative messages with bounded context; fine-tune Laya, then fit temperatures on a separate calibration split. This is distillation, not proof the teacher is correct. Keep evaluation conversations/time periods separate from training and calibration, and avoid near-duplicate leakage.

**Fair comparison:** one frozen, independently hand-labeled held-out set, separate from teacher-derived training labels; same input/context for Laya, keyword rules, majority and Jev. Primary metric is correction/candidate **recall** because a miss loses a capture opportunity. Also report precision, fraction passed to the reflector, and representative misses—an all-positive filter gets perfect recall while removing no work. Set the operating point on calibration data, not test outcomes. Name served checkpoint, prompt, temperatures and threshold. Report labeling/training cost separately from local per-message cost. No new evaluation has been commissioned.

**Privacy/cost boundary:** local serving removes per-message vendor dependence and transcript egress for the filtering step. A hosted frontier teacher, Jev comparison or uploading messages to Kaggle still involves egress; the entire proposed workflow is not automatically local. Kaggle is an author-provided training route, not a recommendation to upload Brian's transcripts. Data route and training resources remain explicit choices before any separately authorized execution.

**Recommendation:** keep as option B's optional trained capture component, not its prerequisite or default retirement mechanism. Confidence medium in architectural fit, low in local benefit until measured. Capture was not the leading reported bottleneck; this component must reduce reflector workload without materially losing candidates to earn adoption. Supersession on the c67 fixtures remains deterministic rules. The independent trigger and the trained classifier are separate responsibilities; no deployed reflector integration is claimed.


## Cycle81 scope extension — pair screening is a separate task

Brian now proposes a three-stage supersession/correction cascade: Laya pair screening → provisional LLM relations → nightly scoped consolidation. The earlier message-level correction detector and this pair-level invalidation screener require different labels/inputs; success on one does not validate the other. The cascade target≈0.98 recall is unmeasured and requires candidate-generation coverage plus a locked test after threshold selection. Daytime flags never suppress content. [Complete option B and challenge](../OPTION-B-CASCADE.md). No model call, training or store scan performed.


**Cycle81 learning-loop extension:** periodic retraining from provenance-tagged provisional and human-corrected examples; nightly random unflagged exploration; frozen gold promotion test separate from training/calibration and prompt retrieval; rollbackable model/temperature/threshold bundle. Judge and reflector learn from retrieved examples with weights fixed. [Survey evaluation](../OPTION-B-LEARNING-LOOP.md). Proposed only; no trained-task result or automatic promotion facility verified.
