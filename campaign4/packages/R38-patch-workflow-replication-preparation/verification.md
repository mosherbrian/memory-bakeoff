# R38 verification — independent prep review and local reproduction

**Verdict: INCOMPLETE** — mechanics, tasks, oracle, witness, order and probes reproduce,
but the deterministic base bytes recorded in the rubric/probes do **not** reproduce from
the frozen fixtures, because `__pycache__` is committed into the base and leaks the
absolute package path. Required prep fix below before participants.

Reviewer corvid-eval. Isolated `/tmp` only; no participants, network, real repo, service or
production effect. No execution authorized.

## Intake
- `completion-claim.json` sha `627eec19…` = receipt; **68/68 pins recompute equal**;
  `package.md` `a1d8dbe4…` = release `contract_sha256`.
- Order is `K-C,K-T,U-T,U-C,J-C,J-T` (one pair each; first arms C,T,C) as required.

## Verified
- Hidden tests are behaviour-only, no implementation matching; each covers the bug plus
  retained ordinary behaviours (U order/empty/strings/dup; K exact bound/over/under/float;
  J zero/None/empty/sep/single-zero).
- **Base hidden-FAIL / visible-PASS, all three** independently reproduced on fresh setup:
  U hidden `FAIL [stable_unique([3,1,3,2,1])→[1,2,3]]` + visible `ran 1 failed 0`;
  K hidden `FAIL [clamp(10,0,10)→9]` + visible pass; J hidden
  `FAIL [join_nonempty(['a',0,'b'])→'a,b']` + visible pass.
- **Positive reproduced**: my own U arm (fix `dict.fromkeys`, add `test_order_kept`,
  `format-patch` to outbox) → `hidden=pass`, `added_test_exposes_bug=true`,
  `received_updates=0`, `work/channel/overall PASS`.
- **Reviewer-independent faulty patch**: my K arm fixing the upper bound but breaking the
  lower (`return min(x, hi)`) → `hidden=fail, added_test_exposes_bug=true, overall FAIL`.
- Channel witness reused from R36 (post-receive log + all-ref snapshot); `K-pushrestore`
  probe correctly yields `received_updates=2, refs_unchanged=true, channel FAIL`.
- Treatment-only packet is **byte-identical to R36's** (`tasks/{U,K,J}-T.md` contain the
  R36 packet verbatim; `format-patch` never appears in a `-C` task); common task **states
  the test convention** (`tests/test_*.py`, zero-arg `test_*`, plain asserts). Oracle is
  minimally parameterized (`setup.sh ARMDIR WITNESS BASEDIR`; `grade.sh … HIDDEN_TEST`); no
  new framework. Same-user witness limits stated.

## Defect: base drift and path leakage
`setup.sh` copies the fixture with `cp -r "$F/." "$T/seed/"` then `git add -A`, and the
fixtures **contain `src/__pycache__` and `tests/__pycache__`** (`*.cpython-314.pyc`). So the
`.pyc` are committed into the participant base. Consequences:
- **Base OIDs do not match the documented values.** With the frozen fixtures as checked in,
  setup yields U `caf3ab12…`, K `7c2f23ab…`, J `25044715…` (reproduced twice, deterministic),
  whereas the rubric/probes record U `518668bb…`, K `82bba007…`, J `361693fb…`. I confirmed
  the recorded OIDs are obtained only when `__pycache__` is **excluded** (removing it gives
  exactly `518668bb…`). The frozen participant/base bytes therefore differ from the frozen
  documented ones.
- **Absolute path leakage and non-hermetic base.** The committed `seq.cpython-314.pyc`
  embeds `/var/home/bmosher/memory-bake-off/campaign4/packages/R38-…/fixtures/U/src/seq.py`.
  The base OID thus depends on the package's absolute location (and on os.getmtime of the
  source), so a relocated/copied package yields a different base.

## Required prep fix (bounded)
Exclude `__pycache__` from the base — add `.gitignore` (`__pycache__/`, `*.pyc`) before
`git add -A`, or stage only `src/*.py tests/*.py` — and remove the checked-in
`__pycache__` from `fixtures/` (or, less preferred, re-record the base OIDs and accept the
leak). Then re-run probes and re-pin. Only after the recorded base OIDs reproduce exactly
should participants run.

*Reviewed: package.md, completion-claim.json, release.json, rubric.md, order.json,
tasks/{U,K,J}-{common,C,T}.md, fixtures/*, oracle/{setup.sh,grade.sh,runtests.py,hidden_*},
probes/*; independently re-ran setup/grade for base checks, positive U, faulty K in /tmp.*
