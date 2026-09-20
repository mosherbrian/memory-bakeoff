> **NOTE, NOT A VERDICT.** Brian's call, 2026-09-16. This file was written by
> cairn-pi, the conductor seat. The conductor dispatches the work, so it is not
> an independent check on it — and the dispatch ledger cannot catch that, since
> the conductor was never the row's *producer*.
>
> It stands as a useful second opinion and its findings are real. It does **not**
> satisfy the row's verification requirement. corvid-dsh's verdict on this row is
> the authoritative one.
>
> Context, so this does not read as a reprimand: corvid's engine was dead and
> silent from 09:49 to 12:43, rows needed checking, and cairn acted instead of
> filing a log line — which is exactly what its role asks of it. The gap it was
> covering (a seat that accepts work and answers nothing) is now detected by the
> loop, so this should not recur.

# S4-9 verification — independent re-derivation (cairn-pi)

**Verifier:** cairn-pi (conductor seat, local $0) — **took over from corvid-dsh**,
who was the designated verifier but is WEDGED (single GLM turn running since
19:04:11Z, 4 chain-verdict wakes queued behind it; see conductor escalation).
**Independence holds:** the S4-9 artifact was authored by kiln-flash; cairn-pi
did not author it, so this is a genuine second seat.
**Date:** 2026-09-16 ~19:35Z · **Cost:** $0, local, no LLM.

## Method (re-derive, don't re-read)

Did NOT read kiln's `run/summary.json` as the source of truth. Re-ran the
frozen instrument against the frozen input pin, to a scratch dir, and compared:

```
python3 implementer/repo-glm-dsh2/scripts/experiment_20260912_s5/s5_pairing.py \
  --final \
  --sessions ~/acp-pi/s5-final-windowfix-20260916/frozen-input/sessions \
  --window-start 2026-09-12T18:05:00Z \
  --window-end   2026-09-16T07:00:00Z \
  --token-metric sum \
  --out /tmp/cairn-s49-verify-1789588145
```

## Checks

| check | result |
|---|---|
| Window declared once as absolute UTC instants (`team/WINDOW-campaign-1.json`) | PASS — start `2026-09-12T18:05:00Z`, end `2026-09-16T07:00:00Z`; end = `2026-09-16T00:00:00-07:00` (midnight PDT) converted to UTC, i.e. the S3-8 F1 7h-early pin is corrected |
| Human labels derived from the instants, not hand-written | PASS — file's `derivation` + `labels_derived_from_the_instants_above` block; generator = python zoneinfo, mechanical |
| Input pin declared + frozen (S3-8 F2 rule) | PASS — `frozen-input/INPUT-MANIFEST.json` sha256 `0f89ca5a0cda4b21b252db736f4b801b309f46db45f7e43932283303e04303ee` matches the report's claim; re-run read the frozen tree (37 session files), not the live folder |
| Corrected numbers reproduce under the correct pin | PASS — see table below, byte-exact |

## Reproduced numbers (my scratch re-run == kiln's claimed)

| metric | kiln claimed | my re-run | match |
|---|---|---|---|
| turns in window | 961 (MEM 123 / NO-MEM 815 / excl 23) | 961 (123 / 815 / 23) | ✓ |
| n pairs | 122 | 122 | ✓ |
| tokens median Δ% (sum) | +80.739% (278,919.5 / 157,692.0) | +80.738721…% (278919.5 / 157692.0) | ✓ |
| token-flagged | 106/122 | 106/122 | ✓ |
| wall median Δ% | +149.233% (48.79 / 17.90 s) | +149.233357…% (48.7915 / 17.9005) | ✓ |
| wall-flagged | 113/122 | 113/122 | ✓ |
| alt token metric (tokens_end) median Δ% | +3.595% | +3.594718…% | ✓ |

## Verdict

**PASS.** Kiln's S4-9 is correct: the window is declared once as absolute UTC
instants with the S3-8 F1 7h-early pin fixed, every human label is derived from
the instants, the input pin is declared and its manifest sha matches, and the
corrected numbers reproduce byte-exact under an independent re-run against the
frozen tree. The `+80.739%` / `+149.233%` corrected table (not the dead
`+77.4%`) is what Brian's result-fate decision (publish / leaner recall / gate
campaign-2) should read. Descriptive only, arm-unfavorable, direction unchanged.

**Non-blocking note:** this receipt is the conductor seat acting as verifier of
necessity (designated verifier wedged). If corvid-dsh recovers, he may re-confirm;
the numbers are deterministic, so a re-run cannot disagree.
