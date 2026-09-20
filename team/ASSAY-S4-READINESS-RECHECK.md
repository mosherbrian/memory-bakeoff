# Assay — S4 packet-builder readiness re-check (current window)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~22:4x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — sealed-packet dry-runs when rater blinding requires it
**Content scope:** sealed output only. No fire-log content read; no rulings;
no packet text reported.

## What ran

The committed builder's `--self-test` over every current worker-pi session
(`--window-open 2026-09-12T00:00:00Z`, no `--scan`), plus the proposed
`packet_leak_scan.py` over the emitted **real** packets.

## Result — clean

| | value |
|---|---|
| sessions | **19** |
| turns | **135** |
| markers == raw memory-traffic | **383 == 383** |
| B7 self-test | **all PASS, 0 failures** |
| `packet_leak_scan` on real packets | **PASS** (no unredacted substance) |

Row-16 baseline was 17 sessions / 37 turns / 120 == 120; the window has grown
~3.6× in parsed turns, and the property still holds with no leak-scan hits.

## Caveats / limits

- `EXCLUDED-unsupported-state` = 135 (every turn), because no S6 `--scan`
  receipts were passed — a dry-run artifact, not state loss (see
  `ASSAY-POWERCHECK-S4-RECORDSET.md` for the verified semantics).
- The builder is unchanged since row 16 (sha256 `96904d8a…`), so the register's
  B7-count-parity finding still applies to this run: `packet_leak_scan` is the
  substantive check here, and it passes on real output.
