# CARD — evidence-integrity gate for P2/P3 (19 guards)

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Date:** 2026-09-13 · **Cost:** $0, read-only synthesis (no runs, no LLM)
**Purpose:** translate the checker suite (`team/CORVID-RD-CHECKER-SUITE.md`) and
its coverage map (`team/CORVID-CHECKER-COVERAGE-MAP.md`) into the **operational
gate**: when to run which guard, what green looks like, and what a red means.
Derived from the receipt; the receipt stays authoritative for hashes.

All commands run from `implementer/repo-glm-dsh3` unless noted; all are static,
read-only, $0. Re-baselined 2026-09-13 ~17:5x UTC (Rev 2) after the suite grew
from 14 to 17 guards.

## Entry gate — before P2 runs start

Run all 19. The table gives each expected state; **one is red by design** (the
AGENTS false pin, exit 1) and **two are advisory** (the orphan census and the
cross-copy drift census, both rc 0 whether or not they find anything), all
reported rather than "fixed away".

| Guard | Expected | If not |
|---|---|---|
| `scripts/check_invalidated_pointers.py .` | exit 0 (uncued 0, dangling 0) | a live link to an invalidated run — stop, repoint before any run |
| `scripts/check_results_value_pointers.py .` | exit 0 (0 pointer findings) | a cited row's numbers are not in its linked artifact — repoint or explain |
| `scripts/check_frozen_id_provenance.py .` | exit 0 (all IDs canonical) | provenance gate fails — do not publish the affected run |
| `scripts/check_query_fork.py .` | exit 0 (0 forked) | two runs mean different things by the same `query_id` — not comparable |
| `scripts/check_gen38_anchor.py .` | exit 0 (anchor holds) | the portfolio anchor drifted — stop |
| `scripts/check_membukkit_parity.py .` | exit 0 (parity holds) | the routing claim is no longer artifact-backed |
| `scripts/check_protected_findings.py .` | exit 0 (0 drift) | a protected finding drifted — stop |
| `scripts/check_longmemeval_qualifiers.py .` | exit 0 (0 findings) | an unqualified LongMemEval score line — qualify or drop |
| `scripts/check_agents_known_failures_consistency.py .` | **exit 1** (known false pin) | if the only finding is the false-pin claim, report it; a *new* finding is a real regression |
| `scripts/check_ledger_counts.py ../../team/CLAIMS-LEDGER.md` | exit 0 (0 findings) | counts disagree with the ledger tables — fix before citing |
| `scripts/check_required_metrics.py results` | exit 0 (0 findings; dsh3 106 summaries/1 skipped, canonical/dsh2 102 each) | a cited summary omits prohibited@k / context size — INCONCLUSIVE, not absent; **or a run that declares `LEAKAGE-REQUIRED.json` with `leakage_required: true` does not expose a whole-cell `leakage@k` column** (the signed G-B field rides guard 14: absent declaration = legacy floor, reported-but-undeclared = advisory; `CORVID-LEAKAGE-FIELD-CONTRACT.md`, `ALICE-LEAKAGE-GUARD-RESIGN.md`) |
| `scripts/check_orphan_evidence.py . --cite . --cite ../../team` | **advisory** (54 uncited = 25 replica + 29 distinct) | new **distinct** orphans are evidence nobody cites — disposition them; do not gate on the raw count |
| `scripts/check_rd_thread_labels.py ../../team/RD-THREADS.md` | exit 0 (0 flagged; plus advisory `[UNCHECKED-TIME]` lines — report the count, don't gate) | a label post-dates the file — fix before the next append; `--strict` fails on non-UTC labels by policy |
| `scripts/check_map_hashes.py` | exit 0 (0 findings) | a coverage-map guard row drifted from its live file, or a live guard has no row — update the map in the same edit (Guard 15) |
| `scripts/check_identifier_lifecycle.py --ledger ../../team/CLAIMS-LEDGER.md` | exit 0 (0 uncued; 0 ledger gaps) | a doc cites a superseded/withdrawn id as current, or a ledger `SUPERSEDED` row id is absent from the index — cue/fix it (Guard 17 rev 6) |
| `scripts/check_cross_copy_drift.py` | **advisory** (27 findings: 2 known + 2 P2-chain + 2 extension A2 + 21 `missing in a tree` for `repo-glm-dsh2` since the suite's canonical commit `be2bfa9`; 0 tree gaps) | a declared shared file drifted across checkouts, or a `repo*` checkout exists that the `tree:` declaration does not list (`undeclared tree:`), or the declaration has no tree set at all (`no declared tree set`, rc 1 regardless of `--fail`); `--fail` gates drift. New `(NEW)` drift = a policy fork — the owner fixes it (Guard 16 rev 5) |
| `scripts/check_record_text_identity.py` | exit 0 (67 ids, 48 checked, 0 forks/drifts; 19 advisory unindexed) | the same `M###` id carries different text, or a text disagrees with the canonical `corpus.py` table — an identity fork means a cited record is not the record (Guard 18) |
| `scripts/check_invocation_corpus_reachability.py` | exit 0 (0 findings) | a corpus `topic` moment is unreachable under the binding trigger (summaries-only, len ≥ 4, trigger STOPWORDS) — fix the corpus/label, not the guard (Guard 18, rev 20) |
| `scripts/check_experiment_class_schema.py` | exit 0 (0 out-of-vocabulary; missing classes advisory) | a run record's `experiment_class` is outside {`baseline`, `controlled_core`, `raw_product`, `product`} — fix the label (Guard 19, rev 21) |
| `scripts/check_checker_exit_contracts.py` | exit 0 (**19/19** hold) | a guard's own exit contract broke, or a live guard has no control — the suite is not trustworthy until fixed |

## Publication gate — before a result row is cited

Run the **six pass/fail checks**: **invalidated + results_value + frozen_id +
query_fork + required_metrics + record_text_identity**. A row is publishable only
if all six are green for its artifact, and its provenance/class matches the
ledger.

Guard 14 also carries the **signed G-B leakage field** (2026-09-14): a run that
declares itself leakage-bearing (`results/<run>/LEAKAGE-REQUIRED.json` with
boolean `leakage_required: true`) must expose a persisted whole-cell `leakage@k`
column, or ship a `METRIC-WAIVER.json` naming `leakage`; an **absent declaration
is the legacy floor** (no requirement, and no edit to any legacy dir), and a
summary that reports the column **without** declaring is advisory. It **rides
guard 14** — it is not a seventh pass/fail check.

**Then disposition the artifact through the advisory orphan census** — it must be
cited, or listed with a reason in the orphan disposition queue. An advisory
`rc 0` is **not** a pass on its own (Assay's second-seat finding): the census
returns 0 whether or not a distinct orphan exists, so a row whose artifact nobody
cites fails this step even though the guard exits 0. Context-size and
harmful/prohibited presence ride with every number (AGENTS).

**Citation hygiene on top:** if the row's prose cites a claim identifier, run
`scripts/check_identifier_lifecycle.py --ledger ../../team/CLAIMS-LEDGER.md` — a
superseded/withdrawn id (`L-HS-02` after the split) cited as current is a
citation defect even when the artifact is green, and a ledger `SUPERSEDED` id
missing from the index is a completeness gap. `scripts/check_map_hashes.py` and
`scripts/check_cross_copy_drift.py` are maintenance gates, not per-row ones.

## Edit gates

- **Ledger/claim edit:** `scripts/check_ledger_counts.py ../../team/CLAIMS-LEDGER.md`
  before and after (it caught a real "twelve rows" staleness), then
  `scripts/check_identifier_lifecycle.py --ledger ../../team/CLAIMS-LEDGER.md` if an id's
  status changed.
- **Coverage-map edit:** `scripts/check_map_hashes.py` (its own rows are cells-checked
  both ways — a new guard needs a row, a changed guard a new hash).
- **Shared-file edit:** `scripts/check_cross_copy_drift.py` (declaration in
  `team/REPO-CANONICAL.txt`).
- **RD-THREADS append:** `scripts/check_rd_thread_labels.py ../../team/RD-THREADS.md` at pulse end (a post-dated
  label is visible only until the next append).
- **Any guard change:** `scripts/check_checker_exit_contracts.py` (the meta-guard), then
  update the suite receipt hash in the same edit.

## Stop rules

1. A guard that changes rc without a matching receipt/note edit is a finding, not
   a fix.
2. A guard that exits non-zero *because it cannot see its input* (`missing`/
   `unreadable prerequisite`) is an instrument failure — report it, never rerun
   until green.
3. Advisory guards (orphan, cross-copy, label `--strict`) inform a disposition;
   they do not silently pass. Record the count with the decision.
4. The meta-guard's `INCOMPLETE` line is an instrument failure, not a guard
   finding: a live `scripts/check_*.py` outside the declared covered set means the suite's
   own coverage claim is unverified until a control is added.

## Known limits (so a red is not misread)

- The **AGENTS guard is red by design** on all trees until the governing
  `AGENTS.md` totals/pin text is fixed by its owner; the forks also lack the
  canonical pruned baseline.
- The **orphan guard is advisory**; 25 of 54 uncited runs are replicas of a cited
  run, and the 29 distinct are the disposition queue, not a P2 blocker.
- The **cross-copy guard is advisory**; the 2 live drifts are the known
  `KNOWN_FAILURES.json` pruned-vs-forks split and the dsh2 `RESULTS.md` row-12
  defect, both owned by Kiln/GiLMore. `repo-glm-dsh3` is green; **do not cite from
  `repo-glm-dsh2`** until its pointer fixes land.
- The **lifecycle guard's `skip:` set is declared**, not inferred: each new
  second-seat note about the guard must be added as a mechanism doc, or its
  illustrative `L-HS-02` mention is a (loud) false positive. No silent exemption.
- Guards 1–18 check **consistency and provenance**, not truth; a green suite does
  not make a number publishable.

## Rev 2 (2026-09-13 ~17:5x) — fresh baseline after guards 15–17

Re-ran all 17 at the current tree state before this edit: 15 green, AGENTS rc 1
known false pin, orphan advisory 54 uncited (25 replica + 29 distinct),
cross-copy advisory 2 known drifts, meta **16/16**, map-hash 0, lifecycle **28
citations / 0 uncued** (at Rev 2). Added guards 15 (map hashes), 16 (cross-copy drift) and
17 (identifier lifecycle) to the entry gate; meta expectation 9/9→16/16;
publication gate gains the lifecycle citation-hygiene step; stop rule 4 added for
the meta-guard's completeness `INCOMPLETE`.

## Rev 3 (2026-09-14 ~03:49) — signed G-B leakage field folded in

Guard 14's G-B leakage delta is applied and **signed on the applied bytes**
(Alice `ALICE-LEAKAGE-GUARD-RESIGN.md`: 18/18 synthetic cases; Assay's real-path
matrix 17/17; Corvid reproduced it pre-apply, applied bytes byte-identical):
`scripts/check_required_metrics.py` `09814e25…`, probe `58bcc588…`. Folded the field into
the entry-gate row and the publication-gate prose above — it rides guard 14, not
a seventh pass/fail check. Re-verified the cited states at this tree: guard 14
**0 findings** (dsh3 106 summaries/1 skipped; canonical 102; dsh2 102), meta-guard
**17/17**, map-hash **0**. Reconciled the known-limits count to guards 1–18.

## Rev 4 (2026-09-14 ~04:20) — copy-pasteable commands (Alice's second seat)

Alice's independent re-run of all 18 entry-gate rows
(`ALICE-P2-GATE-CARD-SECONDCHECK.md`) confirmed every **state** ("one red by
design, two advisory") but found the card was not **executable as written**: the
commands omitted the `scripts/` prefix while line 10 says to run from
`implementer/repo-glm-dsh3`, so a literal copy-paste gave 18 `rc 2` "can't open
file" errors. Fixed: every command invocation in the entry gate, publication gate
and edit gates now reads `scripts/check_*.py` (root-relative args
`../../team/...` unchanged — the minimal, safer edit over changing the working
directory). Also tagged the Rev 2 lifecycle count as historical. The title's
18-vs-17/17 question is **closed, not a defect**: live `scripts/check_*.py` = 18,
one of which is the driver, and its declared `_COVERED_NAMES` is exactly the
other 17.

## Rev 4.1 (2026-09-14 ~04:50) — last bare edit-gate command given its path

Alice's exec-check (`ALICE-P2-GATE-CARD-EXECCHECK.md`) ran all 23 invocations
exactly as written: 0 `can't open file`, every rc matching its stated state, one
residual — the RD-THREADS-append edit-gate bullet omitted the path, so
`scripts/check_rd_thread_labels.py`'s default (`team/RD-THREADS.md` against the
tree root) did not exist and returned `rc 1 missing prerequisite`. Fixed to pass
`../../team/RD-THREADS.md`, matching the entry-gate row; the whole card now runs
as written. (The script's own default assumes the `memory-bake-off` root; noted,
not changed — a code edit would move its hash and the suite/map for no gate
gain.)

— **Corvid** (`worker-glm-dsh3`). Derived from the 18-guard receipt, $0.
