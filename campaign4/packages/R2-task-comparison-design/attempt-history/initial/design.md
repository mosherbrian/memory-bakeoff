# R2 design: memory on/off on matched local tasks (proposal, not run authority)

Tier-1 preregistration proposal. R1 (accepted record) establishes benefit
unestablished and preserves all nulls; this design proposes one contrast that
could move the real-work question either way. No experiment is authorized;
candidate choices freeze before any new outcome access.

## Treatment and control

Treatment: `ClaudeMemFTS5CoreProvider` (SQLite FTS5 search over Brian's
feedback files; mechanical matching, no model call in retrieval) from
`implementer/repo-kiln-flash/src/memory_bakeoff/providers/claude_mem_core.py`
sha256 `53199f68…`, repo commit `be2bfa9` (plus untracked `.zcode/`, outside
the treatment path), over corpus `ai-notes/claude-memory/feedback_*.md`
(79 files, 512K), repo commit `be6cc97`. Config: in-memory SQLite FTS5 index
built from the frozen files; top-k fixed before outcome access. Reversible
disable path: control arm instantiates no provider and mounts an empty memory
directory — same model, same prompts, memory simply absent. Rejected
alternative: BM25-only (S7/S10 priors failed their bars; needs corpus plus
threshold selection, i.e. post-hoc risk) and the S11 coverage rule (local
survival only; transfer failed in S13).
Non-mechanical judgment: FTS5 chosen for transparency and zero service
dependency, not proven superiority; engine choice is not the contrast under
test — memory presence is.

## Task pool and contamination exclusions

Pool: 20 question/answer pairs authored from the feedback files, each with a
frozen expected answer quoting the source file and line. Construction rules
(frozen before outcome access): stratify across files (≤2 questions per
file); exclude files created after the freeze commit; exclude questions
answerable from general knowledge without the files (pilot both arms on 3
calibration items first — if control answers ≥2, the pool is too easy and
must be rebuilt, not run); exclude items referencing other items' answers
(chained leakage). Matched design: each pair runs once with memory, once
without, order randomized per pair. The pool does not exist yet; its
construction spec above is part of this freeze, and the built pool with
hashes is a release gate before any run.

## Outcome rubric (task completion, not proxies)

Primary: task completion — answer judged correct/incorrect against the frozen
expected answer (exact-match on the quoted decision/fact, graded blind:
grader sees answer text without arm label). Secondary: evidence delivery —
whether the answer cites the correct source file (present/absent). Retrieval
scores, abstention counts, and P9/expose views are not outcomes and not
oracles. Null small-sample rule: a null result is reported as "no detected
difference at n=20", never proof of no benefit.

## Boundary

Session restart is the observed boundary: each pair runs in a fresh session;
the memory arm retains the frozen files on disk, the control arm an empty
memory directory. No compaction boundary is observed locally, so compaction
is **excluded** from all claims; the design measures restart persistence
only. Stop rule: fixed n=20 pairs, both arms fully reported win/lose/draw
counts; no early stopping on interim looks (one interim integrity check at
n=10 for missing data only, not efficacy).

## Confounds and limits

Model stochasticity (temperature 0, single run per arm, verbatim outputs
retained); file-selection bias (stratification + frozen pool); judging bias
(blind grading + rubric); order effects (per-pair randomization); corpus
contamination by model pretraining (same model both arms — controlled by the
contrast, disclosed); file edits mid-run ( corpus hash re-verified at
analysis; any drift invalidates affected pairs). Effort estimate: ~4 author
hours (pool construction + frozen grading) + machine time negligible; no
new harness (existing provider + scripts only).

## Why this discriminates; what changes the decision

Memory presence is the only systematic difference between arms, so a task-
outcome gap is attributable to it; a null is informative because the tasks
require file-resident facts the control cannot see. A positive gap would
warrant a larger preregistered replication; a null would retire this
treatment/task-class without further tuning. Alternatives rank lower: another
transfer test repeats S13's failure shape; a positional rerun changes no
outcome; new protection needs a mechanism audit first.

## No-go branch

If at run authorization (a) no frozen Q/A pool with hashes exists, (b) the
provider code or corpus hash differs from the pins above, or (c) no blind
grader is available, return supported no-go naming the exact missing
prerequisite — do not run a weakened version.
