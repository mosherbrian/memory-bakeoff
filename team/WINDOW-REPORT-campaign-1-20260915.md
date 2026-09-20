# Campaign-1 trial window report — close-day draft (QUEUE S3-8)

**Author:** muse-drafter (Spark), Assay-lane staffing of the unowned goal-3 report row
**Date:** 2026-09-15 (window closes EOD today) · **Cost:** $0, local
**Verifier:** Verity. **Claim ceiling:** descriptive, local-arm, no score import.

> **Status label:** the **authoritative FINAL close run** (`s5_pairing.py --final`)
> has been executed (Cairn, 2026-09-16T02:22Z, close-dir `~/acp-pi/s5-final-20260915/`).
> §2 carries the FINAL numbers; the PREP preview is retained below it for audit.
> Any external quote uses the FINAL block.

## 1. Window

- **Bounds:** `[2026-09-12T18:05:00Z, 2026-09-16T00:00:00Z)` — window-close is
  **Tuesday EOD**, pinned at midnight local (end of calendar day 2026-09-15);
  the pin is a close-owner choice, disclosed here.
- **Token metric:** `usage_total` — the **pinned sum** (per `S5-INTERPRETIVE-NOTES.md`,
  conductor pin at the S5 freeze).
- **Population (FINAL):** 878 turns in window; classes **MEMORY 121 / NO-MEMORY 735
  / excluded 22**; 35 sessions. (Excluded = the frozen unsupported-state/stalled
  classes, counted separately per rule.)
- **Population (PREP, audit):** 794 turns; MEMORY 118 / NO-MEMORY 654 / excluded 22;
  33 sessions.

## 2. S5 pairing — **FINAL** (authoritative close run, descriptive)

| quantity | FINAL value |
|---|---|
| n pairs | **120** |
| median token delta% (MEMORY vs NO-MEMORY) | **+77.4%** (mem 276,409.5 vs no-mem 157,692.0 tokens, pinned sum metric) |
| pairs flagged (±25%, token) | **104 of 120** |
| median wall delta% (secondary) | **+147.6%** (mem 48.33 s vs no-mem 18.06 s); 111 of 120 flagged |
| provisional pair(s) | 1 (pair 6) |
| alt metric `tokens_end` (transparency only, not a candidate) | +3.6% median, 79 of 120 flagged |

Run: `s5_pairing.py --final --window-start 2026-09-12T18:05:00Z --window-end
2026-09-16T00:00:00Z --token-metric sum --out ~/acp-pi/s5-final-20260915` (2026-09-16T02:22Z).
Full n-pairs table: `~/acp-pi/s5-final-20260915/S5-REPORT.md`; summary `summary.json`.

### PREP preview (audit, superseded by FINAL above)

| quantity | PREP value |
|---|---|
| n pairs | **117** |
| median token delta% (MEMORY vs NO-MEMORY) | **+75.0%** (memory turns used more tokens under the pinned sum metric) |
| pairs flagged (±25%) | **113 of 117** |
| provisional pair(s) | 1 (pair 6) |

Reading: under the frozen same-family nearest-in-time rule, matched MEMORY turns
**used substantially more tokens** than their NO-MEMORY partners in this window.
This is descriptive only and arm-unfavorable; it is consistent with memory turns
carrying the extra perseus `recall/remember/confirm` tool round-trips. **Pair
identity and the coarse-family caveat must travel with it** (all pairs sit in the
`trial-cycle-tick@<date>` family — see §5).

## 3. Safety / lifecycle (from window receipts, not this run)

- **S6 scan-after-write:** last receipt (WINDOW-OPENING, 2026-09-13 ~08:4x):
  **13 active rows all cli-write and recall-visible, 3 deprecated expected-absent,
  0 unsanctioned transitions, 0 demotions.** Script run as committed.
- **T0 tier:** live and proven end-to-end (Cairn, config → behavioral →
  stored-state → delivery); first self-capture `record-073e444c`, 0 demotions.
- **Burden at opening:** the first T0 capture cost Brian **0 confirms**.

## 4. Provenance (frozen at window open; unchanged)

| artifact | value |
|---|---|
| Extension lineage | A1-amended `2e247bb`: `index.ts 24296ad6…`, `vault.ts 905f604c…`; other five files byte-identical to `060d842`; suite 47/47 |
| Perseus binary | `c8a222ec…` (2.23.2, pinned) |
| S4 adjudication rule | `team/S4-ADJUDICATION.md` sha `8856d101…` |
| S5 rule | frozen draft in `WINDOW-OPENING.md` §(2) + `S5-INTERPRETIVE-NOTES.md` (tokens = sum) |

## 5. Caveats / limits (required)

1. **FINAL run executed** (2026-09-16T02:22Z); the PREP preview is retained for
   audit only. The window-end pin (midnight local) is a close-owner choice —
   turns after 2026-09-16T00:00:00Z are outside the window by construction.
2. **Family coarseness.** Nearly all pairs are in one `trial-cycle-tick@<date>`
   family; the pairing rule pairs nearest-in-time across classes, so pair identity
   is reported and the family key is coarse. Descriptive only; no causal claim.
3. **Token metric is arm-unfavorable by design** (pinned `sum` before further
   data accumulated) — the direction is against memory, and it is reported as such.
4. **No retrieval-quality claim** here; this report is goal-3 outcome-side
   descriptive only.

## 6. Close procedure — DONE

```
# executed by Cairn 2026-09-16T02:22Z (close owner per this section):
python3 implementer/repo-glm-dsh2/scripts/experiment_20260912_s5/s5_pairing.py --final \
  --window-start 2026-09-12T18:05:00Z --window-end 2026-09-16T00:00:00Z \
  --token-metric sum --out ~/acp-pi/s5-final-20260915
# FINAL block pasted into §2 above; Verity verifies.
```

$0, local. FINAL freeze performed. — muse-drafter (Spark), close run by Cairn

---

## SUPERSEDED WINDOW PIN (2026-09-16, QUEUE S4-9) — read before quoting

The §1 bound and the FINAL block of this report are **unquotable-as-run**: the
pin `2026-09-16T00:00:00Z` is 17:00 PDT Sep 15, not the "midnight local" the
same line declares — the window closed 7 h before its own label (S3-8 F1,
found by Assay). The corrected window, input pin, and numbers live in
`team/WINDOW-REPORT-campaign-1-CORRECTED-20260916.md`, declared once in the
machine-read file `team/WINDOW-campaign-1.json` (end **2026-09-16T07:00:00Z**),
input pin `0f89ca5a…` (37-session frozen snapshot). Quote only the corrected
table. The original text above is retained verbatim for audit.
— kiln-flash, S4-9, 2026-09-16
