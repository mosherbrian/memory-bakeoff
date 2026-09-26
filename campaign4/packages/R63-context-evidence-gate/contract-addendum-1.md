# R63 contract addendum 1 (director semantic-scope addendum 04:38:23Z; written before the matching code change)
Receipt gains two required fields:
- source_evidence in {observed, inferred, indeterminate, contradicted, not_applicable}: the reviewer's check of CONTEXT_SOURCE against transcript/memory evidence. Self-report alone never establishes source.
- ask_relevant in {yes, no, not_applicable}: whether QUESTION asks for a missing task parameter.
Gate rules added (evaluated after hash/outcome binding, before approve):
- candidate in {candidate_primary, target_guessed, wrong_context_guessed, wrong_context_attributed}: approve requires source_evidence in {observed, inferred}; indeterminate -> HOLD; contradicted -> HOLD (must be rejected, not approved); not_applicable -> HOLD.
- candidate asked_no_run: approve requires ask_relevant = yes; no or not_applicable -> HOLD (irrelevant question is never legitimate clarification).
- reject stays FINAL withheld_semantic. Candidate asked_no_run alone is not semantic approval (no receipt -> HOLD, unchanged).
Also recorded: first harness run found an implementation bug (rule 9 missing the ctx != target check, so a target run with an open question became wrong_context_attributed); the frozen expectation was right and the code is fixed to match contract rule 10.
