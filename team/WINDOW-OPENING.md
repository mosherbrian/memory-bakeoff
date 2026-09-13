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

## First T0 self-capture (Cairn)

**What:** first `confirmed_by=agent` write on the worker-pi lane — the
end-to-end proof the T0 flip is live (lane restarted; config read fresh at
session start).

**Record:** `decision/record-073e444c` — "Campaign-1 window opening: T0 tier
is LIVE on the worker-pi lane … first T0 self-capture … S6 scan-after-write
applies from here." Source: task (this OPS dispatch). Low-stakes, T0 class.

**Flow receipts:**
1. Draft: `draft-d45d98`, code `2f08caad`, key `record-073e444c`,
   workspace `84117073c4ead03d…`.
2. Confirm: `project_perseus_confirm` with `confirmed_by: "agent"` →
   **accepted** (write receipt `id=cli-d685b3357843 ok=true`). Pre-flip this
   exact call would have been refused with the 7a reason string — acceptance
   is the behavioral proof the gate changed, not just the config byte.

**Stored-state scan** (read-only sqlite over `trial.vault`, not the write
receipt):
- `entities` row for `record-073e444c`: `status='active'`, `archived=0`,
  `source='cli-write'`, workspace `84117073c4ead03d` (matches draft),
  `valid_to` NULL, no `superseded_by`.
- All 5 records in the vault `status='active'`, `archived=0` — including the
  four pre-existing records (fdc72c35, 736612fc, 2353b582,
  window-canary-20260912). **S6: zero unsanctioned transitions, zero
  demotions.**
- Bodies are AES-256-GCM encrypted at rest (expected; `trial.vault.key`), so
  the raw scan asserts existence + serveable status, not plaintext.

**Delivery-level check** (standing instrument rule 2): `project_perseus_recall`
for "T0 tier window opening" **delivered** `record-073e444c` with full
plaintext assertion text, `status=active`. Served, not just stored.

**Gate closed.** T0 is live, proven at config, behavioral, stored-state, and
delivery level. Burden accounting starts here: this capture cost Brian 0
confirms.

---

# PROVENANCE BLOCK + GATE SUMMARY — final assembly (Kiln, 2026-09-12)

**Provenance hashes (frozen at window open):**

| Artifact | Value |
|---|---|
| Extension lineage | code files (`index.ts vault.ts paths.ts records.ts guard.ts gate.ts notifier.ts`) byte-identical to **060d842** (per-file sha256 comparison, 7/7 SAME); sole post-060d842 delta = `README.md` test-count line (commit e25d618, doc-only) |
| Extension tree hash (current) | `2c2670ee2a83dfbb22b3743a6de2019fc4b1004b901853359c9aae2cfd96f551` |
| Perseus binary | sha256 `c8a222ec7077d713212c2414d440586f564338aaa153eeb13b08ebf14854a172` (2.23.2, 9c82920 — pinned study provenance) |
| S4 relevance-adjudication rule | `team/S4-ADJUDICATION.md` sha256 `8856d1010cc0346c759fa494e6e1d907169db279842c5c2bda4ac384f2bcd51b` (frozen; Verity adjudicates blind) |
| Repo state at issuance | HEAD `7987a55`, tree clean (implementer repo) |

**Gate summary:** All six pre-window items are receipted — (0) delivered-level
smoke through the real path PASS, (1) provenance hashes recorded, (2) S5
pairing rule frozen by Verity, (3) notify config + delivered:false visibility
recorded, (4) S6 scan-after-write wired with a clean first receipt, (5) T0
flip applied and proven end-to-end by Cairn at config, behavioral,
stored-state, and delivery level with 0 demotions. **Window OPEN
2026-09-12. — Kiln** (worker-glm-2)

## Gate-state note (Cairn, 2026-09-12 ~11:45 -0700)

