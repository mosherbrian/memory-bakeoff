# Campaign-1 window report — CORRECTED (QUEUE S4-9; supersedes the 20260915 FINAL block)

**Author:** kiln-flash (S4-9) · **Date:** 2026-09-16 · **Cost:** $0, local
**Verifier:** corvid-dsh · **Supersedes:** the FINAL block of
`WINDOW-REPORT-campaign-1-20260915.md` (S3-8 finding F1: window closed 7 h
before its own label). That report carries a supersession banner pointing here.

## 1. The window, declared once (machine-read)

**`team/WINDOW-campaign-1.json`** is the single declaration:

- `start_utc` **2026-09-12T18:05:00Z** · `end_utc` **2026-09-16T07:00:00Z**
  (84.917 h) — tz America/Los_Angeles.
- Every human label is *derived from* those instants by the file's generator:
  close = midnight PDT ending Tuesday 2026-09-15 ("Tuesday EOD"), start =
  2026-09-12 11:05 PDT. Labels are never hand-written again.
- Why 07:00Z: the original §1 label said "midnight local (end of calendar day
  2026-09-15)" but pinned `2026-09-16T00:00:00Z`, which is **17:00 PDT Sep 15**
  — the label stated the intent, the instant was miscomputed (S3-8 F1). The
  corrected instant is `2026-09-16T00:00:00-07:00` converted to UTC.

## 2. Input pin (S3-8 F2 rule: frozen list, not the live folder)

- Frozen snapshot: `~/acp-pi/s5-final-windowfix-20260916/frozen-input/`
  (`s5_freeze_inputs.py`, freeze-on-read), **37 session files**, per-file
  sha256 in `INPUT-MANIFEST.json`, whose own sha256 is
  **`0f89ca5a0cda4b21b252db736f4b801b309f46db45f7e43932283303e04303ee`**.
- The re-run read the frozen tree (`--sessions …/frozen-input/sessions`), so
  reproducing this run uses these bytes, not the live folder.
- Run (2026-09-16, as-of 17:18:39Z):
  `s5_pairing.py --final --sessions ~/acp-pi/s5-final-windowfix-20260916/frozen-input/sessions --window-start 2026-09-12T18:05:00Z --window-end 2026-09-16T07:00:00Z --token-metric sum --out ~/acp-pi/s5-final-windowfix-20260916/run`
  Output: `summary.json` / `pairs.json` / `S5-REPORT.md` / `turns.csv` in that dir.

## 3. Corrected numbers (and what they supersede)

| metric | superseded run (end 00:00Z = 17:00 PDT) | **corrected run (end 07:00Z = midnight PDT)** |
|---|---|---|
| turns in window | 878 (MEMORY 121 / NO-MEMORY 735 / excl 22) | **961 (MEMORY 123 / NO-MEMORY 815 / excl 23)** |
| matched pairs (n) | 120 | **122** |
| tokens median Δ% (memory over) | +77.442% | **+80.739%** (mem 278,919.5 / nomem 157,692.0) |
| token-flagged pairs | 104/120 | **106/122** |
| wall median Δ% | +147.558% | **+149.233%** (48.79 s / 17.90 s) |
| wall-flagged pairs | 111/120 | **113/122** |
| alt token metric (final) median Δ% | +3.594% | **+3.595%** |

**Reading (descriptive only; arm-unfavorable, unchanged in direction):** the
extra 7 hours add 83 in-window turns and 2 pairs; the matched-pair token delta
moves from +77.4% to **+80.7%** — slightly *stronger* against the memory arm.
All S3-8 caveats travel: pair identity is reported, the family key is coarse,
memory turns carry the perseus `recall/remember/confirm` tool round-trips, and
`--window-end` bounds a turn's start, not its completion (freeze docstring).

## 4. For Brian — the result-fate decision, on corrected numbers

The options are unchanged in shape; only the numbers move:

1. **Publish as-is** — the corrected descriptive result is *memory-arm-negative
   and slightly stronger than first reported* (+80.7% tokens, +149% wall).
2. **Leaner recall** — the mechanism suspect remains the recall round-trips;
   a leaner-recall arm is the obvious campaign-2 change.
3. **Gate campaign-2** — hold until the invocation-side results (S4-10/S4-12)
   land, so campaign-2 design sees both instruments.

Quote the corrected table only; the +77.4% headline is **unquotable-as-run**
(marked in the original report). Input snapshot for any reproduction:
the frozen tree above, pin `0f89ca5a…`.

— kiln-flash, 2026-09-16
