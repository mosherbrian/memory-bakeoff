# Design option B: Perseus + native Claude Code/Pi + one reflector

**Sponsor input, 26 September 2026.** Sketched by Brian and Claude in conversation. This is a candidate for the panel to challenge, not a decision. Claude is not independent here: Claude wrote the sketch, and several ratings in it are Claude's own reading, not verified. Tern and the panel may reject it, change it or replace it.

## Idea

Keep Claude Code, Pi and Codex as the runtimes. Durable memory has one writer: a separate reflector that runs at night. The working agents read memory; they cannot write to it. Software enforces what it can check. Anything too large fails loudly; nothing is cut off silently. Nothing is deleted.

## Components

| Component | Job | Build or borrow |
|---|---|---|
| `agent-memory` git repo | Source of truth for what every session must get: `prefs/` (one file each: Brian's quote, date, scope, `replaces:`), `skills/`, `rules/`, `context.md` | Borrow (git + layout) |
| Pre-commit validator | Required fields, size limits, read-only files (pattern from Letta MemFS) | Build, small |
| Perseus Context Engine (`perseus-ctx` 1.0.26, pinned) | Renders one source into `CLAUDE.md` / `AGENTS.md`; `@budget strict` fails an over-budget render; `@profile` sets a budget per model | Borrow |
| Native skills (Claude Code and Pi) | Procedures that load when the task matches the description; one directory, symlinked | Borrow |
| cc-safety-net + Claude Code managed settings | Enforce checkable rules; stop working agents from writing to `agent-memory` | Borrow |
| Perseus Vault (our v2.23.2 Linux build, MIT) | Decision memory: scoped, provenance-stamped, declared `supersede` with reason, old record kept, searchable by every seat over one MCP server. Agent-confirm tier ON, so drafts cannot expire. The known defect (valid time lost at approval) stays unless we patch our own build | Borrow |
| Perseus Ledger (`perseus-ledger` 1.2.4) | Hash-chained record of what the automated steps did: Laya flags, judge verdicts, supersedes, reverts, model version, cost. It is the label history for retraining. Git already covers the repo, so repo commits are not logged again | Borrow, phase 2 |
| Transcripts, pi-lcm | Recoverable history | Already running |
| Reflector (nightly, headless) | Reads all of Brian's messages (about 150 a day, which is cheap to read in full). Finds corrections and repeated explanations. Fixes each in software first (a rule), otherwise writes a skill or a preference. Commits; rebuilds the instruction files; posts counts to the board | **Build: the one real new part** |
| Supersession cascade | (1) Fine-tuned local Laya screens new-vs-old pairs for high recall and is allowed many false positives; during the day it only soft-flags. (2) An LLM judge decides replaces / narrows / coexists / unrelated. (3) The nightly run writes Vault `supersede` records and `replaces:` links | Build + train, phase 2 |
| Self-improvement loop | Judge verdicts and Brian's reverts become labels; Laya is retrained. Guards: a random sample of unflagged pairs goes to the judge every night; a frozen hand-labelled test set; promote only if recall is not worse; keep the old model for rollback; human labels outweigh model labels | Phase 2 |
| Board | Repeats per week, lessons learned, supersedes, failures | Extend the existing phone page |

**Removed:** claude-mem (no stale-memory mechanism; 327 unretired corrections; wrong findings re-injected, including one on 26 Sep). The reflector reads transcripts directly, so claude-mem's capture adds nothing.

## Rules

- Nothing is deleted: git history, `replaces:` links and Vault lineage keep the old versions.
- No approval queue that can starve: commits go straight in, Brian gets a daily digest, and `git revert` undoes a change. Only rules that block actions may need Brian's approval.
- Brian's corrections outrank any model's.
- A software fix is preferred to a memory note.
- Laya never makes a final decision. Explicit-wording supersession goes to the keyword rule (46/46).

## Coverage (Claude's reading; to be verified)

1 yes (still LLM judgment) · 2 yes for our parts; each host's own prompt and skill list are outside our control · 3 yes, bypasses untested · 4 yes for delivery, not for obedience · 5 partial: skill loading is still the model's choice · 6 yes · 7 mostly, Vault valid-time defect · 8 yes, and it keeps the runtimes, subscriptions, mobile UI and ACP · 9 not yet: the weekly repeat count is the measure · 10 partial: about ten named parts, two or three built by us, three from one vendor.

## Two uses

- **Personal:** Brian's Claude Code and Pi sessions. The outcome is Brian's repeats per week.
- **Fleet memory:** Tern (Codex, `AGENTS.md`), Pi seats and Claude share one source, with a per-model budget. Vault gives shared, scoped decisions without stale prose claims. The Ledger follows the fleet principle "a file an agent can write is not evidence about that agent", and it could replace some existing fleet logs. The reflector learns fleet procedures. Cautions: one Vault MCP server process for all seats; per-seat and per-project scopes against cross-agent poisoning (Corvid's shared-principal concern, MINJA); do not let it become another thing the fleet audits.

## Rollout, each stage small and able to stop

0. Now: fix Claude's MEMORY.md index; the cc-safety-net `python3` pilot (Tern's current recommendation).
1. Repo + validator + Context Engine render + shared skills on one project; then the reflector and the weekly repeat count.
2. Only if stage 1 shows value: Vault with agent-confirm, the Laya cascade, the Ledger, the self-improvement loop.
3. Optional, in parallel: a one-week Letta Code trial as the single-product comparison.

## Open questions for the panel

- Pilot target: the fleet (high volume, mistakes cost agent time) or one of Brian's projects (the outcome that matters), or both?
- Patch the Vault valid-time defect in our own build, or live without valid time?
- Are Claude's upgraded ratings right: Claude Code managed settings for requirement 3, and Context Engine `@budget strict` for requirement 2?
- The Perseus vendor risk: the source is offline and the Context Engine is one 35k-line file. Fallback: a plain template plus a size check.
- Where would this design fail first?
