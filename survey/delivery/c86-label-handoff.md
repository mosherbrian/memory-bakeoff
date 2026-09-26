# c86 local label handoff — prepared queue complete

Tern ·26September2026. **973 message/control records and197 pairs labelled by gufo, source-checked and retained privately.** No training, calibration, threshold selection or model evaluation authorized or performed. All source gold fields remain null. [Manifest, hashes and counts](c86-label-handoff.json).

Private handoff: `/tmp/tern-laya-label-c86/handoff-v1/`, directory0700/files0600. It contains merged teacher annotations, separate independently sealed reference judgments and a manifest. Original batch files remain unchanged. No raw quotes in tracked artifacts.

| Message field | Teacher positives,973 records | Independent reference agreement | Reference abstentions |
|---|---:|---:|---:|
| Correction |292|86/97|1|
| Repeated instruction |23|91/95|3|
| Stated preference |118|67/98|0|
| Procedure |60|74/98|0|
| Unresolved |0|85/98|0|

**Receipt correction:** procedure total60, not56, because batch01 has4 rather than0 positives. All other reported grand totals match hashed files. No annotations were changed to obtain these counts.

Tern selected six random examples per60-record batch and two from the final13-record batch;98 total references were sealed before reading corresponding teacher outputs. Last-batch inclusion probability differs. The98 records contain93 unique normalized texts. Agreement is descriptive, not truth accuracy, screener recall or calibration; high negative agreement especially does not establish correction recall. Pair sample separately:20/197, relation9/20, screening13/20. Preserve both annotation layers, not a consensus called gold.

**Main usable finding:** the class definitions need to be fixed before training. Teacher preference/procedure labels exclude many situational instructions and one-off task requirements; the reference included explicit scoped preferences and some ordered methods. Missing-referent treatment also differs: the reference marks13/98 unresolved; teacher marks none. Neither agreement nor a zero-unresolved count settles which interpretation is right. The original contract did not fully resolve these distinctions. Avoid interpreting every disagreement as a gufo error; avoid silently narrowing the sponsor's high-recall capture task to standing preferences only.

**Integrity and evaluation limits:**973 messages include19 matched-control records and collapse to863 normalized texts. Exact duplicates have consistent teacher labels. Rechecking messages, both pair endpoints and controls yields zero conversation-split and zero normalized exact-text split crossings. Near-duplicate/paraphrase leakage remains untested. Splits: messages759/106/108 and pairs176/12/9 (train/calibration/heldout). These are provisional group splits, not an independently hand-labelled evaluation set; pair heldout9 is particularly small. Candidate nomination filtered the population, so these data cannot estimate missed corrections outside the candidate pool.

**Handoff decision:** close extraction/labeling of this prepared queue. Preserve provenance and disagreements. Before a separately authorized training effort, choose a task definition appropriate to capture, adjudicate a genuinely frozen evaluation sample with its needed context, and account for candidate-generation coverage. No new extraction, labeling pass, GPU test or training starts automatically. Continue the delivery queue; corrected reflector source remains the named dependency for the next CPU retest.
