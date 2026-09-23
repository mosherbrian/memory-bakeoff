# P11 — preregistered acceptance checklist (corvid, before author)

Pinned before author release. Each item is a concrete check with a required
outcome. **DRY=1 command printing cannot establish any F1/F2/F3 behavioral PASS.**
A failed required wait/assertion must yield FAIL or INCOMPLETE, never disappear
behind final rc0. Inspect every results row, not just process exit.

## Preconditions

- [ ] Contract unchanged: `package.md` sha256 `61ae7ed6…` (`6f780b3`); all 17
      `inputs.json.paths_sha256` recomputed equal; source `1341f04…` / binary
      `c1c49a29…` unchanged (rechecked at review, not rebuilt).
- [ ] Only F1/F2/F3 corrected, in package-local copies; historical P10 files
      untouched; no Go/core/host/installed-binary/main/dependency/research change.
- [ ] Mechanical P11 renaming listed in the diff; no silent expansion to other
      defects.
- [ ] Budget itemization reconciled with sponsor 410 m (currently 310 m; blocked).

## F1 — captured stdout is data only

- [ ] Reproduce old failure on pinned P10 (`live-driver.sh` `912b55b2…`): valid
      REST fixture makes `verdict()`/`state_is()` fail (log line + JSON on stdout).
- [ ] Non-DRY corrected helper parses valid `rest`, `ok`, `starting`, `unknown`
      fixtures (each asserted, exact expected state).
- [ ] Malformed/missing/empty fixture → **explicit failure** (FAIL/INCOMPLETE),
      never rc0 and never "unknown"/pass.
- [ ] A failed required wait/assertion produces FAIL/INCOMPLETE; diagnostics
      preserved; per-row inspection shows the failure.
- [ ] One unshared negative: e.g. a valid-JSON-but-wrong-state fixture must not be
      accepted as the asserted state.

## F2 — wall expiry stops the original driver and its effect-capable children

- [ ] Reproduce old failure on pinned P10: wall-stop `cleanup()` leaves the
      original driver able to issue effects after its bound.
- [ ] Deadline armed and **verified before** tasks; inability to arm = failure
      **before** any effect.
- [ ] On expiry: explicit **WALLSTOP/INCOMPLETE** record; original driver and
      effect-capable children terminated; cleanup idempotent (one effective run).
- [ ] Identity is a validated process identity/group or owned service scope — **not
      an unvalidated PID file** vulnerable to reuse.
- [ ] Offline subprocess witness triggers expiry **during a blocked operation** and
      proves: no later dispatch / drop-in / command sentinel, children terminated,
      exactly one cleanup; no effects after bound or cleanup.

## F3 — L2 settles and is reconciled before later cases

- [ ] Reproduce old failure on pinned P10: L2 left open; later timeout contaminates
      subsequent `state_is rest` cases.
- [ ] L2 reaches a **supported, evidenced settled state**; its timer/effects
      reconciled before later cases. No invented `decide` command valid only in
      another phase.
- [ ] Settlement proven against the **frozen Go CLI** with injected transport
      (offline), not by script self-report.
- [ ] Sequential case chain shows no L2 cancel/wake in L6 and `rest` asserted only
      with **no open work**.
- [ ] Original restart/no-resend assertion preserved (unchanged strength).
- [ ] One unshared negative: e.g. an L2 still-open condition must not be accepted
      as rest.

## Independent review method (author deliverables)

- [ ] Author emits source diff, plan hashes, claim with residuals, executable
      regression logs, and command/results coverage.
- [ ] Corvid reproduces old failures on pinned P10, exercises corrected **real
      shell helpers/processes** and the **Go sequence offline**, and adds one
      unshared negative per family.
- [ ] All required outcomes and adverse command failures checked; no lost case,
      weaker timing gate, swallowed failure, or forged PASS.
- [ ] Unchanged Go source/binary rechecked.

## Inheritance / downstream gates

- [ ] P10 section C live matrix and section D cutover inherited in full; P10
      recovery bounds explicit (30 s / 180 s + acknowledged ownership or 60 s;
      totals 90 / 240). Wake delivery alone is not acknowledgement; no case
      reclassified after a failed bound; all failed/censored cases retained.
- [ ] Live release only after candidate PASS + Tern signature; fresh
      worker/verifier/duty/director fixtures; no author/live overlap or live
      dispatch before PASS. Missing required live evidence → NOT READY, no cutover.
- [ ] PASS-only cutover with fresh production ledger, exact bindings, one owner,
      rollback reconciliation; first real package `P11-production-handoff-1`.

---

## Budget/pin reconciliation (append; original pin preserved)

- Corrected contract pin: `package.md` sha256
  `ca512b21c7017d126908d7b42d02c0ac8dfa84403247704bde8d2d090a6f047e`
  (`budget-correction.json`, push `0e3847e`). Supersedes the precondition hash
  `61ae7ed6…` above; all other preconditions and checks unchanged.
- Stage allocations unchanged; corrected total **310 m** (sponsor has no numeric
  figure). Budget precondition now **met**.
