# Reading note c81 — pi-reflect: what admits a generated edit, and does the active context ever see it

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 81.**
Skeleton first; **matrix 2/3/4**; existing card + bounded primary trace of the admission path
only (`extensions/reflect.ts`, HEAD `33a72886c8d5`, 21 Jul 2026; no run, no model call, no
install). File-scope with Kiln: this note owns **admission-to-active-context**; trigger/filter
interface and operational versioning are theirs.

*(trace + verdict appended below)*

## Admission checks, verified at HEAD

`applyEdits` admits a proposed edit only on **content-integrity** grounds: exact match required;
ambiguous matches (multiple occurrences) skipped; replacement text checked for duplication;
insertion needs a unique anchor plus a not-already-present check; removal needs an exact match.
Every skip is recorded with a reason. Before writing, a timestamped backup is taken.

**What does NOT run:** no size or blast-radius cap in the edit path — the README's "rejects
suspiciously large deletions" is **confirmed absent at HEAD** (card gap holds); no protected-file
logic in the admission path (targets are config-named files; protection is whatever the repo
already is); and the commit **bypasses validation by construction** — `git add -A` then
`commit --no-verify` at the target repo root, re-confirmed at HEAD.

## Reload into active context: no

No reload/refresh code exists in the extension. Edits land in the canonical file; **the next Pi
session** loads them natively (Pi's start-up load boundary, c77). The active session never sees
its own reflection — consistent with Pi's boundary, not a new defect, but it means reflection
feedback loops are session-granular at best.

## The boundary that changes option-B fit

**pi-reflect is an in-house hook-bypasser.** Its generated edits are admitted by match-uniqueness
alone, then committed with validation disabled and the whole worktree staged. If Brian later adds
commit-level gates — the exact mechanism Letta uses for budget rejection (c74) — **pi-reflect's
own commits sail through them**, and a dirty worktree gets swept into the reflect commit. Option B
therefore needs its write path decided **before** any commit-gate is trusted: either accept
reflector commits as privileged, or the reflector's admission must inherit the gate.

## Cell deltas (mechanism-level)

- **Pi capture:** pi-reflect supplies a real transcript→canonical-file reflector (mechanism yes;
stickiness measured by its recidivism metric, outcome unproven).
- **Requirement 3:** generated-edit commits bypass validation (`--no-verify`) and stage unrelated
work (`add -A`) — documented bypass of any future commit-level protection.
- **Requirement 2:** no size cap on generated edits (README mismatch confirmed); `fileSize`
metrics are observational only.
- **Requirement 4:** next-session delivery native; **no active-session refresh**.

**Confidence: high on all HEAD facts (direct read of applyEdits/commit path), high on
no-active-refresh (no such code in the extension), medium that the hook-bypass boundary is the
option-B-critical one (design judgment; depends on whether commit gates are ever adopted).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, CAPABILITY-MATRIX.md,
RECOMMENDED-DESIGN.md, panel-response-c80.md, systems/pi-reflect.md.