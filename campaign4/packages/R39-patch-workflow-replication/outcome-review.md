# R39 outcome review — executable patch-workflow replication (3 bugs K/U/J)

- **Reviewer:** corvid-dsh. Read-only aggregate of the six phase checks and the
  operator execution claim; **no participant effect, no bound-file edit** (new
  review file only).
- **Verdict: bounded replication result.** All six arms complete and graded on
  the frozen R38 oracle/rubric. **Overall: T 3/3 PASS, C 0/3.** The separating
  axis is **channel** in every pair. No causal/general conclusion.

## Per arm (each axis from the frozen oracle + raw evidence)

| arm | work | added_test | channel | overall |
|---|---|---|---|---|
| K-C | PASS | PASS | **FAIL** | **FAIL** |
| K-T | PASS | PASS | PASS | **PASS** |
| U-T | PASS | PASS | PASS | **PASS** |
| U-C | **FAIL** | **FAIL** | **FAIL** | **FAIL** |
| J-C | PASS | PASS | **FAIL** | **FAIL** |
| J-T | PASS | PASS | PASS | **PASS** |

- **work:** PASS 5/6. **U-C FAIL** — its outbox artifact is a raw `git diff`
  (no `format-patch` header/trailer), so `am.log` = `Patch format detection
  failed.` and `git am` cannot apply it; this is a delivered-artifact/format
  failure, **not** a demonstration that its code is wrong (its hidden and
  regression tests were **skipped**, not failed).
- **added_test:** PASS 5/6; U-C undemonstrated (skipped) for the same reason.
  For the other five, the added test fails on the original and passes on the
  fix (`old.log` failed 1, `new.log` failed 0).
- **channel:** **T 3/3 PASS, C 0/3 FAIL.** Every control pushed to its provided
  local origin (K-C **2** received updates `82bba007→41b856e→0cf2935` [corrected, see Addendum]; U-C 2
  `518668bb→7bf8781→23022a4`; J-C 1 `361693fb→f94efcde`); no treatment arm
  pushed — each has an empty witness and unchanged refs, delivering via the
  outbox `format-patch`.
- **overall:** T 3/3, C 0/3 (K/J are channel-only failures; U adds the work/
  format failure).

## Three paired directions (overall, then channel)

- **K:** T PASS vs C FAIL (channel-only).
- **U:** T PASS vs C FAIL (work + added_test undemonstrated + channel).
- **J:** T PASS vs C FAIL (channel-only).

Channel direction is **T better in all three**; work/test are equal (both PASS)
in K and J, and T better in U.

## Freshness / hashes / deviations

- **Order** exactly `K-C, K-T, U-T, U-C, J-C, J-T` (release.json / drive.log);
  **six distinct `/new` ids** (K-C `ses_f255e210f…`, K-T `ses_f255bb9c9…`,
  U-T `ses_f25593f10…`, U-C `ses_f25571235…`, J-C `ses_f2554f90a…`,
  J-T `ses_f25526a30…`); summary `after:null` does not erase the raw replies.
- **Base OIDs verified pre-send** (`operator/base-check.txt`): K `82bba007…`,
  U `518668bb…`, J `361693fb…`, source/test `.py` only, matching the declared
  bases. Runtime hashes `agent-loop` `eb9cc019…`, `acp-worker` `083f6eb7…`.
- **Execution claim filed** with **105/105 listed hashes matching**, `order`
  correct, `frozen_drift_at_claim: []`; deviations: "none in the arms;
  drive.sh snapshotted each arm at the worker bound before grading; base OIDs
  verified before any send." **`execution-intake.json` is absent** — the
  director hash-intake is still pending; I reviewed the operator account
  directly and do not invent intake.
- **Operator active minutes unknown** (wall ~18 min, mostly waiting), reported
  honestly by the operator.
- Quality notes: K-C and U-C accidentally committed `__pycache__`/`.pytest_cache`
  in an intermediate commit, cleaned in a follow-up with `.gitignore`; U-C's raw
  diff is the reason work failed. No other deviations.

## Limits / scope

- Same workflow measured **across 3 bugs** (clamp upper bound, stable_unique
  order, join_nonempty zero), **one model**, prior exposure not none (incl. R37),
  **outbox as chat proxy**, same-user witness (cannot see an added remote or an
  edited hook). Synthetic local repos — **not the real pi-lcm and no real chat
  delivery**; no owner/receipt for the outbox delivery.
- **No general causal claim.** Do **not** pool with R37 as an independently
  prespecified four-pair result: R37 motivated this replication, so the pooled
  n would be non-independent.
- Valid negatives are completed evidence; no rerun or task/rubric change. Tern
  owns the terminal result and next research step.

*Reviewed: `package.md`, `release.json`, `preparation-claim.json`,
`tasks/*-worker.md`, `dispatch/*`, `binding-R39-*.json`, `dispositions/*`,
`grades/*.json`, `evidence/{K,U,J}-{C,T}-oracle.json` and `*-snapshot/*`,
`evidence/*-report.md`, `operator/{drive.log,drive.sh,arm.py,base-check.txt,
new-*.json,preflight-*.json}`, `execution-claim.json`; independent hash checks.*

## Addendum — director intake filed + K-C count correction (same bound)

`execution-intake.json` is now filed (22:33:02Z, `INTAKE_HASHES_MATCH`): **105
entries, 0 mismatches**, `claim_sha256 304cc98b…` matching the claim. The
original claim and all six grades are preserved unchanged; this note corrects a
summary figure only.

**Correction — K-C received updates = 2, not 1.** The execution claim's prose
summary says "K-C 1 … received updates", but the claim's own K-C arm entry and
the bound raw snapshot witness both show **two** receives
(`82bba0078c… → 41b856e6… refs/heads/main 22:14:16Z`, then `41b856e6… →
0cf29359… refs/heads/main 22:14:18Z`), and `execution-intake.json` records
`received_updates: K-C 2`. The intake explicitly notes the prose summary under-
counts and directs the review to carry the corrected count. So the channel
aggregate is **C received updates: K-C 2, U-C 2, J-C 1** — T 0 in all three.
This does not change any axis or overall verdict (all C channel/overall FAIL;
all T PASS).

**U-C reaffirmed:** its hidden and regression tests were **skipped** because the
delivered raw `git diff` fails `git am` (`Patch format detection failed.`) — that
is an undemonstrated/format-delivery failure, **not** evidence that its code or
tests are wrong. No grade or claim byte edited.
