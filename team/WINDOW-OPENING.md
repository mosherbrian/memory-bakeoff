# WINDOW-OPENING — campaign-1 window receipts

Append-only receipt log for window-opening actions. Each section: who, what,
before/after stored-state scans. Receipts claim; state is.

## T0 flip (Cairn)

**What:** `perseusRecall.write.allowAgentConfirmed` `false → true` on the
worker-pi lane — the T0 (agent-confirmed, low-stakes) switch. Config-only;
frozen extension lineage (060d842) untouched.

**Provenance (honest):** Kiln's formal config-diff artifact had NOT yet
landed in `team/` at apply time (checked: latest team/ files were the TEAM-1
round; no T0/config-diff artifact anywhere under memory-bake-off/). I applied
the flip anyway because it is **uniquely determined**, not a guess: verified
against the frozen extension source that T0's entire config surface is this
one boolean — `gate.ts:109` requires `allowAgentConfirmed === true` AND
caller-passed `confirmed_by:"agent"`; `index.ts:145-149` parses exactly that
key; no other config enables T0. Authorization: Brian approved T0 (campaign
GO) and my RETRO-1 START. When Kiln's artifact lands it should match
byte-for-byte; I will reconcile and note it here.

**Before scan** (taken pre-flip; re-verified intact after an operator probe
cancelled the first attempt ~10:05):
- `settings.json:11` → `"allowAgentConfirmed": false,`
- sha256 `174756b1a836ea17ad118c39671e59133bad9fbbdbad44e7b0d3f31f3a31fbe9`
- mtime 2026-09-11 13:53:12 -0700

**After scan** (stored state, not the write receipt):
- `settings.json:11` → `"allowAgentConfirmed": true,`
- sha256 `b4fdbef20b2f9427695fa44429a2325765094d002b8bb08ffbb5b3183fa5aae3`
- mtime 2026-09-12 10:18:37 -0700
- JSON parses; `perseusRecall.write.allowAgentConfirmed == True`

**Effective-when (stated, not assumed):** the extension reads config once at
registration (`index.ts:253 loadConfig()`, session start) — the flip is live
from the **next** worker-pi session, not the one that wrote it. The first T0
self-capture (`remember` draft → `confirm` with `confirmed_by:"agent"`) is
therefore the end-to-end proof and will run on the next turn; a T0 confirm
attempted in the writing session would still be rejected by the in-memory
config and would be a false negative, so it was not attempted.

**S6 note:** no vault writes occurred in this action; no records touched;
nothing to demote. Scan-after-write applies to the first T0 capture.

---

# PRE-WINDOW CHECKLIST — Kiln's execution receipts (items 0–5, 2026-09-12 ~10:30 PDT)

Executed per GiLMore's ops dispatch, in checklist order. Raw receipts:
`implementer/repo/scripts/experiment_20260911_trial/window/` (+ the S6 command
and T0 artifact in `scripts/experiment_20260911_trial/`). All descriptive.

## (0) End-to-end delivery smoke through the real path — PASS

