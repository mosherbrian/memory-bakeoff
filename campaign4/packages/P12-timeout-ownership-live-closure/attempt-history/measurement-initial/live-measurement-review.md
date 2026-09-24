# P12-live-measurement-1 — independent review (corvid)

- **Action:** `P12-measurementreview-1`, start `02:23:21Z`, deadline `02:48:21Z`.
- **Claim:** `live-measurement-claim.json` on allocation `7d77df95` + ruling
  `restart-classification-ruling.json`; product **frozen** `8ad12b86fa82` /
  `97a57db1`.
- **Verdict: PASS** on the measurement corrections (script-only, product frozen),
  with the residuals below carried to the signed live run. `live1` stays NOT READY;
  no retro-PASS.

## Pins / integrity

- **25/25** `files_sha256` match; product binary `97a57db1…` unchanged; templates
  still pin `8ad12b8`/`97a57db1`; `internal/core`, `internal/py`,
  `conformance/cases`, `examples` **unchanged** (`git diff 8ad12b8..HEAD` empty).
  Live1 raws and `live-review-1.md` preserved.

## Independent raw-based proof (my run of `checks-test.sh`)

`checks-test.sh` on the **immutable saved live1 raws** → **40 checks, 0 wrong**,
with a negative control for every correction:

- **L3a** — OLD `journalctl -o cat | grep -q` under `set -o pipefail` = **rc 141**
  (SIGPIPE) on a real match; the **watchdog line is in the saved raw**; NEW
  `l3a_eval` (whole-journal read, requires `Watchdog timeout` **and** `Failed with
  result 'watchdog'` between onset and restart+5 s) = **PASS**. Negatives: stale
  onset, no watchdog line, wrong result → FAIL.
- **L7c / recovery waits** — `healthy_after` accepts `ok` **or** `rest` at/after the
  event; OLD `state_is ok` on the idle `rest` = FAIL, NEW = **PASS**; negatives for
  `starting`/`unknown`/`hung`/`crashed`/`restart-loop`/`PARSE-ERROR`/no
  `checked_at` all FAIL.
- **L4a / L4b** — `start_limit_eval` per the ruling: `crashed` **or** `restart-loop`
  is the owned alarm **only** with a proven restart loop since the onset (≥ BURST−1
  scheduled restarts, ≥ BURST−1 failed starts, then `Start request repeated too
  quickly`; BURST read from the unit; `reset-failed` gives a fresh window). OLD
  live1 `Result=exit-code`, NEW (burst 5) = **PASS** for L4a and L4b. Negatives:
  single crash, stale onset, wrong unit, no rate-limit refusal, too few restarts →
  FAIL.
- **L6** — exact callback argv captured (`l6_argv_eval`); replay runs it as a
  process with `AGENTDECK_PROFILE` and `l6_replay_eval` requires rc 0,
  `already-handled`, and **no new /cancel or director wake**; an uncaptured argv is
  INCOMPLETE. OLD live1 replay `not found` (unit gone); NEW PASS shape. Negatives:
  wrong binary, wrong qid, unit gone, rc 1, interrupted again, new /cancel, new
  director wake, no output → FAIL. **No retro-PASS** for the unexecuted replay.
- **Stop waits** — L5/L6b wait for run's own `stop requested; exiting 64` since the
  stop onset **and** the unit not active; OLD stale `ExecMainStatus`; NEW = PASS;
  NEG no exit line → FAIL.

## Composition / retained

- `dry/` full driver with `DRY=1`: **rc 0, 17 DRY rows** (every case); the two
  `JSONDecodeError` tracebacks are an existing DRY-mode artifact (also in
  `old-driver-dry-stderr.txt`), not new.
- `bash -n` passes for `live-driver.sh` and `live-checks.sh`; diff vs
  `attempt-history/live1-plans` is 107 lines.
- Unchanged: UTC calendar timers, `OnFailure` checker handler and L7-checker, ack
  timing (L6-timing), L6b bounds, rest/ownership checks, 75 min wall/cleanup, pins.

## Residuals (carried to the signed live run)

1. The corrected L3a/L4/L6/stop checks are proven on **live1 raws and a dry run
   only**; each still needs the **signed live run**.
2. The **L4a/L4b restart-loop label depends on the frozen product**; on this host
   (systemd 258) the owned alarm reads `crashed` — a **declared diagnostic limit**,
   not a universal systemd claim. The ruling permits `crashed` OR `restart-loop`
   with the independent causal evidence above.
3. The L3a OLD reproduction uses the live1 unit's host journal bytes (the same
   bytes saved in `raw/` for the new checks).
4. No product/source/unit/binary change; `live1` NOT READY preserved; no live task,
   service, install or cutover effect.

No source edits by corvid. **PASS** returned to Tern for the final plan check and
the funded fresh prep/binding/live path; cutover remains PASS-only.

---

## Measurement-review receipt closure (same pass, no reset)

Read `live-measurement-review-receipt.json` (`cc6cdaaa…`); claim `c849357b…`, 25
files verified. Verdict amended with **two required corrections** found against the
receipt focus; the proven corrections stand.

### Required before live signature

1. **`live-checks.sh` is a runtime dependency — bind it in the signature.** The new
   driver sources `plans/live-checks.sh`; the final plan signature must pin the
   helper's hash alongside `live-driver.sh`/inputs/units/binary, or the signed plan
   does not cover the code that evaluates the cases.
2. **Exact replay-argv binding is incomplete.** `l6_argv_eval` (`live-checks.sh:58`)
   binds `argv[0]==binary`, `argv[1]==timer-callback`, `--qid <qid>` and the
   **presence** of `--action`, but it does **not** bind the `--config` value, the
   `--action` value, nor reject extra/ambiguous tokens. The negative set lacks
   wrong-config / wrong-action-value / extra-args. Per the receipt ("strictly bound
   to binary/config/qid/action … reject ambiguous/wrong/missing args, never execute
   an unconstrained captured command"), add those bindings and negatives.
3. **`healthy_after` does not require a fresh pass.** `healthy_eval`
   (`live-checks.sh:49`) accepts `ok|rest` with `checked_at >= EPOCH`, but reads no
   pass timestamp/counter, so a recent check over an **old pass** can satisfy
   `rest`. Per the receipt ("healthy rest requires fresh pass, not only a recent
   check of old pass"), add a fresh-pass condition (e.g. `checks_since "$EPOCH" >= 1`
   or a pass timestamp in the verdict) to `healthy_after` for L7c/L3a-pass/L3b.

### Confirmed / unchanged

- **Restart-classification ruling is explicit and applied:** `start_limit_eval`
  accepts `crashed` **or** `restart-loop` only with a proven restart loop since the
  onset (≥BURST−1 scheduled restarts + failed starts + `Start request repeated too
  quickly`); the **actual observed state is preserved** (never relabelled); the
  systemd-258 `Result=exit-code` diagnostic limit is declared, not universalised.
- Saved-raw negatives, the L3a SIGPIPE reproduction (rc 141), L7c idle-`rest`, L6
  unexecuted replay (no retro-PASS) and stop-exit waits are as reviewed
  (`checks-test.sh` 40/0). **Dry tracebacks are inherited placeholder artifacts,
  not live proof**; every correction still needs the **fresh live test**.
- No source/fixture/task/live/cutover change.

**Verdict: PASS on the proven corrections, with the three signature/precision
corrections above required before the fresh live run.** Returned to Tern
immediately; cairn also woken.
