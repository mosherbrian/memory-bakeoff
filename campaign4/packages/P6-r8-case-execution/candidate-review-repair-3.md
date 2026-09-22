# P6-r8-case-execution — post-repair-3 review (independent)

- **Reviewer:** corvid (independent of kiln/author)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Repair receipt:** `repair-3-receipt.json`, action `P6r8-repair-3`, start
  `2026-09-22T08:13Z`, deadline `2026-09-22T08:53Z`
- **Governing decision:** `allocation-extension-5.md`
- **Checklist:** `host-composition-checklist.md` `c076dddc093d…`
- **Bound artifacts:** `case_entry.py` `ed392e66…`; `composition-manifest.json`
  `1e2308620aac1b1f0943358aabe4f025ba600151bbde6ef6d2a3fbc2f8916f5c`;
  `stagec-plan.json` `1263fdf79cdf…`
- **Claim:** `completion-claims/ex-p6r8-repair-3.json`
- **Contract:** `package.md` `1e0305fe…` @ `8ceb879` (no contract edit)
- **Git:** HEAD `c706e98` (authorization committed); working tree carries the
  three repair-3 artifacts uncommitted, as declared

## Verdict

**Repair substance PASS; bound manifest/contract PASS; claim-as-written
WITHHOLD — one changed-artifact hash is invalid.** The causal race is
independently reproduced on the old bytes with the exact disclosed error, the
gate is correct against the durable commit record, the manifest is clean and
externally bound, and I could not re-induce the failure on the new code in 3
whole-suite runs plus 6 repeats of the previously flaky test. But the
completion claim binds `tests/test_fault_ordering.py` to
`8b60d34e…cea07` (61 hex chars), which is not a sha256 and does not match the
disk/manifest `34548dc2…343d`. That is a provenance-gate defect in the claim,
not in the artifact; it needs a one-field superseding correction. No launch,
preparation or live release follows this ruling.

## Causal race — PASS (independently reproduced)

The diagnosed ordering is exactly what I reproduced, not merely read:

- On the **old bytes** (`case_entry.py` from `cc8cc2b` = `e83caa37…`, the exact
  version the repair-2 review saw fail) I ran the exact five-command CLI
  sequence (`test_r2_five_command_sequence_one_suite_root`, simulated) in an
  isolated copy of the package (private `/tmp`, sibling `P6-r5-launch-binding`
  symlink so the R3 parent path resolves). Result: **FAIL on run 1 of 5** with
  `failed-verification not provably open: {'verdict': 'incomplete', 'reason':
  'no success rows at all; fixture did not run'}` (`E_CASE_FAIL`, rc3) — the
  exact signature the repair-2 review recorded. A confirmation loop then
  reproduced the same failure on its first run (captured
  `/tmp/opencode/oldrun-1.log`). So the old code is flaky at roughly the
  disclosed rate, and this is the real race, not a test-scheduler artifact.
- On the **new bytes** (`ed392e66…`) the same exact test passed **6/6**
  targeted repeats and the whole suite passed **3/3** (18/18 each, each of
  which runs that sequence), plus
  `tests/test_host_composition.py` real-branch 5/5 and `test_r3_lifetimes.py`
  3/3.

The diagnosis — producer publishes artifact → claim → end sequentially, while
the deliver thread applied `corrupt-after-worker` on *claim observation* and
the handoff validates/recomputes on *end observation*, so a tamper landing in
that window failed the worker handoff the fault was meant to follow — is
consistent with the code and with the reproduction. It is correctly called a
production-code defect (the tool applied a post-commit fault on a pre-commit
signal), not test scheduling.

## Fix review — correct at the external boundary

`_maybe_apply_corrupt_tamper` (`case_entry.py:602-634`) applies the fault only
when the durable `handoff-done:<action>:<execution>` record exists.
`_commit_present` reads that key read-only. I verified the key is written by the
real harness **after** claim validation + artifact recompute + ledger drive
(`src/r3harness/turn_handoff.py:257`, written at `:319` after
`validate_claim`/`recompute_artifacts`/`drive_next`), using the same
`(action_id, execution_id)` identifiers as the manifest. So the gate models the
actual host precondition (fault after worker commit) rather than manufacturing
an ordering. Edge cases hold:

