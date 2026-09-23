# P12-review-1 — independent candidate review (corvid)

- **Action:** `P12-review-1`, start `17:14:43Z`, deadline `17:44:43Z`.
- **Claim:** `completion-claim.json` on contract `1315196` + checklist `c9106b57…`
  + supplement `c8d91ce`; source `cbfe3d91` on base `1341f04`.
- **Verdict: PASS on all substantive checks, with ONE bounded evidence FAIL** —
  `evidence/conformance-cbfe3d9.txt` is **empty (0 bytes)** while the claim cites
  it as "conformance 125/125". The retained conformance result itself is true (I
  re-ran it), but a claim must not cite an empty artifact as its proof. Correct the
  artifact (or amend the citation) before live signature.

## Pins / integrity

- **40/40** claim hashes match (29 evidence + 11 plans); contract files
  `package.md 6391857222e0…`, checklist `c9106b57…`, supplement `293b08af…`.
- Source `cbfe3d91d02c86942e7640cbd0fe41027bfcbad0` on base `1341f04…`;
  `git diff 1341f04..cbfe3d9` is **empty** for `internal/core`, `internal/py`,
  `conformance/cases` — frozen as claimed. Changed set is bounded (loop/shutdown/
  transport/tests + `conformance/host/adjudicated.json` + `mutate_go.py`).
- Release binary `/home/bmosher/projects/agent-loop-releases/agent-loop-cbfe3d91d02c/bin/agent-loop`
  = `cf54a94a…`, matching the claim; `BUILD.json` go1.27.1, CGO_ENABLED=0.

## Independent reproduction (my runs)

- **A (timeout settlement):** `a-cli-timeout.sh` on `cf54a94a` — idle →
  `interrupted`, step `timed-out`, **1 director wake**, timeout notice carrying the
  exact `timeout-ack` command; replay `already-handled` (no new wake); ack wrong
  actor refused, director accepted, conflicting refused. `refused` mode: cancel
  failure recorded (`interrupted-effect-failed`, receipt) with the director told —
  **no swallowed transport error**.
- **C (shutdown):** baseline `1341f04` real systemd idle stop = **20.142 s**,
  `Result=timeout`, SIGABRT. Candidate `cf54a94a`: notifier SIGTERM **0.007 s**,
  fallback SIGTERM **0.008 s**, restart ×2 **0.031/0.035 s**, all `Result=success`;
  `agent-loop stop` **1.016 s** → `exiting 64`, no restart after 7 s,
  `NRestarts=0`. Both notifier and fallback paths exercised.
- **D (driver):** `f1-helpers.sh` on the P12 driver **29 PASS / 0 FAIL**;
  `r1-repair-tests.sh` **53 PASS / 0 FAIL**.
- **E (wall):** `e-wall-reload-witness.sh plans/live-driver.sh 10 25 3` — 3 **real**
  `daemon-reload`s, `LATE_FROM_DEADLINE=0`, `WALLSTOP_ROWS=1`, `CLEANUPS=1`,
  `DRIVER_ALIVE=0`, `SECOND_CLEANUP_EFFECTS=0`, wall agent-deck profile logged.
  Evidence `e-wall-reload-p12.txt` shows `TimersCalendar next_elapse=@1790183105`
  **unchanged across all three reloads** and `WALLSTOP` at deadline+0.396 s; the
  first attempt's `NextElapseUSecRealtime` bug is preserved and failed closed.
- **Retained:** `go test ./...` all ok; `go test -v ./internal/conform` **126 PASS /
  0 FAIL** (my independent count; claim says 125/125); host parity `316/321` + 5
  adjudicated; mutation `104/104` caught. Frozen dirs empty diff.

## Independent negative (unshared)

- **Wrong-action ack** (valid principal, non-existent action): refused
  (`L2 has no open step timeout for WRONG-ACTION`) — the B boundary is enforced.
- **C baseline vs candidate** is itself the negative contrast (20.142 s/SIGABRT vs
  0.007 s/success).

## Residuals (carry to live signature)

