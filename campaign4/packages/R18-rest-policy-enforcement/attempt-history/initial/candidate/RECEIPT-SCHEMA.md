# R18 receipt schema (compact)
A receipt is a JSON object stored at `next_step.receipt_path` (absolute, or
relative to GAP_CAMPAIGN). Fields: question_id, action_id (alias `action`
accepted on read), owner, deadline (UTC instant string, exact match to
next_step.deadline), objective (nonempty concrete text).
Match rule: receipt.question_id == rest.question_id AND receipt.action ==
next_step.action_id AND receipt.owner == next_step.owner AND
receipt.deadline == next_step.deadline AND receipt.objective nonempty.
A receipt proves a RECORDED COMMITMENT (a stored, question-bound next step
with owner and deadline). It does NOT prove work executed or adequate.
Substantive adequacy remains director/reviewer judgment; the checker never
claims a string match proves concreteness or completion.
