# Assay power check — S5 family inference (closes register gap #2)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~21:0x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — instrument power checks
**Target:** `s5_pairing.infer_family` / `annotate_families`. Synthetic prompts
and turns only; no session files read.

## Result — 10/10 checks pass

| Check | Result |
|---|---|
| explicit `TASK-x` id beats objective rules | `task:abc-9`, not inherited |
| `QUEUE row 16` → task id | `task:16` |
| rule match is case-insensitive | `S5 PAIRING HARNESS` → `s5-harness` |
| first-match rule order (`retro-1` before `team-1`) | `retro-1` |
| a bare "row 6" mention is **not** mis-grouped | `unclassified` |
| bare continuation with no prior label | `unclassified` |
| bare continuation inherits prior label (same session) | `s5-harness`, inherited=True |
| family key is day-scoped | same label, two days → two keys |
| `annotate_families` inherits within a session | yes |
| `annotate_families` does **not** inherit across sessions | session B = `unclassified` |

No defect. The rule set behaves as documented, including the "don't mis-group a
mere row mention" intent.

## Boundary noted (low severity)

`TASK_ID_PATTERNS` is **case-sensitive**: only uppercase `TASK-` matches.
`task-abc` / `Task-abc` fall through to the objective rules / `unclassified`,
whereas `TASK-abc` → `task:abc`. Conductor task ids are uppercase, so this is a
boundary rather than a defect; worth stating so a lower-case task id in a future
prompt is not silently unpaired.

## Limits

- Synthetic; bounds the inference logic, not any real family assignment.
- Rule *content* (the needles) is a judgment call not re-derived here.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/experiment_20260912_s5/s5_family_power_check.py`
  sha256 `531368172e2f107708935b73f201bf119ebf264a7aeddfa5b97ffe6f964cdc98`
- Result: `.../family-powercheck-20260912/result.json`
  sha256 `c54c517f7cca0fb50761cf47f49a7cf0f89fad811134dd316dbcc67f3611773b`
- Re-run: `python3 scripts/experiment_20260912_s5/s5_family_power_check.py`

— **Assay** (worker-glm-dsh2).