- Clock discontinuity for calendar timers (backward step postpones the wall) — not
  exercised; fail-safe forward. Fallback cleanup timer must be explicit-UTC
  calendar (P11's was `--on-active`).
- Failed-cancel + later replay can produce a duplicate director **notice** (never a
  duplicate cancel/dispatch).
- Unacknowledged timeout stays `timed-out` with `waiting_on=director`; only an
  acknowledged response deadline auto-expires.
- L4a/L4b, step-timer precision and ack latency are proved only in the signed live
  run.

## Effect

Substantive candidate work is sound and independently reproduced; **PASS** on
A–E, baseline reproduction, retained conformance/parity/mutation. **Bounded FAIL**
on the single empty `conformance-cbfe3d9.txt` evidence artifact — re-capture it (or
amend the citation) before live signature. No source/live/cutover change made by
corvid. Returned to Tern.

---

## Candidate-intake addendum (same 30 m pass, no reset)

Claim `2f597065…`; 43/43 bound files + binary `cf54a94a…` match.

### NEW bounded FAIL — L6 ack bound is total-only, not ack-from-detection

`plans/live-driver.sh:133-145` `l6_eval` computes `det = settled - deadline`,
`own = ack - deadline`, and passes on `0 <= det <= 30 and det <= own <= 90`. It
**never checks `ack - detection <= 60`**. The contract requires the acknowledged
ownership/recovery bound of **60 s from detection** *and* **90 s total**. The
author's own test proves the gap: `r1-repair-tests-p12.txt` line 47-48 —
"L6 ack at 90 s exactly: PASS (detection 10.0s, acknowledged ownership 90.0s)" —
i.e. an **80 s detection→ack latency PASSes**. Correct rule:
`det <= 30 and 0 <= ack-det <= 60 and ack-deadline <= 90`. This must be fixed
before the live gate can certify acknowledged ownership. (Delivery-only still
correctly FAILs.)

### Conformance evidence — independently established, artifact still empty

`evidence/conformance-cbfe3d9.txt` is empty (0 bytes, `e3b0c442…`). Per the intake
I ran the **shipped binary**: `agent-loop-cbfe3d9…/bin/agent-loop conformance
conformance/cases` → **exit 0, `conformance: 125/125 cases ok, 1751 steps`**. So the
retained conformance is real and independently replayed; the empty file remains a
citation defect to re-capture. (My earlier `go test ./internal/conform` also
126 PASS / 0 FAIL.)

### Other intake checks

- **Principal/session authority:** `timeout_p12_test.go` rejects a changed-principal
  (forged) ack and a conflicting ack, and requires delivery≠ack; my CLI run refused
  wrong actor and wrong action. OK.
- **Missing-ack / no notification:** `l6_eval` FAILs when no ack is recorded (not a
  pass). Product residual: an unacknowledged timeout stays `timed-out` with
  `waiting_on=director`; only an **acknowledged** response deadline auto-expires, so
  a never-acknowledged timeout has no bounded escalation — a **liveness gap** to
  carry into live (must not be called acknowledgement/recovery).
- **Replay vs dispatch identity:** replay of the same callback is `already-handled`
  with no new wake (A), stable `T-<action>` incident identity; the disclosed
  duplicate is a director **notice** only, never a duplicate cancel/dispatch.
- **Calendar backward-clock:** not exercised; the claim discloses a backward step
  postpones the wall. Per the intake this is **not** automatically accepted — it
  needs controlled injected-clock/schedule evidence (without changing the host
  clock) before the calendar-timer exception is signed.

### Reconciled verdict

Substantive A–E corrections remain **PASS**; conformance is independently
established. **Bounded FAIL** stands on the L6 ack-from-detection rule (and the
empty conformance artifact should be re-captured). No live/main/install or repair
released by corvid.

### Steer closure (7 points, same pass)

1. **Ack bound:** bounded FAIL as above — `l6_eval` enforces total ≤90 but not
   ack−detection ≤60; the author test accepts ack-at-90 with detection-at-10
   (80 s). Interval boundaries must be tested separately.
2. **Missing-ack liveness:** `l6_eval` FAILs without ack (not a pass); the product
   has no escalation for a never-acknowledged timeout — `waiting_on=director` is
   neither acknowledgement nor recovery; flagged as a bounded-progress gap.
3. **Authority:** changed-principal (forged) and conflicting acks rejected;
   wrong-actor/wrong-action refused; CLI by-name does not defeat the binding.
4. **Replay:** stable `T-<action>` identity; replay `already-handled` with no new
   wake; the disclosed duplicate is a director **notice**, never a duplicate
   cancel/dispatch — at-most-once on effects holds.
5. **Calendar backward-clock:** not exercised; disclosed risk is **not** accepted —
   needs controlled injected clock/schedule evidence without touching the host
   clock.
6. **Conformance:** shipped binary `conformance conformance/cases` → exit 0,
   **125/125 cases, 1751 steps**; release `MANIFEST.sha256` 8/8 verified; parity
   adjudication `final_corrected` (host timers → explicit-UTC `--on-calendar`
   `AccuracySec=1s`) inspected and named. Empty artifact to re-capture.
7. **Hygiene:** real argv used; isolated real stop/reload witnessed; no leftover
   `p12test-*`/`p12live-*`/`p11live-*` units; installed preview `221bb3aa…`
   unchanged (main stays preview).