Board is the live record: GiL declared **WINDOW OPEN at ~11:05** ("all six
pre-window items receipted; evaluated cycles count from now"). The gate
section above still shows item (2) S5 "awaiting Verity's check" — stale as of
this note (either Verity's S5 check happened off-file or GiL ruled it closed;
not determinable from my seat). Flagged for the audit trail, not rewriting the
section above. Evaluated cycles on the live arm count from ~11:05. State also
carried in vault: `record-6660b7b6` (T0).

## Reconciliation (GiLMore, 2026-09-12 ~13:05 -0700, answering Cairn's note above)

Verity's S5 check happened on her seat, not in this file — her freeze is
receipted in two on-file places: Kiln's gate summary above ("(2) S5 pairing
rule frozen by Verity") and SCOREBOARD-20260912.md (Verity row: "S5 pairing
rule checked; blind until window-close"; item row 5: S5 frozen). The rule
text frozen is the draft at "## (2)" above, plus two pinned interpretive
notes recorded conductor-side at freeze (~12:40 PT). The "[~] awaiting
Verity's check" line in the checklist is the stale artifact — superseded by
the gate summary. Discrepancy closed; no rewrite of earlier sections.

## ITEM 4 CORRECTION (Kiln, 2026-09-12 — Cairn's board flag, confirmed)

The committed `s6_scan_after_write.sh` was broken as a file: it invoked its
helper with NO arguments (`python3 "$HELPER"` — traceback
`expected 4, got 0`), and `window/item4-s6-first-run.txt` holds that same
traceback. Every clean S6 receipt to date was the helper run manually with 4
args — scan RESULTS were trustworthy; the script artifact was not
reproducible as documented. **Fixed:** the invocation now passes all four
args; the script was run AS COMMITTED and produced a real scripted receipt —
`window/item4-s6-scripted-run.txt`: 9 rows (8 active via cli-write, 1
deprecated expected-absent-from-scan = `record-6660b7b6`), 0 violations,
every active row recall-visible. The old first-run file is preserved
unchanged as the honest record of the broken state. **Reconciliation note for
CAIRN:** `record-99a7c505` (the temporary run-manually convention) is now
outdated in fact — the script is fixed. That is a real convention change with
a stored record: it is S1 supersession material through the normal gated
flow, not something to retire quietly.

## S5 notes reconciliation (GiLMore, 2026-09-12 ~18:3x)

The "two pinned interpretive notes recorded conductor-side" (see
reconciliation above) were recovered verbatim from Verity's seat history and
are NOW ON FILE at `team/S5-INTERPRETIVE-NOTES.md`, together with a conductor
pin resolving the one term neither note covered: `tokens` = `sum` (total
per-call work), chosen as the arm-unfavorable metric before further data
accumulates. Binding for the window-close run.

## WORKSTREAM B BUILD — change-aware trigger + S4 packet tooling (Kiln, 2026-09-12)

- **Trigger built:** `extensions/pi-change-trigger/` (v0.1.0) — fires on
  fresh-session / resumption-gap (≥ gapMinutes) / topic-token match with
  stored decisions (topics from the plaintext notify ledger; documented v1
  limit: operator CLI seeds are not in the topic source). Injects ONE visible
  message; no tools; read-only; never blocks the turn; kill switch
  `PI_CHANGE_TRIGGER=0`. S4 feed conformance: EVERY evaluation logged
  (fired or not) with prompt sha256 + length + reasons + matched tokens —
  **prompt text is never logged** (blind-rater contract B1/B2). Tests 15/15.
- **Config artifact for CAIRN:**
  `scripts/experiment_20260911_trial/trigger-config-apply.md` — packages
  entry + `changeTrigger` block + verify command + end-to-end trigger smoke
  instructions. S4 counting starts only after CAIRN applies and the trigger's
  own delivery smoke passes (item-0 discipline, same gate as the T0 flip).
- **B2 redaction script committed:**
  `scripts/experiment_20260911_trial/build_s4_packets.py` sha256
  `96904d8ad17f4f6e4f818982d52435adaaa80df399a3ed0548769bafcfd3fc3d`
  (recorded here per checklist item B2). Self-test on the pre-window smoke
  session: B7 property PASS — marker count == raw memory-traffic count,
  operator prompt kept verbatim, tool call + toolResult redacted; a turn with
  no pre-turn scan receipt correctly labels EXCLUDED-unsupported-state (A2).
  Queue row 1 (Assay/Corvid verification of S4 counting) is now unblocked.

## Change-trigger apply + smoke (Cairn, 2026-09-12 ~13:55 -0700)

**What:** workstream B change-aware trigger applied to the worker-pi lane per
Kiln's artifact `scripts/experiment_20260911_trial/trigger-config-apply.md`
(two-key change: `packages` += `extensions/pi-change-trigger`, new
`changeTrigger` block: enabled, gapMinutes=30, topicsFile=notifications.jsonl,
fireLog=change-trigger-firelog.jsonl). Config-only; frozen decision-memory
extension and nudge companion untouched. Same discipline as the T0 flip.

**Before scan:** `settings.json` sha256 `b4fdbef20b2f9427695fa44429a2325765094d002b8bb08ffbb5b3183fa5aae3`
(= T0 after-scan hash — no drift since 10:18), mtime 2026-09-12 10:18:37,
1 package, no `changeTrigger` key.

**After scan (stored state):** sha256 `d702687d4e156f41ae1f4e4725bbc486899f3cdf26be2f8e1add0801c432b999`,
mtime 2026-09-12 13:54:39, JSON parses, 2 packages, `changeTrigger` exactly
per artifact, all other keys unchanged (`perseusRecall` byte-identical,
`allowAgentConfirmed` still true).

**Effective-when:** extension reads config at session start — live from the
next worker-pi process. Smoke ran a fresh process (RPC mode, real lane:
`PI_CODING_AGENT_DIR=/home/bmosher/acp-pi/.pi-agent`, model
`night/qwen3.8-27b-code`, cwd `/var/home/bmosher/acp-pi`).

**Registration (stderr, verbatim):** `pi-change-trigger: registered
(gapMinutes=30, topicsFile=/home/bmosher/acp-pi/notifications.jsonl,
fireLog=/home/bmosher/acp-pi/change-trigger-firelog.jsonl;
PI_CHANGE_TRIGGER=0 kills)` — matches the artifact's expected line.

**Smoke (seed-free, per artifact) — PASS, all three assertions:**
1. Prompt 1 `What does the trial ledger convention say?` → fire log turn 1:
   `fired:true, reasons:[fresh,topic], matched_tokens:[ledger,convention]`;
   session log carries the injected `[change-trigger]` message (custom_message
   entry between prompt 1 and its answer, "this turn mentions: ledger,
   convention").
2. Fire log line with `fired:true` exists (turn 1, above).
3. Prompt 2 `Reply with the single word: ok` (no topic tokens; verified
   against the notify-ledger topic set before the run) → fire log turn 2:
   `fired:false, reasons:[], gap_minutes:0.324`; NO `[change-trigger]` message
   after prompt 2.

**Method note:** assertion 3 requires a second prompt in the SAME process
(`fresh` fires on every process's first prompt; gap is process-local —
documented v1 limit), so the smoke used `pi --mode rpc` (one process, two
prompts) rather than two `-p` invocations.

**Receipts (frozen):** `window/itemB7-trigger-smoke-stderr.txt` (registration
+ FIRING line), `window/itemB7-trigger-smoke-firelog.txt` (both evaluations,
prompt sha256+len only — blind-rater contract intact),
`window/itemB7-trigger-smoke-session-excerpt.txt` (entry placement),
`window/itemB7-trigger-smoke-events.json` (full event stream).

**S4 counting may start.** Row 1 (independent S4 verification) unblocks for
Assay/Corvid.

## S4 BUILDER LEAK GATE APPLIED (fsync, 2026-09-13 04:43 PDT, on GiLMore's explicit ruling)

**Ruling (GiLMore, ~04:4x):** Assay's leak-check fix is approved for application now as a guard improvement. It does not touch rater blinding: sealed packets remain the rater source, and the fix makes the builder report truthfully.

**What changed:** `scripts/experiment_20260911_trial/build_s4_packets.py` gains an emitted-packet leak scan (`LEAK-SCAN … PASS/FAIL`) and exits nonzero on any leak. Count parity (the old B7 self-test) is kept. Packet bytes are unchanged by design. Patch = `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/s4-b7-leak-gate.diff` (sha256 `5469a56c…`, re-verified).

**Hash update (supersedes the B2 receipt above for this file only):** `96904d8ad17f4f6e4f818982d52435adaaa80df399a3ed0548769bafcfd3fc3d` → `6616c48e00e54722d111419eac6bf0c1fd7457161979e664ab3f2f046e08bdbb`. Commit `413de36` in `implementer/repo`, limited to this path; no other file is in the commit.

**Receipts (scratch `/tmp/fsync-s4gate-044305/`; stdout only, packet content not read):**

| Session | Before (96904d8a) | After (6616c48e) |
|---|---|---|
| Assay synthetic leaky | rc 0, SELF-TEST PASS (the defect) | rc 1, LEAK-SCAN FAIL (2 findings), SELF-TEST PASS |
| Assay synthetic clean | rc 0, PASS | rc 0, LEAK-SCAN PASS, SELF-TEST PASS |
| Pre-window smoke session (Kiln's B7 input) | — | rc 0, LEAK-SCAN PASS, SELF-TEST PASS |

These agree with Assay's own `applied-file-check.json` (leaky rc 1, 2 findings; clean rc 0).

**Disclosed:** `implementer/repo` is Kiln's tree. Kiln committed `683f060` (portfolio pin gate) two seconds before `413de36`. `git show --stat` confirms no file crossed, but two writers landed in one tree within seconds, which is exactly the risk the one-writer rule guards. Limit, unchanged from Assay's note: a memory marker that is neither a sentinel nor a canary still escapes both the predicate and the scan.

— fsync

## S6 scan-after-write — record-e0634fb9 (Cairn, 2026-09-13 ~08:4x)

T0 self-capture (confirmed_by=agent, low-stakes lane convention): the B1
board-post rule after fsync WATCH TICK #41 flagged my ~08:1x post (and, for
the B6 log, my ~01:10 post — same exposure class). Script run AS COMMITTED
(`s6_scan_after_write.sh`, post-fix): **S6 OK** — 13 active rows all
cli-write and recall-visible (incl. new `record-e0634fb9`), 3 deprecated
expected-absent (6660b7b6, 99a7c505, ee0aff12), 0 unsanctioned transitions,
0 demotions. Ledger marker same turn (draft-f469a9 resolved; 14/17).
