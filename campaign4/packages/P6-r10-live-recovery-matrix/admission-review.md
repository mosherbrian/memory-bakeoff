# P6-r10-live-recovery-matrix — admission review (independent)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r10-admission-1`, start `2026-09-22T16:45Z`, deadline
  `2026-09-22T16:55Z` (`campaign4-p6r10-admission-deadline.timer`)
- **Brief:** `P6-r10-live-recovery-matrix/package.md` sha256
  `b6585efa82d9d921a350d44f22abf014deb20a5a3b588560413ecdee2b93923f`
- **Scope:** independent admission + pinned four-case checklist on exact-CLI
  fault feasibility. Read-only; no production edit, no run, no send, no pin
  modified.

## Verdict

**ACCEPTED (bounded).** All named pins resolve and the accepted exact CLI
(`P6-r9-observer-lifetime/src/case_entry.py` sha256 `9a1bb23c…`, candidate
`f1d7c86`) already contains first-class implementations for each of the four
required cases and their fault controls; none requires a new harness feature.
One bounded materialization precondition attaches (queued-ambiguous-restart must
demonstrate **both** `queued` and `ambiguous` durable receipts in one case — see
§Precondition). No entrypoint contradiction was found that would force
rejection. Admission confers no live release; Tern still owes exact per-case
plans, signatures and releases.

## Pin resolution (all four-case inputs)

- **Brief:** sha256(`package.md`) = `b6585efa82d9…` (the wake's
  "exact-CLI fault feasibility" identifier **is** the brief hash).
- **Parent pin:** commit `0a77303c96a92fc7484789425e19d97b9b60d76b`
  ("Accept first real positive handoff and preserve live cleanup evidence")
  resolves and contains `live-positive-acceptance.json`
  (sha256 `1df268c1…`) and `live-review-3.md` (sha256 `89f28ccb…`).
- **Candidate:** commit `f1d7c86f0b38fb653734beb9d906dae44a10a41a` resolves;
  composition manifest on disk sha256 `161afac5…` (29/29 file hashes already
  independently rehashed by me in the r9 live review).
- **Full-gate pin `77d5b03ec040`:** resolves as the `verdict_sha256` of
  `candidate-acceptance-repair-3.json`, which equals sha256 of
  `candidate-review-verification-completion.md` (34 tests PASS on `f1d7c86`).
- **Governing inputs:** commits `4be99bf` (recovery), `84f094e` (identity),
  `883107e` (turn/handoff), `b2384d7` (retirement map), `650830c` (clock),
  `92467e4` (package sessions), `7abab5f` (portability/harness amendment),
  `afa126f` (shadow reference), `58704e9` (LIVE-AUTHORITY) all resolve.
- **Tools:** preparation/cleanup remain the P6-r6 exact hashes pinned by
  `preparation-release-4.json` (prep tool `462596ee…`, cleanup `57bb7e4e…`);
  `case_entry.py` on disk still `9a1bb23c…` — accepted source byte-identical.

## Exact-CLI feasibility (mechanism, not keywords)

Plan enumerates all five cases with per-case actions/timer units
(`stagec-plan.json`); `run-case` dispatches one case and already branches for
each (case_entry.py:1173 lost-completion, :1212 failed-verification, :1217
queued-ambiguous-restart, :1268 quiet-rest). Controls are executable and
enumerated (`case_entry.py:749-751`): `none-declared`, `hold-verifier-texts`,
`corrupt-after-worker`, `transport-queued-first`, `delay-worker-completion`;
`fault_arm` records actor/time/scope before any send (`:761-785`) and
`_check_causal` enforces armed < onset < detection with finite uncertainty
(`:845-886`).

- **lost-completion — FEASIBLE.** Needs a real imposed delay plus a source
  onset. `delay-worker-completion` supplies the delay; the accepted R4 resume
  waits the remainder of the ORIGINAL grant (never extends, never resends)
  while the first bounded slice still misses — exactly what the live positive
  run exercised for the observer path. CLI requires first-run
  `owned-failure/no-end`, then `_reattach_cli` commit, `msg` count +1 only,
  prior `outbox-sent:` identities unchanged, worker claim retained
  (`:1173-1211`). Onset via the plan's producer sidecar / `fault_onset.py mark`
  protocol. No missing mechanism.
- **failed-verification — FEASIBLE.** `corrupt-after-worker` applies the
  artifact tamper only after the worker handoff durably commits
  (`_maybe_apply_corrupt_tamper` `:614-670`, driven `:1039-1058`); the CLI
  forbids any COMPLETE close (`:1212-1216`) and the verifier must stay open
  (`expect_open`, `timecheck` accept-open `:1398-1411`). Independent
  recompute (`check: recompute-sha256`) reconciles reason/disposition to
  artifact bytes.
