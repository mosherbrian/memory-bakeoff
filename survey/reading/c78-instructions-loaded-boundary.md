# Reading note c78 — InstructionsLoaded: does the event expose omissions, or only confirm a subset?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 78.**
Skeleton first; **requirement 2**, one official source: Claude Code **InstructionsLoaded** hook
docs (plus linked payload/reference only if needed). No probe/runtime/model call, no
comprehensive hook audit. Determine what is actually reported: loaded source paths, trigger/scope,
content/hash/size, **skipped/oversized/unreadable sources** — and whether the event can **block**
loading or only observe. Does it mechanically expose the omission class behind Brian's native-index
failure (109/301 unloaded), or just confirm a successfully selected subset? Keep auto-memory
separate from CLAUDE.md/rules; do not infer coverage from the event name. Deliver exact row/cell
delta or explicit no-change, and the smallest useful interpretation. C77 carried: resupplied
canonical instructions ≠ fresh disk reread; no fit guarantees.

*(facts + delta appended below)*

## What the official docs establish (code.claude.com hooks page, read 26 Sep 2026)

**Trigger:** fires when a **CLAUDE.md or .claude/rules/\*.md** file is loaded into context —
session start for eager files, again on lazy loads (nested CLAUDE.md traversal, `paths:`
frontmatter glob match). Does **not** fire when AGENTS.md is read directly via the Project
instructions setting; does fire when CLAUDE.md imports or symlinks it. Matcher runs against
`load_reason` only.

**Reported fields:** `file_path` (absolute), `memory_type` (User/Project/Local/Managed),
`load_reason` (**session_start | nested_traversal | path_glob_match | include | compact** — the
last fires when instruction files are **re-loaded after compaction**), plus `globs`,
`trigger_file_path`, `parent_file_path` for the special cases. **No content, no hash, no size.**

**Power: observation only, explicitly.** "The hook doesn't support blocking or decision control.
It runs asynchronously for observability purposes"; JSON output fields are **discarded**; the docs
name the intended use as "audit logging, compliance tracking, or observability."

## The commission's question: does it expose the omission?

**Not directly.** Only **successful loads fire** — skipped, oversized, and unreadable sources are
silent by construction. The event confirms the selected subset; Brian's 109/301 class of failure
would appear only as **absence in a diff against an expected set** — and the expected set plus the
diffing are **unbuilt glue**, to be judged under the sponsor's single-design constraint, not
assumed to exist. Auto-memory is out of scope of this event; the separation is kept.

## Exact cell delta

**New narrow row candidate — "Claude InstructionsLoaded event": requirement 2 = partial
(observability-only): mechanism yes (path/scope/reason incl. post-compaction reload), omission
exposure no (diff against expected set required, unbuilt), blocking no (documented).** No change
to any broad Claude row; the event does not repair the index failure and must not be credited as
a load bound. Side credit: `load_reason: "compact"` is documented, machine-visible evidence of
instruction **resupply after compaction** on this host — requirement-4 observability, scoped to
CLAUDE.md/rules, not a fresh-content or application claim.

**Smallest useful interpretation:** during the guard pilot's verification window, log the event to
a plain append-only ledger and check that the **declared** instruction files fire at
`session_start` and again at `compact`. That is one existing mechanism, one output file, no
monitoring pipeline, and it turns "was it loaded?" from argument into a diffable record — while
the omission guarantee itself stays explicitly unbuilt.

**Confidence: high on all documented facts (verbatim page), high that omissions are silent by
construction (successful-load-only + no decision control), medium that the ledger-diff is the
cheapest sufficient observability for the pilot (design judgment, not evidence).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, CAPABILITY-MATRIX.md,
RECOMMENDED-DESIGN.md, panel-response-c77.md.