# P6-r5-launch-binding — repair-2 candidate recheck

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-22; one ≤20-minute recheck (extension-2)
- **Authority:** contract `40fce2e2…`; checklist `e47a1c29…`;
  `allocation-extension-2.md`; `director-live-gate-findings.json` + probe
- **Bound:** `cd84e8dd4db6…` = `src/harness.py`
  `cd84e8dd4db623586d960233ffc8f674c0cbfb801b4fffb5bfa9fb6289109142`
- **Archive:** `p6r5-attempt-history/repair1-pass-withheld/` (51 files)
- **Mode:** injected boundaries only; **no live seat/service**.

## Verdict

**PASS.** The two withheld L2/L4 defects are corrected. Preparation now verifies
every claimed binding against an authoritative launcher source and rejects
invented identifiers even beside unrelated valid streams; timing separates
event/onset-to-detection from dispatch and returns an explicit
UNMEASURABLE/INCOMPLETE (never `gates-hold`) when onset/source evidence is
missing. The exact revised plan runs under injection with one worker and one
verifier send, settled outbox and clean rollback; 189 candidate + 59 core tests
pass.

## Bound / probe results

| Artifact | sha256 |
|---|---|
| `src/harness.py` | `cd84e8dd4db623586d960233ffc8f674c0cbfb801b4fffb5bfa9fb6289109142` |
| `src/prepare_evidence.py` | `921a702354d7fe9c9606bd5c3322c0e770cde24938ec5a0bc3f59b553fb91bfb` |
| `src/fixture_worker.py` | `8ebb4e6593225efcde4d13f58e1c65bfabd107a2cf25443b110623f0f9860ebe` |
| `fixture-plan.json` | `06ba06dfb62778b934e5a640f3398ac593c7f53be7decffe349ef6edd30efebd` |

```bash
cd campaign4/packages/P6-r5-launch-binding
PYTHONPATH=src python3 -m pytest tests/ -q        # 189 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
```

## Supplied probe: archived bytes vs corrected bytes

| Probe | Archived repair-1 | Corrected |
|---|---|---|
| empty-root preparation with invented ids | rc **0**, emitted `invented-*` identifiers with `observed_streams: []` | rc **3** `E_UNKNOWN_SESSION` "session 'invented-session' not in launcher source (live-agent-deck)" |
| unknown-source latency row | `gates-hold` (1 success) | `unmeasurable-incomplete` — "onset/source evidence missing … event-to-detection unmeasurable; receipt-to-recovery max 1.0s reported separately" |

## Unshared cases

**L2 evidence authenticity**
- invented session → `E_UNKNOWN_SESSION`.
- real session id but invented worker/verifier stream keys → `E_UNKNOWN_SESSION`.
- unrelated valid stream present but wrong keys → rejected (`E_UNKNOWN_SESSION`/`E_UNBOUND`); unrelated streams do not bind.
- positive (fixture session list with worker/verifier ids, worker socket, both stream files) → rc0 evidence with `launcher_source: "fixture-injected:<file>"`, `observed_streams` both, and `incarnation_mtime`; a fixture run is explicitly labelled so shim identities cannot substitute for the declared live launcher path at Stage C.

**L4 timing honesty**
- unknown onset → `unmeasurable-incomplete` (never `gates-hold`).
- prompt onset after long normal work (`dispatch_at` an hour earlier) → `gates-hold` — dispatch duration is no longer used as detection.
- onset→detection 40 s → `E_GATE_DETECT` (late fails its bound).
- detection before onset → `E_BAD_SAMPLE`; `source_time_known` true with absent `source_at` → `E_BAD_SAMPLE`.

## Exact revised plan under injection

`prepare_evidence` (fixture launcher source + sock + per-seat streams) → SETUP-OK
→ `run-fixture --live` → `check-latency` → `rollback`:

```
PREP-OK / SETUP-OK
{"decision":"terminal-rest","latency_samples":2,
 "outbox_settled":["ob-…","ob-…"],"worker":{"decision":"transition-committed",…}}
worker sends: 1  verifier sends: 1
check-latency: {"verdict":"unmeasurable-incomplete","unmeasured":2,"success":2,...}
rollback: {"intents":"none-outstanding-verified","timers":"none-armed-verified",...}
```

L1 one-send holds; L3 dispatch-sufficient text consumed by the fresh producer;
L4 honestly reports the fixture's missing onset/source as unmeasurable; O
outbox settled and rollback clean; T/N retained.

## Observation (scope for Stage C, non-blocking)

To reach `gates-hold` the live fixture must supply independently recorded
fault-onset/source evidence with provenance and uncertainty in the exact plan.
The corrected checker correctly refuses to certify the campaign latency
criterion from an injected fixture that lacks it.

## Limitations

Simulated/injected evidence only. Stage C and the single live witness 15 / cairn
fixture 15 remain HELD; cumulative 345/265. No live effect, seat action, service,
wrapper edit, Signal or clock change occurred. Candidate PASS returns to Tern for
the signed exact-plan live release.
