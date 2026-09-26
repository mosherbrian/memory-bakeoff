# Laya supersession sanity probe — pre-call plan

Tern ·26 September2026. Brian authorizes one small local LAN probe after fair panel design. **Prepared, awaiting panel review; no model calls yet.** Scope: read-only existing synthetic fixtures, one memory decision, maximum46 inference requests, no install or store changes.

## Fixed task and labels

Use all46 trials in `team/S10-PI-LCM-HIST/trials.jsonl`, SHA256 recorded in [manifest.json](manifest.json). Each case pairs the original record with the last incoming record and the original query. The historical declaration, written before its run, labels13 genuine updates and33 different-fact distractors. The model receives only query and the two record texts; it sees no trial id, family, role, expected result or baseline. Exact requests/labels are frozen in [cases.jsonl](cases.jsonl).

Question: does the later record supersede the old record's **current value for the same entity/property**? This is not permission to delete the original or decide whether it remains useful historically. Query terms and records are equal inputs for the classifier and keyword baseline. Distinct services or properties do not supersede each other. The labels and examples are inherited synthetic construction, not a fresh human study or unseen test set.

## Baselines and policy, before inference

- Always predict **no**, the majority class:33/46 correct, all13 updates missed.
- Whole-token keyword rule: every query token appears in the new record, with hyphenated compounds retained as whole tokens. Regex and predictions are recorded in the manifest/cases. Already computed **46/46 correct**. This rule is informed by the known fixture mechanism; no blind-generalization claim.
- Laya: the single fixed `noul` question in the cases; yes at p≥0.5. No training, fitting, prompt search, retries or threshold selection.

The baseline ceiling is intentional. This run can reveal a broken/unhelpful classifier on a previously solved distinction; it cannot demonstrate improvement over the rule or justify general memory automation. Do not import the historical22/33 retrieval-displacement error as this classifier's baseline metric.

## Execution and reporting

After panel review, use one persistent TCP connection to `Brians-MacBook-Air.local:8799`, newline-delimited JSON, via `/bin/bash` and Python standard library. Maximum46 requests; socket timeout10s, overall180s; stop on errors or malformed replies. Existing source data is untouched. Preserve requests/replies, timestamps and measured request latency. No daemon restart: first-request time is not a cold-model benchmark. The served checkpoint/configuration is unknown unless returned in metadata; limit conclusions to this observed service, not every Laya version.

Report attempted/completed counts, confusion matrices, accuracy, false-retirement and missed-update counts, descriptive Brier/ECE(5 fixed equal-width bins), and the predeclared high-confidence subset p≤0.1 or p≥0.9 with retained fraction/error. Small template-correlated cases cannot certify calibration or rare-error rates. Report all cases and families; no dropping inconvenient failures. Latency includes transport/serving, not labeling or setup; no end-to-end work-saving claim. A pass only says this served model handled this fixture under this question.

The [larger relevance proposal](../../proposals/jev-laya-mac-probe.md) is deferred. It is not a second authorized run within this plan.
