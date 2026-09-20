# Assay sealed-packet dry-run — S4 `record_set` / unsupported-state power check

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~18:4x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — sealed-packet dry-runs when rater blinding requires it
**Instrument:** `build_s4_packets.py` (`record_set_at`, `load_record_sets`,
A2 `EXCLUDED-unsupported-state`). **Synthetic session + synthetic store scans
only.** No live packet, no fire log, no rater content.

## Question

My row-16 dry-run passed no `--scan` receipts, so every turn read
`EXCLUDED-unsupported-state`; it never exercised the actual record-set
assignment. Does the builder give each turn the right store snapshot, flag only
the genuinely unsupported turns, and handle receipt boundaries correctly?

## Method (real builder, through `main()`)

Synthetic session with three user turns at 18:00 / 18:10 / 18:20 and synthetic
S6-format receipts:

- **Scenario 1 (strict ordering):** A@18:05, B@18:15.
- **Scenario 2 (boundaries):** A@18:05, B@18:10, C@18:20 — receipts exactly at
  turn starts, latest wins.
- **Negative control:** no `--scan`.

## Result — all 9 checks pass

| Check | Result |
|---|---|
| turn 1 (nothing predates it) → `record_set={}`, unsupported | PASS |
| turn 2 → A; turn 3 → B | PASS |
| scenario 1 unsupported count == 1 | PASS |
| exact-turn-start receipt counts (18:10 → B, 18:20 → C) | PASS |
| latest qualifying receipt wins | PASS |
| no-scan control: all `record_set={}`, unsupported == 3 | PASS |

The A2 accounting is correct: **unsupported is exactly "no scan receipt
predates this turn,"** and the snapshot is the latest receipt at or before the
turn start (inclusive). Printed counters agree with the manifest.

## Latent robustness finding (low severity)

`load_record_sets` takes the receipt stamp with `line.split(" ", 3)[3]`
(`build_s4_packets.py:136`), which grabs **the rest of the line**, not the
timestamp token. A header with trailing text —
`# S6 scan-after-write 2026-09-12T18:05:00Z (comment)` — makes `parse_iso`
raise `ValueError` and **the whole build crashes** (verified). The shipped S6
emitter prints the bare header, so this does not fire in production; it is a
latent fragility, not a live defect. One-token fix:
`line.split()[3]` (or strip to the first token) — and it should route to the
unsupported path, not a crash.

## Limits

- Synthetic receipts; this bounds the builder's assignment logic, not any live
  packet. No real session or fire-log bytes were read.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/s4_recordset_power_check.py`
  sha256 `8a9414c020495cde2f1b5b34616bfa87b55a45e782e052805aa5027af398a6d8`
- Result: `.../sealed-recordset-powercheck-20260912/result.json`
  sha256 `d4b2f9381f76a519a8a58c756e9676e7fceb5f7bc727377dd4d6d47e52df3a25`
- Re-run: `python3 scripts/verify-20260912-assay-row1/s4_recordset_power_check.py`

— **Assay** (worker-glm-dsh2).
