# P10-go-requalification-cutover — admission review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P10-admission-1`, start `13:58Z`, deadline `14:13Z`
- **Brief:** `package.md` sha256
  `9a8b6b665d623397f2d00345b7687aa7f029f2d378a1f641f67337b648e6b00e`; director
  release `db40e97`; `inputs.json`; `resume-receipt.json` (rest ended, watchdog
  rearmed/verified).
- **Scope:** read-only admission + pinned checklist. No implementation/live/cutover.

## Verdict

**ACCEPTED (bounded).** Pins and input hashes resolve; the rest is explicitly
ended with `campaign4-watch.timer` rearmed and verified; the fixed implementation
scope (three liveness fixes) is buildable on the isolated branch without moving
main/installed; and the retirement inventory is concrete and campaign4-scoped. The
415/420 allocation is consistent. Two bounded items are pinned (shared-timer
overlap check; `coax-dry` is already agent-loop-based, not legacy-only). Author
release follows this unchanged ACCEPTED admission + pinned checklist.

## Pin resolution / rest

- Source `agent-loop` commit `c124d82cd26ae4966f3e6a935cb24d971347ec8c`; installed
  `/home/bmosher/.local/bin/agent-loop` sha256 `221bb3aa…` verified. Contract
  `db40e97` resolves.
- All `inputs.json` `memory_bake_off_paths` recomputed equal from root:
  `SPONSOR-REQUALIFICATION d111be15…`, P8 `qualification-final f6009bbc…`,
  `liveness-blockers-addendum 32963c79…`, P9 `acceptance 6faa8aa3…`
  (`ACCEPTED_SUPERVISED_PREVIEW`, source `c124d82`), `ACCEPTED-ARCHITECTURE
  cf390ce0…`, `RECOVERY-ACCEPTANCE-RULING 20bcfa45…`, `RETIREMENT-RULING
  52f26a6a…`.
- `prior-rest.json` LEGITIMATE_REST, no in-flight; `resume-receipt.json` shows
  `campaign4-watch.timer` armed and `is-active` = active (verified). Historical
  verdicts preserved.

## Three P8 blockers to reproduce (base) and correct (same case)

1. **Damaged/unreadable incident state** must not abort silently: owned `UNKNOWN`
   alarm through an independent viable route; preserve original bytes (or explicit
   inability-to-read evidence), incident identity/ack/deadline continuity and
   notification dedup; no silent empty-state reset; quarantine must not overwrite
   the only copy. Malformed/unreadable/truncated/partial state and repeated
   checker/reopen exercised.
2. **Future heartbeat** beyond a small justified tolerance → `UNKNOWN`/alarm;
   clock rollback and exact boundary; negative age never freshness.
3. **Incarnation binding:** completed pass bound to the authoritative current
   process incarnation (systemd `InvocationID` + process identity); prior-run
   pass, PID reuse, missing/unreadable identity and restart-before-first-Tick must
   not certify current health; bounded startup grace never called recovered.

## Retirement inventory (read-only; campaign4 scope, names are not scope)

- **Campaign4 effect sources:** `openwork.timer` (active; `Environment=AGENTDECK_PROFILE=campaign4`,
  `ExecStart=%h/.config/agent-deck/openwork`), `coax-dry.timer`/`.service`
  (active; `agent-loop coax --live --notify …` — already Go-based, not legacy),
  `shadow-watch.timer`/`.service` (active; observe-only replay), `campaign4-watch.timer`
  (active, rearmed; `%h/.config/agent-deck/campaign4-watch`).
- **Keep:** `campaign4-pause` hard-stop actuator (must not fail quietly); wake
  transport and lane wrappers.
- **Outside campaign4 (not retirement scope):** `escalation-watch`, `igw-watchdog`,
  `clawdbot-*`, `fleet-unit-failed@` — verify no campaign4 profile dependence
  before excluding.
- **Bounded items:** (a) confirm whether any of the four campaign4 timers is shared
  with another project and isolate campaign4's caller/config before switch, else
  return the concrete overlap to Tern; (b) `coax-dry` retires the Go coax caller,
  not a legacy script — record it as such (no script deletion).
- Historical failed `campaign4-p8-live1-driver.service` is not a live effect source.

## Pinned checklist (stages)

- **A (this):** checklist pinned before author; P8-failure reproduction + expected
  corrected outcomes + fault-injection/true-evidence sources per live case;
  unit/command feasibility read-only; retirement inventory above. No watcher/pause
  execution, no tasks.
- **B (author60/corvid30):** reproduce pre-fix failures; positive/negative
  incident/clock/incarnation; retained core/host/loop/expose + 125 conformance +
  adjudicated parity; corvid unshared malformed-state/incarnation mutations; actual
  CLI + systemd unit semantics (not imported functions); no hidden heartbeat
  goroutine, no false recovered from ack/send, bounded external calls,
  notification-failure handling, persisted response deadlines; immutable candidate
  source/binary/manifest + executable live and rollback plans.
- **C (prep15/binding10/live60/review20):** fresh isolated fixtures
  (worker/verifier/duty/director), no main-seat faults; positive handoff with
  terminal disposition and no duplicate on restart; kill-run auto-restart without
  blind resend; hang → real watchdog restart + outside detection without in-loop
  helper; restart-loop owned escalation with real ack binding owner/next/deadline;
  intentional stop rc64 and stray start cannot undo marker; healthy rest and
  deliberate stop quiet ≥3 min and ≥3 outside-check cycles; real granted step
  timeout interrupts once and deadline enforces while stopped; corrupt
  incident/future/prior-incarnation owned/UNKNOWN in the actual checker. Trusted
  host/journal timestamps + monotonic intervals; recovery ruling detect30/
  suspicion180/recovery-or-ack-escalation60 (total90/240); no `ACP` source-time
  overlay; failures/censored cases stored.
- **D (cutover45/postcutover10):** only on corvid live PASS + Tern qualification
  acceptance + exact cutover signature; capture pre-switch hashes/unit/registry/
  ledger and restoration commands; drain in-flight; NEW production ledger/config
  with validated role bindings; stop/disable the four campaign4 old effect sources
  and Cairn's manual dispatch/deadline role; verify no old effect source remains;
  enable candidate run + independent health timer; no dual owners; keep
  wake/lanes/pause; first real package `P10-production-handoff-1` (kiln writes the
  operator handoff; corvid checks it read-only; authoritative dispatch/handoff/
  claim/decision must run via agent-loop); rollback archives/reconciles in-flight
  identities, disables candidate effects, restores previous binary/config and
  re-enables exact old timers + Cairn ownership, verifying one effect owner.

## Bounds

415/420 minutes explicit: admission15 + author60 + candidate-review30 + sole
repair30 + recheck20 + prep15 + binding10 + live60 + live-review20 + cutover45 +
postcutover10; remaining 5 unallocated. Every stage host-read start/absolute
deadline + one-shot duty; no automatic extension/P10-r2; cutover grants cannot be
spent before qualification; unfinished required gate → NOT READY/CUTOVER_FAILED
with rollback/owned-rest. Candidate PASS is not live PASS or cutover release.

## Effect

Admission **ACCEPTED (bounded)** with the pinned three-fix reproduction, retirement
inventory and stage checklist; two bounded items named. No implementation/live/
cutover conferred. Returned to Tern for the notify-claude author release.
