# R16-review-1 — independent design review

- **Reviewer:** corvid-dsh. Read-only; **no trial, test run, historical fleet
  script, network, Signal or kiln prompt.** Within bound.
- **Intake:** review-receipt `830a7151…`; **both hashes recomputed and match**
  (`decision-brief.md` `5e284920…`, `manifest.json` `874534e7…`). Word count
  **794 ≤ 800** (the 802 was the prior commit; the trim is real, not a
  formatting issue).
- **Verdict: INCOMPLETE — a feasible task lead, not a release-ready
  preregistration.** The pinned task/check are genuine, but three design
  corrections are needed before the pair could answer anything, and the
  brief's own stop rule may already fire on this file-recoverable task.

## Pinned task/check verified (read-only)

- `inference-gateway` `e4a9aca` exists; broken `e4a9aca^` = `f6b2fc45…` (the
  manifest's `broken_commit`, whose message is the selftest-fix parent);
  check sha `d30cc10c…` and broken engine sha `bc312015…` both match the
  commits; curator reference engine `022be41b…` = `e4a9aca:igw/router/engine.py`.
- `test_active_reaches_the_load_stage` tests **behavior** (a fresh conversation
  must land on empty box-2 over the faster occupied box-1), not a signature.
  The defect is a multi-step wiring drop (`decide` → `_decide_pool_a` →
  `_load_rank`), so the diagnosis is interruption-relevant.
- The contrast is **not run** and the brief says so; it must be reproduced on
  `e4a9aca^` vs `e4a9aca` isolated copies before release (as R8/R12 did). Good.

## Correction 1 — the frozen check discloses the diagnosis (substantive)

The test's docstring literally states the defect: "decide() must forward
`active` to `_decide_pool_a`. **It did not.** … A default argument turned a
wiring mistake into silence. This asserts the wire." Any worker that runs the
check (which both arms are told to do) can read the diagnosis and the fix
target from the test file. That makes the task largely **file-recoverable**, so
the memory treatment has little to add and both arms are likely to pass — which
is exactly the case the brief's own stop rule says should end single pairs.
Either choose a check whose docstring does not name the defect, or accept the
brief's stop rule and record this as file-recoverable, not as a discriminating
test of restart memory.

## Correction 2 — the 5-minute cutoff and 2× threshold look chosen, not justified

R14's observed phase-2 times were C 263.1s and T 98.0s. A **5-minute** cutoff
leaves the control ~37s of margin, so a slightly slower control is timed out
mechanically — a cutoff set near the control's observed time can favor the
treatment. Likewise "at least 2× the phase-2 tool calls before the first edit"
has no prior basis and, from n=1, cannot be a decision rule. Either justify
both from prior recorded timings/counts with explicit margin, or demote them to
secondary descriptions (time-to-first-edit and rediscovery effort) with the
decision resting on the frozen check plus repeated observations.

## Correction 3 — equal-information confound is asserted, not shown

The brief asserts R9/R14 were uninformative "whatever memory does" because both
arms wrote/had notes. That is a plausible hypothesis, not a demonstrated cause
(R15's unit-level-check finding is an alternative; both arms may simply have
found the task easy). Recast it: the removed note instruction is a design change
to test **"automatic summary over ordinary work,"** not "total memory vs no
memory." And pre-register the control-spontaneous-note case as an
**uninformative pair about the summary**, not as a null about memory — natural
control notes are part of the baseline and must not become a post-hoc reason to
discard a null.

## Other checks

- Exposure/contamination handling is sound: fixed `engine.py` is present in
  `/var/home/bmosher/r14-arms/*`; the brief requires fresh `e4a9aca^` arms and a
  scan flagging reads of `r14-arms` or `~/inference-gateway`; the reference fix
  stays curator-only and out of kiln's conversation. Kiln history shows 0
  matches for the relevant symbols.
- Equal ordinary files preserved on both arms (no note deletion, no
  withholding); the treatment is the sole added summary. Lead 2 rejected for
  being a feature task — reasonable. Inference limits (one ordered pair, one
  model, not proven unseen) are stated.

## Addendum — word-count correction (director ruling, no re-review)

`word-count-correction.json` (16:37:01Z, commit `ceb7f39f`) confirms the
staLeness was in the intake prose, not the artifact: the review receipt's
`claim_sha256 830a7151…` already binds the corrected 794-word claim. I diffed
`attempt-history/pre-trim-committed/decision-brief.md` against the current file
— the only change is line 21's heading ("everything else as R14: …" →
"otherwise as R14"); **research content is unchanged** and the manifest is
unchanged. This review already assessed the corrected 794-word bytes, so the
verdict stands; no new pass or deadline reset. The pre-trim version is
preserved and was not represented as the reviewed hash.

## Recommendation

**Feasible lead, not release-ready.** Minimum corrections: (1) neutralize the
test-docstring disclosure or explicitly accept file-recoverability and the
brief's stop rule; (2) justify or demote the 5-min cutoff and 2× threshold;
(3) recast the causal claim and pre-register the spontaneous-note case
symmetrically; (4) keep contrast validation a hard gate. No formatting repair
for the two prior excess words.

*Reviewed: `review-receipt.json`, `decision-brief.md` (`5e284920…`),
`manifest.json` (`874534e7…`), `package.md`, `completion-claim.json`;
`inference-gateway` commits `e4a9aca`/`e4a9aca^`, `tests/test_router_engine.py`,
`igw/router/engine.py` (read-only `git show`).*
