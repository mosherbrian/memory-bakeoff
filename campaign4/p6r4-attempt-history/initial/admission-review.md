# P6-r4-notify-timer-drain — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P6-r4-notify-timer-drain/package.md`,
  sha256 `c5725d291c4362bfda2e0c76ee883ad3e666b0b475bf4785a81062332606a03a`,
  commit `214e73c` (per receipt; file hash re-derived and matches)
- **Receipt:** `admission-receipt.json` (`4ab68b30…`), start
  2026-09-22T01:47:35Z, deadline 2026-09-22T02:02:35Z
- **Pinned checklist:** `three-case-checklist.md` (written this pass)

## Disposition

**ACCEPTED**, bound to the exact bytes above, together with the pinned
`three-case-checklist.md`. The contract is a narrow successor that targets the
three concrete recovery-verdict defects (N/T/O) as blocking, keeps all inherited
requirements, and is feasible under injected boundaries with the explicitly
permitted private `/tmp` notification test. No live seat/service/effect occurs
during admission.

## Pinned inputs resolve

- Base parent `campaign4/packages/P6-r3-cli-recovery` at
  `4b02d0aa14d711b3d5673892ce760deb601f3ce5` — resolves; its full manifest and
  `candidate-review-recovery.md` (`3cc00b9e…`) are named.
- Parent contract `a35eace…` and preregistered CLI cases `f87810b…`; parent
  director repair decision `d925834…`; allocation extension `643d1ae…` — all
  resolve.
- Rulings turn `883107e…`, recovery `4be99bf…`, identity `84f094e…`, retirement
  `b2384d7…`, clock `650830c…`, deployment `f858729…`, context `54b6087…`/
  `92467e4…`; accepted P5-r2 `80092f9…`; core `d27d5be…`; P2 `5bfbb071…` — all
  resolve. Short pins to be expanded in the receipt.

## Contract validity

The three defects are exactly the ones my recovery verdict found, and each is
required as **BLOCKING** with observable evidence:

- **N (notification wait):** replace `poll`+`sleep` with an actual
  notification-backed wait using the available runtime/OS file-notification
  primitive; persisted event reading is the **drain**, not the primary trigger;
  attach before the initial drain to close the subscribe/read race; handle
  startup-existing event, partial record, truncation/rotation, overflow/loss,
  restart and timeout with bounded owned reconciliation; no busy/model polling.
  Evidence is the production notification class on private `/tmp` files with an
  actual-format end appended **after** the wait starts, plus the same CLI with
  injected runtime producers on distinct worker/verifier streams, and proven
  bounded timeout, cancelled watcher and fd cleanup. This is explicitly allowed
  in Stage A and touches no agent-deck effects.
- **T (enforced timer):** declare a stable action→unit mapping in the bound
  plan/manifest used consistently by create/query/cancel/callback; a missing
  allowlist or failed `systemd` creation returns owned failure, prevents a
  successful-supervised-dispatch claim, and reconciles already-delivered work;
  in-memory create is never a real timer. Evidence is the exact CLI trace with a
  relative `systemd-run` timer carrying the remaining authorized duration and an
  executable candidate callback, then query/cancel, with callback authority and
  duplicate/stale/early/cancelled behavior after reopen, plus rejected-allowlist
  and failed-runner negatives.
- **O (delivered-outbox drain):** settle the matching durable intent only after
  transport acknowledgement **and** actual verifier start/outcome evidence are
  correlated to the exact action/execution/message — not merely because the
  phase is terminal; preserve queued/ambiguous handling, no blind resend or
  premature clear. Evidence is the positive CLI→verifier receipt→terminal→
  restart→rollback with zero unresolved delivered intents, no second send and
  consistent archived ledger, and the negative ambiguous case leaving the intent
  pending with rollback BLOCKED; crash before/after delivery/ack reconciles the
  same identity. The rollback guard must not be removed.

Parent C1–C12 and 156+59 semantics are retained; changes are confined to the
connected N/T/O paths and supporting plan/tests/docs, with no broad rewrite or
silent weakening, and a not-implemented gate must be reported FAIL/incomplete
rather than non-blocking. Stage limits keep all host services, seat actions,
runtime-wrapper edits, real Signal and clock changes out of A/B.

## Allocation

Worker initial ≤30m + sole repair ≤10m = **40m**; candidate verifier ≤15m per
pass × 2 = **30m**. Prior cumulative **205 worker / 175 verifier** (the recovery
verdict's 185/175 was stale; extension `643d1ae` added 20 worker minutes), plus
40/30 = **245 worker / 205 verifier** — arithmetic correct; parent r3 worker60
and candidate40 spent, no reset. The single live witness 15 and cairn fixture 15
remain unspent, reassigned and HELD, not added again. Admission ≤15m + one ≤10m
confirmation; actual runtime/cost distinct from ceilings.

## Release conditions

Release only after independent ACCEPTED unchanged contract + checklist pinned,
director admission recorded and the parent `EXHAUSTED` disposition pinned; cairn
checks no overlap, records trusted start/deadline before wake with a relative
timer, and preserves the version before the sole repair; bound output before
corvid. Real expiry stops work, BLOCKED+wake Tern after session/hash
reconciliation; no reset or second repair. Candidate PASS returns to Tern for the
live signature.

## Non-blocking observations

- The parent `EXHAUSTED`/supersession disposition and its full archive are not yet
  present in this package directory; cairn must pin them before worker release.
- The private `/tmp` notification test is the only host-touching allowed operation
  in Stage A and must remain confined to private temporary files (no agent-deck
  runtime effects, no live seats/services).

## Effect

Bound to contract bytes
`c5725d291c4362bfda2e0c76ee883ad3e666b0b475bf4785a81062332606a03a` at commit
`214e73c` and to `three-case-checklist.md`. Cairn may release the worker only
under the recorded conditions above. No live seat/service/effect, runtime-wrapper
edit, real Signal, host clock change or script retirement occurred.
