# Rival reviews

Verbatim output from the team-of-rivals pre-flight (`~/rivals/review-generation`).
Both models read this repository themselves through Pi, blind to each other, and
each declares its own verdict token on line 1. Committed so that attribution in
the handoff is checkable against an artifact rather than asserted.

- `20260906-004659/` - review of Gen114. Both found the temporal reconciliation
  and the recency-cue asymmetry that Gen115 went on to confirm.
- `20260906-011828/` - review of Gen115. Both returned `DEFECTS_MINOR`; the loop
  decided FIX FIRST. Their defects are repaired in `results/gen115/attempt4`.
