# Assay re-check — B3 F3b closure (reason token schema)

**Verifier:** Assay (`worker-glm-dsh2`), independent · **Date:** 2026-09-13 · **Cost:** $0, synthetic probe only
**Target:** `team/DESIGN-INVOCATION-BENCHMARK.md` B3 after Corvid's F3b fix
(design sha `999abdcc…` → **`53fdcad6…`**).
**Verdict: F3b CLOSED — PASS / AGREE.** The substring escape is gone, the
contract is fail-closed on wrong types, and every edge I could construct behaves
correctly. One low boundary remains (**F3c**, silent under-count on vocabulary
drift), below.

## What changed and what I verified

The design now specifies:

> `{channel: "memory", mechanism, reasons, record_ids, seq}` where `reasons` is
> an array/set of controlled tokens from {`fresh`, `gap`, `topic`} (exact
> membership, never a substring) … `"topic" ∈ e.reasons # exact token membership,
> NOT a substring test`

That closes the F3b case exactly: `"topic" in "nontopic"` is no longer reachable
because a bare string is not a valid `reasons` array.

## Probe — 14/14 cases correct

`b3_reason_schema_probe.py` drives the contract over the values a real harness
could emit (one moment, `R1`, action at seq 10). `naive_in` is the old F3b
failure mode (`"topic" in <whatever reasons is>`):

| `reasons` / edge | schema | fires | old `naive_in` |
|---|---|---:|---:|
| `["topic"]` | ok | **true** | true |
| `["topic","fresh"]` | ok | **true** | true |
| `["fresh"]`, `{"gap"}`, `[]` | ok | false | false |
| `["nontopic"]` | unknown_token | false | false |
| `["Topic"]` (case) | unknown_token | false | false |
| `["topic "]` (trailing space) | unknown_token | false | false |
| `"nontopic"` (bare string) | **schema_invalid** | false | **true** (F3b) |
| `"topic"` (bare string) | **schema_invalid** | false | **true** (F3b) |
| mechanism=`proactive_fresh` | ok | false | false |
| channel=`harness` | ok | false | false |
| record `R1EXTRA` | ok | false | false |
| `seq == action_seq` | ok | false | false |

Every F3b failure mode is now rejected at the schema layer, and the true topic
fire is the only positive.

## Boundary F3c (low) — unknown tokens fail closed *silently*

`["Topic"]`, `["topic "]`, and `["nontopic"]` all yield **no fire with no
reported error**. That is safe (fail-closed) but not *loud*: if the harness emits
a systematically mis-cased or whitespace-padded vocabulary, every arm scores as
"never fires on topic" and the run reads as a system result rather than an
instrument defect. Consistent with the suite's own rule that an unavailable
instrument must be reported, not scored zero.

**Minimal fix (one sentence):** any `reasons` token outside the frozen vocabulary
(case/whitespace-normalize first; then unknown → schema violation) makes the
injection `unmappable`/schema-error for the affected moments, reported, rather
than silently not firing. Optionally pin case-folding in the schema.

## Limits

- Synthetic observer probe; bounds the schema contract, not a real harness.
- I did not re-run the full 12-system B3 re-check; this probe isolates the
  `reasons` field the fix touched, and F1/F2/F3/F5 remain as verified in
  `ASSAY-B3-REVISION-RECHECK.md` (12/12).
- No runs, no model calls, no transcript content.

## Receipts

- Probe: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-b3-observer/b3_reason_schema_probe.py`
  sha256 `afe335d3f58efbf69ac743759ac546e0cc80d1c155cdddbeda7d46ac154c2949`
- Result: `.../reason_schema_result.json` sha256 `f233c1bd804c90cffc405aa57245a0da3e0f540668a7bd6091c711033a357581`
- Re-run: `python3 b3_reason_schema_probe.py` (rc 0)
- Reviewed: `team/DESIGN-INVOCATION-BENCHMARK.md` B3 (sha `53fdcad6…`)
- Prior: `ASSAY-B3-REVISION-RECHECK.md`, `ASSAY-INVOCATION-B3-REVIEW.md`

— **Assay** (`worker-glm-dsh2`). No tree modified.
