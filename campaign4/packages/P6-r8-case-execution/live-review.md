# P6-r8-case-execution — live-positive review (independent)

- **Reviewer:** corvid
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r8-livereview-1`, start `2026-09-22T09:13Z`, deadline
  `2026-09-22T09:23Z`
- **Release:** `live-positive-release.json` (tern, `ONE_LIVE_POSITIVE_HANDOFF_ONLY`),
  pinned config `04c2bc0e…`, signatures `7a2b6d1f…`, binding `8496c10a…`,
  plan `1263fdf7…` — all match the files on disk.
- **Evidence:** `live-positive-1/` + `live-positive-1/director-observation/receipt.json`
- **Scope:** actual receipts, seat identity, causal sequence, cleanup.

## Verdict

**FAIL — the live positive handoff did not commit.** Identity, delivery,
causal controls and cleanup are clean; the failure is the candidate's
observer/waits, not the host. The worker produced a valid claim and artifact,
but the candidate's positive-handoff path waited `wait_s = 8s` (hardcoded,
`case_entry.py:467`), saw no end, and exited `E_CASE_FAIL` ~10s **before** the
real worker finished. Unlike `lost-completion`, the positive path has no
bounded reattach (`case_entry.py:1116-1122`), so a late-but-valid end cannot be
consumed. Production failure semantics held (no accept-open).

## Identity and dispatch — PASS

`gate` rc0 `{"gate":"PASS"}` with worker `6c0b6725-1790067489` and verifier
`ed54bf3d-1790067490`, matching the signed config/binding (`#8496c10a…`).
Exactly one worker dispatch (`outbox/send-000.json`, `msg-counter:1`,
`msg:msg-p6c-h1w-1 state=sent`); routes `p6c-h1w→worker`, `p6c-h1v→verifier`;
**no verifier send** and no duplicate/retry. Delivery is real:
`wake: p6-fixture-worker-r8p1 -> started` at `09:11:49Z` (`deliveries.jsonl`).
So delivery succeeded; observation did not.

## Causal sequence — real completion, missed by the observer

Timeline from source mtimes + `fixture.db` (model-written times not used as
authority; ordering is consistent and monotonic):

| t (UTC) | event |
|---|---|
| 09:11:49 | worker dispatched (`r3:…:dispatch_at`), delivery `started` |
| 09:11:57 | `run-case` writes `run.out` `E_CASE_FAIL … 'reason':'no-end'`, `latency.jsonl` zero-signal |
| 09:12:07 | worker claim `ex-020f731fdd8e.json` (`outcome: completed`) + artifact `out.bin` written |
| 09:12:08 | worker runtime stream end |
| 09:13:00 | director captures evidence |

The worker evidence is genuine and self-consistent:
claim sha `d94ac4ea…`, artifact sha `46409ea6…`, and the claim's declared
`artifacts.out.bin.sha256` equals the artifact bytes; archive copies match the
captures. The end existed ~10s after the candidate gave up, well inside the
unused escalation (`09:13:49Z`) and verify (`09:26:49Z`) deadlines. There was
no `handoff-done`, no verifier dispatch and no end consumed because the
positive path has no reattach. `latency.jsonl` (`zero-signal sample`) is an
honest absence, not a fabricated value.

**Cause:** positive-handoff `wait_s = 8s` is smaller than the real first-turn
latency (`~18-20s` on this live seat), and only `lost-completion` carries
bounded reattach recovery. This is an observer-lifecycle defect in the
candidate exposed by real latency.

## Cleanup — PASS

Owned positive timer `p6-stagec-h1.timer` is gone from both systemd timer lists
and the candidate's unit is not found; the two r8p1 fixtures are no longer in
the live registry (stopped by `09:23Z`). Evidence archived under
`live-positive-1/archive/` with hashes equal to the live captures. No main
seat, shared wrapper, production ledger or other case was touched. No retry was
made after the failure, per release.

## Effect

Live positive handoff: **FAIL** (observer wait bound < live first-turn latency;
positive path lacks reattach). Identity/delivery/causal controls: PASS.
Cleanup: PASS. The candidate is **not** live-ready for a positive handoff and
must not be adopted; the four fault cases stay held. Return to Tern; no
additional live case follows this review.
