# CORVID-S4-9-VERIFY.md — corvid-dsh verification of QUEUE row S4-9

**Verdict: PASS** — 2026-09-16 14:45 PDT. kiln-flash authored; corvid-dsh
verifies (independence holds). This row gates Brian's result-fate call, so it
was verified first and most deeply.

## Declared check

`test -f team/WINDOW-campaign-1.json` → rc 0. (The check is intentionally
thin — existence of the single declaration file — so the substantive review
below is the real verification.)

## Window correctness (the S3-8 F1 class)

- `WINDOW-campaign-1.json` declares absolute UTC instants once
  (2026-09-12T18:05:00Z → 2026-09-16T07:00:00Z, 84.917 h) and derives every
  human label from them; the derivation note names the generator, and the
  labels are arithmetically consistent (07:00Z = 00:00−07:00; the superseded
  00:00Z pin = 17:00 PDT Sep 15 — the 7-hour error is real and correctly
  explained).
- The original report (`WINDOW-REPORT-campaign-1-20260915.md` :103) carries
  the **unquotable-as-run** banner with original text retained; the corrected
  report marks the +77.4% headline unquotable. Supersession chain intact.

## Input pin (the S3-8 F2 rule)

`~/acp-pi/s5-final-windowfix-20260916/frozen-input/INPUT-MANIFEST.json`
re-hashed this pass: `0f89ca5a…303ee` — exact match to the report's pin. The
run summary's `meta.sessions` points into the frozen tree (37 sessions), not
the live folder.

## Corrected numbers recomputed from the run outputs

From `~/acp-pi/s5-final-windowfix-20260916/run/{summary.json,pairs.json}`
directly:

| Report claim | Recomputed | Match |
|---|---|---|
| 961 turns in window (MEMORY 123 / NO-MEMORY 815 / excl 23) | 123+815+23 = 961, class_counts + excluded_count exact | ✓ |
| n=122 pairs | 122 | ✓ |
| tokens median Δ% +80.739% (mem 278,919.5 / nomem 157,692.0) | 80.7387 / 278,919.5 / 157,692.0 | ✓ |
| flagged 106/122 tokens; 113/122 wall | 106; 113 | ✓ |
| wall median Δ% +149.233% | 149.2334 | ✓ |
| alt token metric +3.595% | 3.5947 (tokens_end) | ✓ |
| run as-of 17:18:39Z | meta.generated_at exact | ✓ |

Independent corroboration: my S4-13 verification recomputed the same medians
from `pairs.json` by a different path — identical values.

## Verdict

The corrected table is real, pinned, and reproducible; the window defect and
its repair are both arithmetically sound. Brian's decision (publish as-is /
leaner recall / gate campaign-2) now has a quotable basis. Row S4-9 moves
done → **VERIFIED (PASS)**. corvid-dsh, 2026-09-16 14:45 PDT.
