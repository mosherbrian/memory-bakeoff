# Diagnose repeated execution failures before continuing

Adopted by Tern, 2026-09-25T19:12:18.623360+00:00. Director release rule; no new daemon, automated enforcement or allocation.

On a second worker timeout or execution/verifier FAIL in the same declared package family, Tern must record a diagnosis before releasing another attempt or phase in that family. Do not infer family from name suffixes: the package contract or release identifies the sequence. R19's twelve participant phases are one family.

The record links both failures, reads the workers' last replies and relevant tool/runtime history, and distinguishes task failure, delivery failure, check failure and missing evidence. It states the suspected or demonstrated common cause, the smallest authorized remedy, and why the next dispatch should not repeat that cause. Acknowledging, preserving, or merely reading the error does not satisfy the rule.

If proceeding unchanged is scientifically necessary, Tern must explicitly record the reason and how the repeated failure will be interpreted before dispatch. This is not permission to spend the remaining allocation repeating a known broken delivery path. A negative experimental outcome is not itself an execution FAIL: correctly delivered and graded noncompliance remains research data, not a trigger to improve participant answers.

Diagnosis has a 10-minute bound from recognition of the second failure, with an actual reminder. If unresolved at that bound, Tern sends Claude the evidence, owner and concrete question through notify-claude; the affected family remains held pending a bounded decision. Independent work may continue. No automatic extension, rerun, permission bypass, budget increase or silent prompt change follows. Frozen trials need an explicit protocol deviation and retained originals for any amendment.

For R19, Tern had already read the refusal and identified the conflicting delivery instructions, but continued unchanged after PY2-C/PY2-T. That was a release-decision error, not absent evidence. delivery-amendment-release.json in packages/R19-saved-feedback-pilot now owns the correction; operator-delivery-1.json preserves the recovered answers without retrospective loop success. Existing LB1-T is not interrupted or rewritten.

For Brian: Keep going means fixing the reason work failed, not sending the next task into the same failure. After two execution failures, we diagnose and choose a concrete remedy before continuing.
