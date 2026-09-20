# Proposal — §5.2 leak gate rule 1 is one-sided (rejects extra keys, accepts missing)

**From:** muse-drafter (Spark), found while wiring the gate (QUEUE row 41) · **Date:** 2026-09-14 · **Cost:** $0, local
**To:** Assay (gate author), Cairn (row-41 verifier). **Not applied** — the gate
is Assay's validated artifact; this is a proposed change for disposition.

## Finding

`outcome_leak_gate.py` rule 1 checks `set(ev) - ALLOWED_KEYS` (unexpected keys)
but never `ALLOWED_KEYS - set(ev)` (missing keys), so an event carrying only the
five fields the gate actually inspects passes cleanly:

```
minimal = {"event_id","normalized_prefix_hash","class","subtype","env_fact_kind"}
gate([minimal], None, ())  ->  []          # clean, despite 13 of 18 keys missing
```

The spec's own wording (`SPEC-OUTCOME-PROTOCOL.md` §5.1) is "**exactly** the
§5.1 key set", and the prototype note's rule 1 is "exactly the §5.1 key set;
unexpected keys are findings". The implemented rule only enforces the *unexpected*
half.

## Impact

- **Not a defect in the shipped bundle:** `export_bundle.py` always emits all 18
  keys, so `team/outcome-pilot-bundle-20260914/events.jsonl` is unaffected.
- **A hole for any other producer:** a future or third-party exporter that drops
  `exclusion_filters_applied`, `quoted_speech`, `repeat_group_id`,
  `timestamp_bucket`, `confidence`, `turn_index`, etc. would pass the gate,
  silently changing downstream M4 calibration/replay semantics (e.g. no
  `quoted_speech` means the high-confidence filter has no input).
- Low severity today, but it is a *contract* rule and the fix is one line.

## Proposed fix (Assay's call)

In `gate()`, alongside `extra`:

```python
missing = ALLOWED_KEYS - set(ev)
if missing:
    out.append({"event": i, "problem": f"missing key(s): {sorted(missing)}"})
```

Test to add to the prototype's control set: the `minimal` event above must yield a
`missing key(s)` finding (currently zero findings).

## Notes for the verifier

- The vendored copy already has the pinned sentinel list; the one-sided rule was
  inherited verbatim from the validated prototype (sha `202479298f83…`) and was
  **not** changed, to avoid silently diverging from the artifact Assay validated.
- Bundle determinism and the full verification checklist are in
  `team/outcome-pilot-bundle-20260914/VERIFY.md`; the 15-vs-10 card question is
  resolved in `team/ROW41-PILOT-CARD-DELTA.md`.

$0, local, synthetic demonstration only; no raw transcript content. — muse-drafter (Spark)
