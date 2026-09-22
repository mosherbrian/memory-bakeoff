# P6-r5-launch-binding — recovery candidate check

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-22; one ≤20-minute recovery check
- **Authority:** contract `40fce2e2…` @ `e40ce397`; checklist `e47a1c29…`
- **Bound:** `67dd472d0e7f…` = `src/fixture_worker.py`
  `67dd472d0e7f2bac23bd9b7836751ab11f768c4a271443092930cecc8facc591`
- **Mode:** injected OS boundaries / private `/tmp` only; **no live
  seat/service**.

## Verdict

**FAIL** — the shipped fixture plan is not executable from its declared
preconditions, so L2 is unmet and the end-to-end acceptance cannot be reached.
The L1–L4 *code* is substantially implemented and 180 candidate + 59 core tests
pass, but the exact plan's setup step cannot produce a binding manifest.

## Bound hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/fixture_worker.py` | `67dd472d0e7f2bac23bd9b7836751ab11f768c4a271443092930cecc8facc591` |
| `src/harness.py` | `d35864757d0bb062d0bd8c58679b68f52c3edf7d093f71e22cf8c0d415298aa3` |
| `src/turn_handoff.py` | `ecbec3109defb58345e04917ae6f4d447f6da867d8ae8dd33968ca29889dc6ff` |
| `tests/test_launch_binding.py` | `461028580042ab6712a6f47d937479989aef62ce6f31b2fccd9ab3646371a735` |
| `fixture-plan.json` | `343044def70ef15f5f9fb6fc9417e39b2e88c08db3e4a5e44b2096e7c600571b` |

## Commands and results

```bash
cd campaign4/packages/P6-r5-launch-binding
PYTHONPATH=src python3 -m pytest tests/ -q        # 180 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
```
Plus executing the **exact shipped plan setup** in a fresh `/tmp` root.

## L2 — FAIL (bounded, blocking)

`setup_manifest` now **requires** explicit `--worker-stream-key` and
`--verifier-stream-key` (`harness.py:201–205`, "suffix inference is forbidden"),
and its launcher-evidence parsing reads only `session`/`stream_key`. The shipped
plan's setup step passes **neither**:

```
harness.py --plan fixture-plan.json --manifest $R/manifest.json \
  --evidence-cmd "cat $R/launcher-evidence.json" setup
```

Reproduced in a fresh `/tmp` root (with `launcher-evidence.json` containing
`{"session":…, "stream_key":…}`):

```json
{"error":"E_UNBOUND","detail":"setup needs explicit --worker-stream-key and
 --verifier-stream-key; suffix inference is forbidden","owner":"cairn"}
```

Adding `--worker-stream-key wk --verifier-stream-key vk` makes setup succeed,
proving the plan simply omits the required bindings. Two further L2 issues are
present: the `--evidence-cmd` is a `cat` of
`/tmp/p6h/launcher-evidence.json`, which **no plan step creates** (the checklist
explicitly forbids "a cat of a file nobody creates"), and the plan never invokes
the available read-only `discover_runtime` producer-root discovery. The plan is
therefore not executable from declared preconditions without an undocumented
manual step, which L2 and the plan requirements forbid.

**Required correction:** make the plan's preparation resolve the actual
session and per-seat worker/verifier stream keys from read-only discovery (e.g.
`discover_runtime` over the inventoried producer root) or an executable
allowlisted evidence command that emits them, pass them explicitly to `setup`,
create no invented launcher evidence, and re-sign the plan hash. Do not infer
keys by suffix, fabricate the runtime stream, or truncate a producer file.

## L1 / L3 / L4 — code-level status (not end-to-end accepted)

- **L1:** `test_l1_exactly_one_worker_one_verifier_send` and
  `test_l1_rerun_manufactures_no_fresh_identity` pass; `run_handoff`/outbox
  now owns the single send and the harness no longer sends a second verifier
  wake. The duplicate-sender defect does not reproduce in the unit tests.
- **L3:** `fixture_worker.py` parses only the labelled wake text and the files
  it names, with no hidden manifest reads; `test_l3_failed_check_cannot_close`
  and `test_l3_fresh_producer_unit_shapes` pass. Task texts now carry
  action/execution/attempt/step/claim/artifact/worker_claim/check.
- **L4:** `test_l4_timestamp_free_events_unmeasurable_source` passes; latency
  rows are expected to carry `source_time_known` false and unmeasurable (never
  zero) for timestamp-free `emit(end)`.
- I could not complete an independent positive end-to-end run from the shipped
  plan because its setup step fails as above; a manual run that bypassed the
  plan's setup gap (explicit keys) returned `owned-failure no-end` with zero
  sends in my harness, so I report the end-to-end result as **incomplete**
  rather than PASS. This must be re-verified once the plan is executable.

## Limitations

Simulated/injected evidence only; private `/tmp` and shimmed OS commands were
the only host operations. Stage C, live witness 15 and cairn fixture 15 remain
HELD; historical 315/245 unchanged. Per the checklist, L2 is reported FAIL, not
a non-blocking forward item. No live effect, seat action, service, wrapper edit,
Signal or clock change occurred.
