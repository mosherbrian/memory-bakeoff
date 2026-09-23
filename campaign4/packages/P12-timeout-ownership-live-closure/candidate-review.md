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
