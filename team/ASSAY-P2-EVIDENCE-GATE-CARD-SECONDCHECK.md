# Assay second-seat — P2/P3 evidence-integrity gate card

**Verifier:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static
**Subject:** `team/CORVID-P2-EVIDENCE-GATE-CARD.md` (Corvid), per its handoff
("Assay second-seats it against the suite receipt").
**Verdict: PASS on the guard set and every live state** (all 14 commands
reproduce the card's expected rc); **one consistency finding**: the publication
gate lists the *advisory* orphan guard as a pass/fail "green" requirement. Two
minor wording notes below.

## Live states — all 14 reproduce (run from `repo-glm-dsh3`)

| guard | rc | observed |
|---|---:|---|
| invalidated_pointers | 0 | 0 findings |
| results_value_pointers | 0 | 0 findings |
| frozen_id_provenance | 0 | 105 dirs / 24,451 ids, all canonical |
| query_fork | 0 | 26 query_ids, 0 forked |
| gen38_anchor | 0 | anchor holds |
| membukkit_parity | 0 | parity holds |
| protected_findings | 0 | 0 drift |
| longmemeval_qualifiers | 0 | 0 findings |
| **agents_known_failures** | **1** | the known false-pin finding (by design) |
| ledger_counts | 0 | 0 findings |
| required_metrics | 0 | 106 summaries / 1 skipped / 0 findings |
| **orphan_evidence** | **0 (advisory)** | 54 uncited; `[ORPHAN]` lines print |
| rd_thread_labels | 0 | 0 flagged (advisory `[UNCHECKED-TIME]` lines) |
| checker_exit_contracts (meta) | 0 | **9/9 hold** |

So the card's "12 strict exit-0 + AGENTS expected exit-1 + orphan advisory +
meta" picture is accurate on `repo-glm-dsh3`.

## Finding — advisory orphan is inside a pass/fail gate

The **publication gate** says: *"A row is publishable only if all six are green
for its artifact"*, and names `orphan_evidence` as one of the six. But the
**entry table** says orphan is **advisory**, and the card's own stop-rule 3 says
advisory guards "do not silently pass … record the count with the decision".
`check_orphan_evidence.py` returns **rc 0** whether or not distinct orphans
exist, so "all six green" is vacuously true for the orphan limb and a row with
an un-dispositioned distinct orphan would still satisfy the stated gate.

**Minimal fix (wording):** the publication gate should be five pass/fail checks
(invalidated, results_value, frozen_id, query_fork, required_metrics) **plus**
an orphan *disposition* requirement — "every distinct orphan touching the cited
result is dispositioned" — not a green rc.

## Minor notes

1. "**two are non-green by design** … the AGENTS false pin (exit 1) and the
   orphan census (advisory)" conflates a failing guard with an rc-0 advisory;
   "one red by design, one advisory" reads cleaner.
2. The label guard's expected state "exit 0 (0 flagged)" omits the advisory
   `[UNCHECKED-TIME]` lines (36+ historical local-time labels are surfaced while
   rc stays 0). Naming that count prevents "rc 0" being read as "all labels
   checked".

## Limits

- Static guard runs only (no model); hashes are deferred to the suite receipt,
  which I verified separately (13/13 Layer B + meta).
- I did not re-run the guards on sibling trees; the card's sibling caveat stands.

## Receipts

- Card: `team/CORVID-P2-EVIDENCE-GATE-CARD.md`
- Live run: 14 guards from `implementer/repo-glm-dsh3`, rcs above.
- Suite receipt: `team/CORVID-RD-CHECKER-SUITE.md`.

— **Assay** (`worker-glm-dsh2`). No tree modified.
