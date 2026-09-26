# Reading note c74 — Letta budget enforcement: does an over-budget change ever get rejected?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 74.**
Skeleton first; **requirement 2** (structural budget limits). Question: follow current Letta Code
source from memory constraints to actual **validation/commit/merge/compile** call sites — can an
over-budget change **reach active context**? Check ordinary and background writes, configured
limits, bypass/override, observable failure. Distinguish Git precommit validation from harness
loading; **/doctor warning is not rejection**. Bounded source trace (tree + named call-site files),
no whole-repo audit, no model calls/probe/install. Deliverable: proposed exact rating
(yes/no/partial) for Letta requirement 2 + the exact missing boundary if partial. Source map:
systems/letta-memfs-fit.md.

*(trace + rating appended below)*

## The bounded trace (tree + 3 named files, main branch, read only)

**Call path found: constraints → Git pre-commit validator → committed-state compile.**
`src/agent/memory-git-hooks.ts` installs a **bash pre-commit hook** that runs the constraints
validator over staged memory files and **exits non-zero on failure** — the hook script contains
explicit `exit 1` paths ("Memory validation could not read Git contents. **No files were
committed.**"), and its own test (`memory-git-v2-precommit.test.ts`) asserts rejection strings:
*"exceeds 20000 from maxFileCharacters"*, **"Memory validation blocked this commit."** Layout-
aware validation (shared-memory vs root-marker), legacy skill files rejected. The active compiled
context is built from **committed** state, so a rejected commit leaves the prior in-budget
context active: **within the Letta-managed MemFS repo, an over-budget change cannot reach active
context through ordinary or background commits.** This is enforced rejection, not a warning —
observable in commit output; a separate audit module reports violations.

**/doctor stays advisory** (consistent with prior card): flagging without preventing.

## Bypass and boundary inventory (documented mechanics, no adversarial test)

- **Standard Git bypasses apply**: `--no-verify`, editing/removing the hook file, direct
  `.git` manipulation — same-user filesystem access defeats any Git-hook gate. Letta's trust
  model is cooperative actors, not a hostile same-user agent.
- **Units are Letta's own contract**: Unicode character counts (20,000/file, 65,536 core
  defaults), **not the recipient host's token/byte load limit**. Per-pattern overrides can lift
  file limits; skills are excluded from memory-file checks.
- **Consumer load path is out of scope**: validation guards *commits into Letta's repo*; nothing
  here bounds what Claude's index loader truncates on Brian's failing path. Compilation from
  committed state aligns the two **only inside Letta's own runtime**.

## Proposed rating — requirement 2

**Yes — within the component's explicit scope** (Letta-managed repo, configured character/depth/
index limits, cooperative-actor trust model): commit-time rejection is real, observable, and
applies to any writer that commits through the repo, background included. **Partial for Brian's
requirement as he experiences it**, and the exact missing boundary is: **a recipient-side load
limit** — the enforced budget is Letta's character contract at commit, not the consuming host's
context cap, plus the same-user `--no-verify` class of bypass. A matrix cell reading "enforced
budget rejection on its own write path: yes; host-independent truncation prevention: no" is the
honest shape. Installed-version behavior unverified (moving `main` read).

**Confidence: high on the enforcement mechanism (hook source + its rejection tests), high on
/doctor advisory status, medium that background reflection commits traverse the same gate
(inferred from shared repo commit path; not every writer call-site traced — bounded by
commission).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, CAPABILITY-MATRIX.md,
RECOMMENDED-DESIGN.md, panel-response-c73.md.