# P6-r11 — rejection-1 independent verification (authenticated verifier rejection + bound manifest)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r11-rejection-verify-1` (existing ≤30 m verify grant; deadline
  timer `campaign4-p6r11-rejectionverify-deadline.timer` → 19:12:41Z)
- **Candidate:** `candidate/` at entry `candidate/src/case_entry.py` sha256
  `2326e6b89740…`, `candidate/src/r3harness/turn_handoff.py` `2b6aa7efe8af…`,
  manifest `a821a52538b7…`; amendment at commit `253a66b`.
- **Evidence:** `candidate-review-rejection-evidence/` (reproducer, logs,
  observed R3_REVISION). No candidate/receipt/manifest edited by this review.

## Verdict

**PASS (bounded).** Authenticated verifier rejection is genuinely implemented
and independently reproduced end-to-end: post-commit tamper, verifier `failed`
claim, `verified-rejection` with `expected` = committed worker hash and
`observed` = tampered disk hash, `accept-open`, exactly 1+1 sends, never
`COMPLETE`/`terminal-rest`. The bound manifest is correct (33 entries, no
self-entry, all hashes match, bound externally from the claim). One bounded
residual metadata defect remains in `R3_REVISION.json` (see below); it does not
affect behavior or the gate.

## Independent reproduction (candidate-pointed, immutable plan, injected only)

```
python3 /tmp/p6r11-rej-repro/repro.py      # FV-W, FV-WV, QR-W on candidate bytes
PYTHONPATH=candidate/src python3 -m pytest candidate/tests -q -p no:cacheprovider
PYTHONPATH=candidate/src python3 -m pytest candidate/tests/test_r11_rejection_newpass.py -q
```

- **FV-W** (worker 18 s): rc0, `timecheck accept-open`,
  `sends {worker:1,verifier:1}`, `decision verified-rejection`,
  `expected {out.bin: 46409ea6…}` (committed worker hash),
  `observed {out.bin: 9809428b…}` (tampered bytes),
  `reason "hash mismatch: out.bin"`. No `COMPLETE`.
- **FV-WV** (worker 18 s, verifier 18 s): rc0, `accept-open`, 1+1, same
  rejection evidence.
- **QR-W** (worker 18 s): rc0, `timecheck accept`, 1+1,
  `duplicate-end-ignored`/`terminal-rest`; quiet/reopen retained.
- **New-pass/negative unit file:** 4 passed.
- **Full retained+new gate:** **38 passed in 841.88 s** (independent run;
  claim reported 839.75 s), no skips, no cache provider.

## Authenticated-rejection correctness (not a blessing)

Traced source `candidate/src/r3harness/turn_handoff.py`:
`_committed_worker_hashes` locates the worker handoff intent bound to this
verify action/execution; `_authenticated_rejection` requires
`contract_step=="verify-run"`, `outcome=="failed"`, code in
`{E_ARTIFACT_MISMATCH,E_ARTIFACT_MISSING}`, re-validates the claim
(routing/authority) **before** trusting outcome, requires the claim's declared
expected hash to equal the committed worker reference, and independently
recomputes actual bytes; only a real mismatch yields the distinct
`verified-rejection` record (expected/observed/reason/claim identity persisted
durably and idempotently). `case_entry.py` consumes it as `accept-open` only
when `verified-rejection` is returned, and still forbids `COMPLETE` after the
reattach. Independent negative probes on frozen candidate bytes all return
`None` (never a rejection): invented expected hash; completed-claim mismatch;
`worker-run` step; wrong action/execution (forged binding); `failed` verdict
with no demonstrated mismatch; forged route. This matches the amendment's
"never trust a forged claim's invented expected hash" requirement.

## Bound manifest

`candidate/composition-manifest.json`: 33 entries; **no self-entry**; every
listed path exists with a matching recomputed sha256; `baseline 05eba448`;
`bound_from completion-claims/ex-p6r11-rejection-1.json`; `changed` correctly
names `case_entry.py`, `turn_handoff.py`, `R3_REVISION.json`, the new test and
the two docs. `candidate/stagec-plan.json` supplied (sha256 `1263fdf7…`,
byte-identical to the signed plan). `harness.py` `d7b4e517…` and
`host_adapter.py` `231f45f0…` unchanged from the r9 lineage — the change is
confined to the two authorized modules.

## Bounded residual (correct before final acceptance)

`candidate/src/r3harness/R3_REVISION.json` marks `turn_handoff.py`
`identical: true` while `copy_sha256 2b6aa7ef…` ≠ `parent_sha256 ecbec310…`
(the r9/P6-r5 parent). The file was in fact modified, so the flag is wrong
(contrast `harness.py`/`host_adapter.py`, which correctly carry
`identical: false`). `_r3_hash_check` validates `copy_sha256` against the
working copy and `parent_sha256` against the pinned parent — both pass, so the
gate is unaffected — but the revision descriptor misreports provenance. Set
`identical: false` for `turn_handoff.py`. Minor, metadata-only; not a behavior
or gate failure.

## Scope / not promoted

- Loss-completion and queued/ambiguous controls remain out of scope and
  unresolved; this is not four-case acceptance.
- Integration-level negative cases (forged route/wrong incarnation at exact
  CLI) are exercised at unit level and via `validate_claim`; replay/reopen
  idempotence is unit-verified, and expiry/outer-stop was not re-run in this
  bounded pass. No live effect, no retry-until-green, no candidate edit.

## Effect

One bounded verdict: **PASS** — authenticated verifier rejection works on
frozen candidate bytes, the manifest is correctly bound, and the retained+new
gate is independently green (38/38); fix the `R3_REVISION.json` `identical`
flag. Returned to Tern.
