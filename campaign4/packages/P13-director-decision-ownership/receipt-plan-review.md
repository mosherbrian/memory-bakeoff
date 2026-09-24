# P13 receipt-plan-1 — independent review (corvid)

- **Action:** `P13-receiptplan-review-1`, owner corvid, `17:47:18Z`–`18:02:18Z`.
- **Bound claim:** `receipt-plan-claim.json` (`60f0b7bc…`) — author **COMPLETE**,
  offline **43 PASS / 0 FAIL**; release `47f69dfd…` (unchanged).
- **Verdict: PASS** on the plan scope, with the offline-vs-live differences below
  enumerated. No live/install/service/source effect; no guard weakened.

## Pins / bound evidence

- **96/96** `files_sha256` match; product/adapters frozen
  (`47f69dfd…`, `df51a1f4…`, `fdf49d0b…`); final `offline.log` = **43 passed,
  0 failed**; `results.tsv` `NOTIFY/PREP/RUNGS/RECUR/DECIDE/LIVE` all PASS.
- **Product receipt guard unchanged** (`internal/host/adapter.go:236-325`):
  settlement still needs transport receipt + action/execution/seat + a
  `turn-seen:<stream_key>:<item>:<exec>`; nothing weakened.

## Three causes — fixed and evidenced (not stub success)

1. **stream key:** turn ends were written to `streams/W1.jsonl/V1.jsonl` while the
   routed sessions are `p6-fixture-w-id`/`p6-fixture-v-id` (stream key = **file
   name**, matched to active seat sessions). The plan now binds titles→IDs and writes
   to the **routed session-id-named** stream files.
2. **claim package/action:** `E_CLAIM_MISMATCH` (template hardcoded `P13FIX` vs
   launch manifest `D-off1`/`D-off1-w1`); `decision-turn.sh --package` is now
   required and the harness passes the real qid/action. Aborted run kept.
3. **re-raise check:** the plan grepped `"reraised": "sent` (space) while Go JSON has
   `"reraised":"sent`; the re-raise **had** happened (2 ledger records, one key).
   Check now parses JSON. Bug run kept.

## Executable live/promotion paths (beyond stub success)

- **Bound:** `2030` removed; `OFFLINE_DEADLINE` is **required** and is the real
  enclosing bound, with a 720 s refusal and the whole run under
  `timeout --kill-after` to that instant; the stub wall uses `STUB_WALL_EPOCH =
  OFFLINE_DEADLINE`.
- **Notify modes:** `NOTIFY_MODE=offline` (default) uses the versioned
  `ticket-notify.sh` + private-HOME ledger + stub ticket; **`NOTIFY_MODE=live`**
  (signed live only) requires the **pinned installed `notify-claude`**
  (`NOTIFY_CLAUDE_SHA`) under `HOME=private` → private ledger + **labelled chat
  notice**, ticket stays a stub. The offline harness asserts **mode offline**, so
  offline success **never proves real notification**.
- **Live path:** four fresh real identities via `prepare_live.py` (non-dry-run) with
  registry binding; tasks commands produce **real claims**; run/check units installed
  where systemd loads them; explicit stop marker + genuine restart; absolute-calendar
  cleanup armed before tasks and the wall stops the original driver scope
  (`live20-plan.sh:70`); caps archived **redacted** (hashes/permissions only) then
  the run-scoped `<P>.db.caps` removed.
- **Promotion/rollback:** `guard_absent` refuses absent adapters / invalid actual
  prospective policy / mid-decision package; `rollback` restores exact
  binary/watcher/timer/service/resolve/config/ownership and verifies the archived
  sha (never the candidate).
- **Isolation:** write-attribution with a **planted negative** detected.

## Remaining late-bound inputs / live differences (honest)

- Offline systemd is **stubbed**: `start` clears the marker but **no real unit
  restarts** — the real restart is the signed live run only.
- Four **real** seats/registry/socket/stream binding are exercised by the live prep
  (agent-deck stubbed offline).
- **Actual Claude chat notification** only in `NOTIFY_MODE=live`; the ticket stub is
  offline proof only.
- Real absolute-calendar timer/cleanup and the real enclosing wall are live-only.
- Late-bound for signature: `RUN/ROOT/LIVE_DEADLINE`, fixture ID/name pairs,
  `RUNG0/1/2_S`, `DECISION_WINDOW_S`, `ESC_LEDGER`, `NOTIFY_CLAUDE`(+sha in live),
  `RESOLVE_CMD`, `TICKET_STUB`, adapter paths/shas.

No concrete executable blocker found for the plan; live/promotion remain separately
signed. No live/install/service/source edit by corvid. Returned to Tern.
