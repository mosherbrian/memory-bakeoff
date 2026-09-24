# P13 live-composition-1 — independent review (corvid)

- **Action:** `P13-livecomposition-review-1`, owner corvid, `18:09:40Z`–`18:24:40Z`.
- **Bound claim:** `live-composition-claim.json` (`313a8faf…`) — COMPLETE,
  **24 PASS / 0 FAIL INJECTED** (not live proof). Candidate `47f69dfd…`,
  adapters `df51a1f4…`/`fdf49d0b…` unchanged.
- **Verdict: bounded issue.** H1–H5 are fixed and directly source-verified; the
  composition is executable-ready. **One bounded finding blocks signature: the
  included `plans/MANIFEST.sha256` is stale and is not the canonical current
  runnable artifact set.**

## Pins

- **111/111** `files_sha256` match. Live branch is now
  `plans/live-p13-driver.sh` (`1c348706…`) + `plans/live-p13-inputs.template.env`
  (`5cc8cbfb…`), derived from the P12 live driver; the old `live20-plan.sh`
  (`1d1c7ab7…`) is archived.

## H1–H5 (direct source)

- **H1:** `live-p13-driver.sh:47-48` pins `WAKE_SHA` and **refuses** any
  `fixture-wake.sh`/`*stub*` WAKE; director/duty are ACP seats
  (`acp-go`, `acp-go-controller`), never `-cmd WAKE`. Negatives present.
- **H2:** live tasks `decision-worker-live.md`/`decision-verify-live.md` write the
  artifact, run the absolute `claim` CLI and end the turn — **no stream/helper/item**;
  `decision-turn.sh` is offline-only and not referenced by the live driver.
- **H3:** `SD=/home/bmosher/.config/systemd/user` (real user search path); units by
  exact name; driver **refuses** unless `OnFailure=agent-loop-liveness-failed-<P>.service`
  (`:304`); cleanup removes the exact files and reloads.
- **H4:** split — `prep-p13.sh` arms an **exact-UTC calendar cleanup first and
  verifies it before launching** four fresh ACP seats (exact IDs recorded one by
  one); `bind-p13.sh` is **read-only** (registry row/title/profile/not-archived/
  idle/live socket/main-seat exclusion); the signed run **consumes the prepared IDs,
  no launch** (injected `agent-deck` refuses launch).
- **H5:** wall stops the driver's owned **scope first**, then cleans exact IDs once
  under a lock (`:238-242`); the TERM trap does not clean from inside the scope;
  archive **excludes `<P>.db.caps`** (modes/paths only) then removes it (`:191-195`).

## Injection test (24/0) — correctly labelled, not live proof

`results.tsv` rows are `INJECTED-PASS` for `DECISION/STOP/RUNGS/ACK/RECUR/DECIDE/
LIVE`; real = wake, `notify-claude`, `escalations`, candidate binary, adapters, unit
files; injected = `systemctl`/`systemd-run`/`journalctl`/`agent-deck`/`ss`/`curl`
and the seat runtime. The harness asserts **mode offline** and `NOTIFY_MODE=live`
requires the pinned `notify-claude` (real chat only in the signed live); pager is a
stub — **no Signal**. `attribution.txt` negative control present.

## Bounded finding — stale manifest / no canonical current set

`plans/MANIFEST.sha256` (`4feeacce…`) is **stale**: `sha256sum -c` fails on **6**
entries (it still lists the **archived** `live20-plan.sh 1dae5bd7…`, plus
`promotion-plan.sh`, `decision-evaluators.sh`, `live-inputs.template.env`,
`decision-worker.md`, `decision-verify.md`) and it contains **0** of the current
live-branch files (`live-p13-driver.sh`, `live-p13-inputs.template.env`,
`prep-p13.sh`, `bind-p13.sh`, `decision-{worker,verify}-live.md`). Per the receipt,
a **stale historical manifest cannot be execution authority**. **Smallest
correction (no unilateral repair):** regenerate one canonical current manifest for
the live set (or remove/annotate the stale one) and bind it in the signature;
`live-composition-claim.json` already lists the 111 current hashes and can seed it.

## Promotion / live differences

- `promotion-plan.sh` (`22c46bd2…`) still meets snapshot/restore: exact original
  binary/watcher/timer/service/resolve/config restoration, actual prospective policy
  guard, active-decision guard; unchanged by the live-plan change. Live qualification
  is separate from later promotion.
- Live-only: real ACP model turns, real systemd timers/journal, real chat listener;
  rung timing live is bound by the 30 s check cadence. Late-bound for signature:
  `RUN`, `ROOT`, `LIVE_DEADLINE`, four seat name/id pairs from `prep-result.env`
  after bind PASS, prep cleanup calendar time.

No live/service/install/edit effect by corvid. Bounded issue returned to Tern.
