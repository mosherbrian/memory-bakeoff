# P6-r19-live-runtime-witness — admission review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P6r19-admission-1`, start `03:38Z`, deadline `03:53Z`
- **Brief:** `package.md` sha256
  `7d5e3ebfdfd70195bc20b79f712f1929b5be321b456089577c6945b032c5e799`; director
  release pinned.
- **Scope:** read-only admission + pinned checklist. No credentials/models/live.

## Verdict

**ACCEPTED (bounded).** The single live failed-verification witness is feasible on
the accepted R18 bytes: the candidate-local instrumented runtime/wrappers/helper
are real and self-selecting, the exact preparation CLI supports explicit lanes,
and `source_mode: runtime` propagates to the actual consumer. One readiness
obligation is pinned (environment applied **inside** the launched lane process;
inspect real session/item derivation and captured argv/env before signature).
Worker 0; evidence-only.

## Pin resolution

- R18 source commit `7857c0ce86fd…`; candidate `../P6-r18-runtime-source-time/
  candidate/`; outer manifest `68367181…` and composition `08c48b25…` recomputed
  equal; independent portability review `95431a9f…`. R18 `acceptance.json`
  co-pinned (`COMPLETE`, source `7857c0ce…`, manifest `68367181…`, verification
  `95431a9f…`).
- R17 missing-source evidence `d0769c2`, terminal `51cef7d`; R16 source
  `c8e99cf`; R14 `02ea693`; core R13 retained. R6 `prepare_live.py`/cleanup reused
  by hash (not rewritten). Governing rulings `4be99bf`, `650830c`, `84f094e`,
  `883107e`, `b2384d7`, `afa126f`, `f7b0cce`, `5fefb0f`, `fc74f65` and authority
  `58704e9` resolve.
- R18 acceptance limitation carried: the worker's final claim timestamp was future
  relative to the director read and is **not** trustworthy source/timeliness
  evidence — consistent with this package's "no timing backfill from model claim".

## Feasibility (inspected, no live effects)

- **Local runtime selected, not merely named:** `candidate/runtime/acp-worker`
  (instrumented copy) + `srcemit.py`; wrappers `launch-acp-go` /
  `launch-acp-go-deepseek` resolve them from the wrapper dir with no shared
  fallback (missing local = hard fail) and reject `ACP_SOURCE_TEST_NOW`/capture.
- **Real runtime fields:** `self.session` (adapter `sessionId`), `self.key`
  (`instance_id()`/`slug(CWD)`), `self.item` (`i` + ms epoch) → the end receipt's
  session/item are runtime-derived, not model-authored.
- **`source_mode` propagation:** plan `source_mode: runtime` → harness
  `setup_manifest` bounds (`harness.py:310`) → manifest → `case_entry` consumer
  (`:998/:1652/:1713`) which joins each receipt to its own detection via the R16
  item→action binding.
- **Exact prep CLI:** R6 `prepare_live.py` accepts `--worker-lane`/
  `--verifier-lane` (`:181-182`), so the canonical preparation can point at the
  candidate wrappers without new implementation.
- **Plan environment:** `launch_closure.exact_environment` is machine-executable
  (order: copy ambient → unset → set); go lane unsets
  `ACP_SOURCE_TEST_NOW/FIXTURE_LAUNCH_EXEC/PINNED_MODEL_OVERRIDE/ACP_GO_MODEL/
  ACP_MODEL` then sets Muse; deepseek sets its own. Wrappers enforce this in-process.

## Pinned checklist (pre-launch)

- **Exact prep CLI** including `--worker-lane candidate/runtime/launch-acp-go`
  and `--verifier-lane candidate/runtime/launch-acp-go-deepseek`, accepted tool
  hashes, fresh `/tmp` root/names (no historical fixture reuse); rendered bytes
  pinned and captured argv/env verified **before** signature.
- **Environment applied INSIDE the launched lane process** (tmux may carry its own
  env): a per-fixture generated launcher is allowed **preparation DATA** only,
  deriving the R18 plan's unset/set operations then `exec` of the exact local
  wrapper — it may not alter routing/core/backend args or manufacture source
  records. Capture on the shipped branch must show both lanes resolve the local
  runtime, preserve models/clocks, and have `ACP_SOURCE_TEST_NOW`/
  `FIXTURE_LAUNCH_EXEC` absent, worker clearing the inherited verifier override.
- **Consumer join:** `source_mode: runtime` reaches the manifest; the end receipt
  (v1 same-record fields, one append) is joined to its own action/execution/item/
  session and own detection. Refuse if the end source cannot be joined without
  invention. No manually invented item/sidecar source time; unavailable/
  discontinuous/test clock/conflicting identity → INCOMPLETE.
- **Fault + onset:** `corrupt-after-worker` applied receipt with before/after
  hashes; independent onset is the **host runtime end append per observation** —
  classify what interval that measures (detection is observer receipt; work
  duration separate); do not claim it measures fault installation if it measures
  verifier completion. Explicit detect≤30/recover≤60/total≤90 (suspicion 180/60/240
  only in that mode); acknowledged progress/escalation is recovery, queue alone is
  not; unknown timing cannot PASS.
- **Grants/stop:** worker 300 s / verifier 300 s max unless a concrete signed
  grant differs, within a 20 m operation including cleanup; outer stop and
  continuation preserve **both** grants; no 8 s final-failure substitution.
  One worker + one verifier send; continuation/restart produces no duplicate.
- **Cleanup/evidence:** arm and verify exact-ID automatic cleanup before effects;
  preserve raw stdout/stderr/partial, all claims/streams/DB; record actual CLI rc
  and per-file manifest; verify owned fixture IDs/timers stopped/removed and
  unrelated seats unchanged.
- **Scope gap:** if the existing host CLI cannot select this closure, return a
  concrete scope gap before implementation or launch. No four-case/adoption/
  retirement/shadow claim from one case.

## Bounds

Evidence-only: worker 0. New corvid admission15 m + binding5 m + live result
review15 m =35 m; cairn prep10 m + live operation20 m incl cleanup =30 m. Candidate
ceilings `1360/1135` unchanged; R17 unused grants cancelled, not recycled. No
auto retries/repairs. Every dispatch/receipt carries an exact executable wake
(profile/destination/action/absolute path). Admission returns Tern; no automatic
prep/live.

## Effect

Admission **ACCEPTED (bounded)** with the pinned checklist and the in-process-env
readiness obligation. No implementation/live release conferred. Returned to Tern.
