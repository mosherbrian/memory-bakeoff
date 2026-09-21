# P1 — agent-deck capability map

- **Worker:** kiln, 2026-09-21. Installed binary `agent-deck` v1.16.4
  (`Agent Deck v1.16.4 (update available: v1.16.16)`); source read at
  `~/src/agent-deck` (CHANGELOG top entry `## [1.16.4] - 2026-09-07`,
  `## [Unreleased]` above it — local checkout predates everything under review).
- **Method:** source (`internal/session/`, `internal/tmux/`, CHANGELOG.md),
  read-only CLI probes under `AGENTDECK_PROFILE=campaign4`
  (`list`, `status`, `session show [--json]`, `fleet status`, `update --check`,
  `--help` texts), and `~/memory-bake-off/RUNBOOK-20260920.md` §2 (used only
  as prior belief to check against, per the completion check).
- **Constraint honored:** no upgrade performed. `agent-deck update` was invoked
  only as `update --check` (read-only release-notes fetch). Nothing written
  outside this directory.

## 1. Launch / identity / status / stop — what agent-deck covers natively

### Launch — covered

- `agent-deck add <path>` (create row) + `agent-deck session start <id>`
  (spawn tmux pane), or the one-step `agent-deck launch [path]`
  (`add + session start + session send` combined — `launch --help`).
  Verified in help text; the four campaign4 seats (tern, corvid, kiln, cairn)
  exist in `AGENTDECK_PROFILE=campaign4 agent-deck list` output.
- Each seat is a named tmux session (`agentdeck_<title>_<hash>`, e.g.
  `agentdeck_kiln_b97e27f7` from `session show kiln --json`); all seats
  visible in plain `tmux ls`, confirming tmux-backed supervision.
- `session restart`, `session send <id> <message>`, `session output <id>`
  round out the launch→drive loop (`session --help`).