- **queued-ambiguous-restart — FEASIBLE WITH PRECONDITION (§below).** Requires
  real transport receipts and durable restart. `transport-queued-first` /
  `hold-verifier-texts` drive the candidate transport's deposit-time wake;
  `fixture_control._classify_receipt` (`:101-111`) maps rc0+wake→sent,
  rc3+wake→queued, else→ambiguous, and labels induced. CLI then requires BOTH
  `queued` and `ambiguous` present among durable receipts and `induced` true
  (`:1222-1245`), then a real reopen `_rerun_cli` yielding
  `duplicate-end-ignored` with no new sends (`:1255-1267`).
- **quiet-rest — FEASIBLE.** `none-declared`; a real setup commit, a 3 s
  no-growth window on both streams and msg count, then reopen
  `duplicate-end-ignored` with unchanged sends (`:1268-1295`). Reachable
  without inventing work; the case cannot be satisfied by labeling an active
  action as rest because the setup must commit and then hold still.
- **Common:** exact-case suite roots, per-case pair/evidence, raw-record
  director binding, pre-armed exact-ID cleanup, real exit-code capture and
  immediate corvid dispatch are all existing CLI/tool behaviors, not new
  features.

## Precondition (bounded, must be fixed in Stage B materialization)

`queued-ambiguous-restart` requires **both** transport kinds in one case
(case_entry.py:1234 and :1238). The current controls each target a single
interruption (`transport-queued-first` holds the first worker delivery;
`hold-verifier-texts` holds verifier text), and no control is documented to
emit both a `queued` and an `ambiguous` durable receipt in a single run. The
mechanism to *observe* both states exists and is fail-closed (missing kind ⇒
`E_CASE_FAIL`, INCOMPLETE). Before release, Tern must specify, in the exact
plan/control params for this case, how both states are produced and preserved
(e.g. a sequence/param that yields rc3-then-ambiguous), or split nothing —
do not satisfy the case by relabeling one state twice. This is a plan
specification obligation, not a rejection of the entrypoint.

## Pinned four-case checklist

Each case's release must carry, bound to per-file hashes:
1. **Bound release** — Tern `stagec-task` signature over plan+config+binding+
   code manifest; fresh suite root/actions/executions; no old stopped sessions
   or expired signatures; `simulated=false`.
2. **Real identity/transport/runtime** — raw launch records → canonical
   corrected binding; live sockets/incarnations/registry/lanes checked;
   `derive-config` rc0.
3. **Applied fault** — `faults/<case>.applied.json` with actor/control/params,
   `induced=true` for fault cases; independent source onset
   (`onset_protocol`) with finite uncertainty; `_check_causal` armed<onset<det.
4. **Claims/artifact/verdict** — worker and verifier claims, recomputed
   artifact hashes, durable ledger/outbox, `committed_actions`/`settled_actions`
   and `timecheck`.
5. **Per-case outcome:**
   - lost-completion: first-run owned `no-end`, recovered via SAME execution,
     `msg` +1 only, no mutated send ids, no extended grant; bounded owned
     outcome; timing accept.
   - failed-verification: actual corruption independently rejected, never
     COMPLETE; `accept-open`; reason/disposition reconcile to bytes.
   - queued-ambiguous-restart: both `queued` and `ambiguous` durable receipts,
     induced-labeled; reopen `duplicate-end-ignored`; ≤1 delivery per intended
     action; authoritative-receipt rule honored (ambiguity stays
     pending/BLOCKED, never guessed successful).
   - quiet-rest: post-commit quiet across observation and reopen, no fresh send
     or repeated alarm; not an active action relabeled.
6. **Timing ruling** — explicit onset detect≤30 s, recover≤60 s, total≤90 s;
   suspicion 180/60/240; signed work duration separate; queued alone is not
   recovery; missing joins/unknown uncertainty = INCOMPLETE; negative controls
   and false alarms weigh equally.
7. **No duplicate effect / timers** — no duplicate after restart or backstop
   fire; host timers reconcile to ledger authority and original deadlines.
8. **Cleanup + archive** — automatic exact-ID archive/cleanup pre-armed and
   verified; only exact fixture IDs stopped/removed and owned units retired;
   actual process exit code archived (never reconstructed if missing).
9. **Independence + matrix** — corvid per-case verdict bound to per-file
   hashes, then a four-result matrix distinguished from the earlier positive
   witness; accepted source byte-identical, 34-test gate carried (not rerun for
   another fixture); any source drift invalidates release.

## Effect

Admission **ACCEPTED** with the pinned checklist and the single
queued/ambiguous materialization precondition. No implementation by operator
or verifier is authorized; Tern materializes the exact per-case plan and
release. Returned to cairn/Tern.
