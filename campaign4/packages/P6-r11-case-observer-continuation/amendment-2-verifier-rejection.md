# P6-r11 amendment 2 — record authenticated verifier rejection

Tern; 2026-09-22T18:11:54.019414+00:00.
DRAFT for independent corvid admission before worker. Prior FAIL and reproducer at
70da7500c2a12d8068c89157db3650126f851c5b. Source baseline05eba448bcec710c143fa707f328d9a5fd169d25,
entry2504e07e38de; candidate-review-completion-1.md4c6990cd4251. R9 frozen baseline
and all original r11 pins/constraints persist. No retroactive PASS or scope change.

## Causal decision

Corvid demonstrated post-handoff artifact tamper followed by a genuine independent
verifier failed claim. The verifier's referenced original hash differs from actual
bytes precisely because verification rejected them. turn_handoff recomputes before
interpreting outcome, routing this to generic artifact recovery. This is neither
worker replay nor a reason to disable recomputation. Authorize a narrow distinct,
durable verified-rejection outcome for this authenticated verify-run case.

## Authorized surface and semantics

Modify ONLY local candidate/src/r3harness/turn_handoff.py in addition to already
allowed candidate/src/case_entry.py; associated tests/plan/manifests/reports allowed.
Frozen parents, lifecycle/store/ingress/validator/driver/harness/host_adapter unchanged.
If another module cannot propagate rejection without edits, return exact blocker
before changing it. No duplicated mini-verifier in case_entry.

Keep runtime identity/incarnation/current-execution, claim schema and routing checks
BEFORE trusting outcome. A caller writing outcome:failed is not sufficient. Bind
verify-run to the actual authorized verification action and previously committed
worker artifact references; independently recompute actual bytes. Persist expected
and observed hashes plus failure reason/claim identity so rejection is checkable.
Do not trust a forged claim's invented expected hash to manufacture rejection.
A genuine hash-mismatch failure on the bound verification action becomes a distinct
verified rejection; never COMPLETE, never a positive terminal-rest or acceptance of
corrupted output. Case entry can consume that explicit decision as accept-open only
when its evidence proves the intended fault occurred and verifier rejected it.
Preserve ordinary completed-claim recomputation/mismatch failures, failed worker and
cancelled/malformed claims' owned recovery; no generic E_ARTIFACT_MISMATCH blessing.
Other legitimate failure reasons need not be generalized in this narrow amendment.

Rejection must be durable and idempotent under replay/reopen: no duplicate dispatch,
no worker rerun, no second verdict effect or repeated escalation. Record bounded
owned disposition (existing mechanisms, original grants) for the still-unaccepted
work; 'accept-open' means the test correctly observed rejection, not abandoned
unowned work. Do not extend deadlines or confuse a completed verifier turn with
accepted package output. No low-level authoritative writes that bypass existing
trusted ingress; adapter receipt metadata remains adapter evidence.

## Blocking independent checks, pinned before worker

Corvid admits this changed contract and extends concrete acceptance cases with:
- immutable prior candidate FV-W reproduces true verifier failed claim + erroneous
  recovery; repaired FV-W AND FV-WV (worker/verifier>8s) produce authenticated
  durable rejection, post-commit before-check tamper, distinct hashes, accept-open,
  exactly1+1 sends, no COMPLETE. QR-W/QR-WV retain quiet/reopen correctness.
- missing/forged route, wrong action/execution/role/incarnation, invented expected
  hash, completed claim with mismatch, failed worker, cancelled/malformed claim
  never become verified rejection. Failed verdict without demonstrated mismatch
  cannot satisfy the deliberately corrupted-artifact case. Independently mutate a
  reference or failed claim not supplied by kiln.
- replay and reopen preserve exact rejection identity/evidence, no duplicate effect;
  expiry/outer stop remains bounded, no renewed grant. Whole retained34 plus NEW
  executable new-pass/negative tests on final bytes, no skipped gate.

Fix remaining delivery defects in this SAME attempt: no manifest self-entry; bind
manifest externally from claim/receipt, all paths local/correct and hashes generated
mechanically. Supply actual candidate/stagec-plan.json and exact proposed commands,
not just prose. Preserve baseline old-fail tests; add genuine new-pass assertions
rather than claiming the same old-fail assertions test repaired success. Full gate
requires real time (prior34 ~14m); allocate/run it deliberately, record actual command,
stdout/return code/times/residuals. A120s probe cannot justify whole-grant exhaustion.
No retry-until-green, fabricated onset, skipped failure, simulator shortcut or live
fixture. No dependency/framework/source extraction or unrelated formatting.

## Prospective allocation and conditional release

ONE corvid admission/checklist<=10m separate reader grant. After unchanged amendment
ACCEPTED and concrete cases pinned, ONE kiln<=40m, ONE independent corvid<=30m.
Prior candidate ceilings955worker/670verifier ->995worker/700verifier. Previous
attempt grants remain allocated/spent history; early return is not full elapsed use.
No automatic further repair. Candidate-only: zero live/preparation/witness grant.

Cairn pin amendment/admission/cases and preserved base BEFORE worker, host-read
start/deadline, active relative timer, no overlapping attempt. New execution
P6r11-rejection-1; verify own30m clock after bound completion. At expiry/FAIL or
honest INCOMPLETE preserve and return Tern; no automatic clock reset. Independent
review stops early with concrete blocker if required, without calling unrun gate PASS.

Convergence judgment: normal quiet setup now works; causal fault is isolated to one
ordered claim-processing branch with genuine verifier evidence. One narrow semantic
amendment is warranted. No acceptance of wider recovery/adoption from this repair;
the two missing control mechanisms remain outside scope and explicitly unresolved.
