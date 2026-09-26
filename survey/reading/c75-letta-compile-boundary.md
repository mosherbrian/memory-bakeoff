# Reading note c75 — Letta compile boundary: what does the compiled context actually read, and is the merge validated?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 75.**
Skeleton first; **requirement 2**, the one path c74 left open: committed memory / reflection
worktree **merge → compiled active context**. Name exact functions/files. Are background merges or
fast-forwards **validated independently of pre-commit**? Does compilation read **HEAD, index, or
worktree**, and does it **enforce limits or only filter**? Inspect only directly relevant call
sites and tests; if unresolved, state where the trace stops. C74 stands: precommit rejection is
real, but not every Git update runs precommit. No whole-repo audit, no runtime test, one queue.

*(trace + rating appended below)*

## Exact call sites (4 files, directly relevant only)

**Compilation reads HEAD, not index or worktree.**
`src/backend/local/system-prompt-compilation.ts`: `collectCommittedMemoryFiles` enumerates via
`git ls-tree -r --name-only HEAD` and reads each file via `git show HEAD:<path>`;
`getCommittedMemfsRevision` = `rev-parse HEAD`. So the active compiled context is the **committed
tree** — uncommitted or index-only edits cannot reach it. Good boundary.

**But compilation does not validate; it only selects.** No constraints-validator call appears in
the compile path; size handling lives in `system-prompt-size.ts`, a **heuristic estimator (~4
bytes/token)** feeding "the startup system-prompt warning" — advisory, and byte-based, not the
commit-time character contract.

**Background merge path skips precommit — the c74 gap is real.**
`src/agent/memory-worktree.ts` (reflection merge into main): `merge --ff-only origin/main`, else
`rebase origin/main` (with `rebase --abort` on failure). Per Git's documented hook semantics, a
**fast-forward creates no commit, so pre-commit cannot run**, and **rebase replays commits
without re-running pre-commit**. The file contains **no independent constraints-validator call**
(grep: zero hits for validate/constraint). The hook script itself resolves via
`git rev-parse --git-common-dir`, so worktree commits **do** run pre-commit at creation — the
merge normally adopts already-validated commits.

**Where the trace stops (stated, not resolved):** whether any caller forces `--no-verify` on
worktree commits, and whether remote `origin/main` can ever contain commits from outside this
hook regime (push-side: no server-side hook is evidenced in these files). If either holds,
over-budget content can enter HEAD via ff-merge and be compiled **without ever meeting a
validator**.

## Requirement 2 — cell refinement

**Confirmed:** HEAD-only compilation (worktree/index edits can't reach active context);
commit-time rejection on the ordinary and worktree-commit paths (c74).
**New, negative:** **merge/fast-forward/rebase are not validated independently of precommit**,
and compilation enforces nothing — selection plus an advisory byte estimate. So "all writers
covered" fails exactly at the reflection merge.
**Proposed cell:** *enforced budget rejection on direct commit paths (ordinary + reflection
worktree): yes; validation at merge/fast-forward or at compile: no; recipient-host load cap: no
(estimator is advisory, bytes ≠ host tokens).* Requirement 2 stays **partial** for Brian's
failure mode; the missing boundary is now named twice: **merge-time validation (or a
compile-time check) and a recipient-side load limit.**

**Confidence: high on HEAD-reads and merge-path absence of validation (direct source), high on
Git hook semantics (documented), medium on remote-push exposure (no server-side evidence either
way — stated as open).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, CAPABILITY-MATRIX.md,
RECOMMENDED-DESIGN.md, panel-response-c74.md.