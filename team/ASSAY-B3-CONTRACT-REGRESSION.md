# Assay — B3 contract regression (F1–F3c) + F3c closure

**Verifier:** Assay (`worker-glm-dsh2`), independent · **Date:** 2026-09-13 · **Cost:** $0, synthetic only
**Target:** `team/DESIGN-INVOCATION-BENCHMARK.md` B3 after the F3c fix
(design sha `53fdcad6…` → **`38ab58cb…`**).
**Verdict: F3c CLOSED — PASS / AGREE.** Vocabulary drift now fails loud
(`unmappable`/schema-error), not silent. One wording ambiguity remains
(**F3c-x**, below). This also consolidates the three prior B3 probes into one
durable 23-case regression.

## Consolidated regression — 23/23 correct

`b3_contract_regression.py` encodes the final observer contract in two sections.

**A) control matrix (9/9)** — only genuine topic fires score:

| control | status | fires |
|---|---|:---:|
| true topic fire (×2) | ok | **true** |
| context dump | ok | false |
| fresh-only | ok | false |
| explicit-call | ok | false |
| post-action (`seq > action`) | ok | false |
| exact tie (`seq == action`) | ok | false |
| substring collision (`R1EXTRA`) | ok | false |
| out-of-band channel (`harness`) | ok | false |

**B) reason schema (14/14)** — exact membership, F3b gone, F3c loud:

| `reasons` | normalized status | fires | raw status |
|---|---|---:|:---|
| `["topic"]`, `["topic","fresh"]` | ok | **true** | ok |
| `["fresh"]`, `{"gap"}`, `[]` | ok | false | ok |
| `["Topic"]`, `["topic "]`, `[" TOPIC ","fresh"]` | **ok (rescued)** | **true** | unknown_token |
| `["nontopic"]`, `["topic","weird"]` | **unknown_token** | false | unknown_token |
| `"nontopic"` / `"topic"` (bare string) | **schema_invalid** | false | schema_invalid |

F3c is satisfied: `["nontopic"]`, a mixed `["topic","weird"]`, and a bare string
all produce a **reported schema/unknown-token status with no fire** — an
instrument finding, not a silent "never fires on topic". `["topic"]` and
`["topic","fresh"]` remain the only positives.

## Wording ambiguity F3c-x (low)

F3c says tokens are validated **"after case/whitespace normalization"** and in
the same sentence that "an unknown/**mis-cased**/padded token makes that
injection `unmappable`". Those are two different rules:

- **reading (a)** normalize first → `["Topic"]`/`["topic "]` are rescued → fire;
- **reading (b)** validate raw → `["Topic"]`/`["topic "]` are `unknown_token` →
  `unmappable`, so a purely cosmetic harness quirk becomes an instrument failure.

The regression scores both (table column 4) and passes under (a), which is the
safer-for-scoring reading (normalize, then only truly unknown tokens are
unmappable). **Minimal fix:** one sentence pinning (a) explicitly — e.g.
"tokens are stripped and case-folded against the frozen vocabulary; only tokens
still outside it after normalization are `unmappable`" — and stating that raw
case/padding is not itself an instrument error.

## Note on consolidation

This script supersedes the standalone edges of `b3_observer_power_check.py`
(`dc145b52…`, F1), `b3_revision_recheck.py` (`757c5adb…`, F1–F5) and
`b3_reason_schema_probe.py` (`afe335d3…`, F3b/F3c). Recommend it become the
standing B3 regression guard; it exits 0 on the current contract.

## Limits

- Synthetic observer probe; bounds the contract, not a real harness/corpus.
- Reading (a) is my recommended interpretation of an ambiguous sentence; the
  design owner should pin it.
- No runs, no model calls, no transcript content.

## Receipts

- Regression: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-b3-observer/b3_contract_regression.py`
  sha256 `0906a8c4ed3875cf7426fa131bc6cd3f61411efbf50e629a850b9e71a594ec2f`
- Result: `.../contract_result.json` sha256 `91d60343eef37e585ab56269646c2000ea6ea5aee7866d06b1dbb60c2890b9f9`
- Re-run: `python3 b3_contract_regression.py` (rc 0)
- Reviewed: `team/DESIGN-INVOCATION-BENCHMARK.md` B3 (sha `38ab58cb…`)

— **Assay** (`worker-glm-dsh2`). No tree modified.
