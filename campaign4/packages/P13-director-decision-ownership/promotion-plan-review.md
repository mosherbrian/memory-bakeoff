# P13-promotion-plan — independent review (corvid)

- **Action:** `P13-promotion-review-1`, owner corvid, `20:23:57Z`–`20:33:57Z`.
- **Claim:** `promotion-positive-claim.json` (`5899063b…`) — COMPLETE; **15/15 claim
  hashes** and **15/15 canonical manifest** pass. Prior two INCOMPLETE preserved.
- **Verdict: PASS** — plan branches and sandbox evidence verified; distinct from real
  promotion. No source/host changes; Live PASS already accepted, not repeated.

## Host branch / sandbox equivalence

- Plan `plans/promotion-plan.sh` unchanged this round (manifest rc 0). The sandbox
  (`evidence/promotion-closure/sandbox-test.sh`) is fully isolated — private root,
  stateful `systemctl` double, sandbox DB, `wake=/bin/true` — and reads production
  paths **only to copy the old binary/config bytes**. Every row is `SANDBOX-*`.
- **Baseline ownership matches the host:** `units.tsv` = loop + liveness timer +
  `escalation-watch.timer` **active/enabled**; liveness service, its OnFailure
  handler and `escalation-watch.service` **inactive/static**; **resolver ABSENT**
  (host `/home/bmosher/.config/agent-deck/escalation-resolve` does not exist).

## Positive path (actual installed candidate run)

- `PROMOTE PASS rc 0`: the sandbox double runs the **installed candidate**
  `agent-loop run` as the unit main process with a **new `INVOCATION_ID`**; the plan
  sees a new invocation, a **fresh ledger pass by that run** (`pass_eval`), and the
  **REAL candidate liveness checker** healthy after the start; required 0/300/600
  policy loaded. Postconditions: candidate binary, **both adapters (resolver absent
  before)** and the config installed; units active as snapshotted.

## Negative paths (honest, nonzero, bounded)

- **Stale pass (old invocation) → `PROMOTE FAIL` rc 3**.
- **Exact restore:** files/modes/units equal the snapshot; **absent resolver restored
  as ABSENT** (introduced file removed, none fabricated).
- **Partial install failure → `PROMOTE FAIL` rc 3**, binary and units restored
  exactly.
- **Start failure → `PROMOTE FAIL`**, and restore cannot restart the still-failing
  loop and reports **`ROLLBACK FAIL`** (not a false PASS).
- **Failed rollback exits nonzero (rc 1)** and records `ROLLBACK FAIL`.
- **Invalid policy refused by the guard; nothing changed, no snapshot taken.**
- `promotion-sandbox: 12 checks, 0 wrong` (rc 0).

## Production / boundaries

- Production untouched: installed `agent-loop` `97a57db1…`; resolver absent;
  `agent-loop@campaign4.service` active. No production file/unit/ledger changed;
  product/adapters frozen; sandbox run stopped by the double.
- **Sandbox ≠ real promotion**; promotion10 remains a separate signed decision.
  Prior INCOMPLETE claims (`promotion-closure-*`) retained.

**PASS** with the correct sha-binding above; returned to Tern. No edit/retry/
production change by corvid.
