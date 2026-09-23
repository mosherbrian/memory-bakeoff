# P6-r17-live-failure-rest — admission review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P6r17-admission-1`, start `02:05Z`, deadline `02:20Z`
- **Brief:** `package.md` sha256
  `a7e1bf06d6b2dabf86ac85349ea6ea3484e8fb6868d10f2aeb5eeb5e016cd013`; director
  release pinned.
- **Scope:** read-only admission + pinned witness checklist. No source edit.

## Verdict

**ACCEPTED (bounded) for failed-verification; SCOPE BLOCKER for quiet-rest.**
Failed-verification is executable on the accepted R16 bytes with a genuine
authenticated rejection and correctly identity-joined causal pairs. Quiet-rest
runs and commits, but its observation is a **hardcoded 3 s sleep**
(`case_entry.py:1487`) that does not cover the configured observation slice
(`wait_s: 8`) and exposes no configurable finite duration — it cannot meet the
contract's declared finite-interval requirement without a bounded correction or
an explicit contract decision. Two additional readiness items are pinned.

## Pin resolution

- R16 accepted source `c8e99cf9…`; candidate `../P6-r16-causal-identity/candidate/`;
  outer manifest file sha256 `3862a0a2…`; review `8acd6a49…`
  (`candidate-review-repair.md`). R14 parent `02ea693` retains all core bytes;
  R16 changes `case_entry` causal join only.
- R15 preserved live evidence `872bb3c…` and terminal `de31388` (real
  authenticated rejection/no-COMPLETE/1+1; INCOMPLETE causal timing). R16
  diagnostic replay does not change R15. R9 positive `0a77303` remains separate.
- Governing rulings `4be99bf`, `84f094e`, `883107e`, `650830c`, `b2384d7`,
  `afa126f`, `f7b0cce`, `5fefb0f`, `fc74f65`, authority `58704e9` resolve.

## Executable readiness (injected, no host effects)

| case | rc | outcome | sends | notes |
|---|---|---|---|---|
| failed-verification | 0 | `accept-open`, verified-rejection | 1+1 | receipt `causal.pairs`: worker item↔worker detection, verifier item↔verifier detection (own-action join, filename-independent) |
| quiet-rest | 0 | `accept`, `duplicate-end-ignored` | 1+1 | but observation = fixed `_t.sleep(3)` < configured `wait_s: 8` |

Exact mechanism for the live run: `fault arm --case <case> --run-root SUITE_ROOT
--control <control> --actor cairn` then `run-case --case <case> --suite-root
SUITE_ROOT`; onset via the producer sidecar (`item`/`time`/`provenance`/
`uncertainty`), no synthesized onset; evidence at
`faults/<case>.applied.json`, `claims/`, `latency.jsonl`, `witness-rows.jsonl`,
`receipt.json`. Failed-verification requires the tool-applied post-publication
tamper detected by a genuine verifier; missing explicit onset item → `E_NO_ONSET`.

## Pinned readiness items

1. **Quiet-rest observation duration (scope blocker).** The accepted code's
   finite quiet window is a fixed 3 s; the configured observer slice is 8 s
   (`wait_s: 8`). No plan/config knob sets the observation duration, so quiet-rest
   cannot be signed as covering "the actual configured cycle" without either a
   bounded `case_entry.py` correction to make the window configurable/≥cycle or a
   Tern decision accepting 3 s. Return for the smallest bounded correction before
   a quiet-rest live release.
2. **Stale inherited executable strings.** R16 `stagec-plan.json`
   `host_commands` and per-case `fault_controls.command` still point at
   `P6-r8-case-execution/...` (`deposit_wake`, `wake`, `case_entry.py` fault arm).
   The signed R17 plan must replace these with the **actual accepted R16 paths**
   and execute the preparation commands **verbatim** (no retyping roots/
   timestamps); record and reconcile any discrepancy before binding.
3. **Binding/causal checks.** Confirm in the live receipt that causal pairs use
   worker item↔worker detection and verifier item↔verifier detection regardless
   of filename order (verified injected); D1 requires an explicit nonempty
   matching onset `item` (missing/null/empty/wrong → `E_NO_ONSET`); no synthesized
   producer onsets.

## Negative control (unshared)

Wrong action/execution (`E_ACTION_MISMATCH`/`E_EXECUTION_MISMATCH`),
missing/conflicting item (`E_NO_ONSET`/`E_ITEM_MISMATCH`/`E_CONFLICT`), and
pre-planted starts/ends without delivery (`E_UNDELIVERED`) must reject before a
false case PASS. Final matrix separates these two fresh cases from R9's
historical positive and the unexecuted lost-completion/queued cases; no four-case
PASS, adoption, retirement or research claim.

## Witness checklist (pinned)

- One case at a time (failed-verification first), fresh isolated root/action/
  executions and NEW fixture pair; one Tern preparation release per case; binding
  review checks raw IDs/profile/lane/workdirs/sockets/incarnations + canonical
  derive; no stopped historical fixtures or stale signatures; partial launch
  preserved and reconciled, never blind relaunch.
- Tern signs exact current plan/config/binding/code manifest and commands against
  the accepted R16 entrypoint; explicit grants, observation bound, outer
  `live_stop_utc`, fault actor/effect/onset, cleanup IDs/units; arm and verify
  exact-ID automatic cleanup before execution; archive evidence first.
- Both: timer callback identities/authoritative deadlines current; grants
  preserved through continuation; stricter outer stop honored; cleanup verified
  for owned fixture seats/units only; per-file binding; actual exit codes;
  detect30/recover60/total90, suspicion180/60/240; acknowledged progress is
  recovery (queued alone is not); source uncertainty/unjoined timestamps →
  INCOMPLETE; work duration separate; no manufactured onset.

## Bounds

Candidate ceilings `1260/1035` unchanged. NEW witness allocations (admission
corvid15 m; two preparations cairn10 m; two binding reviews corvid5 m; two live
operations cairn20 m each inclusive cleanup margin; two result reviews corvid15 m;
final matrix corvid5 m) = corvid60/cairn60/worker0; R15's unused corvid25/cairn30
were cancelled — these are new. If a live operation cannot fit 20 m, return the
exact proposed allocation before execution. No repairs/retries; unused allocation
cancelled at terminal; every dispatch/receipt carries an executable notification
with exact profile/session/action/absolute path.

## Effect

Admission: **failed-verification ACCEPTED (bounded)**; **quiet-rest SCOPE
BLOCKER** pending the observation-duration correction. No implementation or live
release conferred. Returned to Tern.
