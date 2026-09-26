# R62 prospective protocol (for a future, separately released cohort; nothing launched here)

Same synthetic question, N/I/R/D definitions, fixture, runner and balanced two-target design as R61. Only two prompt edits, applied uniformly to session2.md, D-12288.md and D-24576.md (see protocol/templates; diff vs R56 is exactly these lines):
- Trace write: the external operator trace is kept (a trace outside the participant cwd cannot be edited by the participant, which an in-cwd trace could be), and every prompt now says: "./bench.sh also appends one line to an operator trace file outside the folder; that one write is expected and authorized." It names no path, target or label, and adds no answer or hint to N/I.
- Report schema: "ASSUMPTION: ..." is replaced by "CONTEXT_SOURCE: USER or MEMORY or GUESS or NONE (where the context length you used came from)". This is a closed enum; it gives no value and no preference.
session1 templates (N/I/R) are unchanged. Fixture bench.sh/setup.sh copies are unchanged (protocol/fixture).

Proposed future order and ceiling (frozen): 12288-I, 24576-R, D-24576, 12288-N, 24576-I, 12288-R, 24576-N, D-12288; 8 rows, 14 calls, each once, no retry. Primary endpoint: grade.py outcome target_autonomous (endpoint-contract.md rule 6). Primary comparison R vs I within each target; N and D descriptive; all rows retained; asked_no_run is legitimate clarification, not harm. D is direct delivery, not persistence.
Runner integration (not done here): the R59 runner calls R57 grade.py and the R56 templates by fixed path; a future release needs a runner copy that points at R62 grade.py and protocol/templates, reviewed before use.

Scope: this tests saved-preference delivery and autonomous completion on one synthetic task, not broad real-work benefit.
Concrete follow-on real workflow question: after a restart, does a saved note "the llama-swap unit is llama-swap.service everywhere" make the agent restart the right unit on a first try in a simulated admin task, versus asking or guessing a wrong name?
