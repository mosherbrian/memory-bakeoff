# P6-r6-live-preparation — candidate review (independent)

- **Reviewer:** corvid (independent of kiln/author; receiver of the candidate)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Dispatch/receipt:** `dispatch-receipt.json`, candidate-1, owner kiln,
  start `2026-09-22T03:51Z`, deadline `2026-09-22T04:21Z`
- **Bound contract:** `package.md` sha256 `f2b7df48…` at commit `e32c0dccacb28ba0dc9b9ab107ee9f8f2c569a38`
- **Binding under review:** `src/prepare_live.py` sha256
  `49a6f952dc08fed16e261a521804e641ad66d1e97411b826b2253bfd912a7885`
  (`49a6f952dc08`), invoked by plan phase `1_prepare_idle`
- **Checklist:** `preparation-timing-checklist.md` `ba44f88a…` (P1–P5/T1–T5)
- **Parent pin:** P6-r5 `dad988277b5b7e633735d8eaae2d6134b84fa5a0`; terminal
  `4cef6dc2…`; candidate reused **unchanged**, never relabelled live
- **Scope:** author tools/plan only. No live runtime/service creation.

## Verdict

**PASS** — bound to the artifacts below. The candidate correctly separates
operational live preparation from the simulated P6-r5 evidence, gates every
live step behind Tern's out-of-band signature over the exact plan and manifest
hashes, and fails closed on synthetic identity, stale incarnation, fake
sockets, main-seat repurpose and collisions. Independent boundary probes
re-derived each refusal.

## Artifact hashes (recomputed this review)

- `src/prepare_live.py` `49a6f952dc08fed16e261a521804e641ad66d1e97411b826b2253bfd912a7885`
- `src/prewake_gate.py`  `5e3d333b9a1f22520da2f72ee17a8a703e086a790fe850f06b22756db20f8d73`
- `src/witness_timing.py` `0bf9903371210b4ee2ae87e21d5ce2b81f33e16f9f4eb86dfcc47bc9e8585ca3`
- `src/cleanup_live.py`  `cb40a1349c36ee15061b55fae16f9133ec37af1166f05ef4ee5dc12106d8ef15`
- `live-fixture-plan.json` `1a536965f0db4cf092a08777dfb25518262b5d4f38c5c9f8f863e181bbefb072`
- `launch-manifest.schema.json` `7d709eee919f7c815a38875c8e44089bf9c0799f5d7970f6f6437af9477fbb3b`
- `operator-brief.md` `ddff22f0dad1d332bbb6708e41b1a669ca438dec9d12ae4261e56272edaae87f`
- `tests/test_p6r6_tools.py` `2478642407704faf43fdd73079397129e264b0f46b88b778e0d5ce85d3f74a64`
- `director-admission-release.json` `e24018c880770e82922cb7cde6ed3abd1d00531ad2fe3eb0efccb4b845c5e85b`
- `completion-claims/ex-p6r6-candidate-1.json` (claimed by kiln)

## Checklist conformance

**P1 (isolated new runtimes only):** `prepare_live.py` live path launches
exactly two NEW `p6-fixture-*` sessions on `acp-go` / `acp-go-deepseek`, writes
isolated workdirs under `/tmp/p6live`, and its `launch_idle` argv has **no
`-message`**, so no task is dispatched during preparation. It refuses any
worker/verifier name equal to a main seat (`E_MAIN_SEAT`) or not prefixed
`p6-fixture-` (`E_NAME`), and refuses a name already present in the launcher
list (`E_COLLISION`, never adopts). Confirmed by probes.

**P2 (authoritative binding, both sides):** records real `session_id`, profile,
`role_lane`/launch command, producer root, stream path, and socket
identity/incarnation for both. Probes: wrong profile/lane → `E_WRONG_PROFILE`/
`E_WRONG_ROLE` paths; a regular file where a socket is expected →
`E_FAKE_SOCKET` (via `S_ISSOCK`); identity is taken from the launcher
`id`/`title` record, never inferred from filename.

**P3 (same binding for transport/observer; no forged facts):**
`prewake_gate.py` rejects any manifest whose `launcher_source` is not
`live-agent-deck` (`E_NOT_LIVE`), so a `dry-run-injected`/shim identity cannot
pass; the run walks transport and observer off the same signed manifest.
Probe: a dry-run manifest built by the tool was rejected `E_NOT_LIVE` (rc3),
matching the checklist's "before task wake" requirement.

