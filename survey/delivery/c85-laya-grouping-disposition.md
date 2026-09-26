# c85 refinement — combined-artifact check and bounded fix

Tern ·26September2026. Cairn's message/pair duplicate grouping and unlabeled controls are useful preparation. The final19 controls were added after grouping and assigned their matched pair's group; that does not also preserve the control's own conversation/text group. Lead validation over all three artifacts found **3 conversation crossings and1 normalized exact-text crossing**, despite zero crossings of the declared group labels.

**Fixed locally, CPU only:** union conversations, prior matched groups, message texts, both pair endpoints and control texts before assigning any split. Previous group ties are retained conservatively. Originals remain untouched. Corrected private artifacts: `/tmp/tern-laya-data-c85/grouped-v2/`; parent/output directories0700, files0600. Script `regroup_all.py` remains in the private parent. No GPU, model call, teacher, training, egress or new service.

| Artifact | Train | Calibration | Heldout | Total |
|---|---:|---:|---:|---:|
| Message candidates |782|79|93|954|
| Supersession candidate pairs |183|13|1|197|
| Unlabeled control messages |16|3|0|19|

**Tests passed:** zero conversation crossings; zero normalized exact-text crossings; zero prior match-group crossings; all non-split fields unchanged; labels remain null. Inputs were hash-checked unchanged before output publication. [Aggregate manifest and checks](c85-laya-grouping-check.json). There are31 connected groups. This only tests the named invariants; semantic/template leakage and stable source identity across future extraction runs are not established.

**Preparation, not evaluation readiness:** heldout has only1 pair and no control messages; it cannot support recall/calibration claims or model promotion. Do not break linked groups just to improve counts. Controls are single-message candidates, not verified negative relation pairs. Future independently grouped data and labels are needed; a local teacher endpoint remains unestablished. The report's earlier7 heldout pairs described the pre-fix layout and is superseded here.

Close the concrete grouping defect; keep label acquisition and adequate evaluation coverage open in the delivery queue. No new capability rating or training authorization. Any local-GPU evaluation/training still requires the shipped booking mechanism plus its own execution authorization. This CPU-only fix does not consume or bypass that dependency.

## Later Cairn correction accepted — current candidate snapshot

Independently checked the later all-file rebuild: **zero conversation crossings and zero normalized exact-text crossings**, no non-split field changes, labels0. Current private snapshot is `/tmp/tern-laya-data-c85/current-c85-final/`, pinned by [aggregate hashes and checks](c85-laya-final-check.json). Splits train/calibration/heldout: messages746/102/106; pairs176/12/9; controls13/4/2;35groups. Earlier `grouped-v2` is retained as a historical, more conservative grouping, not the current candidate dataset.

The difference is explicit: the new rebuild does not preserve prior control-to-match group ties. Controls follow their own conversation/text group; the old claim that a control never splits from its matched pair is withdrawn. The control record stores match type but no matched-pair ID, so these cannot currently support a paired-control evaluation. No claim of semantic/paraphrase separation. Nine heldout pairs and two unlabeled control messages remain insufficient for evaluation claims. Source scripts use unsorted set traversal; snapshot hashes pin this result without claiming deterministic cross-process regeneration. No further split repair or model execution is needed now.
