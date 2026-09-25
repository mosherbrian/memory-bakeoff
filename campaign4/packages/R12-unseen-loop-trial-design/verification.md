# R12-review-1 — independent review

- **Reviewer:** corvid-dsh. Read-only; **no kiln prompt, trial, production edit,
  network or Signal.** Within bound.
- **Intake:** review-receipt `86be99d7…`; **all 14 completion-claim hashes
  recomputed and match**.
- **Verdict: INCOMPLETE (outcome failed).** The task/contrast is sound and
  Signal-safe, but two phase-template defects make the prospective loop tasks
  non-executable as delivered. The author's Signal incident is separately a
  recorded scope violation; the research contrast is not tainted by it.

## Safety inspection first (as required) — the gateway check is Signal-free

Static, before any execution: `curator/check-test_drain_on_disconnect.py`
imports only `asyncio`, `httpx`, `igw.router.app._drain_detached` and
`igw.router.config.ClassSpec`; its upstream is a `FakeResponse` and an
`httpx.ReadError`. `igw/router/__init__.py` re-exports pure symbols; the
network/poller/`httpx.AsyncClient`/lifespan code in `app.py` is **inside
functions**, not module-level (verified top-level statements). No Signal,
pager, subprocess, socket or webhook path. Safe to run in isolation.

## Reproduced contrast (isolated `/tmp` archives, no installs)

- `git archive 7b368e2^` + check → **3 failed, 2 passed, rc 1**;
  `git archive 7b368e2` + check → **5 passed, rc 0**. Matches the claim.
- App hashes match the manifest: broken `89459e70…`, fixed `c9ddd60a…`;
  `7b368e2^` = `846dfc1` as listed.

## D1 — phase task files reference a claim/verify command that is absent

`tasks/phase1-worker.txt`, `phase2-worker.txt`, `phase1-verifier.txt` and
`phase2-verifier.txt` each end with "…file your claim with the exact agent-loop
claim command **below**" / "Claim with the exact verify command **below**" — and
nothing follows. The claim/verify commands are not present, so the four
prospective loop tasks are not self-contained. Either embed the exact
`agent-loop claim|dispatch` commands, or state explicitly that the loop's
`dispatch --task` wrapper appends them.

## D2 — phase-1 verifier manifest comparison is not executable

`phase1-verifier.txt` requires "sha256 of every file under `{ARM_DIR}/igw` and
`{ARM_DIR}/tests` equals input-manifest.json." But `input-manifest.json` lists
only three hashes (`broken …/app.py`, the check, and the curator reference) and
does not enumerate the arm tree. Worse, merely running the check (which phase 1
instructs) writes **34 `__pycache__/*.pyc` files** under `igw/` and `tests/`
(reproduced), so the comparison would produce false differences. As written the
verifier either fails spuriously or cannot compare. Fix: define the exact
expected file set (or exclude `__pycache__`/`.pyc` and compare only tracked
sources), and make phase-2's "files under tests byte-identical" reference a
concrete list.

## What passes

- **Exposure evidence** recorded: kiln history (a79067ca) and archived
  kiln-flash (fcb1e5e6) show 0 `inference-gateway`, 16 `igw` as timer names;
  disclosed as unexposed-in-session, not proven unseen.
- **Equal ordinary access/treatment**: same arm recipe, model, prompts and
  budgets; reference fix and curator evidence stay out of arms/prompts; T-only
  summary written **outside** every arm dir (so C's ordinary files cannot
  receive it); summary ≤300 words inside phase 1; naive truncation declared as a
  prospective choice.
- **Loop composition/deadlines/verifier independence**: four named loop
  packages with `question_id`/`stream_id`; loop owns dispatch/claim/deadline/
  decision; director does only the R10-provenance `/new`; verifiers write only
  to `{PKG}/verify/`, never message the worker, and do not teach fixes.
- **Metrics/limits**: first-passing-run taken from acp-history timestamps or
  reported "unavailable", never phase duration; contamination scan and n=1/
  order/seen-task limits disclosed (a scan, not a sandbox).

## Author scope violation — separately classified

The completion claim discloses that screening historical `test-fleet-poller.sh`
versions **paged Brian twice** with synthetic `[Fleet - ACTION NEEDED]` alerts,
violating the standing no-live-effects rule. Preserved facts: the incident is
recorded in `completion-claim.json` and `operator-incident-intake.json`. My
read-only checks found **no lingering fleet-poller process** and **no r12/r13
timers**, consistent with "runs finished." The selected gateway check itself has
no pager path, so the research contrast stands; but the author round is **not**
certified free of live effects, and no historical script was rerun to establish
this.

## Limits

- No execution approval; no sponsor-condition waiver; Stream B is not
  authorized. One ordered pair, n=1, seen-task limits apply. The broken-tree
  failures include a signature-conformance `TypeError` against the check's
  fixed interface — a legitimate frozen broken/fixed contrast, but the task is
  effectively to conform the code to the test's interface.

*Reviewed: `review-receipt.json`, `package.md`, `completion-claim.json`,
`input-manifest.json`, `preregistration.md`, `operator-incident-intake.json`,
`tasks/*`, `curator/*` (hashes recomputed); isolated `/tmp` archives; read-only
host process/timer checks.*
