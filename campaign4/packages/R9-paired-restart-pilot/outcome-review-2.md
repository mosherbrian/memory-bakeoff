# R9-outcome-review-2 — independent outcome review

- **Reviewer:** corvid-dsh. Read-only; no new trial, production effect or fleet
  prompt. Within the 20m bound.
- **Intake:** outcome-review-2 receipt `9aa8cf26…`; `execution-2-claim.json`
  hash `9aa8cf26…`; **all 34 listed files hash-match** (recomputed from bytes).
- **Verdict: PASS — the real paired trial completed under the amended prereg,
  with bounded evidence deviations; conclusions are operational only.**

## Preregistration + `/new` amendment — honored

`new-session-execution-amendment.md` supersedes only the fresh-boundary/
restoration mechanism (sparing the old state-file rewrite), keeps frozen
inputs/templates/treatment/scoring/coin order/limits, and forbids copying
`fixed.sh`. Verified:

- **Order fixed before prompts:** `random_bit 1` → C then T; release 14:34Z,
  first precheck 14:36:41, first phase prompt 14:37:34.
- **Four unique fresh sessions, engine-joined:** C-p1/p2 and T-p1/p2 have
  distinct ids; I independently found all four ids in the opencode engine
  store, and the claim records `engine_store`/`state_matches` true after first
  reply. Prior conversation not restored (per amendment).
- **Equal task/model/files/budgets:** both arms use the identical unchanged
  `test-fleet-poller.sh` `0894381c…`, `rowcheck` `5334ee6a…`, `acp-worker`
  `6871ceb1…`, same model `opencode-go/muse-spark-1.3-contributor`, 10m phases.
- **Treatment ≤300 words, inside phase1, T-only:** `T-summary.txt` is 148 words,
  appears verbatim in `T-p2-prompt.txt`, and is absent from `C-p2-prompt.txt`
  (C's block is empty). Summary turn 8s, inside T's 83s phase 1.

## Outcomes recomputed from bound bytes

On `execution-2/arms-final/{C,T}` with the unchanged test and pinned
`rowcheck`/`acp-worker`: both **rc=0, 0 failed** (success criterion met). The
solutions are independent, not the known fix: C `ae053e06…`, T `06ece045…`,
neither equal to `fixed.sh` `6607dc1a…`; diffs touch only `fleet-poller.sh`
(C 17 lines, T 25). Pre-state was the broken copy (`a987e2e9…`) reproducing
116/1 rc1 in each arm.

## Deviations / limits (recorded, not disqualifying)

1. **Timing metric.** The preregistered secondary was "minutes to first passing
   run"; the claim reports **total phase-2 wall time** (C 263.1s, T 98.0s). That
   is not first-pass time, and with C run first the order confounds any T/C
   difference (practice effect). Recorded as a paired observation only; no
   efficacy inference from n=1.
2. **Environment-dependent tally.** The bound post-run is `117 passed, 0 failed`
   with `skips: 0`; a clean re-run yields **116 passed, 0 failed with exactly one
   identical SKIP** per arm (`cannot resolve the conductor's wrapper`). The
   prereg explicitly allows a documented identical SKIP and rc 0/0-failed holds
   in both arms, so outcomes stand — but the "117/0, skips 0" figure is
   environment-specific and should be recorded as such.
3. **`timer_cancelled: false` semantics.** Per-arm `timer_cancelled:false` reads
   as "not cancelled", while the prose says the one-shots were armed, never
   fired, and stopped at turn end. I confirmed no `r9e2` timers/units remain on
   the host. The field name should be reconciled/renamed (one-shot retired, not
   cancelled) so the record is unambiguous.

## Contamination and integrity

Records scan for `fixed.sh`, `director-closure`, `cbc9d52`, `git log/show/diff`,
`R8-work-task` → **0 hits**; `conductor-chat/` appears only as a path string
inside the test inputs. `test/rowcheck/acp-worker` unchanged; ordinary notes
retained in both arms. No install/restart/activation performed here.

## Exactly supported conclusion

The `/new` mechanism plus an optional self-written summary can be run as a
complete paired procedure on this seen task: both arms fixed the exit-127
defect to a green unchanged test, with one paired observation (T's phase 2
shorter than C's, order-confounded). This is **operational completion only** —
not evidence that memory helps in general, not a clean estimate, and **no
streamB release** or scoring change. Old execution-1 remains INCOMPLETE.

*Reviewed: `outcome-review-2-receipt.json`, `execution-2-claim.json`
(`9aa8cf26…`), `preregistration.json`, `new-session-execution-amendment.md`,
`run-plan.md`, `input-manifest.json`, all `execution-2/**` evidence (hashes
recomputed), host `systemctl --user` timer/unit state, opencode engine store.*
