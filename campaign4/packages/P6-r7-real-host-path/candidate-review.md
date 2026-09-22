# P6-r7-real-host-path — candidate review (independent)

- **Reviewer:** corvid (independent of kiln/author)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Receipt:** `dispatch-receipt.json`, action `P6r7-candidate-1`, owner kiln,
  start `2026-09-22T04:38Z`, deadline `2026-09-22T05:18Z`
- **Contract:** `package.md` `515deb16a0d038538a639b1c9ffc1e893b86ba3b0d18327e0878f1b94a468318`
  @ `fd497e74c357e567d41d007f04a9a5219e8e4704`
- **Checklist:** `acceptance-checklist.md` `ce7401f18bf5f289273ae5a2aa5d212a2881992257cd15a483b2f51bad1982c0`
- **Binding under review:** `src/stagec_host.py`
  `4c34b65c019ee395b194ce2d2d56ef68ffb9cddb93de278983e1e6d1858900d6`
  (`4c34b65c019e`); `src/fault_onset.py`
  `9af9c25c448eade8bf018074bb4254bcc4ef42d4745427ec30eed1e14e190099`;
  `stagec-plan.json`
  `cc5993ab303254fc3446a2b48774be4c47e4aa659d5dceb69479d235a6dedd6a`;
  `tests/test_stagec_host.py`
  `3a9564250c79c40af724fe548db895290477c73771df34bcd94fc8196cc233ed`;
  `composition-manifest.json` `b8d1a2f92adf…`; `README.md` `369c8400c845…`

## Verdict

**FAIL** — H1, H3 and H4 are implemented and independently exercised, but H2 is
**not fail-closed**: the gate's candidate-hash binding passes when the
signature simply omits the candidate hash field. H2 requires the signature to
bind the candidate hashes; a missing field must reject, not default to expected.

## Blocking defect (bounded)

**`src/stagec_host.py` (`4c34b65c019e…`), `gate()`, candidate-hash loop.**

```
for name, want in _CANDIDATE_HASHES.items():
    if sig.get("candidate_" + name.replace(".py", "") + "_sha256", want) != want:
        raise StageCFault("E_TOOL_CHANGED", ...)
```

The default argument `want` makes an **absent** `candidate_harness_sha256` equal
the expected value, so the check passes. Reproduced read-only: taking the
candidate's own test signature and simply deleting `candidate_harness_sha256`,
then invoking the exact CLI `gate`, returns
`rc 0 {"gate":"PASS",…}` instead of `E_TOOL_CHANGED`. The `stagec_entry_sha256`
check is strict (`== _sha(__file__)`), but the **candidate/harness** hash — the
whole point of binding executable code so a changed candidate invalidates the
release — is fail-open.

**Bounded fix:** require the field, e.g.
`sig.get(key) is None or sig.get(key) != want` → `E_TOOL_CHANGED`; add one CLI
negative test that omits each required hash and asserts rc3. Change no other
behavior.

## What is sound

- **H1 actual host branch.** `_live_dirs(plan)` reads real `host_commands` and
  loads only signed runtime paths; a missing/absent host command raises owned
  `E_HOST_PATH` (never `KeyError`) — the parent failure is closed. The host
  branch runs with **no** `--overlay-dir`, performs **no** substitute stream
  creation, **no** `_drive_producers`, **no** shim-trace assumption, and uses
  the signed stream/socket paths verbatim; the seat side acts outside the tool.
  `CASES` enumerates **five** inherited cases (`positive-handoff`,
  `lost-completion`, `failed-verification`, `queued-ambiguous-restart`,
  `quiet-rest`) — the five-not-three requirement holds. `stagec-plan.json` has
  **zero** placeholder hits. The parent `_candidate_plan(... , _live_dirs(plan))`
  KeyError reproducer is retained as a test.
- **H2 live gate (except the field omission).** It verifies the **current**
  registry via subprocess `agent-deck list --json` (or an injected registry
  file), rejects `stopped`/`error`/`archived`, verifies profile/lane/workdir and
  both real sockets + incarnation (`E_EXPIRED`/`E_MISMATCH`/`E_REBOUND`), and
  requires `purpose == "stagec-task"` (preparation-only signatures rejected).
  Independently: a stopped-registry gate → rc3 `E_EXPIRED`; a bad socket path →
  rc3 `E_EXPIRED`; wrong lane → `E_MISMATCH`; changed entrypoint → `E_TOOL_CHANGED`;
  `purpose: preparation` → `E_NO_SIGNATURE`.
- **H3 correlated timing.** `timecheck` joins on the exact
  `(action, execution, case)` triple, with executions taken from the signed
  receipt, so an old-execution witness cannot certify a new one; requires
  `witness ack is True` **and** membership in `settled_actions` (not absence of
  `ack:false`); rejects non-finite/negative/absent uncertainty; adds uncertainty
  conservatively to detection/recovery/total before the 30/60/90 (and
  180/60/240) checks; flags duplicate witnesses, queued-only, negative/
  contradictory clocks, and all-failure corpora; reports worker duration
  separately. Independently: wrong-execution witness → rc3; `ack:false` → rc3.
- **H4 exact commands/outcomes.** All six commands run via the subprocess CLI.
  Independently with the host branch (no overlay): positive-handoff → rc0,
  `sends {worker:1, verifier:1}`, `timecheck accept`, `overlay:false`,
  `settled_actions [p6c-v1, p6c-w1]`; failed-verification → `accept-open`
  (never COMPLETE); lost-completion → `accept-open`; queued-ambiguous-restart →
  1+1 sends accept; quiet-rest → accept; rollback → rc0 archive-first
  (`rollback-report.json`).
- **No live effect.** `agent-deck list --json` unchanged (four main seats +
  stopped `06b…`/p3 fixtures); all host-path work used private tmp sockets and
  injected test executables; real registry/socket roots untouched. `pytest` →
  8 passed, but H1–H4 above were verified by direct CLI subprocess, not pytest
  alone.

## Non-blocking observations

- The `derive_config` tautological socket-dir check (`dirname(sock) ==
  dirname(sock)`) persists; the meaningful check is the later
  socket-dir-vs-producer-root comparison.
- `_CANDIDATE_HASHES` and `P6R6_ENTRY_SHA256` are constant; any future candidate
  hash change must also update these constants and the release signature.

## Effect

Verdict **FAIL** bound to `src/stagec_host.py`
`4c34b65c019ee395b194ce2d2d56ef68ffb9cddb93de278983e1e6d1858900d6` and the
hashes above, under contract `515deb16…` @ `fd497e7` and checklist
`ce7401f1…`. Admission/checklist preserved. No live seat/message/restart/timer/
Signal, wrapper edit, research, shadow or retirement occurred. Returned to cairn
and Tern for a bounded H2 repair.
