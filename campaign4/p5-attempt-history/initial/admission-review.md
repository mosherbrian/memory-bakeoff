# P5-clock-ingress — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P5-clock-ingress/package.md`,
  sha256 `ca8a9e054025f5cd9b28b79addf8c970d5d3a4289d2e145fabc9dc43325da710`,
  commit `ec3325463eff8677fab733d2413fd7bc8266fbe8` (re-derived; working tree
  matches)
- **Receipt:** `admission-receipt.json` (`4994acec…`), start
  2026-09-21T22:52:20Z, deadline 2026-09-21T23:07:20Z

## Disposition

**ACCEPTED**, bound to the exact bytes above. The contract measures the intended
question — make the trusted write boundary own receipt time and deadline
derivation before any live ledger adoption — its inputs resolve, its required
behavior is complete and testable, and the allocation arithmetic is correct.
This is admission, not execution verification.

## Pinned inputs resolve

- `campaign4/packages/P4-r2-durable-events` at
  `4c07bd83ec571bec9aa4022369f3ec7e9263051b` — resolves; its `src/driver.py`
  is `8f7c61ce…`, the cleaned accepted tree (no duplicated method bodies), with
  36 local tests and prior verification files.
- `campaign4/CLOCK-AUTHORITY-DECISION-20260921.md` at
  `650830cae62e5f163409d7a906bbb626f58ec8e7` — resolves; the contract mirrors
  its required design (host-side trusted `recorded_at`, separate
  `occurred_at`, deadline from authorized duration/pinned grant, explicit
  justified skew tolerance, monotonic in-process discontinuity detection,
  restart persisted UTC + new monotonic epoch, no occurrence-proof claim).
- `campaign4/CONTROLLER-DEPLOYMENT-20260921.md` at
  `f858729239608c3b178011aa1e0c631e92c37cb7` — resolves; supersedes older lane
  parentheticals without changing role/authority, as the contract states.
- P3-r3 `d27d5be…` and frozen P2 `5bfbb071…` — resolve.
- Abbreviated commits are explicitly to be resolved to full ids in the receipt;
  no moving-HEAD dependency.

## Contract validity

- **Task/evidence** (lines 7–13): the accepted rehearsal uses an injected
  `FakeClock` and caller `event.at`, suitable for simulation but not a trusted
  production ingress; the observed future-dated manual rows motivate fixing
  ingress first. Accurate against the clock-authority decision, and the contract
  does not treat host clock as occurrence proof.
- **Required behavior** (lines 30–64) is complete and testable:
  1. One clearly identified trusted ingress obtains `recorded_at` from an
     injected UTC-aware host clock on append; caller/seat cannot override it,
     the actor attribution, or an authorized deadline; untrusted `occurred_at`
     and provenance are kept separate; legacy lower-level APIs are explicitly
     internal (no alternate accepted external route); trusted receipt metadata
     is persisted and replayed unchanged, so reopening never stamps historical
     events with now.
  2. Trusted start is recorded before dispatch; the deadline derives from its
     authorized phase/action duration or a separately pinned director-approved
     absolute grant; caller attempts to extend a deadline, change the
     phase/grant association, use malformed/nonpositive duration, or exceed
     allocation are rejected; validation remains ledger-authoritative **after**
     ingress verifies the write; a valid far-future deadline within a real
     grant is not occurrence-time skew.
  3. Claimed occurrence is validated separately against host receipt time with a
     finite justified future-skew tolerance; malformed or excessively future
     claims are rejected or quarantined with deterministic owned evidence before
     affecting lifecycle; backdated/delayed receipts retain both times and
     cannot retroactively authorize work or erase expired allocations; no
     clock-based completion proof is claimed.
  4. Host UTC plus in-process monotonic elapsed time detect forward/backward
     discontinuity, with an explicit threshold and owned response; restart uses
     persisted UTC/grants and a new monotonic epoch and never compares counters
     across epochs as absolute timestamps; deadlines are not reset or silently
     lengthened after an anomaly, and ambiguous continuity requires bounded
     reconciliation.
  5. A production-clock adapter reads host time while tests inject clocks; no
     sleeps/network/actual dispatch; the named test set (forged receipt fields,
     minute-only/naive/unsupported instants, future/backdated occurrence,
     legitimate long deadlines, delayed completion, duplicated append, restart,
     wall-clock jumps, expired grants) and the requirement to report exact
     schema and error/owned dispositions; 36 rehearsal + 59 core regressions
     preserved, with copied-API adaptation authorized but lifecycle weakening
     forbidden.
  6. Corvid independently exercises unshared forged-field and clock-jump cases
     through actual ingress and reopened stores, verifies no alternate public
     write path bypasses ingress, compares input/output persistence rather than
     helper units, and verifies the full manifest and regressions with **no
     duplicated method bodies** (explicitly incorporating the prior artifact
     defect); a passing count alone is insufficient and evidence is simulated
     only.
- **Outputs/permissions** (lines 66–73): only `src/`, `tests/`, `fixtures/`,
  `README.md`, `interface.md`, `implementation-report.md` here and disposable
  `/tmp`; stdlib only; no live `state.json`, watcher/services, model calls, seat
  actions, research, upgrades, migrations or previous-package edits; no host
  clock change; no retrospective campaign-log migration; pinned originals stay
  intact.
- **Independence** holds: author/director Tern, reader/verifier corvid, worker
  kiln, controller/duty cairn; the reader did not author or repair this contract.

## Allocation

New question P5: worker initial ≤40m + one eligible repair ≤15m = **55 worker**;
verifier ≤20m per pass including post-repair = **40 verifier**; admission ≤15m
plus one ≤10m confirmation. P4 historical grants 133m56s/85m remain separately
recorded and spent, never reset or transferred; actual usage is distinct from
attempt ceilings and provider charges — arithmetic and history handling correct.

## Non-blocking observations

- Tern's separate P4-r2 `acceptance.json` is not yet present in the P4-r2 tree;
  the dispatch requires cairn to pin it before execution — a cairn release step,
  not a contract defect.
- The future-skew tolerance value and discontinuity threshold are intentionally
  delegated to the worker with explicit justification (no blanket N-minute
  rule), as the clock-authority decision requires; the contract correctly
  demands they be selected and documented rather than fixed arbitrarily.
- Abbreviated input commits (`650830c`, `f858729`) are to be resolved to full
  ids in the receipt as the contract states; I resolved them for this review.

## Effect

Bound to contract bytes
`ca8a9e054025f5cd9b28b79addf8c970d5d3a4289d2e145fabc9dc43325da710` at commit
`ec3325463eff8677fab733d2413fd7bc8266fbe8`. Cairn may dispatch this exact
contract under the recorded conditional release once admission is recorded and
Tern's P4-r2 acceptance is pinned; changed bytes require independent
confirmation. No live integration or host clock change.
