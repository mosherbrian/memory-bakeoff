# Assay — S4 builder B7 leak gate: validated patch + power check (register #1)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-13 (R&D pulse) · **Cost:** $0, offline
**Finding:** `ASSAY-POWERCHECK-S4-B7.md` + register #1 (high: S4 blinding assurance)
**Prior artifacts:** `packet_leak_scan.py` (standalone checker), `s4_b7_power_check.py` (gap demo)

## Defect

The committed `build_s4_packets.py --self-test` asserts
`marker_count == raw_memory_traffic`; both sides use the same
`is_memory_traffic` predicate, so a classification miss lowers both counts
equally and the self-test **PASSes while substance leaks**. The standalone
`packet_leak_scan.py` proves the gap but is not wired into the builder.

## Fix (`s4-b7-leak-gate.diff`)

Adds an emitted-packet leak scan to the builder itself, using the same rules as
the validated `packet_leak_scan.py`:

- `LEAK_CANARIES = SENTINELS + ("key=record-", "draft_id", "confirmation_code")`;
- per emitted packet, `packet_leaks()` flags non-user entries that are not
  redacted **and** carry a sentinel/canary, and user turn-start entries
  carrying a draft secret;
- the summary prints `LEAK-SCAN (emitted-packet substance): PASS/FAIL`, and the
  gate exits nonzero on any leak (with `--self-test`, both count parity **and**
  leak-scan must hold).

**No packet bytes change** — the scan is read-only over the emitted JSON — so
it is safe for already-built packets; it only adds output and fails the exit
code when a leak exists.

## Power check (real builder, synthetic sessions)

| Run | self-test | LEAK-SCAN | rc | leaked canaries in packets |
|---|---|---|---|---|
| canonical, leaky session | **PASS** | (absent) | 0 | `key=record-secret-xyz`, `key=record-novel`, `[perseus-maint]` |
| guarded, leaky session | PASS | **FAIL** (2 findings) | **1** | same (now caught) |
| canonical, clean session | PASS | (absent) | 0 | none |
| guarded, clean session | PASS | **PASS** | 0 | none |

The guarded leaky run shows the point precisely: **count parity still PASSes
and the leak scan is the check that fails**. Checks block: all `true`,
failures `[]`.

**Applied-file evidence:** the diff `git apply --check` rc 0 against a fresh
copy of canonical; the applied file is **byte-identical** to
`build_guarded(canonical)`; direct runs of the applied file: leaky → rc 1 /
LEAK-SCAN FAIL, clean → rc 0 / LEAK-SCAN PASS.

## Apply note (owner decision, not self-applied)

Canonical builder sha `96904d8a…`. The S4 window is live, so applying mid-window
changes the instrument hash and needs the usual re-freeze receipt. Unlike the
S6/R2H patches this one is **fail-closed and byte-preserving**: it cannot alter
an emitted packet, only refuse-to-PASS when substance is present. Recommended
for the next verifier revision / before any new packets are handed to the
rater. Standalone `packet_leak_scan.py` stays as the independent entry-level
check (two implementations, same rules — the builder copy is the gate).

## Receipts

- Patch: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/s4-b7-leak-gate.diff`
  sha256 `5469a56c3a610bd376c2faa6459a8db2284b81b057da1dde1df5beddb75d8b2e`
- Power check: `.../s4_b7_leak_gate_power_check.py`
  sha256 `9d32efa997ff7a5fa497180d18df77d368f269c9dbf2535bcba2a00437dbc3d8`
- Sealed result: `.../sealed-s4-b7-leak-gate-20260912/result.json`
  sha256 `a4948be7ad902ce4c7a07cd45890cb8e775244d280b7054b6a35c6c60feaf341`
- Applied-file check: `.../sealed-s4-b7-leak-gate-20260912/applied-file-check.json`
  sha256 `fdb9446a53431dc3016607069c1665164f9da9b5af0dea93616a5107b9fe8167`
- Re-run: `python3 scripts/verify-20260912-assay-row1/s4_b7_leak_gate_power_check.py`

## Limits

- Canary vocabulary is the builder's own sentinel set plus `key=record-`; an
  unknown memory marker that is neither a sentinel nor a canary still escapes
  both the predicate and this scan (the same limit stated on
  `packet_leak_scan.py`).
- Synthetic sessions only; `EXCLUDED-unsupported-state` is nonzero because no
  `--scan` receipts are passed, which does not affect the leak logic.
- The scan reads the serialized `entries`, not `record_set` metadata, by
  design (mirrors the standalone checker).
