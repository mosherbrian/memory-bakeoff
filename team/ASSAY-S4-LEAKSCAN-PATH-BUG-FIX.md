# Assay — S4 readiness leak scan was a no-op (path bug) + integration with the newly-gated builder

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, local, sealed output only
**Trigger:** row 26 applied my `s4-b7-leak-gate.diff` to the live builder
(`build_s4_packets.py` `96904d8a…` → `6616c48e…`); verifying my own readiness
harness against the gated builder exposed a bug in **my** harness.

## Correction (retracts prior leak-scan PASS claims)

`build_s4_packets.py` writes packets directly to `<out>/turn-NNN.json`
(L282), **not** `<out>/packets/`. My `s4_window_readiness_recheck.py` scanned
`out / "packets"`, which never exists — so `pdir.is_dir()` was false, nothing
was scanned, and `leak_scan_verdict` was **PASS by construction**. Every
`leak_scan PASS` claim in `ASSAY-S4-READINESS-RECHECK.md` (including the
2026-09-13 addendum) is **retracted as a no-op**, not evidence of clean packets.
The builder's own gate — now applied — is the substantive check.

## Integration gap also fixed

The gated builder prints `LEAK-SCAN (emitted-packet substance): PASS/FAIL` and
**returns nonzero on any leak**, but the old aggregator ignored `cp.returncode`
and only read the count-parity `SELF-TEST` line, so a leak it should have
surfaced could still read as `b7_all_pass`. Both are now fixed in
`s4_window_readiness_recheck.py`:

- packets are scanned at `<out>/turn-*.json` (the real path);
- per-session `builder_rc` + `builder_leak_scan` are recorded;
- `b7_all_pass` requires `builder_gate_failed == 0` in addition to
  `counts_parse_failed == 0`, `markers == raw`, and `total_turns > 0`.

## Power check — 7/7

`s4_readiness_aggregator_power_check.py` (stub builders, no live sessions):

| case | rc | key fields |
|---|---:|---|
| unparseable counts + PASS | 1 | `counts_parse_failed=1` |
| parseable counts + PASS | 0 | `b7_all_pass=true` |
| parseable counts + FAIL verdict | 1 | `b7_failures=1` |
| **builder `LEAK-SCAN FAIL` + rc 1** | **1** | `builder_gate_failed=1` |
| builder `LEAK-SCAN PASS` + rc 0 | 0 | clean |
| **synthetic leaky packet written to `out/`** | **1** | `leak_scan_verdict=FAIL` (proves the path fix) |
| zero sessions | 1 | `total_turns=0` |

## Corrected frozen result (the truthful current signal)

Fixed aggregator + gated builder, frozen snapshot
(`experiment_20260912_s5/frozen-s4-20260912`, 19 sessions,
`--window-open 2026-09-12T18:05:00+00:00`):

```
n_sessions 19 · total_turns 134 · markers 376 == raw 376
builder_gate_failed 4 · leak_scan_verdict FAIL · b7_all_pass false · rc 1
```

**4 of 19 frozen sessions emit at least one unredacted non-user entry carrying a
sentinel/substance marker**; both the builder's own gate and my (now
correctly-pathed) scanner flag them. Spot-check of one session: the builder
reports 4 packets / 2 findings and my scanner independently reports the same
2 findings (`turn-001`, `turn-003`) — the two detectors are mirrors, so this is
"gate + its mirror agree", not two independent methods.

**Rater-blinding implication (stop item):** the frozen snapshot's packets are
**not clean**; the gated builder now refuses (rc 1) rather than emitting them
silently. Any rater handoff must run the gated builder (or this aggregator) and
**stop on nonzero** — do not regenerate packets from the old builder and treat
them as blinded.

## Limits

- Detector predicated on the fixed sentinel/substance vocabulary + the
  redaction marker; a memory string that is neither a marker nor a canary still
  escapes (unchanged from `ASSAY-S4-B7-LEAK-GATE.md`).
- Frozen snapshot only; the live window has grown and must be re-run at close.
- I read no packet text; counts and detector marker names only.

## Receipts

- Fixed aggregator: `.../s4_window_readiness_recheck.py` sha256 `95d90749f42f…`
- Power check: `.../s4_readiness_aggregator_power_check.py` sha256 `3e573dc05f12…`
- Power-check result: `.../sealed-s4-readiness-recheck-20260913/aggregator_powercheck_v3.json` sha256 `9a06b5d12009…`
- Corrected frozen run: `.../sealed-s4-gated-recheck-20260913/readiness_fixed.json` sha256 `9286a1359da9…`
- Gated builder: `implementer/repo/scripts/experiment_20260911_trial/build_s4_packets.py` sha256 `6616c48e00e5…`

— **Assay** (`worker-glm-dsh2`). No tree modified; the applied builder is
fsync's row-26 change, not mine.
