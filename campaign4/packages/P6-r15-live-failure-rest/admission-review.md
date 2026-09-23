# P6-r15-live-failure-rest — admission review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P6r15-admission-1`, start `00:35Z`, deadline `00:50Z`
- **Brief:** `package.md` sha256
  `c6a79a3a3bc44e242d1bc768d6fe8ed652730ae9a43b77ba5dd15df23ec560cc`; director
  release `director-release.txt`/`director-release-receipt.json`
- **Scope:** read-only admission + executable readiness + pinned checklist. No
  source edit, no live activity.

## Verdict

**ACCEPTED (bounded).** Both cases are feasible with the accepted R14 entrypoint
and do **not** require implementation or an invented control. An injected
readiness check on the final R14 bytes reaches `verified-rejection`/accept-open
for failed-verification and `duplicate-end-ignored`/accept for quiet-rest. Three
bounded readiness items are pinned (stale executable paths in the plan; onset
requirement; finite quiet observation window). Conditional Tern release follows
this admission plus the pinned checklist; R15 is evidence-only, no worker
allocation.

## Pin resolution

- R14 candidate source commit `02ea693e48cc…`; outer manifest file sha256
  `8584cbed8a97…` = `candidate/manifest.json`; review `93127630…` =
  `candidate-review-repair.md`. R14 `acceptance.json` present
  (`ACCEPTED_SCOPED_CANDIDATE`, source `02ea693e…`, manifest `8584cbed…`,
  verification `93127630…`) — co-pinned.
- Prior evidence: R13 accepted core `5410332`; R10 terminal `5826c33`; R9
  positive `0a77303` (historical, not an R14 witness).
- Governing rulings resolve: `4be99bf`, `84f094e`, `883107e`, `650830c`,
  `b2384d7`, `afa126f`, `f7b0cce`, `5fefb0f`, `fc74f65`.
- Plan enumerates the two target cases with controls: `failed-verification` →
  `corrupt-after-worker`; `quiet-rest` → `none-declared`.

## Executable readiness (injected, no host effects)

Ran both cases against the R14 candidate entrypoint with the accepted
exact-CLI test pattern (intercepted collaborators, no `--simulated`):

| case | rc | outcome | sends | notes |
|---|---|---|---|---|
| failed-verification | 0 | `timecheck accept-open`, `decision verified-rejection` | 1+1 | post-commit tamper, expected/observed hashes, worker open |
| quiet-rest | 0 | `timecheck accept`, `duplicate-end-ignored` | 1+1 | setup committed, reopen no new send |

Exact mechanism: `fault arm --case <case> --run-root SUITE_ROOT --control
<control> --actor cairn` then `run-case --case <case> --suite-root SUITE_ROOT`;
onset via the producer sidecar or `fault_onset.py mark` (uncertainty explicit);
applied evidence at `faults/<case>.applied.json` plus `claims/`, `latency.jsonl`,
`witness-rows.jsonl`, `receipt.json`. Failed-verification needs an authentic
post-publication mismatch applied by the tool and detected by a genuine verifier;
quiet-rest needs a reachable terminal+disposition and a bounded restart/reopen.

## Bounded readiness items

1. **Stale executable paths in the plan.** `stagec-plan.json` `host_commands`
   (`deposit_wake`, `wake`, `systemctl`, `systemd_run`) and the per-case
   `fault_controls.command` strings still point at `P6-r8-case-execution/...`,
   and `wake` is a live host wrapper. Tern's signed release must pin the **exact
   accepted R14 candidate entrypoint** (`case_entry.py 64edb54e…`), the pinned
   R5/R6 preparation/fixture dependencies, and rehashed commands — do not trust
   the plan's descriptive strings verbatim, and reinventory the host wrapper/
   runtime (older signatures are stale).
2. **Onset requirement.** A failed-verification result without an independent
   onset is INCOMPLETE (`E_NO_ONSET`), never a PASS; normal slow startup is not
   induction. Applied control + independent source onset required.
3. **Finite quiet observation.** Quiet-rest must declare a finite interval
   covering the observer/reconcile cycle and invoke bounded restart
   reconciliation; no eternity claim; no synthetic failure rows added.

## Negative control (unshared)

Wrong action/execution and missing required onset must reject before any false
case PASS: `E_ACTION_MISMATCH` / `E_EXECUTION_MISMATCH` (T1 guard) and
`E_NO_ONSET` (causal gate); plus `E_SELF_VERIFY`/`E_UNKNOWN_PRODUCER` from the
accepted core. The final matrix must distinguish these two fresh cases from R9's
historical positive and from the still-unexecuted lost-completion/queued cases;
no four-case PASS, adoption, retirement or research claim from two cases.

## Checklist (pinned; full detail in `admission-checklist.md`)

- Fresh isolated root/action/executions and a NEW fixture pair per case; one at a
  time, failed-verification first; cairn prepares only on a concrete signed
  preparation release; binding review checks raw IDs/profile/lane/workdirs/
  sockets/incarnations and canonical derive; no stopped historical fixtures or
  stale signatures; partial-launch race preserved and reconciled, no blind
  relaunch.
- Tern signs exact current plan/config/binding/code manifest and commands for the
  accepted entrypoint; work grants, observation bound, outer stop, fault
  actor/effect/onset, precise cleanup IDs/units explicit; exact-ID automatic
  cleanup armed and verified before execution; archive before cleanup.
- Cairn executes exact signed commands, captures actual exit/stdout/stderr,
  transport receipts and source timestamps; fault claims need applied evidence;
  corvid independently witnesses each case before the next release. No manual
  sender, synthetic producer, fabricated receipt or source edit.
- Both: timer callback identities/authoritative deadlines, grants preserved
  through continuation, stricter `live_stop_utc` honored, cleanup verified for
  owned fixture seats/units only, per-file binding and actual exit codes.
  Recovery timing detect30/recover60/total90, suspicion180/60/240; queued alone
  is not recovery; source uncertainty/unjoined timestamps → INCOMPLETE; work
  duration separate.

## Bounds

Evidence-only: worker 0; NEW witness allocations admission15m, two preparations
cairn10m each, two binding reviews corvid5m each, two live operations cairn20m
each (inclusive cleanup margin; if it cannot fit, return the exact proposed
allocation before execution), two result reviews corvid15m each, final matrix
corvid5m. Candidate ceilings `1200/975` unchanged. No repairs/retries; unused
allocation cancelled at terminal. Every dispatch/receipt carries an executable
completion notification with exact profile/session/action/absolute path.

## Effect

Admission **ACCEPTED (bounded)** with the pinned checklist and three readiness
items. No implementation or live release conferred. Returned to Tern.
