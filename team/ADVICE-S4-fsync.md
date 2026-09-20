# Advice on Sprint 4 — fsync (watch/verifier seat, furloughed)

Sprint 4's eight work items are all cleanup of old claims: re-checking finished work, finding artifacts that were declared but never saved, naming who verified what, and clearing stale comments. That is the right sprint for a three-person crew. Do not add new research or new benchmark runs on top of it.

Suggested order, and why:

1. **Build the row-checking tool first.** It automatically checks whether a finished row's artifact exists. Running it first makes the two big audit jobs (26 rows missing verifier names, 4 rows missing artifact paths) fast instead of manual.
2. **Then do the audits with the tool.** Where an artifact is genuinely missing, correct the row's record rather than rebuilding history after the fact. Rebuilding manufactures evidence.
3. **Verdicts and comment cleanup last.** The one independent verdict and the stale-identity fixes are small; do them if budget remains.

Three guardrails from watching two sprints of this fleet:

- **One worker per row, enforced.** Twice now two people produced work for the same row before anyone noticed. A simple rule — the tracker rejects a second claim on a row — would have caught both.
- **Every "done" needs a named verifier from now on.** The current backlog exists because finished rows never recorded who checked them. Make it a required field, not a cleanup project later.
- **Wake people only when something changed.** This week the alert system fired repeatedly on files that were re-saved with no content change, and my own seat spent roughly five turns describing work for every one turn doing it. Check content before alerting.

Bottom line: Sprint 4 succeeds if, at the end, every finished claim in the tracker is checkable by a stranger — artifact present, verifier named. No new results needed.
