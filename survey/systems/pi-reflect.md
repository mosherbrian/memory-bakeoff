# System card: pi-reflect (transcript-driven file reflection for Pi)

**kiln · 2026-09-26 · implementation read (README + extensions/index.ts + extensions/reflect.ts, shallow clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context. jo-inc/pi-reflect, MIT, 48 stars / 11 forks / 45 commits, 137 tests claimed.**

## How edits are generated, applied, versioned

- **Generate:** one LLM run per reflection over transcripts (pi-sessions, filtered to ≥1 user turn and ≥3 exchanges) + file/command/url context sources, all byte-capped and lookback-windowed. The model returns typed edits (strengthen/add/remove/merge) through a tool call; prompts are target-aware (behavioral correctness for AGENTS.md, factual completeness for MEMORY.md, identity convergence for SOUL.md).
- **Apply (`applyEdits`, read in full):** exact-match required; ambiguous matches (2+ occurrences) skipped; insertion requires unique anchor plus not-already-present check; merge requires all sources found. **Gap vs README:** the README claims "rejects suspiciously large deletions" — no size cap exists in the edit path as read. Documented safety is anchor-uniqueness, not blast-radius.
- **Version:** timestamped backup copy, then write, then `git add -A` + `git commit --no-verify` at the target's repo root. Two practitioner flags: `--no-verify` bypasses repo hooks, and `add -A` stages *everything* in that repo, not just the target — a dirty worktree gets swept into the reflect commit.
- **Invoke:** `/reflect` manually, headless via cron/launchd (`pi -p --no-session`), backfill dry-run with pre-run cost estimate and confirm gate.

## What reaches future context, and what does not refresh

Edits land in the target markdown file itself (AGENTS.md/MEMORY.md/SOUL.md), which Pi loads as its behavioral/memory surface — so delivery to future Pi sessions is native, no new retrieval path. Impact metrics (correction-rate trend, rule recidivism ≥2 edits, file-size trend) make convergence observable; recidivism is the honest instrument (a rule strengthened 3+ times is not sticking). **No cross-host refresh exists**: it operates on local files; a second host never sees the edit except by whatever sync already moves the files.

## Cost / fit

Install: `pi install git:...` + LLM key; per-run cost one model call (README: ~$0.05–0.15 Sonnet-scale; Brian's local models change the number, not the shape). Maintenance: target config, lookback tuning, reviewing auto-commits. Fit: Pi-native, fills the exact Pi-side hole (no observed auto-capture); irrelevant to Claude Code directly, though the pattern ports.

## Against the c13 glue list

REMOVES two real items: Pi-side **automatic capture** (transcript → canonical-file edits) and the **canonical-update trigger** (scheduled/manual run + versioned history + recidivism signal). LEAVES: cross-host refresh (still symlinks/manual), prerequisite-change detection (it mines *corrections in transcripts*, not changed prerequisites — silent drift with no user correction stays invisible), and mistaken-correction entrenchment (an LLM-proposed edit is only as good as the reflection prompt; recidivism detects it late).
