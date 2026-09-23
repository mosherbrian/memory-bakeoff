# P7-expose-status — read-only derived status view

View-only package. Nothing here schedules, publishes, mutates shared
state, or certifies liveness. The director may publish the derived view
at the campaign root on independent PASS.

## Render (single documented command)

    python3 src/render_status.py --out-dir <dir> [--as-of <UTC ISO Z>]

`--as-of` defaults to host UTC now. Inputs are declared in
`inputs-index.json` (pointers with hashes, not a second authority).
Outputs: `status.md` + `pending-decisions.json`, host-stamped with the
as-of time. Rendering writes only the output dir; repeat renders are
byte-stable for a fixed `--as-of`.

## Source map

| File | Role |
|---|---|
| `src/render_status.py` | stdlib-only renderer (parse + derive + write) |
| `tests/test_status_view.py` | adversarial checklist tests (6) |
| `status.md` | rendered derived view (as-of stamped) |
| `pending-decisions.json` | machine-readable pending list + checks + input hashes |
| `inputs-index.json` | declared input pointers + sha256 (read-only) |
| `package.md` / `admission-review.md` | contract + pinned checklist (frozen brief) |

## Inputs (read, never written)

- `campaign4/pending-decisions.md` — open S13-1 (owner tern); the
  07:38 retracted false-alarm row is linked, never pending.
- `campaign4/CONNECT-FINISH-LINE-20260923.md` — Connect ruling + eight
  checks (3 met at boundary, 5 partial to P8).
- R18 `acceptance.json` (ACCEPTED_SCOPED_CANDIDATE, commit 7857c0ce…)
  vs R19 `terminal-disposition.json` (TERMINATED, not a technical
  failure) — distinguished, never merged.
- `campaign4/control-events.tsv` — labelled activity log (counts are
  activity, not cost, not truth).
- `CHARTER.md`, `ACCEPTED-ARCHITECTURE.md` — sheets 5/7/8 context.

## Truthfulness rules enforced by tests

Open judgments render owner/question/dependents/next action; resolved
ones cease pending; missing/stale/contradictory evidence is
UNKNOWN/CONFLICT with owner+links; accepted vs merely-PASS/historical
evidence distinguished; costs unknown (allocations are ceilings); no
invented sponsor decision; no scheduling claim (P8 owns enforcement).
