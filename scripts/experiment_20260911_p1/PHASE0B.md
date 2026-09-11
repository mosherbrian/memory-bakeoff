# STUDY-20260911-P1B — phase-0-style re-smoke record (conductor-dispatched)

Dispatch context: STUDY-20260911-P1 completed 24/24 but its behavioral
question was left UNANSWERED by a delivery defect
(`docs/STUDY-20260911-P1-results.md` root cause 1): the
`pi-perseus-recall` adapter returned a bare string from `execute()`, which
the harness recorded in the execution stream but delivered to the model as
an EMPTY toolResult; the original phase-0 gate asserted stream-level
presence only, so it passed while the agent received nothing. The conductor
ordered (2026-09-11): adapter return-shape fix + delivered-level gate
assertions in both the re-smoke and the per-slot walk + a p1b rerun
harness on the SAME frozen case set. **The walk does not run until the
conductor gate passes this receipt.**

## Changes (this record)

1. **Adapter fix** — `extensions/pi-perseus-recall/index.ts`: `execute()`
   now returns `{content:[{type:"text",text}]}` at all three return sites
   (hits / no-hits / error), the shape `pi-project-recall` always used and
   the B-round machinery demonstrably delivers. Byte-identical across arms
   B/C (unchanged single-variable discipline). index.ts sha256 after fix:
   `9be99551cca4cf8ad566b0a1fe8db402e9cb393147e3d7237a61d5bea7731fc7`.
2. **Delivered-level gate** — `run_p1b.py` `parse_delivery`/`gate_slot`,
   shared by the re-smoke and the walk: G1 parity (every project_recall
   execution must have a model-visible toolResult, same toolCallId,
   non-empty text carrying every `record-*` key from the execution
   result); G2 arm A must show zero project_recall executions; G3 arms B/C
   must deliver ≥1 record key per slot. A gate failure ABORTS the walk
   (stop-and-report — delivery defects must not silently become results).
   Both execution-stream shapes (old flat string, new `{content:[...]}`)
   are normalized, so the gate also detects any regression to the old
   defect.
3. **p1b rerun harness** — `run_p1b.py`: reuses `run_p1.py`'s frozen
   machinery verbatim via `EXPERIMENT_P1_PRIVATE` (native env hook; frozen
   files unmodified); fresh private dir `experiment-20260911-p1b` (fresh
   per-slot worktrees/stores/vaults); `setup` verified per-case hashes
   (case.json / records.json / verifier.py) IDENTICAL to the p1
   PREP_MANIFEST (freeze 4048e12 content) and asserted the study binary
   sha. Schedule reused as frozen (`schedule_p1.json`). `decide_p1.py`
   gained only the same env-var path override — decision logic untouched,
   verified to emit byte-identical output against the original p1 ledger.

## Re-smoke — all four items PASS

Receipt: `PHASE0B_RECEIPT.txt` in
`~/.local/share/memory-bakeoff/experiment-20260911-p1b/phase0b-smoke/`
(binary sha asserted before any vault operation; provenance block
recorded). Reproducible via `scripts/experiment_20260911_p1/
phase0b_smoke.py` or `run_p1b.py smoke`.

1. **Adapter as Pi recall path** — registered=True; pi-lcm ACTIVE (prime
   2.2s warm, task 3.5s, store written); `project_recall` called once
   through the real path; genuine resume (`reason='resume'`,
   injected=True).
2. **Supersession toggle** (direct vault RPC, receipt
   `phase0b_toggle.txt`): OFF `['record-new','record-old']`; ON
   `['record-new']` only.
3. **Stream-level retrieval** (retained from the original smoke; necessary
   but insufficient — the p1 defect passed exactly this level): current
   record (P1-NEW-9 + helm) in stream=True; old record (P1-OLD-1) absent
   from stream=True.
4. **DELIVERED-LEVEL GATE (new)** — exec=1, delivered non-empty=1, keys
   delivered `['record-new']`; G1 parity True (203 chars delivered,
   nothing missing); P1-NEW-9 + helm present IN THE MODEL-VISIBLE
   toolResult; P1-OLD-1 absent from delivered text. Ungated behavioral
   evidence: the final answer quotes the record verbatim — the exact
   inversion of the original smoke, whose agent reported "The
   `project_recall` tool returned **no results**".

## Verdict

**PHASE0B RE-SMOKE RECEIPT: PASS.** Stopped at the conductor gate; the
24-slot p1b walk runs only on the conductor's go (budget headroom ≈1.3 h
aggregate after this phase; walk ≈45 min machine).

## Time account

This phase (fix + harness + re-smoke + records): ≈0.5 h implementer agent.
Token/cost figures for the implementer harness: unavailable (logged as
unavailable, not zero). No GLM quota refusals (quota-stop remains in
force; the study agent under test runs on the local bosgame model).
