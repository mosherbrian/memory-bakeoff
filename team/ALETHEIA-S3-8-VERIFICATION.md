# S3-8 verification — Campaign-1 window report FINAL (verifier: Aletheia/Alice, `worker-glm-dsh`)

**Row:** QUEUE S3-8 · **Artifact:** `team/WINDOW-REPORT-campaign-1-20260915.md` (FINAL block §2) + close-dir
`~/acp-pi/s5-final-20260915/` · **Producer:** muse-drafter; close run by Cairn (close owner, §6) · **Date:** 2026-09-16
**Cost:** $0, local. **Independence:** I did not author the report or the run (Cairn reproduced the FINAL run;
neither of us is the named verifier). Verifier-of-record Verity is furloughed — this closes the gap.

## Method (re-derived from source, not from the report's own summary)
1. Recomputed every §2 FINAL aggregate directly from the raw `pairs.json` (medians, flags, provisional).
2. Re-ran the frozen harness to a fresh dir — `python3 …/scripts/experiment_20260912_s5/s5_pairing.py --final
   --window-start 2026-09-12T18:05:00Z --window-end 2026-09-16T00:00:00Z --token-metric sum --out
   /tmp/opencode/s5-verify` (script sha256 `eb01800c…`, rc 0) — and diffed against the committed close-dir.
3. Read the raw class/exclusion counts out of the run's `meta`.

## Result — FINAL block reproduced exactly (PASS)

| §2 FINAL quantity | Report | My recompute | Match |
|---|---|---|---|
| n pairs | 120 | 120 | ✓ |
| median token Δ% (`sum`) | +77.4% | +77.442% (mem 276,409.5 vs no-mem 157,692.0) | ✓ |
| token flagged (±25%) | 104/120 | 104/120 | ✓ |
| median wall Δ% (secondary) | +147.6% | +147.558% (mem 48.33 s vs no 18.06 s) | ✓ |
| wall flagged | 111/120 | 111/120 | ✓ |
| provisional pair(s) | 1 (pair 6) | 1 — pair 6, family `unclassified@2026-09-12` | ✓ |
| alt `tokens_end` (transparency only) | +3.6%, 79/120 | +3.595%, 79/120 | ✓ |
| population | 878 turns; MEMORY 121 / NO-MEMORY 735 / excl 22 | identical; excluded reasons 8+13+1=22 | ✓ |

**Determinism / provenance:** the fresh run's `pairs` list, `summary`, `excluded`, `unpaired_memory`,
`unpaired_nomem`, and `families.effective.json` are **identical** to the close-dir; the `S5-REPORT.md`
body (everything after the header) is **byte-identical**. Only two header fields differ: `generated_at`
(by construction) and "session files scanned" **35 → 36** — a post-window session file appeared after
the close. It contributes **0 in-window turns**; the 878/121/735/22 population and all pairs are unchanged.

## Findings
1. **[CORRECTED — I missed this; Assay's verification caught it first] F1 (material, not cosmetic): the
   window label contradicts the pin.** §1 says the window is pinned "at midnight local (end of calendar
   day 2026-09-15)", but the run's `--window-end` is `2026-09-16T00:00:00Z` = **2026-09-15 17:00 PDT**
   (host TZ is PDT −0700). Midnight local would be `2026-09-16T07:00:00Z` — **7 h later**. So the window
   closed ~7 h early vs its own label and excludes the final 7 h of the local Sep-15 day (that is exactly
   the post-close session file my re-run saw appear: 35 → 36 scanned). The §2 numbers are faithful to the
   *pinned* bounds; the §1 prose is wrong. Any external quote must use the actual Z bounds, and §1 needs
   fixing before it travels. (Confirmed independently: `datetime` PDT math.)
2. **F2 (cosmetic): session count is a live-dir fingerprint, not pinned.** §1's "35 sessions" is the
   close-time scanned count; a re-run sees 36 (post-window file) with no in-window change. Cite the
   frozen `session-manifest.json`, or say "scanned at close".
3. **Provisional pair 6 sits in `unclassified@2026-09-12`** — the one pair outside the
   `trial-cycle-tick@…` families §5 caveats about; name the family to make "coarse family" concrete.
4. The report's §3/§4/§6 quotes (S6 receipt, provenance hashes, close command) are consistent with the
   close-dir and `BOARD.md` 2026-09-15 21:2x; I did not re-run S6 or re-hash the frozen extension
   (out of scope for the S5 number and not what S3-8 claims).

## Verdict
**PASS on the numbers as pinned; §1's window label is defective (F1) and must be corrected.** The §2 FINAL
block reproduces to the reported precision and the run is deterministic (`S5-REPORT.md` body
byte-identical), arm-unfavorable direction stated as such — descriptive-only, no score import.

**Attribution:** Assay's `team/ASSAY-S3-8-VERIFICATION.md` (2026-09-16) is the row's verification-of-record
here and it landed before mine; it found F1, which my first pass missed. This receipt is therefore an
**independent corroboration**, not the primary verdict — and a duplicate-work instance of the RETRO-3
"one-writer/one-verifier-per-row" blind spot: the row was already being verified the moment I started.
Net: goal-3 is verified; the deliverable needs the §1 label fixed before it is quoted.

— Aletheia (Alice), `worker-glm-dsh`. $0, no new work beyond this verification.
