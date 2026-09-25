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
(21 files, 53,225 bytes; corrected from "79 files" — 79 is all `*.md` in the
dir; per-file hashes in `corpus-pins.json`; the ai-notes repo commit does
not pin these untracked bytes, so content hashes are the pin). Config:
in-memory SQLite FTS5 index built from the frozen files; top-k fixed before
outcome access. Reversible disable path: control arm instantiates no provider
and mounts an empty memory directory — same model, same prompts, memory
simply absent. Rejected alternative: BM25-only (S7/S10 priors failed their
bars; needs corpus plus threshold selection, i.e. post-hoc risk) and the S11
coverage rule (local survival only; transfer failed in S13).
Non-mechanical judgment: FTS5 chosen for transparency and zero service
dependency, not proven superiority; engine choice is not the contrast under
test — memory presence is.

## Task pool and contamination exclusions

Pool: 20 question/answer pairs authored from the feedback files, each with a
frozen expected answer quoting the source file and line. Construction rules
(frozen before outcome access): stratify across files (≤2 questions per
file); exclude files created after the freeze commit; exclude items
referencing other items' answers (chained leakage). Calibration uses a
separate disjoint 6-item set, frozen with the pool and run once to validate
the harness executes: if calibration fails (missing outputs, harness
errors), the setup is INCOMPLETE — the pool is never rebuilt or retuned on
calibration results. Matched design: each pair runs once with memory, once
without, order randomized per pair. The pool does not exist yet; its
construction spec above is part of this freeze, and the built pool with
hashes is a release gate before any run.
Excluded existing corpora (inspected, not used): `team/invocation-corpus-
v2-standard/` and `-v3-standard/` (60 synthetic env-fact/convention
scenarios each, `correct_action_set`/`wrong_action_set`, `run_standard.py`;
structure and scoring read, results/ never opened — no prior outcome
exposure) are excluded because they test synthetic invocation routing, not
Brian's real work, and their string-presence action matching is exactly the
presumed-completion the contrast must not rely on.
`team/outcome-pilot-bundle-20260914/` (10 aggregate structural events, no
text) is excluded: aggregates with no task-level outcomes cannot serve as a
task pool. `team/PROPOSAL-R2-explicit-prompt-habit-v1.md` is excluded: it
requires Brian's explicit budget/decision plus self-install and five work
days — sponsor-gated, not available.

## Outcome rubric (narrow cued-recall endpoint, not useful work wholesale)

Primary: cued-recall task completion — answer judged correct/incorrect
against the frozen expected answer (exact-match on the quoted
decision/fact, graded blind: grader sees answer text without arm label).
This endpoint is explicitly narrower than "useful work": it establishes at
most that memory delivers file-resident facts into answers, which is
necessary but not sufficient for a real-work benefit claim. It must never
be reported as proof that the aid improves Brian's work. Secondary:
evidence delivery — whether the answer cites the correct source file
(present/absent). Retrieval scores, abstention counts, and P9/expose views
are not outcomes and not oracles. Null small-sample rule: a null result is
reported as "no detected difference at n=20", never proof of no benefit;
a null retires only the tested configuration, never the treatment class.

## Boundary

Session restart is the observed boundary: each pair runs in a fresh session;
the memory arm retains the frozen files on disk, the control arm an empty
memory directory. The observed transition is recorded, not assumed: memory-
directory sha256 before the first session ends and at each fresh session
start (continuity of state), plus per-arm claim/answer artifacts retained
for both sessions. Hash mismatch invalidates the affected pairs; absent
transition records mean the boundary was not observed for those pairs.
No compaction boundary is observed locally, so compaction is **excluded**
from all claims; the design measures restart persistence only. Stop rule:
fixed n=20 pairs, both arms fully reported win/lose/draw counts; no early
stopping on interim looks (one interim integrity check at n=10 for missing
data only, not efficacy).

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
warrant a larger preregistered replication; a null retires only the tested
configuration at n=20, leaving the treatment class open. Alternatives rank
lower: another transfer test repeats S13's failure shape; a positional rerun
changes no outcome; new protection needs a mechanism audit first.

## No-go branch

If at run authorization (a) no frozen Q/A pool with hashes exists, (b) the
provider code or corpus hash differs from the pins above, or (c) no blind
grader is available, return supported no-go naming the exact missing
prerequisite — do not run a weakened version.
