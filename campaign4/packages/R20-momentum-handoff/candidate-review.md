# R20 candidate review — corvid-eval, independent

- **Verdict: FAIL** — core required controls are absent or broken: question binding,
  owner authorization, attributable drop receipts, and director-stamp persistence/
  exact-action measurement. The shipped unit suite is green, but three unshared
  independent negatives fail against the candidate.
- **Reviewer:** corvid-eval; qid R20-candidate-review-1; receipt 19:49:10Z, deadline
  20:04:10Z. Isolated copy at `/tmp/opencode/r20src`; no live seats/services, no install,
  no config/service change, no author repair grant implied.

## Intake (verified)

- `implementation-claim.json` sha `a256dfe241cf…` matches receipt; **5/5 `files_sha256`
  exact**.
- Commit `d0264366…` in worktree, base `df5e6fc6…`; `internal/core`,
  `internal/py`, `conformance` 0 diff.
- Installed binary **unchanged**: `/home/bmosher/.local/bin/agent-loop` =
  `47f69dfd…`; private candidate `bin/agent-loop` = `9aea1675…` (matches claim).

## Suite independently run

`go1.27.1`, isolated copy, `GOPROXY=off`: `go test ./...` — every package `ok`. The 15
R20 tests pass. I then added **three unshared negatives** (not in
`momentum_r20_test.go`), each asserting the secure behaviour:

```
--- FAIL: TestNegQuestionBinding          undeclared question_id advanced to verify
--- FAIL: TestNegUnknownOwnerNotAllowed   unknown next.owner advanced to verify
--- FAIL: TestNegSelfAttestedAckIsNotAttribution  worker-authored receipt for another owner accepted
```

## Concrete defects

1. **No question binding.** `ValidateStamp` requires `moved.question_id` to be merely a
   non-empty string (`momentum.go:72`); it is never compared to the package's declared
   research question (the loop has no such binding — `Pkg` carries none). An arbitrary
   or operational id is accepted. Focus explicitly requires a match.
2. **No owner authorization.** `next.owner` is checked only for non-emptiness
   (`momentum.go:79`); it is not required to be a seat/role allowed by the bound config
   or contract. Any string advances.
3. **Drop receipts are self-attested, not attributable.** `receiptProblem`
   (`momentum.go:105-121`) accepts any file under `artifacts_dir` whose JSON has
   `ack:true` and matching `qid`/`item`/`owner`. The same worker that writes the stamp
   writes that file, naming any owner it likes; `TestDroppedItemWithAcknowledgement…`
   confirms a worker-authored ack for `tern` counts as valid. `STAMP.md`'s "written by
   the owner … the receipt is [proof]" overstates an attribution that does not exist.
4. **Director stamp is not persisted.** `DecideStamped` (`loop.go:956+`) reads and
   validates `--stamp`, then discards the bytes: the `decide` event carries only
   `{kind, decision_ref, reason}` and `Pkg` has no stamp field. Later measurement cannot
   recover the director's `next.deadline`/`owner`; it is a validation-only artifact.
5. **Exact-action measurement (e) is unimplemented and, as documented, too weak.**
   No code joins `next.deadline` to a start; `STAMP.md` says it "is joined to the first
   later `start` event whose package is bound to the same question" — question-only, not
   the exact action+owner+question+deadline the focus requires.
6. **Minor: stamp/claim artifact path is not confined to `artifacts_dir`.** Both
   `stampFault` (`momentum.go:142`) and `DecideStamped` join the caller-supplied path
   with no `IsAbs`/`..` check (unlike the receipt path, which was hardened). Read-only
   escape of the stamp read.

## Verified sound (for contrast)

Size bound (8192; the over-size stamp blocks), identity qid/role/execution, malformed/
missing/terminal-for-worker stamps block **before** transition with `E_STAMP_*`, owner =
existing director escalation, claim retained, one director notice, replay tick is a
no-op; `decide` validates before mutation so a refusal leaves the decision open and the
ladder running; terminal only for the director's `question_answered`/`budget_spent`;
`blocked` needs a concrete recovery `next`; verifier stamp enforced before on-pass;
off-by-default, `Pkg.Stamp` fixed at dispatch (prospective migration), pre-activation
package keeps the old contract, rollback documented and non-destructive (old binary
ignores the unknown JSON field); R21 untouched.

## Limits

Unit-rig reconstruction only (in-process `host.Runner` stub); the installed binary was
verified present and unchanged but **not** exercised; no stub-transport live witness, no
activation, no service restart. Director-persistence and measurement findings are from
source and event structure, not a running DB. Item 5 is partly out of this candidate's
tier2 scope, but items 1-4 are required by the candidate's own focus and by `STAMP.md`.

*Reviewed read-only: candidate-review-receipt.json, implementation-claim.json, package.md,
implementation/STAMP.md, implementation/source.diff, mutants-results.txt, test-results.txt,
extracted private binary, worktree source (`internal/loop/momentum.go`, `loop.go`,
`cmd/agent-loop/loop.go`, `momentum_r20_test.go`); isolated `go test ./...` + 3 unshared
negatives.*