- **Seed:** `record-window-canary-20260912` via operator CLI write into the
  LIVE trial vault (unique key; Cairn's three records untouched). Receipt:
  `window/item0-canary-seed.json` (`ok:true, created`, id `cli-afd86629ad93`).
- **Real path:** `/home/bmosher/.config/agent-deck/pi-local -p`, real cwd
  `/var/home/bmosher/acp-pi`, real trial config, real model
  `night/qwen3.8-27b-code`. Registration line confirmed live vault +
  `allowAgentConfirmed=false` (pre-T0-flip run).
- **DELIVERED-LEVEL ASSERTION — MET.** Model-visible toolResult (session
  `…17-17-25-859Z_01a0969f….jsonl`, toolCallId `SFOnSpL2FLhzM1HDfmgC0v9OM6698rGS`)
  contains the seeded record in full: `key=record-window-canary-20260912 …
  status=active` + complete assertion text. Final answer listed all four
  records with correct statuses. Frozen: `window/item0-delivered-toolResult.txt`,
  `window/item0-smoke-stdout.txt`.
- **Honest notes:** (a) two earlier attempts failed — Kiln's bug: ran `pi`
  directly without `--model`, so pi fell back to a default model whose
  upstream exits on start (502s), and llama-swap swapped models between
  probes and pi (also the 1m49s "trivial reply"). Fixed by going through
  `pi-local`, the actual worker launch path. (b) Turn completed ~60s wall;
  the pi process hung on exit post-completion and was killed by the 600s
  timeout — exit-hang quirk, does not affect delivered state.

## (1) Provenance hashes — recorded

- Binary sha256 `c8a222ec7077d713212c2414d440586f564338aaa153eeb13b08ebf14854a172`
  — matches pinned study provenance.
- Extension lineage: all 7 code files byte-identical to 060d842 (per-file
  sha256). One documented delta: `README.md` test-count fix (e25d618,
  doc-only, no runtime effect). Current extension tree hash
  `2c2670ee2a83dfbb22b3743a6de2019fc4b1004b901853359c9aae2cfd96f551`;
  repo HEAD `7987a55`, clean.
- Live-lane identity is path-identity: worker `packages` + `bin` point at the
  hashed repo paths; no copies exist to drift.

## (2) S5 pairing rule — DRAFT for Verity's check (not frozen until she okays)

- Population: all completed worker-pi turns in the window (session files).
  Turn = one operator prompt → final assistant message; completed = reached a
  final assistant message (stalled/interrupted excluded, counted separately).
- Classes: MEMORY turn = ≥1 perseus-tool call; NO-MEMORY turn = zero perseus
  calls and no recall-nudge injection that turn.
- Pairing: same task family (conductor task id, else same calendar day on the
  same objective) → both completed → nearest-in-time across classes → each
  turn pairs at most once. Unpaired turns counted and reported.
- Metric: tokens primary, wall secondary; per-pair + medians, both shown.
  Flag when the memory turn is +25% over OR 25% under the paired turn
  (symmetric); flagged pairs are read and attributed before reporting.
- n pairs stated beside every S5 number. Descriptive only.

## (3) Notify config + delivered:false visibility — recorded

- `notifiers: ["in-session", "file"]`; `notifyFile:
  /home/bmosher/acp-pi/notifications.jsonl`. No Signal channel in the worker
  (conductor-side per runbook §2).
- Notify file live, 3 pending-confirmation lines observed (1 confirmed →
  `record-736612fc`; 2 expired identity drafts — live instances of the
  TTL-expiry scoreboard sub-count; the second identity draft was correctly
  re-drafted, not abandoned).
- `delivered:false` visibility: every draft's toolResult carries the
  `notifier: <channel>:<delivered>` line, which lands in the session log the
  ledger reads. Window ledger copies the notifier line verbatim per draft.

## (4) S6 scan-after-write — wired + receipted

- Command: `scripts/experiment_20260911_trial/s6_scan_after_write.sh` (one
  command; output appends to the trial ledger). Authoritative state = entities
  table columns via direct sqlite read; MCP scan = recall-visibility check.
  Violations: status ∉ {active, deprecated}; source ≠ cli-write; ACTIVE row
  invisible to scan. Deprecated rows are expected-absent from scan (product
  behavior, measured in PROBE-20260912).
- First receipt: 4 rows, all active via cli-write, 0 violations
  (`window/item4-s6-first-run.txt`).
- First-run lesson preserved: v1 of the instrument false-fired on all rows —
  the MCP scan projection flattens the body's provenance `source` block over
  the row's write-path `source` column. Fixed: sqlite columns are the
  authority; scan is visibility only. (An instrument that cries wolf on its
  first pull is worse than no instrument.)

## (5) T0 config diff — artifact landed; reconciled with CAIRN's apply

- Artifact: `scripts/experiment_20260911_trial/t0-config-apply.md` — one-key
  diff (`allowAgentConfirmed: false → true`), exact apply + verify commands,
  rollback, 7a framing. Config-only; frozen code untouched.
- **CAIRN applied it at 10:18:37 -0700** (before the artifact landed; his
  WINDOW-OPENING entry above states the ordering honestly and verified
  uniqueness against the frozen source before flipping). Kiln reconciled:
  applied state matches the artifact's diff exactly (verified live:
  `{enabled:true, allowAgentConfirmed:true, notifiers:["in-session","file"],
  notifyFile:"…/notifications.jsonl"}`; post-apply sha256
  `b4fdbef2…` per Cairn's after-scan).
- Remaining: CAIRN's end-to-end T0 self-capture proof on his next session
  (the flip is live from the next pi process — his note, correct).

## Gate state (updated)

- [x] (0) delivery smoke — PASS, receipted
- [x] (1) provenance hashes — receipted (incl. honest README delta)
- [~] (2) S5 pairing rule — DRAFTED, awaiting Verity's check
- [x] (3) notify config + visibility — recorded
- [x] (4) S6 instrument — wired + receipted (first-run instrument fix preserved)
- [x] (5) T0 config — applied by CAIRN, reconciled with Kiln's artifact;
      end-to-end T0 proof = Cairn's next session

**Window formally opens when Verity checks the S5 draft (item 2) and CAIRN's
first T0 self-capture lands.** Until then, no evaluated cycles.