- No fire log, no rater content; this is a readiness signal, not an S4 result.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/s4_window_readiness_recheck.py`
  sha256 `dbdda532d0ae7cced603482bcb5fef9f6d4a14847a2f0a2151f2b2492cddde10`
- Result: `.../sealed-s4-readiness-recheck-20260912/readiness.json`
  sha256 `53e70ed9c1b28801f6a853aef54e7d31b9ed6bb978f74c2e200a95de8804adff`
- Re-run: `python3 scripts/verify-20260912-assay-row1/s4_window_readiness_recheck.py`

— **Assay** (worker-glm-dsh2).

---

## In-window bound (window-open `2026-09-12T18:05:00Z`, the board-declared open)

The first run used `00:00:00Z` (whole day). Re-ran bounded to the actual S4
window:

| | value |
|---|---|
| sessions | 19 |
| in-window turns | **125** |
| markers == raw | **367 == 367** |
| B7 self-test | **all PASS, 0 failures** |
| `packet_leak_scan` | **PASS** |

So of the whole-day 135 turns / 383 markers, **10 turns / 16 markers are
pre-window**; the S4 packet population is 125 turns / 367 markers, and the B7 and
leak-scan properties hold there. Same caveats as above
(`EXCLUDED-unsupported-state = 125` is the no-`--scan` dry-run artifact).

- Script extended with `--window-open/--window-close`; current sha256
  `d0eeff54367f7d341e0761271b0c57afbb9c10f7651b6d9a7d7b94c3a4b6e82b`
  (supersedes the `dbdda532…` recorded above, which only lacked the args).
- In-window result: `.../sealed-s4-inwindow-recheck-20260912/readiness.json`
  sha256 `ad289b73198adfa8ee8e691e907afca1c256513d267d1eaffe844f8797aa8f99`

---

## Drift note + frozen re-derivation (cross-check)

The live-directory counts are **point-in-time**: the in-window run read 125
turns, but an independent count of the same live sessions minutes later read
**134** — one session kept growing. Same class as the S5 sample drift.

Re-ran on a **frozen snapshot** of the session bytes (via `s5_freeze_inputs.py`):

| | frozen run | independent count on same bytes |
|---|---|---|
| sessions | 19 | 19 |
| in-window user turns | **134** | **134** |
| markers == raw | 376 == 376 | — |
| B7 / leak scan | PASS / PASS | — |

So the builder's turn parser agrees **exactly** with an independent counter when
the input is frozen; the moving number is the input, not the parser. Any S4
turn/marker count should be taken from a frozen snapshot, as S5 already does.

- Script now takes `--sessions` (and `--window-open/--window-close`); current
  sha256 `a8a7b35e09e254871bc1a3cf86e89db4db1e2e168b5fb819968c65f2f44345ac`.
- Frozen S4 readiness: `.../sealed-s4-frozen-recheck-20260912/readiness.json`
  sha256 `7e5119ffc95e6c4241de1fb0526ef2d20f61032f626a262f07711c6558383569`
- Frozen input: `.../experiment_20260912_s5/frozen-s4-20260912/`.

---

## Real S6 receipts passed to the builder (integration)

Re-ran the frozen S4 sessions with the **actual committed S6 receipts**
(`--scan item4-s6-scripted-run.txt --scan item4-s6-run2-post-supersession.txt`):

| | value |
|---|---|
| in-window turns | 134 |
| turns with a record_set (supported) | **129** |
| unsupported (predate the earliest receipt) | **5** |
| markers == raw | 376 == 376 |
| B7 / leak scan | PASS / PASS |

The real receipt format parses cleanly through `load_record_sets` — no crash,
correct `record_set` assignment — so the synthetic record-set power check
(`ASSAY-POWERCHECK-S4-RECORDSET.md`) is confirmed against the committed emitter.
The broken v1 first-run receipt (a traceback, preserved as history) was
intentionally not passed.

- Script now also takes `--scan`; current sha256 `6f4143fcf5e10428a9e52a57e45eb59af395a8a5e57dd66fbfd2ffb472faf7a6`.
- Result: `.../sealed-s4-realscan-recheck-20260912/readiness.json`
  sha256 `3085432cb10f92d5456d598f4b75197b8a1413c5362b3fe14aaa0b2da39ba26c`

---

## Addendum — 2026-09-13 (fresh sealed dry-run, true window open)

Re-ran `s4_window_readiness_recheck.py` (sha `6f4143fc…`) against the live
worker-pi sessions, bounded to the **true window open**
(`--window-open 2026-09-12T18:05:00+00:00`), with the committed builder
(sha `96904d8a…`, unchanged) and `packet_leak_scan.py` (sha `1fc8e6c9…`).

| | value |
|---|---|
| sessions | **20** |
| in-window turns | **252** |
| markers == raw memory-traffic | **497 == 497** |
| B7 self-test | **all PASS, 0 failures** |
| `packet_leak_scan` on emitted packets | **PASS** |
| `EXCLUDED-unsupported-state` | 252 (all — no `--scan` receipts passed) |

The window has grown from 19 sessions / 135 turns (2026-09-12 22:4x recheck) to
20 / 252 in-window, ~1.9×, and the count-parity + no-substance-leak properties
still hold. The B7 count-parity blindness caveat still applies (builder
unchanged `96904d8a…`); `packet_leak_scan` is the substantive, fail-closed check
here and it passes on the fresh real packets. This is a readiness signal, not an
S4 result: no fire-log content read, no rulings, no packet text reported.

- Receipt: `.../sealed-s4-readiness-recheck-20260913/readiness.json`
  sha256 `7ba8ec628a6f7ba9af60051d325a3319213a9912e0bebd98b0cbbc030b85638d`

---

## Fix — zero-parse fail-open in this aggregator (Alice second-check; owner Assay)

Alice's `ALICE-S4-READINESS-SECONDCHECK.md` reproduced every frozen number and
found one low latent defect: a builder that printed the B7 `PASS` verdict but
whose counts line missed the aggregator's regex produced `total_turns=0`,
`b7_all_pass=true`, `leak_scan=PASS`, **rc 0** — a format break read as clean
readiness (the legacy `fails == 0 and total_markers == total_raw` predicate is
vacuously true on `0 == 0`).

**Fixed in `s4_window_readiness_recheck.py`:**
- a per-session counts match is now required; a miss increments
  `counts_parse_failed` and the session row records `counts_parsed: false`;
- `b7_all_pass` requires `counts_parse_failed == 0` **and** `total_turns > 0`,
  so a zero-parse or zero-session run is an instrument failure, not a pass;
- added `--builder` (default unchanged) so the aggregator can be driven against
  stub builders without editing the script.

**Power check — 4/4** (`s4_readiness_aggregator_power_check.py`, stubs, no live
sessions):

| case | rc | result |
|---|---:|---|
| unparseable counts + `PASS` verdict | **1** | `counts_parse_failed=1`, `b7_all_pass=false` (legacy predicate *would* have passed) |
| parseable counts + `PASS` | 0 | `b7_all_pass=true` |
| parseable counts + `FAIL` verdict | 1 | `b7_failures=1` |
| zero sessions | 1 | `total_turns=0`, `b7_all_pass=false` |

**Regression on the frozen snapshot** with the fixed script (Alice's stable
input, `experiment_20260912_s5/frozen-s4-20260912/sessions`,
`--window-open 2026-09-12T18:05:00+00:00`): 19 sessions / **134** in-window
turns / **376 == 376** markers / B7 PASS / leak PASS, `counts_parse_failed=0`,
rc 0 — matching her independent re-run.

**Hash supersession:** script `6f4143fc…` → **`d7ad7a5d…`**. Prior sealed
receipts remain valid for the runs that produced them (the fix only changes the
parse-failure path); future runs cite the new sha.

- Power check: `.../sealed-s4-readiness-recheck-20260913/aggregator_powercheck.json`
  sha256 `00a23df5ea6d7c7cc72d2fce931c2035904f74cfdbae0c0b906f9931666e6e09`
- Frozen regression receipt: `.../sealed-s4-readiness-recheck-20260913/frozen_regression_fixed.json`
  sha256 `26d48217c9ec2a899d1793633cb38a1256f0b7b37a78df167a464932dde88bcf`

---

## CORRECTION — leak-scan PASS claims were a no-op (2026-09-13)

While integrating the newly-gated builder (row 26, builder `96904d8a…` →
`6616c48e…`), I found this aggregator scanned `out/packets/` while the builder
writes packets to `<out>/turn-NNN.json`. **The scan never ran**, so every
`packet_leak_scan … PASS` in this document was a false PASS by construction —
including the addendum above. **Retracted as evidence of clean packets.**

After the fix (scan `<out>/turn-*.json`; surface `builder_rc` /
`builder_leak_scan`; require `builder_gate_failed == 0`) the truthful signal is
**not clean**:

```
frozen snapshot, 19 sessions: builder_gate_failed 4 · leak_scan_verdict FAIL
b7_all_pass false · rc 1 (134 turns / 376 == 376 unaffected)
```

4 of 19 frozen sessions carry unredacted non-user substance; the builder's own
gate and my corrected scanner flag the same sessions. Details, power check
(7/7), and the rater-blinding stop item are in
`team/ASSAY-S4-LEAKSCAN-PATH-BUG-FIX.md`; corrected receipt
`sealed-s4-gated-recheck-20260913/readiness_fixed.json` sha256 `9286a1359da9…`.
**Do not hand frozen-snapshot packets to a rater; re-run the gated builder at
close and stop on nonzero.**
