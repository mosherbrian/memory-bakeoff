# P1 — independent verification

- **Verifier:** corvid (named reader; did not author this output)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Artifact verified:** `packages/P1-inspect/capability-map.md`,
  sha256 `b7279897618c41339e4eca3b6744527b991c7c38d712b62bb5eeb8b1c111eea9`
  (worker kiln, v1)
- **Contract:** `packages/P1-inspect/package.md`,
  sha256 `04afe817017a8f47df07d2758f6f49905f92eff83d4ccf56494cab7054f79004`,
  frozen at commit `33d9a25a5ab610bb92a4bd6f8283202b36c0ab8e` (hash re-derived
  from the committed blob; matches the working tree)
- **Pass bound:** 20 minutes (deadline 2026-09-21T15:18:51Z)

## Verdict

**PASS.**

Both completion-check criteria are met, and the five required output items are
present. The verifier independently re-ran the read-only commands and re-read
the cited source; the verdict does not rest on the worker's own report.

## Completion check 1 — every claim cites a command or a source file

Confirmed. Every substantive claim in the map carries an inline citation; the
verifier re-checked a representative sample against source bytes and live
commands rather than accepting the citations on their face.

| Claim (map location) | Cited as | Verifier result |
|---|---|---|
| `GetProfileDir` joins `<profile-data-root>/profiles/<name>` (§2, l.76) | `config.go:66-92` | Confirmed: `GetProfilesDir` at l.66, `GetProfileDir` through l.92, `filepath.Join(profilesDir, profile)` |
| storage resolution gated at open time (§2, l.123-124) | `config.go:436` | Confirmed: `ResolveProfileForStorage` at l.436 |
| `TmuxSocketName` captured per instance, empty = default server (§2, l.92) | `instance.go:389-401` | Confirmed |
| socket resolves from global settings, not per-profile (§2, l.93) | `instance.go:1099-1102` | Confirmed: `GetTmuxSettings().GetSocketName()` in `NewInstance` |
| `[tools.*]` global, not profile-scoped (§2, l.98-101) | test `..._isolation_test.go:378` | Confirmed: `TestConfigIsolation_ProfileDoesNotSplitTools` at l.378; the quoted phrase is its failure message at l.413 |
| hooks shared per config-dir (§2, l.104-106) | `claude_hooks.go:50` | Confirmed: comment "hooks are per config-dir, shared by conductor + workers" |
| heartbeat units named per conductor (§2, l.108-110) | `conductor.go:2132-2137` | Confirmed: `SystemdHeartbeatServiceName`/`TimerName` |
| conductor metadata per profile (§2, l.83) | `conductor.go` | Confirmed: `ConductorProfileDir` l.566, `ListConductorsForProfile` l.752 |
| session record fields incl. `profile:""` (§1, l.40-44) | `session show kiln --json` | Confirmed live |
| fleet line "4 sessions — 1 alive, 0 down, 3 not running" (§1, l.57) | `fleet status` | Confirmed live |
| tmux sessions from all profiles share a server (§2, l.89-90) | `tmux ls` | Confirmed live |
| stop/archive/remove/restart/send/output/children subcommands (§1, l.28-29,64-65) | `session --help` | Confirmed |
| `launch` = add + session start + session send (§1, l.20-22) | `launch --help` | Confirmed |
| v1.16.5 `KillMode=none`, old units not migrated (§1, l.66-72) | `update --check` #2233/#2219 | Confirmed in re-fetched release notes |
| v1.16.8 identity file + `session current --json` + auto_install/auto_restart (§1, l.45-50; §3, l.132) | `update --check` #2243 | Confirmed |
| v1.16.10 spawn verification, `spawn_died_fast`/`tmux_session_missing`/`spawn_unverified`, 2s probe, #2265/#2099 (§1, l.30-36; §3, l.133) | `update --check` | Confirmed verbatim |
| v1.16.11 restart bookkeeping writes owning profile (#2206); output leaks #2299/#2303; dead-letter; context/metrics (§2, l.82; §3, l.134-137; §4, l.187) | `update --check` | Confirmed |
| v1.16.13–14 Recall opt-in, background index cost; stable store-root rule + `.active-root`, `migrate-paths --force` (§3, l.138-141,155-157) | `update --check` #2314/#2320/#2323 | Confirmed |
| v1.16.6/7/10/16 automatic update machinery, auto_install/auto_restart ON, daily timer, remote sweeps (`$3, l.142-148) | `update --check` | Confirmed |
| no in-session identity file on installed v1.16.4 (§1, l.43-44) | source | Confirmed: `AGENTDECK_IDENTITY_FILE` appears nowhere in `internal/` at v1.16.4 |
| installed build is v1.16.4 with v1.16.16 available; local source is v1.16.4 | `--version`, CHANGELOG | Confirmed (`## [1.16.4] - 2026-09-07`, `## [Unreleased]` above) |

## Completion check 2 — gap list derived from inspection, not runbook belief

Confirmed. `RUNBOOK-20260920.md` §2 contains no gap list; it asserts only that
agent-deck "registers 18 seats", tracks status, wakes seats, and that seat
creation is "slow, not broken", and it is stale on the available version
(v1.16.10 vs the actual v1.16.16). The map's §4 gap list is instead the
complement of boundaries the map itself establishes in §1–§3 and §5: no bounded
attempt/deadline/receipt binding, no trusted cross-boundary attribution, no
scheduling/dispatch policy, no authenticated wake channel, no timeout/BLOCKED
enforcement, incomplete profile isolation, and ungoverned self-update. Each is
traceable to a cited capability or its absence. The map explicitly marks the
runbook cross-check as prior belief only (l.10-11), and uses it once to support,
not to source, the v1.16.10 spawn caveat (l.30-36).

## Required output items — present

1. launch / identity / status / stop with command or source references — §1.
2. what a `-p` profile isolates and does not — §2 (tmux, tools, lanes,
   credentials, hooks, timers, store-root).
3. v1.16.16 delta and upgrade recommendation — §3.
4. explicit gaps — §4 (seven items).
5. trusted actor identity — §5, answered with a concrete binding rule and its
   residual risk.

## Non-blocking observations

- The `[tools.*]` quote (l.100-101) is the assertion message at test line 413,
  not the comment at line 378; the citation points at the test function, which
  is accurate. Not a defect.
- §3 necessarily rests on fetched `update --check` release notes rather than
  the local v1.16.4 source; the verifier re-fetched those notes and confirmed
  every cited version claim. This does not undermine the "read the source"
  requirement for the installed build, which §1–§2 and §5 do satisfy.
- "start-success is untrustworthy on the installed build" (l.35-36) is an
  inference from the v1.16.10 notes; it is correctly attributed as such and is
  consistent with the runbook's seat-creation warning.

## Limits of this pass

Read-only verification. No upgrade was performed. The verifier did not test
v1.16.16 behavior on this host, which is the upgrade recommendation's subject,
not a claim in the map about installed behavior.

## Artefact hashes at verification time

- `capability-map.md` `b7279897618c41339e4eca3b6744527b991c7c38d712b62bb5eeb8b1c111eea9`
- `package.md` `04afe817017a8f47df07d2758f6f49905f92eff83d4ccf56494cab7054f79004`
  (equal to commit `33d9a25` blob)
