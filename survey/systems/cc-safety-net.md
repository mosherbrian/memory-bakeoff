# cc-safety-net — action-guard comparator; first pilot withdrawn

**Current sponsor correction,26 September2026:** not running on Brian's machine; staged for a work pilot. Brian avoided using it because it “seemed to be popping up too often.” This is direct usability evidence against fit, without an interruption-rate measurement. The earlier python3 rule targeted agent execution, while Brian's preference concerns commands written for him to run on Windows. That enforcement-point error withdraws this first-pilot recommendation. Use a [native final-reply pilot](../proposals/final-reply-preference-pilot.md) for output and native permission denies for the initial action scope. Source findings below remain historical mechanism evidence, not installed-use claims.


Tern ·26September2026 · initial primary README/installation reading, moving-main snapshot; no install or execution. Sponsor named this existing mechanism; current details do not establish Brian's installed configuration.

The [author README](https://github.com/kenryu42/cc-safety-net) documents pre-tool checks, additive custom rulebooks, diagnostics and local decision logs. Rulebooks add denials rather than disabling built-in protection. The library exposes `checkCommand`; wrapping it in a custom runner would be additional integration, not free fleet coverage. Invalid/legacy configuration can leave rules inactive. Logs record decisions, not command outputs, so a denial is not a completed violation or a count of Brian's corrections. This mechanism does not provide a memory-index budget check. The [installation documentation](https://ccsafetynet.com/docs/installation) lists Claude Code and Pi integrations; these are documented host paths, untested here.

**Historical choice, superseded above:** strongest concrete first-pilot candidate for a narrow enforceable preference. One scoped rulebook, existing adapters, existing diagnostics; Claude proposed as operational owner, Brian approves the bounded pilot. Test allowed and disallowed examples, bad configuration, covered hosts and stated exclusions. The default rule catalog is not automatically identical to Brian's requested preferences.

Custom-rule schema and installed-version behavior remain next-read questions; the custom-rules page was inaccessible on this pass. No guessed rule syntax, installation commands run, or claim of complete enforcement. **Medium confidence in the mechanism fit; local benefit unmeasured.**

## Kiln addendum: primary custom-rule + integration source (docs read, no install)

- **Schema (v1 + v2):** v1 matches command/subcommand/literal args with reason + intent; v2 uses ordered command paths (literal, first-match-wins; unrecognized options deliberately miss = fail open). Additive-only, user+project scopes, live files, hard caps. Fixtures carry blocked/allowed cases; v2 fixtures are *evaluated* — self-contradicting rulebooks never activate.
- **Interception:** pre-tool-call guard on Claude Code and Pi (both listed integrations; Pi install untested here — documented path, not installed parity). Library `checkCommand` for embedding. Skill for authoring (`/cc-safety-net`, agent-invoked only).
- **Invalid-config behavior:** broken config is *dropped, never enforced* — commands keep running, runtime reports `degraded`; legacy files silently inert until migrated. Fail-open by design: no enforcement plus a status to check, not a safe default. Audit log records decisions, never outputs.
- **Known gaps (same source):** unrecognized-option miss, short-option quirks, Codex write_stdin invisibility, PowerShell concatenation, no egress/process containment. Rulebook from git still needs per-machine hook install.
- Distinguishes rulebook (declarative, additive, fixture-tested) from arbitrary hook scripts (imperative, unvalidated). Action guard only — no index-budget mechanism; delivery arrangement still separate.
