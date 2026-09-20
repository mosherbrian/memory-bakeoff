# Second-seat check — AGENTS.md baseline-drift finding + the new drift guard

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 · **Trigger:** standing second-check of a new R&D artifact
(`team/CORVID-AGENTS-BASELINE-DRIFT.md` + its new checker, un-second-seated) ·
**Cost:** $0, read-only over the three trees + a temp scratch root, one turn.

**Subject:** Corvid's AGENTS.md vs `KNOWN_FAILURES.json` drift finding and
`repo-glm-dsh3/scripts/check_agents_known_failures_consistency.py`
(sha256 `179f8955…`). No canonical or seat tree was modified.

## Verdict

**PASS — the finding and the guard reproduce exactly.** Two boundary findings
the guard does not cover, both in its own failure class (scope, and silent pass
when its prerequisites are missing).

## Verified claims

| Corvid's claim | Independent check | Result |
|---|---|---|
| canonical AGENTS.md says 1557/26/3/5; JSON `_totals` says 1621/10/3/0 | `grep` L49/L75 vs `json.load(_totals)` | ✓ stale on both figure blocks |
| JSON `_pruned` removed 16 `memconflict_dataset_absent` + 5 `memconflict_collection_errors`; clusters now 8 + 2 | `_pruned[0].removed`, `clusters` counts | ✓ |
| `tests/test_preregistration_numbers_are_real.py` never references `KNOWN_FAILURES` | `grep -c` = **0**; file targets `research/pilot_ordering/PREREGISTRATION.md` | ✓ pin claim is false |
| scope: stale totals canonical-only; false pin in all three trees | forks dsh2/dsh3 both `_totals` 1557/26/3/5, both carry the same pin line | ✓ |
| checker sha `179f8955…`, `--self-test` PASS, findings canonical 3 / forks 1 | re-ran: self-test PASS; canonical 3 (2 stale + false pin); dsh2/dsh3 **1** each | ✓ exact |

So the guard is correct for the defect it was built for, and the proposed
AGENTS.md fix (Corvid's §Proposed fix) is the right shape. The checker also
handles the half-applied case correctly: a pin naming a script that is not in
the tree yields a `claimed pin … does not exist` finding, not a crash (verified
in source, lines 86–96), which matters because Corvid's proposed replacement pin
names a script that lives only in `repo-glm-dsh3` today.

## Finding 1 — the guard's scope is narrower than the drift

The checker reconciles **`AGENTS.md` only**. The same superseded baseline is
asserted as *current state* elsewhere in the canonical tree:

- `reviews/reset-R1.md:42` — *"Known-failure reconciliation in AGENTS.md matches
  `tests/KNOWN_FAILURES.json` totals (1557/26/3/5; clusters 8+16+5+2)."* After
  `c30e8fa` this is now **false twice over**: AGENTS.md does *not* match the JSON
  (1621/10/3/0), and the clusters are 8+2, not 8+16+5+2. This is a present-tense
  reset-verification claim, so it is stale, not history.
- `handoff/CODEX_TO_CHATGPT.md:99` — "26 failed, 1557 passed, … matching
  `tests/KNOWN_FAILURES.json` exactly." This one is inside the dated Gen125
  handoff entry, so it is **historical** and arguably should stand; list it as a
  judgement call for the owner, not a defect.

By contrast `reviews/LEDGER.md` rows 172/174 are dated Gen125 records and must
**not** be rewritten — a guard that demanded editing dated testimony would be
the "dangerous guard" LEDGER row 176 warns about. The scope fix therefore needs
a *current-state allowlist*, not a blanket grep.

**Recommendation (owner Corvid):** extend `_findings` to a small list of
current-state documents (at minimum `AGENTS.md`, `reviews/reset-R1.md`) and
explicitly exclude dated records (`reviews/LEDGER.md`, `handoff/`,
`reviews/accounting-*/`). Then add `reset-R1.md:42`'s correction to the proposed
fix — but note it can only be true once AGENTS.md itself is fixed, so AGENTS.md
is still the first move.

## Finding 2 — a missing prerequisite is a silent pass, not a finding

`_findings` returns `[]` when either `AGENTS.md` or `tests/KNOWN_FAILURES.json`
is absent (lines 53–54, "nothing to reconcile"). Measured on a scratch root:

```
$ python3 check_agents_known_failures_consistency.py <empty root>   # 0 findings, exit 0
$ ... <root with AGENTS.md, no tests/KNOWN_FAILURES.json>          # 0 findings, exit 0
```

For a checker advertised as the pin that makes the line unable to "go stale
silently again", deleting or moving either file silently disables the guard —
the same "a check that cannot report its own failure" class the drift finding is
about (and LEDGER 172/175 name). No live tree is affected today; it is a gate
hardening.

**Recommendation:** treat a missing `KNOWN_FAILURES.json` (or AGENTS.md in a
tree expected to have one) as a finding/`KNOWN_FAILURES.json missing` rather than
an empty result, or have the suite's caller pass the expected-file set
explicitly.

## Method and limits

- Read-only over the three real trees; the missing-file probe used a throwaway
  `/tmp` root. No suite run (Kiln owns the measured run); I reconciled documents
  against the JSON as committed, which is what the guard claims to do.
- The scope survey is a `grep` of the canonical tree excluding `.git`,
  `external/`, `results/`; it is not exhaustive over binary/JSON payloads, and
  the current-vs-historical split on `handoff/` is my judgement, flagged as such.
