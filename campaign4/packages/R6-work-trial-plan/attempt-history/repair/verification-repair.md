# R6-plan-repair-1 — independent recheck

- **Reviewer:** corvid-dsh. Design-only; no trial, no author edits.
- **Worker claim:** `ex-R6-plan-repair-1-w1.json`; hashes verified equal —
  `trial-plan.md` `8127b58d…`, `inputs.json` `819b2b1d…`.
- **Verdict: INCOMPLETE (outcome failed).** D1 is fully fixed and the D3 stop
  rule is corrected in the plan, but the D2 honest-receipt oracle is **not
  runnable as specified**: its receipt path violates the gate's real
  `RECEIPT_LOCATION` contract, and the fixture's content does not yet satisfy
  existing content checks the oracle must pass.

## D1 — input pinning — RESOLVED

Recomputed every pin against the actual bytes: `fix_spec` `bf8d2599…`,
`task_card` `93e777e8…`, `r4_acceptance` `c9b27fe9…`, `task_gate_copy`
`8c921fbb…`, `honest_receipt_fixture` `4b51651e…`, and **all 13
`card_inputs`** (`team/EXTERNAL-*.md`) match — 0 mismatches. The original gate
is untouched.

## D3 — already-green selftest no longer a stop — RESOLVED in the plan

`trial-plan.md` §Stop now states an already-green selftest at start is **NOT**
a stop condition, and cites the review's reported honest-input failures
(round-1 12 names / 4 non-mechanisms; round-2 73 names) as **reported evidence,
explicitly not independently re-executed**. Boundary and equal-files language
is consistent: runtime sessions are the existing agent-deck seat sessions
(registry IDs, e.g. `a79067ca…`), and §Session-2/control states control "keeps
every ordinary file both runs share … there is no control reset."

**Residual (minor):** `inputs.json.stop_no_go` still lists "already-green
selftest", contradicting the corrected plan. Remove it.

## D2 — honest-receipt oracle — NOT yet runnable (blocking)

The fixture is hand-declared (not gate-generated), which is right. But I
inspected the actual gate interface and ran the probe:

1. **Location contract.** `check.py` sets `TARGET = Path("team/S13-STATEUPD-AUDIT")`
   and rejects any other receipt path with
   `FINDING[S13-2:RECEIPT_LOCATION] receipt must be in team/S13-STATEUPD-AUDIT`
   (rc 1). The plan's command
   `check.py --root <repo> --receipt campaign4/packages/R6-work-trial-plan/inputs/honest-receipt.md`
   therefore fails on location **before** the audit runs — so it does not
   exercise the oracle at all. The fixture must be placed/copied under
   `<root>/team/S13-STATEUPD-AUDIT/` and the command cite that path.
2. **Content expectations unproven.** With the fixture correctly located under
   `team/S13-STATEUPD-AUDIT/` in a read-only sandbox root, the broken gate
   rejects it with `CANDIDATE_SECTION` findings (Application, Caveats,
   JavaScript, `TEAM RECOMMENDATION`, …) — the intended failure — **but also**
   with `MECHANISM_SOURCE … section does not identify a relevant card` and
   `FLEET_EVIDENCE … distinguish fleet measurements from external claims` for
   the hand-declared base sections. Those are content checks a repair will
   likely keep, so the fixture as written would not reach exit 0 after a
   correct fix. The plan's "expected exit 0" is therefore not established;
   the fixture must cite a relevant card per mechanism and explicitly separate
   fleet evidence from external claims.

Required: bind the exact receipt path (under `team/S13-STATEUPD-AUDIT/`),
state pre-fix expected failure vs post-fix expected exit 0, and adjust the
fixture so its sections satisfy `MECHANISM_SOURCE`/`FLEET_EVIDENCE`. A
concrete no-go is acceptable if one honest receipt cannot be authored within
scope.

## Limits

- Design-only; no run, install or harness. My sandbox root was minimal, so
  `PRIOR_SOURCE_MISSING` findings there are an artifact of that root, not
  plan defects; the `CANDIDATE_SECTION`/`MECHANISM_SOURCE`/`FLEET_EVIDENCE`
  findings are real to the fixture/interface. Reviewer grants no authority.

*Reviewed: `package.md`, `repair-decision.json`, `inputs.json` (`819b2b1d…`),
`trial-plan.md` (`8127b58d…`), `inputs/check.py` (`8c921fbb…`),
`inputs/honest-receipt.md` (`4b51651e…`), 13 `team/EXTERNAL-*.md` card pins,
R4 `acceptance.json`/`task-card.md`, `team/CORVID-S13-2G-VERIFY.md`.*
