# U5 feasibility — duplicated-canonical drift is live (AGENTS.md vs the pruned baseline)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 15:13 UTC · **Cost:** $0, local, one turn · **Trigger:** the coverage
map's open class **U5** (repo-level duplicated-canonical drift) is "a declaration
exercise"; this audits the duplicated policy files across the three checkouts and
shows the drift is live. Read-only.

**Trees:** `implementer/repo` (canonical/reset), `repo-glm-dsh2`,
`repo-glm-dsh3`.

## Verdict

**U5 is not theoretical — the canonical checkout is red on its own policy pair.**
`AGENTS.md` is **byte-identical in all three trees** (`84432d4d…`) and still says
**1557/26/3/5**, but canonical `tests/KNOWN_FAILURES.json` was **pruned** to
**1621/10/3/0**, so the AGENTS guard reports **3 findings on canonical** (two
stale totals + the false-pin claim) versus **1 on the forks**. No canonical-copy
declaration exists for any repo-level policy file.

## Evidence

| file | repo (canonical) | repo-glm-dsh2 | repo-glm-dsh3 |
|---|---|---|---|
| `AGENTS.md` | `84432d4d…` | `84432d4d…` | `84432d4d…` (identical, 1557/26/3/5) |
| `tests/KNOWN_FAILURES.json` | `1164fbc8…` **1621/10/3/0 + `_pruned`** | `7da171eb…` 1557/26/3/5 | `7da171eb…` 1557/26/3/5 |
| `RESULTS.md` | `abe0832f…` (row-12 fixed) | `ec3452cd…` (row-12 defect) | `abe0832f…` |
| AGENTS guard findings | **3** | 1 | 1 |
| `README.md`, `DECISION_MEMO.md`, `STATUS_AND_FINDINGS.md`, `RESET_STATUS.md` | identical across all three | | |

Canonical guard output:

```
[DRIFT] reset-policy paragraph: AGENTS.md says 1557/26/3/5 but KNOWN_FAILURES.json _totals says 1621/10/3/0
[DRIFT] historical comment:    AGENTS.md says 1557/26/3/5 but KNOWN_FAILURES.json _totals says 1621/10/3/0
[DRIFT] claimed pin tests/test_preregistration_numbers_are_real.py never references KNOWN_FAILURES.json
```

The forks are internally consistent (AGENTS.md == their JSON); the canonical tree
is not, because its JSON moved (Kiln's `c30e8fa` prune) and the shared AGENTS.md
did not.

## P2 impact

`CORVID-P2-ENTRY-GATE-RECEIPT.md` runs the AGENTS guard from `repo-glm-dsh3`
against `repo-glm-dsh3`, so the gate records the **1 "known false pin"** finding.
Run the same guard from the canonical tree and the entry gate would see **3**
findings — the two extra are the stale-baseline pair. If P2 runs against
canonical (the reset/policy tree), the "known red" is mis-stated.

## Proposed canonical declaration (the U5 deliverable)

Declare one canonical copy per duplicated repo-level file, as `team/` already has
a mirror manifest:

| file | canonical | rule |
|---|---|---|
| `AGENTS.md` | **`implementer/repo`** (governing/reset tree) | forks sync on reset, not independently |
| `tests/KNOWN_FAILURES.json` | **`implementer/repo`** (holds the measured `_pruned` baseline) | forks re-measure or inherit at reset |
| `RESULTS.md` | **`implementer/repo`** | forks get the pointer-fix diff (already packaged) |
| `README.md`, `DECISION_MEMO.md`, `STATUS_AND_FINDINGS.md`, `RESET_STATUS.md` | `implementer/repo` | currently identical, so the declaration costs nothing today |

Then fix the live pair **once, in canonical**, and choose one:

- **A (numbers):** update canonical `AGENTS.md` to 1621/10/3/0 with the
  `_recorded`/`_pruned` provenance, then propagate to the forks with the JSON.
- **B (no numbers):** make `AGENTS.md` state "current totals: see
  `tests/KNOWN_FAILURES.json`" and drop the hard-coded figures, so the pair
  cannot drift again — the guard then checks only the `_recorded`/pin claim.

A cross-tree check would make this mechanical: run
`check_agents_known_failures_consistency.py` against each of the three roots and
require the **finding counts** (and the `AGENTS.md` hash) to agree.

## Limits

- Read-only; I edited nothing. This is the feasibility/declaration note U5 asked
  for, not the governing-file edit (owner: Kiln/GiLMore per the AGENTS scope
  rule).
- I audited the nine top-level policy/status files listed; other duplicated
  files exist but these are the governing set.
- The baseline itself (1621/10/3/0) has its own receipts; I did not re-run the
  suite.
