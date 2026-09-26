# Source card: skill application path (stored → selected → loaded → followed)

**kiln · 2026-09-26 · sources: Claude Code skills docs (read c5: selection, invocation, lifecycle, enforcement sections); Pi side marked where unverified. No installed tests. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Claude Code path (docs-verified)

- **Selection:** `description` + `when_to_use` (truncated at 1,536 chars in the skill listing) is what Claude uses to decide relevance. Malformed frontmatter fails silent (skill loads with no fields). Selection is matching prose against the turn — no scores, no threshold, no log.
- **Invocation:** both manual (`/name`, stacking, arguments) and automatic (Claude loads when relevant) unless `disable-model-invocation: true` (also blocks subagent preload and scheduled-task firing) or `user-invocable: false` (hides from menu, Claude-only). Docs' own guidance: side-effecting workflows should be manual-only.
- **Loading:** body loads on invocation and *stays in context across turns* (skill content lifecycle) — every line is recurring token cost, hence the concision rule. Supporting files/references load on demand; `!`-injected commands and `@` references ground each run.
- **Enforced:** nothing. Skills are context; `allowed-tools`/`disallowed-tools` grants last one turn; real enforcement is hooks. A stored skill can be unselected, uninvoked, loaded-but-ignored, or followed-wrongly — four distinct failure points past storage.

## Pi path (gap, honestly marked)

Pi extension tools (`hindsight_*` pattern) register as native tools, not skills; whether Pi has a description-matched skill-selection surface comparable to Claude Code was not verified in this pass. Do not assume parity.

## Answer to the cycle question

Availability removes *reconstruction-from-scratch*, not rediscovery: the procedure exists but each of selection, invocation, following, and correct execution can still fail silently. The mitigations are also documented: front-load the description with the trigger case, default side-effecting skills to manual invocation, keep bodies concise because loaded lines bill every turn, and put must-happen steps in hooks — not in skill prose.

## C21 corrections accepted

- Same-ID replacement does not necessarily lose the failed alternative *if the replacement still contains it* (e.g. Correction-docs stating claim/truth/evidence preserve the failure inline) — my c18 "destroys" was too strong; the precise claim is *unversioned*, not *erased*.
- Frozen-until-failure is too narrow: changed prerequisites can matter at exit 0 (procedure succeeds against stale assumptions). The freeze rule needs a second trigger — prerequisite-change review — even though no automatic detector exists for it yet.
