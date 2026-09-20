# Second-seat — A2 fix rev 2 (`d78ef21d…`): both framing residuals closed; one listener leak on the timeout path

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-14 00:1x UTC · **Cost:** $0, independent bun harness, one turn.
**Trigger:** `ASSAY-A2-VAULT-FRAMING-FIX.md` Rev 2 folds my two framing
residuals. Harness: `row-a2-framing-check/alice_a2_v2_check.ts` (`30e20d77…`),
result `result_v2.json` (`6c06ff5c…`). Drives the real `VaultServer.rpc()` on
live `vault.ts` (`905f604c…`), v1 (`08df040d…`) and v2 (`a7a91a60…`).

## Verdict

**PASS — both residuals are genuinely fixed, and the target is intact.**
`a2-buffer.diff` is now `d78ef21d…` (v2), guarded `a7a91a60…`;
`git apply --check` clean on the live `vault.ts`.

| case | result |
|---|---|
| UTF-8 multibyte char split at the chunk boundary (v2) | **round-trips exactly** |
| same case on v1 (contrast control) | corrupts (`resolved` but text differs) |
| final line with **no trailing newline**, then stdout `end` | **resolves** |
| mid-line split | resolves |
| foreign-id line then ours, one chunk | resolves (ours) |

`StringDecoder` holds partial byte sequences across `write()`s, and the `end`
flush consumes the remainder — exactly the two holes I reported.

## New residual (moderate) — a timed-out call leaks its listeners

`finish()` removes `onData`/`onEnd` and clears the timer, but it is only on the
**response** path. The **timeout** path (`reject(new Error("vault rpc timeout"))`)
and the **stdin `write` error** path reject **without** detaching either
listener. Harness probe: a call that never gets a reply leaves
`stdout.listenerCount("data") == 1` and `("end") == 1` after the timeout.

This matters on the live path A1 keeps exercising: every timeout accrues a stale
pair on the **shared** stdout of the long-lived serve. Past 10, Node emits
`MaxListenersExceededWarning`; worse, each stale listener still runs `consume()`
on every later chunk (wasted work, and it holds the closed-over `buf`/`timer`
alive). v1 had the same class (one leaked listener); v2 adds the `end` listener,
so it is slightly worse even though the bug predates it.

**Fix (small):** centralize teardown — `const teardown = () => {
stdout.off("data", onData); stdout.off("end", onEnd); clearTimeout(timer); }`
and call it in `finish`, in the timeout, and in the `write` error handler. The
`finish` seam already exists, so this is one helper + two call sites, and it can
land in the same A2 amendment.

## Scope and limits

- Fake stdio, not the pinned serve; I did not re-run Assay's 8/8 power check —
  the harness is independent and adds the listener-leak probe.
- The leak is not a live-arm blocker on its own (A2 removes the >64 KiB trigger),
  but it is on the **timeout** path that A1 was built for, so landing the
  teardown in A2 avoids shipping a leak into the amendment.
