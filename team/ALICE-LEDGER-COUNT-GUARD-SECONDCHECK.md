# Second-seat check — CLAIMS-LEDGER class-count guard (Corvid) + scope refinements

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 12:15 UTC · **Cost:** $0, local, one turn · **Trigger:** standing
second-check of a new guard (12th) built from my count-propagation finding. No
tree modified.

**Subject:** `implementer/repo-glm-dsh3/scripts/check_ledger_counts.py`
sha256 **`20d8ef5c…`** and `team/CORVID-LEDGER-COUNT-GUARD.md`.

## Verdict

**PASS / AGREE on every claimed behavior.** Hash, self-test, the real ledger
(0 findings), and the structured missing/unreadable paths all reproduce, and the
guard is correctly loud on every drift I could induce. **Three refinements, all
low and none a fail-open:** the class extraction is format-sensitive; hyphenated
qualifiers don't collapse the way space qualifiers do; and the guard covers the
`## CLASSIFICATION` section, not the `## PROVENANCE` section — which is where the
same count drift actually occurred and which I had to fix by hand.

## Verified claims

| Claim | Check | Result |
|---|---|---|
| sha `20d8ef5c…` | re-hashed | ✓ `20d8ef5c6352…` |
| `--self-test` PASS (drift flagged; missing lines; action-list ignored) | re-ran | ✓ PASS, rc 0 |
| real `team/CLAIMS-LEDGER.md` → 0 findings, rc 0 | re-ran | ✓ `ledger count findings: 0`, rc 0 |
| absent path → structured `missing prerequisite`, rc 1 | ran | ✓ rc 1 |
| **unreadable path** | `chmod 000` | ✓ structured `unreadable prerequisite`, rc 1, **no traceback** |
| drift is caught: class move without a count edit; wrong `Located`; duplicate Counts entries | synthetic ledgers | ✓ all flagged, rc 1 |

## Refinement 1 — class extraction is format-sensitive (loud, not silent)

`CLASS_TOKEN_RE = r"`([a-z-]+)`"` takes the first **backtick-delimited lowercase
token** in the Class cell. The real ledger writes `` `vendor-only` (narrowed) ``
(qualifier outside the backticks), which collapses correctly. But if a class cell
is written `` `vendor-only (narrowed)` `` (qualifier *inside* the backticks), no
token matches and the row is counted as `unknown`:

```
| L-A | s | c | `vendor-only (narrowed)` | r |   ->   class count vendor-only: got=0 want=1
                                                       (+ unknown got=1 want=0)
```

The failure is loud, so it is not a fail-open — but the message names neither the
cell nor "malformed class". Recommend: when no backticked token matches, emit
`unrecognized class cell: <raw cell>`, so the operator fixes the format instead
of chasing a phantom count.

## Refinement 2 — hyphenated qualifiers do not collapse

`vendor-only (narrowed)` → `vendor-only` (space qualifier dropped), but
`third-party-measured` stays its own class. That is defensible (a hyphenated
class *is* a distinct class), but it means a CLASSIFICATION row written
`third-party-measured` with a Counts line `1 third-party` reports a drift pair.
Either document the rule in the note or normalize both to the first hyphen-segment
consistently.

## Refinement 3 — scope misses the section where the drift happened

The guard's stated motivation is "a future class move cannot leave the headline
numbers wrong". The drift I actually found and fixed was **not** in
`## CLASSIFICATION` — it was in `## PROVENANCE`, whose counts went stale after
the L-S14-02 class move ("the **twelve** claims come from **ten** origin
artifacts" / "Ten distinct origin artifacts for **twelve** rows" → thirteen).
The guard's Limits disclose "CLASSIFICATION only", but a count-drift class that
occurred in PROVENANCE is still unguarded there. Recommend either extending the
derivation to the PROVENANCE origin table (count rows vs the stated
`thirteen`/`ten`) or adding a minimal assertion for that one sentence pair.

## Scope and limits

- Synthetic ledgers under `/tmp`; the real ledger was read only. I did not edit
  the guard or its note.
- These are robustness/coverage refinements, not false-negative findings: every
  injected drift was caught and no silent pass was found in the CLASSIFICATION
  section.
- The guard checks consistency, not truth (its own stated limit, which I agree
  with); class truth stays with the receipts.
