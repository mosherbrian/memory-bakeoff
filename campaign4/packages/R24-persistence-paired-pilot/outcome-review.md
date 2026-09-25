# R24 outcome review — one persistence-rule pair

- **Reviewer:** corvid-dsh. Read-only; **no new participant runs, no criteria
  edits, no production change.**
- **Inputs:** `package.md`, `execution-claim.json`, both `grades/{T,C}.json`,
  both capture sets and rendered tasks, and R25 `terminal-disposition.json`.
  Execution COMPLETE (both arms dispatched, no timeouts; order T then C fixed
  before outputs).

## Frozen primary vs observed completion (kept separate)

- **Frozen primary (both useful AND compliant):** **T yes/compliant, C
  yes/compliant → a tie.** Both produced a grounded diagnosis grounded in
  `fixtures/failure.json`, started a concrete authorized action, stayed in the
  10-min bound, and used only the allowed CLI.
- **Observed completion of the P-INDEX-7 goal:** **C completed more than T.**
  C ran `diagnose-index` then `rebuild-noextra`, producing a real `index.json`
  that matches my independently recomputed full index (`index_match: true`).
  T ran `diagnose-index` only and named `rebuild-noextra` as the next action but
  did not start the rebuild (`index_match: null`). So on goal completion the
  control exceeded the treatment in this pair; on the frozen rubric they tie.

## Checker limitation (R25) — did not affect these grades

R25 records that the R22 mechanical checker accepted 4/4 deliberately wrong
cases and 2/2 honest ones (reviewer reproduced, plus one extra acceptance), so a
mechanical pass is insufficient. These R24 grades were **semantic**, not checker
halo: I recomputed C's full index from the docs, verified the diagnosis against
`failure.json`, and checked the receipt/evidence/output hash chains for both
arms. R25 explicitly keeps R24's full-index/grounded-diagnosis grading unchanged;
no actual R24 grade was driven by the weak checker.

## Deviations / confounds

- **Capture schema deviation (unchanged through the pair):** the operator wrapper
  records `capture.json` with argv/exit/stdout/out_sha256/start/end but not the
  `action/owner/arm/execution` fields R22 `check_capture` expects, so the checker
  reports "wrong action". Identity was validated manually from argv + the
  evidence/receipt; the wrapper was byte-identical across arms and not repaired
  mid-pair (correctly avoided changing the experiment).
- **Rendered-task deviation:** tasks add an identical operational block (work
  dir, answer path, claim artifact) and substitute `<assigned-id>/<out-dir>`;
  frozen task bytes otherwise unchanged, equal in both arms.
- **Smoke call:** ran with `PINDEX_TEST_NOW` set to prove the wrapper clears it
  (receipt shows host time); kept as operator smoke, not participant evidence.
- **Exposure / action-menu / same-user:** kiln has seen the R18 persistence
  checker work (disclosed); both arms see the exact allowed action menu, so
  discovering that a next action exists is cued for both, not treatment-specific;
  capture is same-user writable. Fresh sessions were distinct
  (`ses_f25d33b99…` T, `ses_f25d09196…` C), order fixed before outputs.

## Plain summary and verdict

**Honest verdict: one descriptive pair; the frozen primary is a tie, and the
control produced a more complete artifact (index) than the treatment
(diagnosis only).** This is **not** evidence that the saved persistence rule
helps or hurts: n=1, one model/seat, fixed order (T before C), prior exposure,
an action menu visible to both arms, and same-user capture. No population,
causal or efficacy claim. R23 remains inactive; the research question stays open
and Tern owns interpretation and the next step (R25's recorded next action is
Tern's to run).

*Reviewed: `package.md`, `execution-claim.json`, `grades/T.json`, `grades/C.json`,
`/var/home/bmosher/r24-capture/{T,C}/call-*/capture.json`, rendered
`tasks/*`, `release.json`, R25 `terminal-disposition.json`.*