- Caveat (supports runbook §2, does not contradict it): v1.16.10 fixed
  `session start` reporting success for a pane that is not there — it now
  probes `has-session` on the session's own socket up to a 2s deadline and
  reports `spawn_died_fast` / `tmux_session_missing` / `spawn_unverified`
  (`update --check` notes for v1.16.10, citing #2265/#2099). Installed v1.16.4
  predates this: **start-success is untrustworthy on the installed build**,
  consistent with the runbook's "seat creation is slow, not broken" warning.

### Identity — partially covered, version-dependent (see §3)

- Installed v1.16.4: `session show --json` reports the stored record —
  `id`, `title`, `group`, `tool`, `command`, `account`, `path`,
  `tmux_session`, `status`, `created_at` (observed live on kiln). `accounts`
  lists named account slots. There is **no in-session identity file** on this
  build.
- v1.16.8 added session identity (`update --check` notes, #2243): every
  locally launched/restarted session gets `AGENTDECK_IDENTITY_FILE` pointing
  at a generated file (session id, title, group, profile, account, parent,
  project path), injected into model instructions for claude/pi/codex/gemini
  paths, with `session current --json` as the full record and
  `[launch] inject_identity` / `--no-identity` opt-outs.
- Load-bearing answer (§5) below builds on this.

### Status — covered

- `agent-deck list` / `status` (observed: `1 waiting • 0 running • 3 idle`),
  `session show [id] [--json]`, `session children`, `fleet status`
  ("4 sessions — 1 alive, 0 down, 3 not running" / "Nothing to recover"),
  `fleet recover`, plus TUI lights. The v1.16.11 notes show heavy continued
  investment in status correctness (hook-lag detection, substate/substate_detail,
  viewers), i.e. status is a maintained core competency, not a gap.

### Stop — covered

- `agent-deck session stop <id>` (stop/kill session process), `session remove`,
  `session archive/unarchive`, `session cleanup` (`session --help`).
- v1.16.5 caveat (`update --check` notes, #2233/#2219): units agent-deck
  creates **from v1.16.5 on** get `KillMode=none` so teardown cannot kill the
  shared tmux server; **units created by earlier versions are not migrated** —
  stopping one from outside agent-deck (`systemctl --user stop`) can still
  kill the shared server. Our seats predate v1.16.5 semantics (created under
  v1.16.4 behavior), so stop-from-outside remains hazardous until sessions are
  recreated under a newer build.

## 2. What `-p` / `AGENTDECK_PROFILE=campaign4` isolates — and does not

Confirmed by source (`internal/session/config.go:66-92` — `GetProfileDir`
joins `<profile-data-root>/profiles/<name>`) and by live state
(`~/.local/share/agent-deck/profiles/{campaign4,claude,default}/`, each with
its own `state.db`; `profile list` shows the three profiles):

**Isolated per profile (separate `state.db`):** session rows, groups, restart
bookkeeping (v1.16.11 fixed restart writing to the owning profile's DB, #2206),
conductor metadata (`ConductorProfileDir`, `ListConductorsForProfile` in
`internal/session/conductor.go`), per-profile notify behavior. The campaign4
`list` shows only its 4 seats, confirming row isolation.

**NOT isolated by a profile:**

- **tmux namespace.** All seats share the default tmux server: plain `tmux ls`
  shows `agentdeck_*` sessions from every profile side by side. Per-session
  socket names exist in the record (`TmuxSocketName`, `internal/session/
  instance.go:389-401`) but resolve via global tmux settings
  (`GetTmuxSettings().GetSocketName()`, `instance.go:1099-1102`), not
  per-profile; kiln's own record carries no socket override (default server).
  A profile does not protect a seat from a shared-server outage, and the
  v1.16.5 KillMode finding (§1, Stop) is therefore fleet-wide.
- **Config and tools.** `[tools.*]` lives in the single user config.toml, not
  per-profile — pinned by test
  `TestConfigIsolation_ProfileDoesNotSplitTools`
  (`internal/session/generic_session_config_isolation_test.go:378`): "tools
  must be global, not profile-scoped". Our `~/.config/agent-deck/config.toml`
  is correspondingly near-empty (one conductor lane + `[costs]`).
- **Lanes / credentials / hooks.** The `acp-*` lane scripts, `~/.claude`-style
  credential dirs, and hook installs live outside any profile dir; source
  comment at `internal/session/claude_hooks.go:50` notes hooks are "per
  config-dir, shared by conductor + workers". Named account slots
  (`[profiles.<name>.claude].config_dir`) cut across profiles by design.
- **Timers / daemons.** Conductor heartbeat units are per-name user units
  (`agent-deck-conductor-heartbeat-<name>.service/.timer`,
  `conductor.go:2132-2137`) on the shared user manager, and the update timer
  (`agent-deck update --install-timer`) is per-host, not per-profile. A
  profile gives no timer isolation.
- **Store-root selection (v1.16.14 behavior change).** Profile data-root
  choice is a global rule with a `profiles/.active-root` marker, not a
  per-profile setting; the v1.16.14 notes describe two 2026-09-19/20 incidents
  where the fleet "looked wiped" from the CLI while the TUI ran on the legacy
  store (#2323). Relevant to upgrade (§3): behavior of *all* profiles shifts
  under the new rule.

**One observation, not a defect:** kiln's `session show --json` reports
`"profile": ""` (empty). Profile scoping here comes from the caller's
`AGENTDECK_PROFILE` / `-p` selecting which `state.db` to open, not from a
profile tag on the row — consistent with `ResolveProfileForStorage`
(`config.go:436`) gating storage resolution at open time.

## 3. v1.16.4 → v1.16.16: what changes, and the recommendation

Full delta read via `agent-deck update --check` (v1.16.5…v1.16.16 notes).
Items touching this package's four questions plus profile isolation:

- v1.16.5: per-session `KillMode=none` for new units (stop safety, §1).
- v1.16.8: `AGENTDECK_IDENTITY_FILE` + `session current --json` (identity, §5).
- v1.16.10: `session start`/`restart` spawn verification (launch trust, §1).
- v1.16.11: `session send` socket transport, viewers, `session context`,
  `session metrics`, pi event-driven status, `session output` truncation/hygiene
  fixes (status/drive surface; the output-leak fixes #2299/#2303 matter to any
  receipt design that reads transcripts).
- v1.16.13–14: Recall (opt-in local conversation index, `[recall] enabled =
  false` default) — new capability with no counterpart on v1.16.4; background
  indexing cost is the thing to watch.
- v1.16.14: explicit stable store-root rule + `.active-root` marker (#2323).
- v1.16.6/7/10/16: automatic update machinery (`auto_install` default ON,
  `auto_restart` default ON, daily install timer, unattended remote sweeps).
  **This is the risk:** upgrading opts the host into self-modifying behavior —
  a newer binary can arrive and the TUI can re-exec in place at the next idle
  opportunity. For a measurement campaign that must pin exact versions
  (per the repo's own evaluation rules: "record exact package/commit… for
  every external result"), an unpinned supervisor is a confound source.

**Recommendation: upgrade to v1.16.16, but only with pins set first.**
The identity (§5), spawn-verification, and stop-safety fixes are load-bearing
for the controller and unavailable on v1.16.4; staying put keeps
untrustworthy start-success and no trustworthy actor identity. Before
upgrading: set `[updates] auto_install = false`, `auto_restart = false`
(or document deliberate opt-in), run `migrate-paths --force` once to plant
the `.active-root` marker so the v1.16.14 store rule cannot flip the active
root mid-campaign, keep Recall disabled, and recreate long-lived seats so
their systemd units carry `KillMode=none`. Re-verify `list`/`status` row
counts against both store roots immediately after the upgrade (the #2323
"fleet looked wiped" signature).

## 4. Explicit gaps — what the controller must supply

Derived from the above inspection (nothing here is taken from runbook belief;
each gap is the complement of a confirmed agent-deck boundary):

1. **Attempt/deadline/receipt binding.** agent-deck has wake/send/output
   primitives and (≥v1.16.8) an identity file, but no notion of a bounded
   attempt, a deadline, or a content-hashed receipt tying an output to the
   seat that produced it. The dispatch protocol (sha256 binding by cairn) is
   controller procedure, not a product feature.
2. **Trusted attribution path.** `session show --json` is trustworthy
   *to the controller host* (reads local state.db), but anything crossing a
   seat boundary (chat text, files) is agent-writable, including the identity
   file's contents as seen from inside the pane. The controller must define
   which side of that boundary each claim is read from (§5).
3. **Scheduling / dispatch policy.** No poller, queue, role separation, or
   verifier assignment exists in agent-deck (`agents`/`agent adopt` is a
   registry of adopted definitions, not a workforce: observed "No agents
   adopted yet"). Tern's stages, seats, and reader assignments are all
   controller scope.
4. **Cross-seat messaging with provenance.** `session send` delivers bytes to
   a pane; there is no authenticated wake channel (the `wake` used by this
   campaign is a local `~/.config/agent-deck/` Python script, outside
   profiles and outside agent-deck's own command surface — it appears in no
   `--help`). Wake discipline, inbox/ledger, and dead-letter handling
   (`inbox dead-letter`, added v1.16.11) need controller ownership to be
   trustworthy rather than merely present.
5. **Timeout / overdue enforcement.** No wall-clock attempt bound, no BLOCKED
   disposition, no event-driven deadline timers — the P1 package itself had to
   have these grafted on by the admission correction. `idle-timeout` on
   `launch` stops quiet sessions; that is resource hygiene, not deadline
   enforcement with a disposition.
6. **Isolation the campaign might assume but does not get.** Shared tmux
   server, shared lanes/credentials/hooks, shared user-manager timers, global
   tool table (§2). Conductor/worker separation, credential partitioning per
   seat, and any sandboxing beyond tmux are controller work.
7. **Version pinning vs self-update.** Per §3, the supervisor's own update
   agency must be explicitly governed or every later measurement inherits an
   unrecorded independent variable.

## 5. Actor identity: can the controller trust it?

**Yes — but only when read from the controller side, and only fully on
≥v1.16.8.**

- The trustable claims are the ones agent-deck resolves itself and serves
  from its own store: `session show --json` / `session current --json`
  (`id`, title, group, profile, account, `tmux_session`) read out of the
  profile's `state.db`, plus (≥v1.16.8) the generated identity file named by
  `AGENTDECK_IDENTITY_FILE`, whose *path* is agent-deck's assertion even
  though its *bytes* pass through agent-visible space.
- What is NOT trustable: anything the agent says about itself in-band (pane
  text, `session send` payloads, file prose) — the harness owns ground truth
  principle applies inside this campaign too: never score, bind, or attribute
  from self-report.
- Concrete binding rule for the controller: attribute an output to
  (`profile`, `session id`, `tmux_session`) as resolved by the controller's
  own `session show --json` at collection time, cross-checked against the
  sha256 the worker reports out-of-band; treat pane/file content as the
  payload, never as the attribution. The known residual risk is pane-content
  spoofing across seats (one seat's output copied into another's pane reads
  as the latter's) — mitigation is collection-time `session output` by the
  controller, not post-hoc text inspection.
- On the installed v1.16.4 the `session show --json` half of this holds
  today; the identity-file half requires the v1.16.16 upgrade (§3), which is
  part of why the upgrade is recommended.
