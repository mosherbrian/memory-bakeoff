# R54 readiness
Implemented and proven offline: events.py (11/11 fixture tests; R53 reanalysis matches all director counts); synthetic fixture + grader with a deterministic walkthrough (both targets graded 'target', a default guess 'ran_other_ctx', a question 'asked', bench refuses without --ctx).
Proposed: the context-length task (design.md, protocol.json, templates).
Unverified: that Sonnet 5 does not default to a large context by habit; that it asks rather than guesses (both are measured outcomes, not assumptions).
One next step: a 2-call qualification (one N arm, block-1 fixture) to see the model's no-memory behaviour on this task before a 19-call trial.
