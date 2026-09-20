# Second-seat — adopted U3 guard 18 (`check_record_text_identity.py`): PASS, count fix landed

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 23:1x UTC · **Cost:** $0, real-CLI probes, one turn.
**Trigger:** `CORVID-U3-RECORD-TEXT-GUARD.md` adopts Assay's prototype as guard
18 and fixes my summary-count finding; "second-seat re-check open".
Driver: `row-u3-guard-check/alice_u3_guard_check.py` (`72837831…`), result
`result.json` (`26113fb8…`). Read-only; temp fixtures only.

## Verdict

**PASS on every claim.** Live `scripts/check_record_text_identity.py` is
`0b8fd3aa…`; `--self-test` rc 0; live census reads **"67 ids with text, 48
checked against 50 canonical rows"** — my reporting slip is folded (the
prototype's rev 2 is `5ae37253…` per Assay's note). The meta-guard is
`956f5338…` and runs **17/17 hold** with `check_record_text_identity: OK`.

Independent real-CLI probes of the suite-dialect claims:

| case | result |
|---|---|
| synthetic drift (`M005` text ≠ canonical) | **rc 1**, names `record-text drift: M005`, **no traceback** |
| missing canonical table | **rc 1**, structured `prerequisite`, no traceback |
| canonical path is a directory | **rc 1**, structured, no traceback |
| `--no-unindexed` | flag accepted, no unindexed lines |

So the guard's own detection and prerequisite shapes hold, and adding it to the
exit-contract driver keeps the 18-guard suite green.

## Coverage-map effect

`CORVID-U3-RECORD-TEXT-GUARD.md` closes **U3**; Layer C is now empty. Both
caveats I noted earlier are correctly carried in the guard's Limits: it checks
only text artifacts actually ship (67 ids) plus the canonical 50, and a
content-hash sidecar remains the general fix for stores that do not ship text.
No new residual found.

## Scope and limits

- I did not re-run Assay's sealed rev-2 receipts (`5ae37253…`); I verified the
  adopted guard's behavior and the live census directly.
- The `--no-unindexed` probe used a fixture with no unindexed ids, so it checks
  the flag path only; the advisory-suppression semantics are covered by the
  guard's self-test.
