# CORVID-D-1-VERIFY — artifact verification of row D-1

Verifier: corvid-dsh, 2026-09-17 10:56 PDT. Author: kiln-flash (claimed 08:42,
closed 08:52). Artifact: the deployed poller
`/home/bmosher/.local/share/agent-deck/conductor/glm/fleet-poller.sh`
(declared check embedded in the row). I am the named verifier; kiln authored.

**Verdict: VERIFIED PASS. No defects. Two observations recorded as limits, not
faults.**

## What was run

1. **Declared check, real path:** `test 0 -eq $(grep -c 'LEDGER=721125ec'
   …/fleet-poller.sh)` → rc 0. The old constant appears nowhere in the
   deployed poller — including kiln's own comment, which was reworded to
   "the old line pointed LEDGER at cairn's id, 721125ec" (prose keeps the
   history; the literal `LEDGER=721125ec` string is gone). Honest rewording,
   not suppression: the pre-D-1 value remains on record in the comment block.
2. **The fix:** line 70 `LEDGER=72180e11-1789149653`. Resolution to
   ledger-claude confirmed three ways: the `LEDGER_HIST` glob
   `$HIST/72180e11-*.jsonl` (line 57) pairs with it by construction;
   `state.json` history entries name the seats ("Ledger 72180e11: …",
   "Cairn 721125ec: …"); and the comment (line 61) states the pairing.
3. **Fallback explicit:** lines 61–69 are a PO ROUTING FALLBACK block citing
   this row by name: ledger-claude is furloughed (2026-09-15 roster) and sits
   in poller-exclude — verified, `poller-exclude:14: title:ledger-claude` —
   so PO-bound notices are NOT sent to $LEDGER; they go to Brian via
   brian_do() (Signal RPC, per-kind cooldown), with cairn-pi conducting and
   holding PO until Ledger is unparked. Line 71 `PO_ROUTE=$CAIRN` names the
   PO holder explicitly. The `brian()` implementation matches the description
   (per-kind cooldown file, DRY_RUN guard, one envelope with action +
   ignored-consequence text).
4. **Routing kept:** `brian_do()`/`brian()` are untouched (row's "brian_do
   path untouched" claim consistent with the code). No code path sends to
   `$LEDGER` at all — the variable is declarative post-fix — so "notices are
   NOT sent to $LEDGER" holds structurally, and removing the cairn-id alias
   changes no delivery.
5. **Syntax:** `bash -n` clean.
6. **Cross-copy and snapshot consistency:** the repo copy
   (`conductor-chat/workers/fleet-poller.sh`) carries the same fix (line 70,
   zero old-constant occurrences) — no cross-copy drift. Both deployed
   snapshots (`fleet-poller.latest.sh`, `fleet-poller.prev.sh`) carry
   `LEDGER=72180e11-1789149653` as kiln stated.

## Observations (limits, not defects)

- **PO_ROUTE is declarative.** No code consumes `PO_ROUTE`; the operative
  fallback is the documented brian_do() path. That satisfies the row's
  "make the fallback explicit rather than accidental" as documentation (which
  is what the row asked for — "keep the routing"), but a future row could
  wire PO_ROUTE into an emit path if the poller ever grows a PO channel
  distinct from Brian's alarms.
- **Stamp audit caveat.** The deployed file's mtime is 10:00:21 — that is
  D-2's later install (D-2 closed 10:00, claimed 09:47), which legitimately
  overwrote the mtime on this shared file. D-1's 08:52 stamp therefore cannot
  be mtime-audited; the substance is verified in the current bytes, and the
  snapshots + repo copy agreeing means the edit plainly happened.
- **Snapshot pre-dating:** `.latest`/`.prev` are dated 2026-09-14 and already
  carried the fixed constant — i.e. the live file had DRIFTED from its own
  snapshots and D-1 re-aligned it. Kiln disclosed this in the done note
  ("snapshots which already carried the fix"); recorded here because it
  means the defect was a regression, and nothing watches snapshot-vs-live
  drift today.
- **Live process:** per kiln's note, the running poller picks the constant up
  on its next managed restart. Harmless in the interim precisely because
  $LEDGER is not machine-consumed.
