# P12-measurement-repair-1 — independent review (corvid)

- **Action:** `P12-measurementrepairreview-1`, start `02:29:20Z`, deadline
  `02:44:20Z`.
- **Claim:** `live-measurement-repair-claim.json` (32/32 hashes match); product
  **frozen** `8ad12b86fa82` / `97a57db1`.
- **Verdict: PASS.** Corrections (2) and (3) from the measurement review are fully
  implemented, independently reproduced, and the runtime helper hashes are bound
  for signature.

## Signature binding (confirmed)

- `plans/live-checks.sh` = `190858566b610a387e18d16834ab29b155356fec65d314dea161f793af958b51`
- `plans/live-driver.sh` = `f6afd9e08f84a0dff8d364a804dc04faa3fae48fb4ac687d3bd0bec78968f8dd`
  (both match the claim; `live-checks.sh` is a runtime dependency and must be in the
  final plan signature set alongside the driver/inputs/units/binary).

## Correction 2 — exact replay-argv binding (PASS)

`l6_argv_eval BIN CONFIG QID` now requires the captured `argv[]` to be **exactly**
`[BIN, timer-callback, --config, CONFIG, --qid, QID, --action, QID-w1, --execution,
ex-QID-w1]`, with **exactly one** `argv[]` entry. The driver passes `$A $CFG $Q`
(`live-driver.sh:408`). Independent negatives on the saved raws: wrong binary,
wrong qid, **wrong config**, **wrong action value**, **extra argument**,
**duplicate `--qid`**, **missing `--execution`**, **ambiguous (two `argv[]`
entries)**, unit gone — **all FAIL**; the exact live1 argv PASSes.

## Correction 3 — fresh-pass `healthy_after` (PASS)

`healthy_after EPOCH` now requires **both** the verdict `ok|rest` checked after
EPOCH **and** the ledger's own loop-pass record (`pass_eval`, read-only sqlite) with
`at >= EPOCH`, `invocation == the unit's current InvocationID`, `pid == MainPID`
(`live-driver.sh:110`). Independent negatives: stale pass, other invocation, other
main pid, unreadable unit invocation, malformed record, missing record — **all
FAIL**; and **a fresh check over an OLD pass FAILs** (a checker timestamp/count is
not pass evidence). The live1 record (fresh, same invocation/pid) PASSes.

## Evidence / retained

- `checks-test.sh` on the immutable live1 raws → **54 checks, 0 wrong** (rc 0);
  v1 test/output kept (`checks-test-v1.*`).
- `dry-repair1/`: `DRY=1` full driver **rc 0, 17 DRY rows**; the two inherited
  placeholder tracebacks remain (not live proof).
- `bash -n` passes; product binary `97a57db1…` unchanged; no product/unit/service
  change.

## Residuals

1. Proven on saved raws and a dry run only — the **signed live run must show them**.
2. The L4a/L4b diagnostic limit is unchanged (`crashed` on this host's systemd;
   ruling permits `crashed` or `restart-loop` with proven restart-loop injection).

No source/fixture/task/live/cutover change. **PASS** returned to Tern immediately;
cairn also woken.

---

## Measurement-repair intake closure (same pass, no reset)

Intake `ebc83170` (claim `32/32`); helper hashes `live-checks.sh 19085856…` +
`live-driver.sh f6afd9e0…` confirmed.

- **Exact argv incl `--execution` matches the actual production callback argv.**
  The live1 journal's captured unit argv is
  `… timer-callback --config /home/bmosher/p12live-p12live1/fxp12live1.json --qid
  L6-p12live1 --action L6-p12live1-w1 --execution ex-L6-p12live1-w1` — byte-for-byte
  the `l6_argv_eval` expectation `[BIN, timer-callback, --config, CFG, --qid, Q,
  --action, Q-w1, --execution, ex-Q-w1]`. This binds the **real production** argv
  (the id format `ex-<qid>-w1` the product arms), **not** a fixture-only invention;
  the negatives (wrong config/action value/extra/duplicate/missing `--execution`/
  two `argv[]` entries) all FAIL.
- **Fresh-pass proof** uses the ledger's authoritative loop-pass record
  (`at >= EPOCH`, `invocation == current InvocationID`, `pid == MainPID`) with
  negatives for stale/other invocation/other pid/unreadable/malformed/missing and
  **fresh-check-over-old-pass**; all correct.
- **Whole driver sources the helper** (`. "$PLANS/live-checks.sh"` at
  `live-driver.sh:105`); no runtime/product change (binary `97a57db1…` frozen).
- **No required correction remains** — corrections (2) and (3) are implemented and
  proven on immutable raws + dry; the helper hashes are bound for the plan
  signature. This is a **bound PASS**, so the conditional **prep-2 release may
  execute** (it is verdict-gated and was not active before this verdict).

No source/fixture/task/live/cutover change.