**P4 (explicit phases, cleanup ownership):** plan phases 1 prepare-idle → 2 bind
→ 3 gate → 4 bounded fixture → 5 check/rollback are explicit; phase 2's
signature is out-of-band and no tool forges it; the gate requires `signer ==
tern` and the exact plan+manifest hashes, rejecting missing/changed signatures
(`E_NO_SIGNATURE`/`E_PLAN_CHANGED`/`E_BINDING_CHANGED`) and stale incarnation
(`E_STALE`). `cleanup_live.py` owns only IDs from a `live-agent-deck` manifest,
refuses main seats and non-`p6-fixture-*` titles, and archives (manifest +
launcher records + witness rows) **before** any stop/remove. Probes confirmed
all of these.

**P5 (real host permission deliberately separated):** phase 1 is gated on a
separate, signed ≤10m preparation release; the plan status is `PROPOSED ONLY -
Tern signature required before any live step`; the exact `agent-deck launch`
argv in `launch_idle` contains no initial prompt.

**T1 (independent witness):** `witness_timing.py observe` stamps host-gmtime
detection, reads a declared controlled onset (`onset_at`, `provenance`,
`uncertainty_s`), and reports detection = onset→detected with `worker_duration`
flagged as reported-never-gated and observation wait as a bound, not exactness;
candidate decision timestamps are not the source.

**T2 (correct interval / INCOMPLETE):** `check` gates 30/60/90 s with 180/240
reported. Probes: no onset → `verdict: incomplete` (rc3, never passing); a
45 s detection → `E_GATE_DETECT` (rc3); a 12 s detection → `within-bounds`
(rc0). Model execution time is explicitly not detection latency.

**T3 (enumerated live cases within the held 15m run):** the plan lists five
mandatory cases (normal handoff 4m, lost completion 3m, failure recovery 3m,
queued/ambiguous+restart 3m, quiet rest 2m) summing to exactly 15m; the
protocol keeps missing independent evidence as INCOMPLETE.

**T4 (one-send/durable outcomes retained):** phase 4 states positive path
retains one worker + one verifier send; the forbidden list excludes production
campaign ledger writes, real Signal/all-seat pause, research runs, retirement.

**T5 (dry-run evidence, not prose):** I independently ran the exact
preparation/signature/gate/cleanup boundary against private `/tmp/opencode`
fixtures (see probes); the candidate's own `tests/test_p6r6_tools.py` covers
label-`injected`-never-live, fake-socket rejection, collision/main-seat refusal,
pre-wake rejection, signature change, stale incarnation, cleanup-owned-ids/
archive-first and the witness incomplete case.

## Independent probes (this review, no live effect)

Run under `/tmp/opencode/p6probe` with injected real Unix sockets:
1. `prepare_live --dry-run` → manifest labeled `dry-run-injected`.
2. gate on that manifest → `E_NOT_LIVE` rc3.
3. gate on a `live-agent-deck` manifest with a genuine Tern-signed
   plan+manifest → `{"gate":"PASS"}` rc0.
4. signer kiln → `E_NO_SIGNATURE` rc3; changed plan hash → `E_PLAN_CHANGED` rc3.
5. re-bound socket (new inode) → `E_STALE` rc3.
6. main-seat name → `E_MAIN_SEAT` rc3; existing name live path → `E_COLLISION`.
7. regular-file socket → `E_FAKE_SOCKET` rc3.
8. cleanup dry-run → owned `["sessw001","sessv002"]`, stop-then-remove, archive
   dir, `executed:false`; non-live manifest → `E_NOT_LIVE` rc3.
9. witness check: missing onset → `incomplete` rc3; 45 s → `E_GATE_DETECT` rc3;
   12 s → `within-bounds` rc0.

Candidate suite: `PYTHONPATH=src python3 -m pytest tests/ -q` → **8 passed**.

`AGENTDECK_PROFILE=campaign4 agent-deck list` before and after shows only the
four main seats (tern/corvid/kiln/cairn) — no live runtime was created, and no
seat was messaged.

## Non-blocking observations

- `prepare_live.py` live path was not executed (not authorized); its argv was
  read and its checks were exercised through the dry-run/inject path.
- `witness_timing.py check` reports `recover`/`total` in the bounds dict but
  gates only detection; a combined recovery/total gate is deferred to phase 5
  candidate assertions — acceptable, since the plan requires those assertions.

## Effect

Verdict **PASS** bound to `src/prepare_live.py`
`49a6f952dc08fed16e261a521804e641ad66d1e97411b826b2253bfd912a7885` and the
artifact hashes above, under contract `f2b7df48…` @ `e32c0dcacb28ba0dc9b9ab107ee9f8f2c569a38`.
No live preparation, Stage C, seat/service creation, Signal, wrapper edit or
clock change occurred. Worker stays held; a PASS never automatically starts
preparation. Verdict returned to cairn.
