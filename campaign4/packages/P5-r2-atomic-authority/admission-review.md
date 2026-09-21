# P5-r2-atomic-authority — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P5-r2-atomic-authority/package.md`,
  sha256 `e09c313c5c99d14c9812b1bbab678a1a8e65b37170d6319cbdab8ac83acba890`,
  commit `7b5772e40fbc4b30c025a87572ef39a906dcca5f` (re-derived; working tree
  matches)
- **Receipt:** `admission-receipt.json` (`20552421…`), start
  2026-09-21T23:37:49Z, deadline 2026-09-21T23:47:49Z

## Disposition

**ACCEPTED**, bound to the exact bytes above. The contract addresses a real,
independently reproduced boundary breach; its required correction and completion
checks are complete and testable; inputs resolve; allocation arithmetic is
correct. This is admission, not implementation verification.

## The claimed breach is real (reproduced on the pinned parent)

Ran `director-mixed-atomic-probe.py` against the parent at
`88f2c18b68c1f71ace8911cec7b74a3df752d2e4` (`src/ingress.py 371b189d…`,
matching the contract's rejected baseline):

- **Parent: `ACCEPTED`.** A claim supplying **both** `atomic.hold` and
  `atomic.decide` was admitted. The persisted `mixed-d` row carries a **forged
  actor** (`seat=kiln, role=director`) with caller time `2099-01-01T00:00:00Z`
  and **no trusted `receipt`/`_trusted` stamp**, while the `mixed-v` verdict was
  trusted-stamped. This is the exact actor/time authority breach the contract
  describes (ingress validates hold then returns; `Store.append` prefers
  decide).

## Pinned inputs resolve

- Parent `campaign4/packages/P5-clock-ingress` at `88f2c18…` — resolves; its
  `src/ingress.py` is `371b189d…`.
- Parent `package.md` `ec332546…`, `director-repair-decision.md` `a339939…`,
  `allocation-extension-1.md` `92299f8…`, clock decision `650830c…`,
  deployment `f858729…`, accepted P3-r3 core `d27d5be…`, frozen P2 `5bfbb071…`
  — all resolve (abbreviated commits to be expanded in the receipt).
- `director-mixed-atomic-probe.py` is present in this package as independent
  evidence.

## Contract validity

- **Task/evidence** (lines 7–22): P5 ceilings 65/55 spent with acceptance
  withheld; the mixed `hold+decide` form validates hold then lets
  `Store.append` prefer decide, committing COMPLETE plus a forged
  kiln/director decision dated 2099 with no trusted receipt. Accurate, and the
  fix is scoped to one unambiguous validation/stamping path per atomic
  operation without removing valid close/hold or adding blanket bypasses.
- **Completion check** (lines 39–61) is complete and testable:
  1. Reproduce the mixed-commit on the pinned parent; candidate rejects it
     deterministically before either event persists; cover key ordering, unknown
     keys, non-dict/malformed atomic values, missing trusted actor and forged
     receipt/time, with an explicit schema/allowed-variants.
  2. Both `record_terminal` and `append(atomic=decide)` accept a genuine verdict
     plus disposition together with both rows trusted-stamped and correct
     qid/revision/type and legitimate post-verdict terminal phase; replay and
     reopen documented; invalid subevent/type/identity/actor/disposition leaves
     no partial rows or lifecycle change, including after reopen.
  3. Genuine bounded atomic hold works with an authorized deadline and owned
     decision task; unauthorized hold deadlines and mixed forms are rejected;
     D1/D2/D3 actor, action-deadline/phase grants, epoch/restart/clock checks
     preserved; no test-only store helper exposed through supported production
     entrypoints.
  4. Retain 77 local and 59 core regression semantics plus no-duplicate
     dispatch and REST/INVALID/ACTION_DUE; tests assert legitimate success as
     well as rejection; no duplicated methods; stdlib only; no live effects;
     `fake.py` documented as internal test-only and not an alternate accepted
     write API.
  5. Corvid independently reproduces the parent failure, mutates both atomic
     API forms including combinations not supplied to the worker, checks
     persisted rows/attribution/receipt/rollback/reopen rather than returned
     errors only, binds full per-file hashes, and reports any accepted-core
     semantic change before making it.
- **Outputs/permissions** (lines 63–69): only this directory's `src/`, `tests/`,
  `fixtures/`, `README.md`, `interface.md`, `implementation-report.md` plus
  disposable `/tmp`; amendments limited to atomic ingress validation/stamping
  and tests/docs with copied-driver adaptation if required; no live state,
  timers, seat actions, model calls, host clock changes, research, old-source
  edits, migration or script retirement.
- **Independence** holds: author/director Tern, admission/verifier corvid,
  worker kiln, controller/duty cairn; the reader did not author or repair this
  contract.

## Allocation

New worker initial ≤20m + sole repair ≤10m = **30 worker**; verifier ≤15m per
pass including post-repair = **30 verifier** (two passes). Prior P5 65/55 fully
spent; cumulative ceilings become **95 worker / 85 verifier minutes** —
arithmetic correct, history never reset or transferred, runtime/provider charges
distinct. Admission ≤10m + one ≤5m confirmation. Conditional release only after
an ACCEPTED admission record and a pinned parent `EXHAUSTED` disposition exist;
no overlap, host-generated start/deadline, one-shot relative timer, preserve
initial bytes before repair, bind completion before verifier dispatch.

## Non-blocking observations

- The parent `P5-clock-ingress` tree currently has no `EXHAUSTED` disposition
  artifact; cairn must pin it (with the director admission record) before
  execution, as the dispatch requires.
- The parent's rejected `src/fake.py` test helper (direct `store.append`) is
  explicitly out of scope here; the contract correctly directs that it be
  documented as internal test-only rather than treated as an ingress route.

## Effect

Bound to contract bytes
`e09c313c5c99d14c9812b1bbab678a1a8e65b37170d6319cbdab8ac83acba890` at commit
`7b5772e40fbc4b30c025a87572ef39a906dcca5f`. Cairn may dispatch this exact
contract under the recorded conditional release once admission is recorded and
the pinned parent terminal disposition is present; changed bytes require
independent confirmation. No live effects.
