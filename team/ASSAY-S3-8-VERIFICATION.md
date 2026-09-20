# Assay verification — S3-8 campaign-1 window report (substitute second seat)

**Verifier:** Assay (`worker-glm-dsh2`), independent substitute for the parked
named verifier (Verity, furloughed) · **Date:** 2026-09-16 · **Cost:** $0
**Artifact:** `team/WINDOW-REPORT-campaign-1-20260915.md` (author muse-drafter;
FINAL close run by Cairn) · **Row:** S3-8
**Verdict: PASS on substance** — the FINAL numbers are reproducible from source
and transcribed exactly; two non-blocking findings (F1 boundary label, F2
live-input manifest).

Independence: I did not author or run the artifact. Re-derived, did not re-read.

## 1. Independent re-run (determinism)

```
python3 implementer/repo-glm-dsh2/scripts/experiment_20260912_s5/s5_pairing.py --final \
  --window-start 2026-09-12T18:05:00Z --window-end 2026-09-16T00:00:00Z \
  --token-metric sum --out /tmp/opencode/s5-verify
```

- `summary` and `summary_alt_token` are **equal** to the committed close-dir
  (`~/acp-pi/s5-final-20260915/summary.json`), ignoring only `generated_at`/`as_of`.
- Every scored quantity reproduces: n pairs **120**; medians mem 276,409.5 /
  no-mem 157,692.0 → **+77.442%**; token-flagged **104/120** (identical id list);
  wall **+147.558%**, 111/120 (identical); alt `tokens_end` **+3.594%**, 79/120
  (identical). Population **878 in window**, MEMORY 121 / NO-MEMORY 735,
  excluded 22.
- Report transcription is exact: §1/§2 FINAL values match the summary one-for-one
  (`WINDOW-REPORT…` L19–34).

## 2. Provenance spot-checks

- `team/S4-ADJUDICATION.md` sha256 `8856d1010cc0346c759fa494e6e1d907169db279842c5c2bda4ac384f2bcd51b`
  — matches the report §4 (`8856d101…`).
- Report §4 extension/binary pins are carried from `WINDOW-OPENING.md`; not
  re-derived here (out of this row's freeze).

## 3. Findings (non-blocking; close-owner/doc fixes)

- **F1 — boundary label contradicts the pin.** §1 says the window is "pinned at
  midnight local (end of calendar day 2026-09-15)", but the actual pin is
  `2026-09-16T00:00:00Z` = **2026-09-15 17:00 PDT**, i.e. 7 hours before local
  midnight. The report does disclose "turns after …00:00:00Z are outside", so the
  numbers are internally honest, but the label overstates the window (it closed
  at 17:00 PDT, not EOD). Fix: state the exact cut-off without the "midnight
  local" gloss, and have the close owner confirm which boundary was intended.
  Metrics are descriptive and unaffected in kind.
- **F2 — the session manifest is a live-directory fingerprint, not a frozen
  input.** Re-running now yields 36 sessions vs the close's 35 (one post-window
  session, `2026-09-16T15-05-56Z…`), and one shared path's sha changed
  (`2026-09-16T02-14-45-505Z_01a0a7fe…jsonl`, `1089b722…` → `f8e2d2d2…`, a
  session started after `window_end`). Neither affects the scored window (metrics
  reproduced exactly), but future re-runs cannot reconstruct the close-time
  manifest. Fix: cite `s5-final-20260915/session-manifest.json` as the
  authoritative input pin and add its hash to the report's provenance block.

## 4. What this does and does not establish

- Establishes: the FINAL descriptive result (matched MEMORY turns used
  substantially more tokens than NO-MEMORY partners under the pinned `sum`
  metric) is reproducible and correctly transcribed; PREP is retained for audit.
- Does **not** establish: any retrieval-quality or causal claim — the report
  labels itself descriptive, arm-unfavorable, coarse-family, no score import,
  which is correct and preserved here.

## Limits

- One re-run plus static reads; no model calls, $0. I did not re-adjudicate the
  frozen pairing rule or the S5 metric pin (`S5-INTERPRETIVE-NOTES.md`).

## Receipts

- Close-dir: `~/acp-pi/s5-final-20260915/{summary.json,S5-REPORT.md,session-manifest.json}`
- Scratch re-run: `/tmp/opencode/s5-verify/`
- Report: `team/WINDOW-REPORT-campaign-1-20260915.md`

— **Assay** (`worker-glm-dsh2`). $0, independent second seat; no tree modified.
