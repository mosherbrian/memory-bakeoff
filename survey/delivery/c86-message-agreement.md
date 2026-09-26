# c86 message-label agreement — first240 records

All240 source records, IDs and split fields preserved; source gold labels remain null. Gufo annotations are provisional. Tern selected six random records per batch and sealed24 reference judgments before reading teacher labels.

| Field | Agreement with reference | Reference abstentions |
|---|---:|---:|
| correction | 19/24 | 0 |
| repeated_instruction | 22/23 | 1 |
| stated_preference | 16/24 | 0 |
| procedure | 19/24 | 0 |
| unresolved | 20/24 | 0 |

This is agreement, not measured truth or screener performance. Single-message context leaves repeat status and the boundary between one-off task instructions and reusable preferences/procedures uncertain. Keep disagreements and both judgments; do not overwrite teacher labels with reference labels or promote them to frozen evaluation gold. No training.

Raw texts and record-level differences remain private. Remaining13 message batches retain the same contract; no model experiment or new endpoint is implied.

**Completion-receipt qualification:** Cairn describes situational directives as outside stated-preference labels, whereas Tern’s reference included some explicit scoped preferences. The original contract did not resolve that distinction. Some disagreement is annotation-policy disagreement, not established teacher error. Preserve both layers; a future task definition must distinguish scoped instructions from enduring preferences before any training/evaluation gold is finalized.

**Aggregate correction from hashed artifacts:** procedure positives total19 (batch01=4), not15 (batch01=0) in the completion message. Other totals match: corrections58, repeats5, preferences39, unresolved0. No annotations were changed during reconciliation.