- claim observed, commit absent → returns `None`, bytes untouched
  (`test_tamper_waits_for_commit`);
- commit present → tamper applies, before/after hashes differ
  (`test_tamper_applies_after_commit`);
- non-`corrupt-after-worker` controls untouched
  (`test_tamper_ignores_other_controls`).

No sleeps, no timeout inflation, no retry-until-green, no weakened assertion,
no reduced case set, no relaxed bounds, no swallowed exception. `case_entry`
missing worker success still yields INCOMPLETE — preserved. The changed
behavior (if the worker never commits, the corrupt fault never applies and is
moot) is disclosed honestly as a residual.

## Bound files — PASS

- `composition-manifest.json` lists **27** files; **0** self-hash entries; all
  27 hash-match on disk. `contract_sha256` re-derives to `1e0305fe…` and
  `package.md` hashes to `1e0305fe…`. Manifest hash `1e230862…` is bound in the
  claim as `manifest_sha256`. R3 copy `harness.py` `88552c98…` retained.
- The commit-causing artifacts are the expected set (`case_entry.py`,
  `tests/test_fault_ordering.py` new, `composition-manifest.json`); no tracked
  test file was weakened (`test_case_execution.py` unchanged at `88c64f1b…`).

## Hash adjudication — `test_fault_ordering` claim `8b60d34e…` vs disk `34548dc2…`

**Disk/manifest is authoritative; the claim field is invalid.** The three
`changed_artifacts` hashes are 64/61/64 hex chars — the middle one,
`8b60d34e…cea07`, is only **61** characters, so it cannot be any sha256 at all.
Disk and manifest agree on
`34548dc2c30daa696c8fe69c9c8445d17f8026bad8f2145550082a17447e343d`, and the
other two claim hashes (`ed392e66…`, `1e230862…`) also match disk. The
mismatch is therefore a **truncated/transcription-corrupt claim string**, not
drift in the artifact, the manifest, or the contract. It is already noted on
`control-events.tsv` (11/12 match). Ruling: the repair evidence stands, but the
claim cannot be certified as a faithful binding while a declared changed-file
hash is malformed. Preserve this claim; a superseding claim (or a correction
note mechanically hashed) must carry `34548dc2…343d` for
`tests/test_fault_ordering.py` before certification.

## Regression-screen scope and residuals

- The committed deterministic regression is a **unit test of the new gate**
  (`test_fault_ordering.py`, old code fails by `AttributeError` because the
  function is absent). It is deterministic, but it does *not* by itself
  reproduce the race ordering; the race reproduction lives in the (flaky)
  exact-CLI sequence above. That is stated plainly and is acceptable, since a
  flaky race cannot be a deterministic committed test.
- My screen covers 3 whole-suite runs + 6 targeted repeats of the exact
  previously-flaky test on this host/load; it is a regression screen, not
  statistical proof of universal reliability. Timing variation covered: same
  host, same load class; the old code still failed 2 of 6 targeted attempts
  while new failed 0 of 9 exact-sequence runs (6 targeted + 3 whole-suite).
- Carried residuals (worker-disclosed, owner triage still owed):
  lost-completion `missing-or-malformed-claim` seen once pre-fix, never
  reproduced; the pre-fix timing-flake history; and the moot-fault behavior
  when a worker never commits. None of these are repaired or claimed repaired.

## No live effects

All independent runs used private `/tmp` sockets/streams/copies or the real
branch with intercepted host/model boundaries; no real seat task/send/launch,
service/timer mutation, credential, production ledger, shared wrapper,
research/shadow or retirement. No source file was edited by this reviewer (the
old-bytes reproduction used a throwaway copy outside the package).

## Effect

Causal race diagnosis+repair, manifest/contract binding and D1–D4 host
composition: **verified PASS**. Completion claim artifact binding:
**WITHHOLD** on the malformed `test_fault_ordering.py` hash — return to Tern
for a superseding claim correction; no launch, preparation or Stage C follows
this review. Independent signature and fresh binding remain separate gates.
