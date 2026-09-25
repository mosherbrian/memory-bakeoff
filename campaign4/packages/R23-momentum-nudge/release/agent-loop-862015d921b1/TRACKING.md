# Tracking the reference

Only ACCEPTED packages are ported. A candidate can be rejected, and porting it
would port work that is later thrown away.

When a package is accepted:

1. Record its tests from the accepted pin (`conformance/tools/check_py.sh`);
   replay must be 100% on that pin.
2. Run `mutate_py.py`; every planted fault must still be caught.
3. Run the Go suite. Every difference is a finding: either the Go port
   diverged, or the reference changed behaviour. Report each to the director
   with the case name and the first differing value.
4. Port until `go test ./...` passes, then `mutate_go.py`.
5. Update PROVENANCE.json and this table.

| Package | Pin | What | State |
|---|---|---|---|
| P5-r2-atomic-authority | `80092f92` | lifecycle, validator, store, ingress, driver, supervisor, status | Ported, 2026-09-22 |
| P3-r3 lifecycle tests | identical lifecycle | pure lifecycle cases | Recorded, 2026-09-22 |
| P6-r13-core-record-integrity | `c4ef8b98` (source `5410332b`) | core record integrity: findings 2, 6, 7, 10, 11 fixed; 5 not reproduced | Ported, 2026-09-22 (125/125, 25/25 faults on Go and Python) |
| P6-r14-host-timing | `a7dadd7b` | host timer callback identity (T1: qid, action, execution required and bound to the persisted record); `harness.py` only | Core unchanged: the 7 core files are byte-identical to R13, and the R13 cases re-recorded from R14 are identical. The harness change joins the harness row below. 2026-09-23 |
| P6-r16-causal-identity | `82b1418f` | case entry: a failure's onset is joined to its own detection by verified identity; `case_entry.py` only | Core unchanged: `r3harness` is byte-identical to R14, R13 cases re-record identical, and the 8 new R16 tests call no core API. The case-entry change joins the harness row below. 2026-09-23 |
| P6-r18-runtime-source-time | `b94ce3f6` | the runtime stamps the real turn-end time; `case_entry.py` and `harness.py` only | Core unchanged: the 7 core files are byte-identical to R16, R13 cases re-record identical, and the 15 new R18 tests call no core API. Joins the harness row below. 2026-09-23 |
| Host building blocks (from R18 `b94ce3f6`) | `host_adapter.py`, `turn_handoff.py`, `notify.py`, the timer-callback guard in `harness.py` | wake transport + receipts, outbox, systemd timers, execution identity, turn watcher, claims, handoff, inotify | Ported, 2026-09-23 (`internal/host`). Checked by `conformance/host`: 23 scenarios, 321 ops, recorded from Python by `tools/host_py.py`; 17/17 planted host faults caught. Two Python faults found and not copied (see below). The fixture runner and P6 timing gates are not ported. |
| The loop product (Go only) | none: Brian's decision 2026-09-23 | `agent-loop dispatch/run/status/claim/decide/stop/timer-callback` on the core + host blocks | Built 2026-09-23 (`internal/loop`). No Python reference: P8 qualification and corvid's review are its proof. |
| P6-r9 / P6-r11 harness | `f1d7c86f` / `924d21ab` | host adapter, timers, observer, case entry | Not started: live host code, needs its own adapters and live cases |

## How I hear about an acceptance

`tools/memory-bake-off-post-commit` is installed as
`memory-bake-off/.git/hooks/post-commit` (hooks are not versioned, so this is
the kept copy). When a commit adds or changes
`campaign4/packages/<pkg>/acceptance.json`, it sends the pin and package list
to the Claude session through `notify-claude` (kind `agent-loop`), which also
records it in the escalations ledger. It runs in the background and can never
block or fail a commit. Log: `~/.local/share/agent-deck/agent-loop-sync.log`.

## Python faults found while porting the host blocks (reported to Tern)

1. `turn_handoff._recover` raises `NameError` instead of `E_NO_ESCALATION_BOUND`
   when a launch has no escalation bound: `OwnedFault` is not imported in that
   function. Go returns the owned fault (a listed divergence in
   `internal/host/parity_test.go`).
2. `_close_verify` commits the verifier PASS, then submits the director decide.
   If the decide is refused (for example a disposition kind outside the core's
   enumeration), the handoff is left declared but not done, and a retry
   rolls forward to `terminal-rest` and marks it closed although the ledger
   has no disposition. Scenario "an invalid disposition fails the close; a
   retry still marks it closed" records this; Go matches Python here until
   the director rules.

## P9 supervised preview (2026-09-23)

Branch `p9-preview` from `71318c4`. Adds `internal/expose` (read-only view,
P7's requirements plus ledger overhead counts) and the `expose` command;
packaging only otherwise (README entry point, templates, unqualified systemd
examples, `docs/SUPERVISED-PREVIEW.md`, `LICENSES/`, `tools/release.sh`). Core,
host, py and all loop control code unchanged from `71318c4`. P8 is NOT READY;
this is not a qualification.
