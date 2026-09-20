# S3-3 verification — green-lane adapters (verifier: Alice / aletheia-dsh)

**Row:** QUEUE S3-3 · **Producer:** kiln-flash · **Verifier:** Alice · **Date:** 2026-09-15
**Cost:** $0, local, read-only. **Artifacts:**
- `implementer/repo/scripts/experiment_20260912_transcript_mining/benchmark_adapters.py` (sha256 `0e48c02a…`, untracked)
- `implementer/repo/tests/test_benchmark_adapters_gatemem.py` (sha256 `ddbac3db…`, untracked)
- plan: `team/KILN-S3-3-ADAPTER-PLAN-20260915.md`

## Confirmed (row claims reproduce exactly)

| Claim | Result |
|---|---|
| 6 green-lane adapters in `benchmark_adapters.py` | **CONFIRMED** — GateMem (`gatemem_operator_turns`/`gatemem_record_texts`), STALE (`stale_conflict_pairs`), SWE-Together (`swetogether_operator_turns`), CodeTracer (`codetracer_trial_rows`), CSTM (`cstm_threat_rows`), HANDBOOK (`handbook_operator_turns`) |
| 10 adapter tests | **CONFIRMED** — 10 `test_*` functions in `tests/test_benchmark_adapters_gatemem.py`; `pytest -q` → **10 passed** |
| combined suites 39 passed | **CONFIRMED arithmetically** — `test_transcript_mining` 18 + `test_outcome_bundle_export` 6 + adapters 10 + `test_external_corpus_adapters` 5 = **39 passed**. NB: 5 of those are the *row-30* Claude-family tests, not S3-3; S3-3's own contribution is 10 |
| ACM documented-deferred, no schema fabricated | **CONFIRMED** — plan §Status: `mem_operations` empty in all sampled runs, no operator voice; adapter not written |
| `bash -n` / import clean | **CONFIRMED** |

Operator-voice definitions read correctly against the row-30 crux (agent/harness narration
excluded; only speaker-carrying turns / user instructions / verbatim user excerpts are voice).

## Findings (not defects in what was claimed, but the row is not finished)

1. **ADAPTERS ARE NOT WIRED INTO THE PIPELINE.** `mine.py` `SOURCES` is still
   `("claude-code", "wisp", "swe-chat", "mindforge-control")`; there is no `--source gatemem|stale|…`
   and `benchmark_adapters.py` is imported by the test only. The plan's own interface spec
   ("each adapter = a `source` value for `mine.py operator_texts()`") is unmet, so the adapters are
   not yet *reusable* by the pipeline. Self-declared in the module docstring ("lives here until the
   owner wires it into `operator_texts()`").
2. **NO PER-ADAPTER RECEIPTS / REAL-DATA SMOKE.** The plan promised "receipts per adapter" and a
   "real-data smoke count" per adapter. Only GateMem has a smoke figure, and it lives in the test
   docstring (education lane, 6,748 turns → all speaker-carrying), not asserted or receipted; the
   other 5 are synthetic-fixture-only. The QUEUE status does not claim smoke, so this is a plan-vs-
   deliverable gap, not a false claim.
3. **CodeTracer is trial-outcome level only.** Step/stage failure-onset labels (the plan's stated
   `stage/step` mapping) are explicitly deferred to a follow-up; the row label "CodeTracer-trial"
   discloses this.
4. Minor: the test file is named `…_gatemem.py` but covers all 6 adapters; both the adapter module
   and its test are **untracked** in `implementer/repo` (durability risk — same class as S3-7).

## Verdict

**PASS on the claimed deliverable** (6 adapters + 10 tests + green suites + ACM deferred + plan).
**Not yet complete as "fully reusable":** wiring into `mine.py` and per-adapter real-data smoke /
receipts are open. Recommend either (a) closing S3-3 with an explicit follow-up row for
wiring+smoke, or (b) leaving S3-3 open and marking the adapter code "unit-verified, unintegrated".

$0, no downloads, no score import. — Alice (aletheia-dsh)
