# P13-receiver-binding-1 — independent review (corvid)

- **Action:** `P13-receiver-review-1`, owner corvid, `19:52:50Z`–`20:07:50Z`.
- **Claim:** `receiver-binding-claim.json` (`be7bfa36…`) — COMPLETE; **174/174 claim
  hashes** and **15/15 canonical manifest** pass.
- **Verdict: readiness PASS on the explicit composition + fail-closed, with two exact
  gaps** (stale freeze citation; prep path exercised indirectly only). Proof
  boundaries and original INVALID outcomes preserved.

## Actual composition (audited as one path, not same-arg tests)

- **prep** (`prep-p13.sh:28-30`): `rec=$PREP/passive-$role.jsonl`, `key=$RUN-$role`,
  wrapper `$PREP/lane-$role` = `exec plans/acp-passive-lane "$rec" "$key"`, launched
  with `-cmd`; `prep-result.env` records `<K>_RECORD`, `<K>_KEY`,
  `<K>_LANE_WRAPPER_SHA`, and the **returned** session id `<K>_ID`.
- **lane** (`acp-passive-lane`): requires exactly `ABS_RECORD_PATH RUN_ROLE_KEY`;
  rejects a relative path/empty key (`exit 2`); `exec`s the **real**
  `acp-worker` with `plans/passive-acp-engine.py "$1" "$2"`.
- **engine** (`passive-acp-engine.py`): requires 2 args, absolute path, non-empty key
  (`exit 2` before any record — **no "unknown" record**); writes
  `{"t","key","text"}` to `REC`; never reads `HOME`/`AGENTDECK_INSTANCE_ID`; imports
  only `json/os/sys/time`; advertises no tools/capabilities; no shell/spawn.
- **driver** (`live-p13-driver.sh:329-330`): reads `D_RECORD/D_KEY/U_RECORD/U_KEY`
  from the signed inputs and checks `receiver_has "$D_RECORD" "$D_KEY" "nonce …"`
  via `plans/receiver-eval.sh` — **HOME-independent**, refuses a non-absolute record
  path, and requires a JSON line with the exact key and the nonce.
- **Distinctness:** per-role record paths (`passive-director.jsonl`,
  `passive-duty.jsonl`) and keys (`RUN-director`, `RUN-duty`), wrapper hash recorded;
  the runtime-owned instance id is **not** overridden. Fail-closed on missing/stale/
  wrong key/path; a nonce is per seat and must appear in that seat's own record.

## Gaps (smallest, exact)

1. **Stale freeze citation.** The claim's `frozen` says "committed **6e60ce5d**
   before the tests", but `6e60ce5d` is the **prior** round
   (`P13-passive-fixture-1`) whose `passive-acp-engine.py` = `9d987847…`, **not** the
   current `3d9ef990…`. The current bytes were frozen at **`ddea0cf7`**
   ("P13-receiver-binding-1: freeze before tests"); HEAD `1b15f68c`. **Reconcile the
   citation to `ddea0cf7`** — the canonical 15/15 manifest already pins the final
   bytes, so this is prose, not code.
2. **Prep path exercised indirectly only.** `prep-p13.sh` itself (real seat launch +
   returned session id → wrapper → `prep-result.env`) was **not run** this round
   (`not_executed`); the composition test launches the same lane with the same
   argument shape under a **different** runtime instance id. The real
   returnID→key/path→bind→driver path therefore remains to be exercised by a fresh
   live prep. No actual seats/services were launched or touched by this review.

## Preserved

- Passive proof boundary retained (director/duty are receiver doubles; **no
  human/model compliance claim**); worker/verifier real; driver alone acks/decides.
- Original outcomes preserved: live1 NOT READY / live2 PRECONDITION INVALID / live3
  INDUCTION INVALID (record-path). Ladder/ack/recurrence/decide/restart remain
  **unexecuted**. Product/adapters frozen (`47f69dfd…`/`df51a1f4…`/`fdf49d0b…`).

Consolidated: **PASS on composition + fail-closed**, with the two gaps above. No
edits/live by corvid.
